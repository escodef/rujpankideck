import logging
import re
import html2text
import requests

from models.models import Translation
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List
from parsers.example_parser import ExampleParser


class WordParser:
    def __init__(self, jardic_url: str):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0"
            }
        )

        self.example_parser = ExampleParser()

        self.short_article_template = r"^[^\n]*\n\[[^\]]+\]$"

        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True

        self.jardic_url = jardic_url

    def parse_word(self, wordlist: List[str]) -> Translation | None:
        word = wordlist[0]
        katakana_reading = wordlist[2]

        try:
            url = f"{self.jardic_url}?q={word}&pg=0&sw=1472&dic_yarxi=1"

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

            self.logger.debug(len(rows))

            for row in rows:
                td = row.find("td") or row.select_one('td[id^="word-"]')

                if not td:
                    self.logger.debug(f"No matching td in row for word: {word}")
                    continue

                text = self.h2t.handle(str(td))

                if not text:
                    self.logger.debug(f"No text extracted for word: {word}")
                    continue

                lines = text.splitlines()

                lines = [line.strip() for line in lines]

                text = "\n".join(lines)

                if re.search(self.short_article_template, text, re.MULTILINE):
                    self.logger.debug(text)
                    self.logger.debug("this is a short article")

                    senses = re.sub(r"^.*\n\[.*\]\n", "", text, flags=re.DOTALL)

                    mainsense_match = re.search(r"[ЁёА-я].*?;", text)
                    mainsense = (
                        mainsense_match.group().rstrip(";")
                        if mainsense_match
                        else senses
                    )

                    self.logger.debug(senses)

                    t = Translation(
                        word=word,
                        reading=katakana_reading,
                        mainsense=mainsense,
                        senses=senses.strip(),
                    )
                else:
                    self.logger.debug("this is a long article")
                    sep = "\nВ сочетаниях"
                    text, _, _ = text.partition(sep)
                    self.logger.debug(text)

                    pattern = re.compile(rf"^{re.escape(word)}.*$", re.MULTILINE)

                    matches: List[str] = pattern.findall(text)
                    mainsense = matches[0].replace(word, "").strip()

                    self.logger.debug("matches found")
                    self.logger.debug(matches)

                    senses = "\n".join(matches[1:])

                    t = Translation(
                        word=word,
                        reading=katakana_reading,
                        mainsense=mainsense,
                        senses=senses,
                    )

                    # t.examples = self.example_parser.parse_word(word)

                return t

        except Exception as e:
            self.logger.error(f"Error parsing word {word}: {e}")
            return None

    def _extract_rendered_text(self, element: Tag) -> str:
        result: list[str] = []

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
