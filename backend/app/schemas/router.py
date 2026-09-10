from typing import Literal
from pydantic import BaseModel, Field


class RouterDecision(BaseModel):
    route: Literal["rag", "superhero", "both"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    rag_query: str | None = None
    superhero_query: str | None = None
