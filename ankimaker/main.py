import os
import logging
import jaconv
import shutil
import hashlib

from anki.collection import Collection
from anki.exporting import AnkiPackageExporter
from template import CARD_CSS, JP_RU_FRONT, JP_RU_BACK, RU_JP_FRONT, RU_JP_BACK

from shared.config import TTS_OUTPUT_FOLDER
from shared.database.db_session import init_db
from shared.database.utils import get_by_word_and_reading, get_by_reading
from shared.csv import get_words
from shared.regex import has_kanji
from shared.media import get_audio_filename


def generate_guid(word: str, reading: str) -> str:
    return hashlib.md5(f"{word}{reading}".encode()).hexdigest()


def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    temp_db = "temp_col.anki2"
    if os.path.exists(temp_db):
        os.remove(temp_db)

    col = Collection(temp_db)
    try:
        model = col.models.by_name("rujpankideck")
        if not model:
            model = col.models.new("rujpankideck")
            col.models.add_field(model, col.models.new_field("Word"))
            col.models.add_field(model, col.models.new_field("Reading"))
            col.models.add_field(model, col.models.new_field("MainSense"))
            col.models.add_field(model, col.models.new_field("Senses"))

        model["css"] = CARD_CSS

        t1 = col.models.new_template("JP - RU")
        t1["qfmt"] = JP_RU_FRONT
        t1["afmt"] = JP_RU_BACK
        col.models.add_template(model, t1)

        t2 = col.models.new_template("RU - JP")
        t2["qfmt"] = RU_JP_FRONT
        t2["afmt"] = RU_JP_BACK
        col.models.add_template(model, t2)
        col.models.add(model)

        words_dict = {f"{w[0]}-{w[2]}": w for w in get_words()[:21000]}
        index = 1

        for word in words_dict.values():
            if index > 20000:
                logging.info("20000 words found")
                break
            end_range = (index // 5000) * 5 + 5
            range_str = f"{end_range:02}k"

            current_deck_id_jp = col.decks.id(f"Слова::Японский - Русский::{range_str}")
            current_deck_id_ru = col.decks.id(f"Слова::Русский - Японский::{range_str}")

            assert current_deck_id_jp is not None, "Не удалось получить ID колоды JP"
            assert current_deck_id_ru is not None, "Не удалось получить ID колоды RU"

            reading = jaconv.kata2hira(word[2])
            if has_kanji(word[0]):
                res = get_by_word_and_reading(word[0], reading)
                translations = [res] if res is not None else []
            else:
                translations = get_by_reading(reading)

            if not translations:
                logging.warning(
                    f"Не найден перевод для слова {word[0]} с чтением {word[2]}"
                )
                continue

            for translation in translations:
                index += 1
                word_val = translation.word.replace("\r", "").strip()
                reading_val = (
                    translation.reading.replace("\r\n", "<br>")
                    .replace("\n", "<br>")
                    .strip()
                )
                mainsense = (
                    translation.mainsense.replace("\r\n", "<br>")
                    .replace("\n", "<br>")
                    .strip()
                )
                senses = (
                    translation.senses.replace("\r\n", "<br>")
                    .replace("\n", "<br>")
                    .strip()
                )

                note = col.new_note(model)
                note.guid = generate_guid(word_val, reading_val)
                note["Word"] = word_val
                note["Reading"] = reading_val
                note["MainSense"] = mainsense
                note["Senses"] = senses

                audio_filename = get_audio_filename(word[0], word[2])
                audio_path = os.path.join(TTS_OUTPUT_FOLDER, audio_filename)

                if os.path.exists(audio_path):
                    col.media.add_file(audio_path)
                    note["Reading"] += f" [sound:{audio_filename}]"

                col.add_note(note, current_deck_id_jp)

                cards = note.cards()
                if len(cards) > 1:
                    card_ru = cards[1]
                    card_ru.did = current_deck_id_ru
                    col.update_card(card_ru)

        exporter = AnkiPackageExporter(col)
        output_file = "japanese_vocab.apkg"
        exporter.exportInto(output_file)
        logging.info(f"Готово! Файл создан: {output_file}")

    finally:
        col.close()
        if os.path.exists(temp_db):
            os.remove(temp_db)
        if os.path.exists(temp_db + ".log"):
            os.remove(temp_db + ".log")
        if os.path.exists("temp_col.media"):
            shutil.rmtree("temp_col.media")


if __name__ == "__main__":
    main()
