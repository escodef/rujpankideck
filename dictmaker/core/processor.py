import sys
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
from shared.regex.utils import has_kanji, split_by_dots
from typing import List
from models.models import DictionaryList
from parsers.word_parser import WordParser
from parsers.gui_word_parser import WordParserGUI

load_dotenv()

dict_url = os.getenv("DICT_URL")
jardic_path = os.getenv("JARDIC_PATH")


class DictionaryProcessor:
    def __init__(self):
        self.is_windows = sys.platform == "win32"
        if dict_url and jardic_path:
            self.parser = (
                WordParserGUI(jardic_path) if self.is_windows else WordParser(dict_url)
            )
        self.running = True

        self.parsed_indexes = get_all_parsed_indexes()

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

    def is_word_parsed(self, word, reading_kata, index):
        if index in self.parsed_indexes:
            return True
        exists = None
        reading = jaconv.kata2hira(reading_kata)
        if has_kanji(word):
            exists = get_by_word_and_reading(word, reading)
        else:
            exists = get_by_reading(reading)

        if not exists:
            exists = get_not_found(word, reading_kata)

        return bool(exists)

    def parse_words(self, words: List[List[str]]) -> None:
        batch_size = 50
        seen_in_batch = set()
        for index, wordcsv in enumerate(words):
            if not self.running:
                save_to_sqlite(self.dictionary)
                break
            word, _, reading_raw = wordcsv[:3]
            try:
                if self.is_word_parsed(word, reading_raw, index):
                    continue
                logging.info(f"Parsing word: {word} at index {index}")

                translations = self.parser.parse_word(wordcsv)

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
                    add_not_found(word, reading_raw)

                if len(self.dictionary) >= batch_size:
                    save_to_sqlite(self.dictionary)
                    self.dictionary.clear()
                    seen_in_batch.clear()
                    logging.info("Batch saved to database.")

            except Exception as e:
                logging.error(f"Error when parsing {word[0]}: {e}")
                logging.error(traceback.format_exc())
                continue
