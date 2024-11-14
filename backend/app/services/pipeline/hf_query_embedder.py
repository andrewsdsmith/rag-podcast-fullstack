from haystack import component
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@component
class HuggingFaceQueryEmbedder:
    def __init__(self) -> None:
        self.model = SentenceTransformer(
            settings.HF_EMBEDDING_MODEL, trust_remote_code=True
        )

    @component.output_types(embedding=list[float])  # type: ignore[misc]
    def run(self, text: str) -> dict[str, list[float]]:
        embedding = self.model.encode(text)

        return {"embedding": embedding.tolist()}
