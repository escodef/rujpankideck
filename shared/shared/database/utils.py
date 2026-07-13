from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .db_session import get_session
from .models import ExampleTable, NotFoundTable, TranslationTable


def save_to_sqlite(dictionary: List, session: Session | None = None) -> None:
    def _save(sess: Session):
        for item in dictionary:
            db_translation = TranslationTable(
                word=item.word,
                reading=item.reading,
                mainsense=item.mainsense,
                senses=item.senses,
                index_csv=item.index_csv,
            )
            for ex in item.examples:
                db_translation.examples.append(
                    ExampleTable(ja=ex.ja, re=ex.re, tr=ex.tr)
                )
            sess.add(db_translation)

    if session:
        _save(session)
    else:
        with get_session() as new_session:
            _save(new_session)


def add_not_found(word: str, reading: str, session: Session | None = None) -> None:
    db_val = NotFoundTable(word=word, reading=reading)
    if session:
        session.add(db_val)
    else:
        with get_session() as new_session:
            new_session.add(db_val)


def get_not_found(
    word: str, reading: str, session: Session | None = None
) -> NotFoundTable | None:
    if session:
        return (
            session.query(NotFoundTable)
            .filter(NotFoundTable.word == word, NotFoundTable.reading == reading)
            .first()
        )
    with get_session() as new_session:
        return (
            new_session.query(NotFoundTable)
            .filter(NotFoundTable.word == word, NotFoundTable.reading == reading)
            .first()
        )


def get_by_word_and_reading(
    word: str, reading: str, session: Session | None = None
) -> TranslationTable | None:
    if session:
        return (
            session.query(TranslationTable)
            .filter(
                TranslationTable.word.contains(word),
                TranslationTable.reading == reading,
            )
            .first()
        )
    with get_session() as new_session:
        return (
            new_session.query(TranslationTable)
            .filter(
                TranslationTable.word.contains(word),
                TranslationTable.reading == reading,
            )
            .first()
        )


def get_by_reading(
    reading: str, limit: int = 3, session: Session | None = None
) -> List[TranslationTable]:
    pattern_middle = f"%・{reading}・%"
    pattern_middle_spaced = f"%・ {reading} ・%"
    pattern_end = f"%・{reading}"
    pattern_end_spaced = f"%・ {reading}"
    pattern_start_spaced = f"{reading} ・%"
    pattern_start = f"{reading}・%"

    query_filter = or_(
        TranslationTable.reading == reading,
        TranslationTable.reading.like(pattern_start),
        TranslationTable.reading.like(pattern_end),
        TranslationTable.reading.like(pattern_middle),
        TranslationTable.reading.like(pattern_start_spaced),
        TranslationTable.reading.like(pattern_end_spaced),
        TranslationTable.reading.like(pattern_middle_spaced),
    )

    if session:
        return session.query(TranslationTable).filter(query_filter).limit(limit).all()
    with get_session() as new_session:
        return (
            new_session.query(TranslationTable).filter(query_filter).limit(limit).all()
        )


def get_all_parsed_indexes(session: Session | None = None) -> set[int]:
    if session:
        results = session.query(TranslationTable.index_csv).distinct().all()
        return {r[0] for r in results if r[0] is not None}
    with get_session() as new_session:
        results = new_session.query(TranslationTable.index_csv).distinct().all()
        return {r[0] for r in results if r[0] is not None}
