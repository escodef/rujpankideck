from typing import List
import re


def has_cyrillic(text: str) -> bool:
    return bool(re.search("[\u0400-\u04ff]", text))


def has_kanji(text: str) -> bool:
    kanji_regex = r"[\u4E00-\u9FFF]"
    return bool(re.search(kanji_regex, text))


def split_by_dots(text: str) -> List[str]:
    return re.split(r"・|･|, |,", text)


def get_yarxi_readings(text: str) -> List[str]:
    return re.findall(r"\[([^\]]+)\]", text)
