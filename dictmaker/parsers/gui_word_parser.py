import logging
import re
import jaconv

from typing import List
from pywinauto import Application
from pywinauto.controls.uia_controls import ListViewWrapper
from pywinauto.findwindows import ElementNotFoundError
from models.models import Translation
from shared.regex.utils import has_cyrillic, has_kanji, split_by_dots


class WordParserGUI:
    JAP_LETTERS = r"\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF"
    YARXI_RE = re.compile(r"^\[([a-zA-Z-:]+)\]")
    JAP_RE = re.compile(rf"^[^\s\w]*[\[\]\/{JAP_LETTERS}\s,]+", re.UNICODE)
    LIST_RE = re.compile(r"\d+[\.\)]:?\s+([^:\n]+)")
    LETTER_LIST_RE = re.compile(r"^[а-яёA-Za-z]\)\s?")
    JAP_IN_BRACKETS_RE = re.compile(rf"\(.*?[{JAP_LETTERS}].*?\)|\[{JAP_LETTERS}].*?\]")

    def __init__(self, jardic_path: str):
        self.logger = logging.getLogger(__name__)
        try:
            self.app = Application(backend="uia").connect(
                title_re=".*Jardic Pro.*", timeout=2
            )
        except ElementNotFoundError, Exception:
            self.logger.debug("App not found. Starting up...")
            Application(backend="uia").start(jardic_path)
            self.app = Application(backend="uia").connect(
                title_re=".*Jardic Pro.*", timeout=10
            )

        self.win = self.app.window(title_re=".*Jardic.*")
        self.win.wait("ready", timeout=10)

    def switch_tab(self, tab_index: int):
        tab_ctrl = self.win.child_window(control_type="Tab")
        tab_items = tab_ctrl.children(control_type="TabItem")

        if tab_index < 0 or tab_index >= len(tab_items):
            self.logger.error(f"Tab index {tab_index} out of range")
            return

        tab_item = tab_items[tab_index]
        tab_item.select()

    def parse_word(self, wordcsv: List[str]) -> List[Translation] | None:
        word = wordcsv[0]
        kata = wordcsv[2]

        try:
            input_box = self.win.child_window(auto_id="202", control_type="Edit")
            input_box.set_edit_text("")

            tab_idx = 3 if has_kanji(word) else 2
            self.switch_tab(tab_idx)
            input_box.type_keys(word, with_spaces=True)
            pane = self.win.child_window(control_id=201)
            table = self.win.child_window(control_id=100)
            table_obj: ListViewWrapper = table.wrapper_object()

            last_article = ""
            while True:
                current_article = pane.get_value().replace("\r", "\n").strip()

                is_article_correct = self.is_article_correct(
                    current_article, word, kata
                )

                if not is_article_correct:
                    if current_article != last_article:
                        table_obj.type_keys("{VK_DOWN}")
                    break

                last_article = current_article
                table_obj.type_keys("{VK_UP}")

            results: list[str] = []

            last_article = ""
            while True:
                current_article = pane.get_value().replace("\r", "\n").strip()
                is_article_correct = self.is_article_correct(
                    current_article, word, kata
                )

                if not is_article_correct:
                    break

                results.append(current_article)
                last_article = current_article
                table_obj.type_keys("{VK_DOWN}")

            return self.process_results(results)

        except Exception as e:
            self.logger.error(f"parse_word(): {e}")
            raise e

    def process_results(self, results: list[str]) -> List[Translation]:
        ts: List[Translation] = []
        for entry in results:
            entry = entry.replace("\r", "")
            sents = entry.split("\n")
            strip = 1

            yarxi_reading = self.YARXI_RE.findall(sents[1])

            self.logger.debug(yarxi_reading)

            if yarxi_reading:
                word = sents[0]
                reading = jaconv.alphabet2kana(
                    yarxi_reading[0].replace("-", "").replace(":", "-")
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

            mainsense = self.get_mainsense(senses)

            t = Translation(
                word=word, reading=reading, mainsense=mainsense, senses=senses
            )

            ts.append(t)

        return ts

    def get_mainsense(self, article: str) -> str:
        lines = article.split("\n")

        if "2-я основа" in lines[0]:
            article = "\n".join(lines[3:])

        if "уст." in lines[0] or "сущ." in lines[0] or "ономат." in lines[0]:
            article = "\n".join(lines[1:])

        art_contain_list = self.LIST_RE.search(article)

        if art_contain_list:
            senses = re.split(r"\d+[\.\)]:?\s*", article.strip())
            senses = [p.strip(" ;\n") for p in senses if p.strip()]
            senses = [item.strip(" ;\n") for s in senses for item in s.split(";")]
        else:
            senses = article.split(";")

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
            if len(result + part) > 25 or not part:
                break
            result = result + ", " + part
            i = i + 1

        return (
            result
            if result.count("(") == result.count(")")
            else result.replace("(", "").replace(")", "")
        )

    def is_article_correct(self, article_text: str, word: str, kata: str) -> bool:
        lines = article_text.splitlines()
        if not lines:
            return False

        if self.YARXI_RE.match(lines[1]):
            kana_line = jaconv.alphabet2kana(lines[1].replace("[", "").replace("]", ""))
            kanji_line = lines[0].split()[0] if has_kanji(lines[0]) else ""
            kana_variants = [kana_line]
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
