from orjson import orjson
from pydantic import BaseModel


class SSEEventMessage(BaseModel):
    message: str


class SSEEvent(BaseModel):
    data: SSEEventMessage

    def serialize(self):
        return f"data: {orjson.dumps(self.data.model_dump()).decode()}\n\n"
