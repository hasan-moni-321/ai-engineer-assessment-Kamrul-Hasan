from backend.app.clients.openai_client import OpenAIClient


class EmbeddingService:
    def __init__(self, client: OpenAIClient):
        self.client = client

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await self.client.embed(texts)
