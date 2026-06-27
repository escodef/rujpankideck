import logging
from shared.config import CSV_PATH
import csv

from typing import List

EXCLUDED_POS = frozenset(["助動詞", "記号", "動詞-接尾", "助詞"])


def get_words() -> List[List[str]]:
    words = []
    line_number = 0

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        csv_file = csv.reader(f)
        logging.debug(f"Открытие файла: {CSV_PATH}")

        try:
            for row in csv_file:
                line_number += 1
                if row[1] in EXCLUDED_POS or "【" in row[0]:
                    continue
                words.append(row)
        except csv.Error as e:
            logging.error(f"Ошибка в строке №{line_number}")
            logging.error(f"Тип ошибки: {e}")
            raise

        return words
