from pgvector.sqlalchemy import Vector  # Custom Vector type from pgvector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class PodcastSegmentSummary(SQLModel, table=True):  # type: ignore[call-arg]
    """Podcast segment summary model for the database."""

    __tablename__ = "podcast_segment_summaries"

    id: int = Field(default=None, primary_key=True)
    title: str
    url_at_time: str
    summary: str
    embedding: list[float] = Field(
        sa_column=Column(Vector(1024))
    )  # Using pgvector's VECTOR type
