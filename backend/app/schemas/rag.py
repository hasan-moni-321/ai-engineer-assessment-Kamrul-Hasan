from typing import Any
from pydantic import BaseModel, Field


# class DocumentChunk(BaseModel):
#     chunk_id: str
#     document_id: str
#     document_version: str
#     source_name: str
#     source_type: str = "pdf"
#     page: int
#     section: str | None
#     topic: str | None
#     content_type: str = "text"
#     text: str
class DocumentChunk(BaseModel):
    chunk_id: str
    point_id: str
    document_id: str
    document_version: str
    source_name: str
    source_type: str = "pdf"
    page: int
    section: str | None
    topic: str | None
    content_type: str = "text"
    text: str

    
class RetrievedChunk(DocumentChunk):
    score: float = Field(ge=-1.0, le=1.0)
