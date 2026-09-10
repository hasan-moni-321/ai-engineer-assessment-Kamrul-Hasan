from backend.app.clients.openai_client import OpenAIClient
from backend.app.clients.qdrant_client import QdrantRepository
from backend.app.schemas.rag import RetrievedChunk


class Retriever:
    def __init__(
        self,
        openai: OpenAIClient,
        qdrant: QdrantRepository,
        top_k: int,
        threshold: float,
    ):
        self.openai = openai
        self.qdrant = qdrant
        self.top_k = top_k
        self.threshold = threshold

    async def retrieve(
        self,
        query: str,
        topic: str | None = None,
        limit: int | None = None,
    ) -> list[RetrievedChunk]:
        vector = (await self.openai.embed([query]))[0]
        return await self.qdrant.search(
            vector=vector,
            limit=limit or self.top_k,
            score_threshold=self.threshold,
            topic=topic,
        )
