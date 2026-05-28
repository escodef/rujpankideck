import re
import logging
import requests
import html2text
from typing import List
from bs4 import BeautifulSoup
import pykakasi

from models.models import Example


class ExampleParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
            }
        )

        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True

        self.kks = pykakasi.kakasi()

        self.article_example_re = re.compile(r"^(.+?)\s+([А-Яа-яЁё].*)$")

    def parse(self, word: str, article_text: str) -> List[Example]:

        examples = self.extract_from_article(word, article_text)

        if not examples:
            self.logger.debug(f"В статье нет примеров для '{word}'. Ищем на Tatoeba...")
            examples = self.extract_from_tatoeba(word)

        return examples or []

    def _convert_to_kana(self, text: str) -> str:
        """Переводит кандзи в хирагану с помощью pykakasi."""
        result = self.kks.convert(text)
        return "".join([item["hira"] for item in result])

    def extract_from_article(self, word: str, article_text: str) -> List[Example]:
        """Извлекает примеры прямо из распарсенного текста статьи Jardic."""
        examples = []

        for line in article_text.splitlines():
            line = line.strip()
            match = self.article_example_re.search(line)

            if match:
                ja_part = match.group(1).strip()
                ru_part = match.group(2).strip().rstrip(";")

                ja_part = re.sub(r"^[\d\)\.:\s]+", "", ja_part)

                ja_part = ja_part.replace("～", word)

                if not ja_part or len(ja_part) < 2:
                    continue

                re_part = self._convert_to_kana(ja_part)
                examples.append(Example(ja=ja_part, re=re_part, tr=ru_part))

        return examples

    def extract_from_tatoeba(self, word: str) -> List[Example]:
        tatoeba_url = f"https://www.jardic.ru/search/search_r.php?q={word}&pg=0&dic_tatoeba=1&sw=1472"
        examples = []

        try:
            response = self.session.get(tatoeba_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            tab = soup.find(id="tabContent")

            if not tab:
                return []

            rows = tab.select("tr")
            for row in rows[:5:2]:
                td = row.find("td") or row.select_one('td[id^="word-"]')
                if not td:
                    continue

                text = self.h2t.handle(str(td)).strip()
                if text:
                    sents = text.split("\n")
                    if len(sents) >= 2:
                        ja = sents[0].strip()
                        tr = sents[1].strip()
                        re_part = self._convert_to_kana(ja)
                        examples.append(Example(ja=ja, re=re_part, tr=tr))

            return examples

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге Tatoeba для '{word}': {e}")
            return []
