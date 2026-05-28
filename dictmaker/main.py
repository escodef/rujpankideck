import signal
import logging
from shared.database.db_session import init_db, SessionLocal
from shared.database.utils import save_to_sqlite
from shared.csv.utils import get_words
from core.processor import DictionaryProcessor


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dictmaker/logs/parser.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def main():
    init_db()
    session = SessionLocal()
    processor = DictionaryProcessor()

    def signal_handler(signum, frame):
        logging.info("Gracefully shutting down...")
        processor.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        words_to_parse = get_words()
        processor.parse_words(words_to_parse[:25])
        save_to_sqlite(processor.dictionary)

        logging.info("Parse done")
    finally:
        session.close()
        logging.info("Session closed.")


if __name__ == "__main__":
    main()
