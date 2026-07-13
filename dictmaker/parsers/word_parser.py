import logging
import html2text
import requests

from parsers.base import BaseWordParser
from models.models import Translation
from bs4 import BeautifulSoup, Tag, NavigableString
from parsers.article_parser import ArticleParser
from typing import List, override
from parsers.example_parser import ExampleParser


class WordParser(BaseWordParser):
    def __init__(self, jardic_url: str):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.text_parser = ArticleParser()

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0"
            }
        )

        self.example_parser = ExampleParser()

        self.short_article_template = r"^[^\n]*\n\[[^\]]+\]$"

        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True

        self.jardic_url = jardic_url

    @override
    def parse_article(self, wordcsv: List[str]) -> List[Translation] | None:
        word = wordcsv[0]
        katakana_reading = wordcsv[2]

        try:
            url = f"{self.jardic_url}?q={word}&pg=0&dic_jardic=1&dic_warodai=1&dic_yarxi=1&sw=1536"

            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            tab = soup.find(id="tabContent")

            if not tab:
                self.logger.debug(f"No tabContent found for word: {word}")
                return None

            rows = tab.select("tr")
            if not rows:
                self.logger.debug(f"No rows in tab for word: {word}")
                return None

            self.logger.debug(f"Found {len(rows)} rows inside tabContent for: {word}")

            translations_accumulated: List[Translation] = []

            for row in rows:
                td = row.find("td") or row.select_one('td[id^="word-"]')

                if not td:
                    continue

                text = self.h2t.handle(str(td))

                if not text:
                    continue

                lines = [line.strip() for line in text.splitlines()]
                cleaned_text = "\n".join(lines).strip()

                if self.text_parser.is_article_correct(
                    cleaned_text, word, katakana_reading
                ):
                    self.logger.debug(f"Matched correct article for: {word}")

                    parsed_ts = self.text_parser.process_results([cleaned_text])
                    if parsed_ts:
                        translations_accumulated.extend(parsed_ts)
                else:
                    self.logger.debug(
                        f"Skipping article (incorrect match) for: {word} with reading: {katakana_reading}"
                    )

            return translations_accumulated if translations_accumulated else None

        except Exception as e:
            self.logger.error(f"Error parsing word {word}: {e}")
            return None

    def _extract_rendered_text(self, element: Tag) -> str:
        result: List[str] = []

        for child in element.descendants:
            if isinstance(child, NavigableString):
                txt = child.strip()
                if txt:
                    result.append(txt)

            elif isinstance(child, Tag):
                if child.name == "br":
                    result.append("\n")

        text = " ".join(result)
        text = text.replace("\n\n", "\n").strip()
        return text
