from pydantic import BaseModel, Field, field_validator
from .common import RouteInfo, Source


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=128)

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("question must not be blank")
        return value


class AskMetadata(BaseModel):
    retrieved_chunks: int = 0
    latency_ms: int
    router_latency_ms: int = 0
    retrieval_latency_ms: int = 0
    answer_latency_ms: int = 0


class AskResponse(BaseModel):
    request_id: str
    answer: str
    route: RouteInfo
    sources: list[Source]
    metadata: AskMetadata
