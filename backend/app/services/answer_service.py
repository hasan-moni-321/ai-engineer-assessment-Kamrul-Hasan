from backend.app.clients.openai_client import OpenAIClient


class AnswerService:
    def __init__(self, client: OpenAIClient):
        self.client = client

    async def generate(self, question: str, context: str) -> str:
        return await self.client.answer(question, context)
