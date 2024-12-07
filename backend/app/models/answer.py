from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.question import Question  # Import only for type checking


class Answer(SQLModel, table=True):  # type: ignore[call-arg]
    """Answer model for the database."""

    id: int = Field(default=None, primary_key=True)
    text: str = Field(sa_column=Column(Text))

    question: Optional["Question"] = Relationship(back_populates="answer")
