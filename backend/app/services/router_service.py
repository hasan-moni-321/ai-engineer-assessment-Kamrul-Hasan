from backend.app.clients.openai_client import OpenAIClient
from backend.app.schemas.router import RouterDecision


class RouterService:
    def __init__(self, openai: OpenAIClient):
        self.openai = openai

    async def route(self, question: str) -> RouterDecision:
        return await self.openai.route(question)
