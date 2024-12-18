from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.answer import Answer


class QuestionBase(SQLModel):
    text: str = Field(max_length=2500)


class Question(QuestionBase, table=True):
    """Question model for the database."""

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Foreign key to Answer.id
    answer_id: int = Field(foreign_key="answer.id")

    # Relationship to Answer
    answer: Answer | None = Relationship(back_populates="question")


class QuestionRequest(QuestionBase):
    pass
