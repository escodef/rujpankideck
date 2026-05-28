from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, mapped_column, relationship

Base = declarative_base()


class TranslationTable(Base):
    __tablename__ = "translations"

    id = mapped_column(Integer, primary_key=True)
    word = mapped_column(String, index=True)
    reading = mapped_column(String, index=True)
    mainsense = mapped_column(String)
    senses = mapped_column(String)
    index_csv = mapped_column(Integer, index=True)

    examples = relationship(
        "ExampleTable", back_populates="translation", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("word", "reading", name="_word_reading_uc"),)


class ExampleTable(Base):
    __tablename__ = "examples"

    id = mapped_column(Integer, primary_key=True)
    ja = mapped_column(String)
    re = mapped_column(String)
    tr = mapped_column(String)
    translation_id = mapped_column(Integer, ForeignKey("translations.id"))
    translation = relationship("TranslationTable", back_populates="examples")


class NotFoundTable(Base):
    __tablename__ = "not_found"

    id = mapped_column(Integer, primary_key=True)
    word = mapped_column(String)
    reading = mapped_column(String)
