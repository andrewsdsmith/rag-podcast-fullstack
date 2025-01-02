from typing import Literal

from orjson import dumps
from pydantic import BaseModel


class ServerSentEventMessage(BaseModel):
    message: str


class ServerSentEvent(BaseModel):
    """Server-sent event response model. Used to stream LLM responses."""

    type: Literal["message", "error"]
    # Wrapper for the message to ensure special characters are preserved
    message: ServerSentEventMessage | str

    @classmethod
    def from_message(
        cls, message: str, type: Literal["message", "error"] = "message"
    ) -> "ServerSentEvent":
        """Factory method to create a ServerSentEvent from a message string."""
        return cls(type=type, message=ServerSentEventMessage(message=message))

    def serialize(self) -> str:
        if isinstance(self.message, ServerSentEventMessage):
            message_data = dumps(self.message.model_dump()).decode()
        else:
            message_data = self.message
        return f"event: {self.type}\ndata: {message_data}\n\n"
