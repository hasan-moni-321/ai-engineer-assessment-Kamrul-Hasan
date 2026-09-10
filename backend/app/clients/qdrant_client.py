from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from backend.app.core.config import Settings
from backend.app.schemas.rag import DocumentChunk, RetrievedChunk


class QdrantRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
            timeout=settings.qdrant_timeout,
        )

    async def health(self) -> bool:
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False

    async def ensure_collection(self, vector_size: int) -> None:
        exists = await self.client.collection_exists(self.settings.qdrant_collection)
        if not exists:
            await self.client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert(
        self,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> None:
        # points = [
        #     PointStruct(
        #         id=chunk.chunk_id,
        #         vector=vector,
        #         payload=chunk.model_dump(),
        #     )
        #     for chunk, vector in zip(chunks, vectors, strict=True)
        # ]
        points = [
            PointStruct(
                id=chunk.point_id,
                vector=vector,
                payload=chunk.model_dump(),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]


        batch_size = 64
        for start in range(0, len(points), batch_size):
            await self.client.upsert(
                collection_name=self.settings.qdrant_collection,
                points=points[start:start + batch_size],
                wait=True,
            )

    async def search(
        self,
        vector: list[float],
        limit: int,
        score_threshold: float,
        topic: str | None = None,
    ) -> list[RetrievedChunk]:
        query_filter = None
        if topic:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="topic",
                        match=MatchValue(value=topic),
                    )
                ]
            )

        result = await self.client.query_points(
            collection_name=self.settings.qdrant_collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        chunks: list[RetrievedChunk] = []
        for point in result.points:
            payload = point.payload or {}
            chunks.append(
                RetrievedChunk(
                    # chunk_id=str(payload["chunk_id"]),
                    # document_id=str(payload["document_id"]),
                    chunk_id=str(payload["chunk_id"]),
                    point_id=str(payload["point_id"]),
                    document_id=str(payload["document_id"]),
                    document_version=str(payload["document_version"]),
                    source_name=str(payload["source_name"]),
                    source_type=str(payload.get("source_type", "pdf")),
                    page=int(payload["page"]),
                    section=payload.get("section"),
                    topic=payload.get("topic"),
                    content_type=str(payload.get("content_type", "text")),
                    text=str(payload["text"]),
                    score=float(point.score),
                )
            )
        return chunks
