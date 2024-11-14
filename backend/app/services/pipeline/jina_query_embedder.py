from haystack import component
from haystack_integrations.components.embedders.jina import JinaTextEmbedder

from app.core.config import settings


@component
class JinaQueryEmbedder:
    def __init__(self) -> None:
        self.embedder = JinaTextEmbedder(
            model=settings.JINA_EMBEDDER_MODEL, dimensions=1024, late_chunking=True
        )

    @component.output_types(embedding=list[float])  # type: ignore[misc]
    def run(self, text: str) -> dict[str, list[float]]:
        # returns dict[str, Any]
        embedding = self.embedder.run(text)

        return {"embedding": embedding["embedding"]}
