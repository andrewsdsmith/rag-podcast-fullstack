from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from sqlmodel import Session

from app.services.pipeline.postgres_retriever import PostgresRetriever
from app.services.pipeline.query_embedder import QueryEmbedder


class PipelineBuilder:
    def __init__(self) -> None:
        self.prompt_template = """
            You are an expert in distilling and extracting key information from reliable sources. You have been tasked with answering health, lifestyle and nutrition
            related questions based on summaries of the UK's leading health and wellness podcast: Zoe Science and Nutrition. The podcasts always include a host, Johnathan,
            and one or more guests who are experts in their field. The podcast episodes are typically around 60 minutes. These podcasts have been distilled down into useful summaries.
            Each summary is based on a 5 minute segment of the podcast and includes the podcast title, the summary and a URL to the beginning of the segment.
            This means that the key information should be available in the context provided to you. It is important to remember that you are not a health expert, but you are
            responsible for extracting the key information from the podcasts in order to answer the questions. Now, let's get started!

                Context:
                {% for podcast_summary in podcast_summaries %}
                Title: {{ podcast_summary.meta.title }}
                URL: {{ podcast_summary.meta.url }}
                Summary: {{ podcast_summary.content }}

                {% endfor %}
                Question: {{ query }}

                Instructions:
                1. Answer using markdown.
                2. Use information from the context to answer the question.
                3. Include relevant titles and URLs in your answer.
                4. Make it clear in your answer that specific content can be found in the timestamped links.
                5. Provide your answer in markdown.
                6 If the context doesn't contain enough information to fully answer the question, say so.

                Your answer:"""

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
