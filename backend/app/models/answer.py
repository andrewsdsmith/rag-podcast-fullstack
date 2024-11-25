from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel

from app.models.question import Question


class Answer(SQLModel, table=True):  # type: ignore[call-arg]
    id: int = Field(default=None, primary_key=True)
    text: str = Field(sa_column=Column(Text))

    question: Optional["Question"] = Relationship(back_populates="answer")  # type: ignore[name-defined]
