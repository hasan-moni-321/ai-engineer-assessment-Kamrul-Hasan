from backend.app.rag.retriever import Retriever
from backend.app.schemas.rag import RetrievedChunk


class RAGService:
    def __init__(self, retriever: Retriever, final_k: int):
        self.retriever = retriever
        self.final_k = final_k

    async def retrieve(self, query: str, topic: str | None = None) -> list[RetrievedChunk]:
        return await self.retriever.retrieve(
            query=query,
            topic=topic,
            limit=self.retriever.top_k,
        )
