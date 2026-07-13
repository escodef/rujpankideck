from shared.regex import has_cyrillic, get_yarxi_readings, has_kanji, split_by_dots
import jaconv
from typing import List
import logging
import re

from models.models import Translation


class ArticleParser:
    JAP_LETTERS = r"\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF"
    YARXI_RE = re.compile(r"\[([a-z-:]+)\]")
    BIG_YARXI_RE = re.compile(r"^([一-龯]+)\s+([а-яА-ЯёЁ].+)$")
    JAP_RE = re.compile(rf"^[^\s\w]*[\[\]\/{JAP_LETTERS}\s,]+", re.U)
    LIST_RE = re.compile(r"\d+[\.\)]:?\s+([^:\n]+)")
    LETTER_LIST_RE = re.compile(r"^[а-яёA-Za-z]\)\s?")
    JAP_IN_BRACKETS_RE = re.compile(rf"\(.*?[{JAP_LETTERS}].*?\)|\[{JAP_LETTERS}].*?\]")

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_results(self, results: List[str]) -> List[Translation]:
        ts: List[Translation] = []
        for entry in results:
            entry = entry.replace("\r", "")
            sents = entry.split("\n")
            strip: int = 1

            yarxi_reading = self.YARXI_RE.findall(" ".join(sents[1:4]))

            self.logger.debug(yarxi_reading)
            big_yarxi = self.BIG_YARXI_RE.search(sents[0])
            self.logger.debug(big_yarxi)

            mainsense = None

            if big_yarxi:
                word = big_yarxi.group(1)
                reading = jaconv.alphabet2kana(
                    text=yarxi_reading[0].replace("-", "").replace(":", "-")
                )
                mainsense = self.get_mainsense(sents[0])
            elif yarxi_reading:
                word = sents[0]
                reading = jaconv.alphabet2kana(
                    text=yarxi_reading[0].replace("-", "").replace(":", "-")
                )
                strip = 2
            else:
                reading = entry.splitlines()[0].strip()
                if not has_cyrillic(sents[1]):
                    word = sents[1]
                    strip = 2
                else:
                    word = reading

            try:
                empty_line_index = sents.index("", strip)
                content_lines = sents[strip:empty_line_index]
            except ValueError:
                content_lines = sents[strip:]

            senses = "\n".join(content_lines).strip()
            tail = sents[strip:]
            is_article_recur = (
                senses.startswith(("см.", "кн. см."))
                or (len(tail) > 0 and " см. " in tail[0])
                or (len(tail) > 1 and "англ." in tail[0] and " см. " in tail[1])
            )

            if is_article_recur:
                continue

            if not mainsense:
                mainsense = self.get_mainsense(senses)

            t = Translation(
                word=word, reading=reading, mainsense=mainsense, senses=senses
            )

            ts.append(t)

        return ts

    def get_mainsense(self, article: str) -> str:
        big_yarxi = self.BIG_YARXI_RE.search(article.split("\n")[0])

        if big_yarxi:
            self.logger.debug("большая статья яркси")
            self.logger.debug(big_yarxi)
            return big_yarxi.group(2)

        lines = article.split("\n")

        if "2-я основа" in lines[0]:
            self.logger.debug(f"слово было во второй основе в строке: {lines[0]}")
            article = "\n".join(lines[3:])

        if "уст." in lines[0] or "сущ." in lines[0] or "ономат." in lines[0]:
            cleaned_label = re.sub(r"\b(уст|сущ|ономат|связ)\b\.?", "", lines[0])
            cleaned_label = re.sub(rf"[{self.JAP_LETTERS}\s\d\W]+", "", cleaned_label)

            if not has_cyrillic(cleaned_label):
                self.logger.debug(f"найдено пояснение в строке: {lines[0]}")
                article = "\n".join(lines[1:])
            else:
                lines[0] = re.sub(r"^\s*(уст|сущ|ономат|связ)\b\.?\s*", "", lines[0])
                article = "\n".join(lines)

        art_contain_list = self.LIST_RE.search(article)

        if art_contain_list:
            self.logger.debug("статья содержит список")
            senses = re.split(r"\d+[\.\)]:?\s*", article.strip())
            self.logger.debug(f"после разделения по цифрам: {senses}")
            senses = [p.strip(" ;\n") for p in senses if p.strip()]
            self.logger.debug(f"после удаления пустых строк: {senses}")
            senses = [item.strip(" ;\n") for s in senses for item in s.split(";")]
            self.logger.debug(f"после разделения по комам: {senses}")
        else:
            senses = article.split(";")
            self.logger.debug(
                f"статья не содержит списка, после разделения по комам: {senses}"
            )

        part = senses[0].strip("\n")
        result = part.partition(":")[-1].strip(" ;\n") or part.strip(" ;\n")
        result = re.sub(self.JAP_RE, "", result)
        result = re.sub(self.LETTER_LIST_RE, "", result)
        result = re.sub(self.JAP_IN_BRACKETS_RE, "", result).strip(" .")
        i = 1

        while i < len(senses):
            part = senses[i].strip()
            part = part.partition(":")[-1].strip(" ;\n") or part.strip(" ;\n")
            part = re.sub(self.JAP_RE, "", part)
            part = re.sub(self.LETTER_LIST_RE, "", part)
            part = re.sub(self.JAP_IN_BRACKETS_RE, "", part).strip(" .")

            if re.search(rf"[{self.JAP_LETTERS}]", part):
                break

            if len(result + part) > 25 or not part:
                break
            result = result + ", " + part
            i = i + 1

        result = re.sub(r"\s*\([а-яёА-ЯЁ]+\.\s*.+?\)\s*", "", result).strip()

        return (
            result
            if result.count("(") == result.count(")")
            else result.replace("(", "").replace(")", "")
        )

    def is_article_correct(self, article_text: str, word: str, kata: str) -> bool:
        lines = article_text.splitlines()
        self.logger.debug(" ".join(lines[1:5]))
        if not lines:
            return False

        if self.YARXI_RE.search(" ".join(lines[1:5])):
            self.logger.debug("распознана yarxi статья")
            romaji_readings = get_yarxi_readings(lines[1])
            kanji_line = lines[0].split()[0] if has_kanji(lines[0]) else ""
            kana_variants = [jaconv.alphabet2kana(r) for r in romaji_readings]
            kanji_variants = [kanji_line.strip()]
        else:
            kana_line = lines[0]
            kanji_line = lines[1] if has_kanji(lines[1]) else ""
            kana_variants = [v.strip() for v in split_by_dots(kana_line)]
            kanji_variants = [v.strip() for v in split_by_dots(kanji_line)]

        self.logger.debug(f"kana_variants {kana_variants}")
        self.logger.debug(f"kanji_variants {kanji_variants}")
        reading = jaconv.kata2hira(kata)

        self.logger.debug(f"Got reading {reading}")

        reading_ok = (
            reading in kana_variants
            or kata in kana_variants
            or word in kana_variants
            or f"…{reading}" in kana_variants
            or f"{reading}…" in kana_variants
            or (
                reading.endswith("する")
                and len(reading) > 2
                and reading.removesuffix("する") in kana_variants
            )
        )

        kanji_ok = word in kanji_variants

        if reading_ok or kanji_ok:
            return True

        self.logger.debug(
            f"Article {article_text} incorrect for word {word} with reading {reading} and kata {kata}"
        )
        return False
