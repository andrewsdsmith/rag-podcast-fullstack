from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Answer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str = Field(max_length=10000)

    question: Optional["Question"] = Relationship(back_populates="answer")  # type: ignore[name-defined]
