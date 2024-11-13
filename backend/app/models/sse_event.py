from orjson import dumps
from pydantic import BaseModel


class SSEEventMessage(BaseModel):
    message: str


class SSEEvent(BaseModel):
    data: SSEEventMessage

    def serialize(self) -> str:
        return f"data: {dumps(self.data.model_dump()).decode()}\n\n"
