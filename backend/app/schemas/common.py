from typing import Any, Literal
from pydantic import BaseModel, Field


class Source(BaseModel):
    source_type: Literal["pdf", "superhero"]
    source_name: str
    title: str | None = None
    page: int | None = None
    section: str | None = None
    chunk_id: str | None = None
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RouteInfo(BaseModel):
    type: Literal["rag", "superhero", "both"]
    confidence: float = Field(ge=0, le=1)


class ErrorResponse(BaseModel):
    request_id: str
    code: str
    message: str
