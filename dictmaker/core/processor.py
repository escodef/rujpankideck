import os
import logging
import traceback
import jaconv

from dotenv import load_dotenv
from shared.database.utils import (
    save_to_sqlite,
    get_by_reading,
    get_by_word_and_reading,
    add_not_found,
    get_not_found,
    get_all_parsed_indexes,
)
from shared.regex import has_kanji, split_by_dots
from typing import List
from models.models import DictionaryList
from parsers.base import BaseWordParser
from sqlalchemy.orm import Session

load_dotenv()

dict_url = os.getenv("DICT_URL", "https://www.jardic.ru/search/search_r.php")
jardic_path = os.getenv(
    "JARDIC_PATH", "C:\\Program Files (x86)\\JardicPro\\JardicPro.exe"
)


class DictionaryProcessor:
    def __init__(self, parser: BaseWordParser, session: Session):
        self.parser = parser
        self.session = session
        self.running = True

        self.parsed_indexes = get_all_parsed_indexes(self.session)
        self.dictionary: DictionaryList = list()

    def stop(self):
        self.running = False

    def _get_variants(self, text: str) -> set[str]:
        if not text:
            return set()
        return {v.strip() for v in split_by_dots(text) if v.strip()}

    def is_duplicate_translation(
        self, translation, seen_set: set[tuple[str, str]]
    ) -> bool:
        new_words = self._get_variants(translation.word)
        new_reading = translation.reading

        for w in new_words:
            if (w.strip("…"), new_reading.strip("…")) in seen_set:
                return True
        return False

    def _add_to_seen(self, translation, seen_set: set[tuple[str, str]]):
        new_words = self._get_variants(translation.word)
        new_reading = translation.reading
        for w in new_words:
            clean_word = w.strip("…")
            clean_reading = new_reading.strip("…")
            seen_set.add((clean_word, clean_reading))

    def is_word_parsed(self, word, reading_kata, index) -> bool:
        if index in self.parsed_indexes:
            return True
        reading = jaconv.kata2hira(reading_kata)
        if has_kanji(word):
            exists = get_by_word_and_reading(word, reading, self.session)
        else:
            exists = get_by_reading(reading, session=self.session)

        if not exists:
            exists = get_not_found(word, reading_kata, self.session)

        return bool(exists)

    def parse_words(self, words: List[List[str]]) -> None:
        batch_size = 50
        seen_in_batch = set()
        for index, wordcsv in enumerate(words):
            if not self.running:
                save_to_sqlite(self.dictionary, self.session)
                break
            word, _, reading_raw = wordcsv[:3]
            try:
                if self.is_word_parsed(word, reading_raw, index):
                    continue
                logging.info(f"Parsing word: {word} at index {index}")

                translations = self.parser.parse_article(wordcsv)

                if translations is None:
                    continue

                logging.info(f"found translations: {translations}")

                for translation in translations:
                    if not self.is_duplicate_translation(translation, seen_in_batch):
                        translation.index_csv = index
                        self.dictionary.append(translation)
                        self._add_to_seen(translation, seen_in_batch)
                    else:
                        logging.warning(f"found dup translation: {translation.word}...")

                if len(translations) == 0:
                    logging.warning(
                        f"translations len: {len(translations)} for word {word} at index {index}"
                    )
                    add_not_found(word, reading_raw, self.session)

                if len(self.dictionary) >= batch_size:
                    save_to_sqlite(self.dictionary, self.session)
                    self.session.commit()
                    self.dictionary.clear()
                    seen_in_batch.clear()
                    logging.info("Batch saved to database.")

            except Exception as e:
                logging.error(f"Error when parsing {word[0]}: {e}")
                logging.error(traceback.format_exc())
                continue
