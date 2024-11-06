from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from sqlmodel import Session

from app.core.config import settings
from app.services.pipeline.postgres_retriever import PostgresRetriever
from app.services.pipeline.query_embedder import QueryEmbedder


class PipelineBuilder:
    def __init__(self) -> None:
        self.prompt_template = settings.PROMPT_TEMPLATE

    def build(self, session: Session) -> Pipeline:
        query_embedder = QueryEmbedder()
        postgres_retriever = PostgresRetriever(session=session)
        prompt_builder = PromptBuilder(template=self.prompt_template)
        pipeline = Pipeline()

        pipeline.add_component("embedder", query_embedder)
        pipeline.add_component("retriever", postgres_retriever)
        pipeline.add_component("prompt", prompt_builder)

        pipeline.connect("embedder.embedding", "retriever.query_embedding")
        pipeline.connect("retriever.podcast_summaries", "prompt.podcast_summaries")

        return pipeline
