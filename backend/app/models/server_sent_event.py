from typing import Literal

from orjson import dumps
from pydantic import BaseModel


class ServerSentEventMessage(BaseModel):
    message: str


class ServerSentEvent(BaseModel):
    """Server-sent event response model. Used to stream LLM responses."""

    type: Literal["message", "error"]
    # Wrapper for the message to ensure special characters are preserved
    message: ServerSentEventMessage

    @classmethod
    def from_message(
        cls, message: str, type: Literal["message", "error"] = "message"
    ) -> "ServerSentEvent":
        """Factory method to create a ServerSentEvent from a message string."""
        return cls(type=type, message=ServerSentEventMessage(message=message))

    def serialize(self) -> str:
        return (
            f"event: {self.type}\ndata: {dumps(self.message.model_dump()).decode()}\n\n"
        )
