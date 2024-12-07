from orjson import dumps
from pydantic import BaseModel


class ServerSentEventMessage(BaseModel):
    message: str


class ServerSentEvent(BaseModel):
    """Server-sent event response model. Used to stream LLM responses."""

    data: ServerSentEventMessage

    def serialize(self) -> str:
        return f"data: {dumps(self.data.model_dump()).decode()}\n\n"
