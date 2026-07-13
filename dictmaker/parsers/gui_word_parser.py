import logging

from pywinauto.controls.uiawrapper import UIAWrapper
from parsers.base import BaseWordParser
from parsers.article_parser import ArticleParser
from typing import List, override
from pywinauto import Application, WindowSpecification
from pywinauto.controls.uia_controls import (
    ListViewWrapper,
    TabControlWrapper,
    EditWrapper,
)
from models.models import Translation
from parsers.example_parser import ExampleParser
from shared.regex import (
    has_kanji,
)


class WordParserGUI(BaseWordParser):
    def __init__(self, jardic_path: str):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.text_parser = ArticleParser()
        self.example_parser = ExampleParser()

        try:
            self.app: Application = Application(backend="uia").connect(
                title_re=".*Jardic Pro.*", timeout=2
            )
        except Exception:
            self.logger.debug("Приложение не запущено. Запускаем...")
            Application(backend="uia").start(jardic_path)
            self.app = Application(backend="uia").connect(
                title_re=".*Jardic Pro.*", timeout=10
            )

        self.win: WindowSpecification = self.app.window(title_re=".*Jardic.*")
        self.win.wait("ready", timeout=10)

    def switch_tab(self, tab_index: int):
        tab_ctrl_spec: WindowSpecification = self.win.child_window(control_type="Tab")
        tab_ctrl: TabControlWrapper = tab_ctrl_spec.wrapper_object()
        tab_items: List[UIAWrapper] = tab_ctrl.children(control_type="TabItem")

        self.logger.debug(f"Tab items: {tab_items}")

        if tab_index < 0 or tab_index >= len(tab_items):
            self.logger.error(f"Индекс вкладки {tab_index} за пределами массива")
            return

        tab_item = tab_items[tab_index]
        tab_item.select()

    @override
    def parse_article(self, wordcsv: List[str]) -> List[Translation] | None:
        word = wordcsv[0]
        kata = wordcsv[2]

        try:
            input_box_spec: WindowSpecification = self.win.child_window(
                auto_id="202", control_type="Edit"
            )
            input_box: EditWrapper = input_box_spec.wrapper_object()
            input_box.set_edit_text("")

            tab_idx: int = 2 if has_kanji(word) else 1
            self.switch_tab(tab_idx)

            input_box.type_keys(word, with_spaces=True)

            pane_spec: WindowSpecification = self.win.child_window(control_id=201)
            pane: EditWrapper = pane_spec.wrapper_object()

            table: WindowSpecification = self.win.child_window(control_id=100)
            table_obj: ListViewWrapper = table.wrapper_object()

            last_article: str = ""
            while True:
                current_article: str = pane.get_value().replace("\r", "\n").strip()

                is_article_correct = self.text_parser.is_article_correct(
                    current_article, word, kata
                )

                if not is_article_correct:
                    if current_article != last_article:
                        table_obj.type_keys("{VK_DOWN}")
                    break

                last_article = current_article
                table_obj.type_keys("{VK_UP}")

            results: List[str] = []

            while True:
                current_article: str = pane.get_value().replace("\r", "\n").strip()
                is_article_correct = self.text_parser.is_article_correct(
                    current_article, word, kata
                )

                if not is_article_correct:
                    break

                results.append(current_article)
                table_obj.type_keys("{VK_DOWN}")

            return self.text_parser.process_results(results)

        except Exception as e:
            self.logger.error(f"parse_word(): {e}")
            raise e
