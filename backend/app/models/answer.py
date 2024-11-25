from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel


class Answer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str = Field(sa_column=Column(Text))

    question: Optional["Question"] = Relationship(back_populates="answer")  # type: ignore[name-defined]
