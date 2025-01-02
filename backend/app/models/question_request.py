from pydantic import BaseModel, field_validator


class QuestionRequest(BaseModel):
    """GET request validation model for a question."""

    question: str

    # Validate that the question is not empty.
    # FastAPI will automatically return a 422 error if this is not valid.
    @field_validator("question")
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()
