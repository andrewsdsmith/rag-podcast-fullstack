from haystack import Document, component
from sqlmodel import Session, select

from app.models.podcast_segment_summary import PodcastSegmentSummary


@component
class PostgresRetriever:
    def __init__(self, session: Session):
        self.session = session

    @component.output_types(podcast_summaries=list[Document])  # type: ignore[misc]
    def run(
        self, query_embedding: list[float], top_k: int
    ) -> dict[str, list[Document]]:
        neighbors = self.session.exec(
            select(PodcastSegmentSummary)
            .order_by(PodcastSegmentSummary.embedding.cosine_distance(query_embedding))  # type: ignore[attr-defined]
            .limit(top_k)
        )

        podcast_segment_summaries: list[PodcastSegmentSummary] = []
        if neighbors is not None:
            for chunk in neighbors:
                podcast_segment_summaries.append(chunk)
        else:
            return {"podcast_summaries": []}

        # Return results in the expected dictionary format
        return {
            "podcast_summaries": [
                Document(
                    content=summary.summary,
                    meta={"title": summary.title, "url": summary.url_at_time},
                )
                for summary in podcast_segment_summaries
            ]
        }
