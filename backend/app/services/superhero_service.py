from backend.app.clients.superhero_client import SuperheroClient


class SuperheroService:
    def __init__(self, client: SuperheroClient):
        self.client = client

    async def search(self, query: str):
        return await self.client.search(query)
