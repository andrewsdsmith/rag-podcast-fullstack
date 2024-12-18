from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Prompt(SQLModel, table=True):
    """The prompt template for the pipeline generator model."""

    __tablename__ = "prompts"

    id: int = Field(default=None, primary_key=True)
    # A prompt update will always require at least a minor version bump
    api_version: str = Field(max_length=10)
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
