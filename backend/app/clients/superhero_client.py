from urllib.parse import quote

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.app.core.config import Settings
from backend.app.core.exceptions import UpstreamServiceError
from backend.app.schemas.superhero import SuperheroResult


class SuperheroClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=3),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def search(self, name: str) -> list[SuperheroResult]:
        if not self.settings.superhero_api_token:
            raise UpstreamServiceError("SUPERHERO_API_TOKEN is not configured")

        encoded_name = quote(name.strip(), safe="")
        url = (
            f"{self.settings.superhero_api_base_url.rstrip('/')}/"
            f"{self.settings.superhero_api_token}/search/{encoded_name}"
        )

        try:
            async with httpx.AsyncClient(timeout=self.settings.superhero_timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamServiceError(f"Superhero API request failed: {exc}") from exc

        if data.get("response") != "success":
            return []

        results = []
        for item in data.get("results", []):
            name_value = item.get("name", "Unknown")
            biography = item.get("biography", {})
            appearance = item.get("appearance", {})
            powerstats = item.get("powerstats", {})

            content = (
                f"Name: {name_value}\n"
                f"Powerstats: {powerstats}\n"
                f"Biography: {biography}\n"
                f"Appearance: {appearance}"
            )

            results.append(
                SuperheroResult(
                    source_name="Superhero API",
                    title=name_value,
                    content=content,
                    metadata={
                        "id": item.get("id"),
                        "powerstats": powerstats,
                        "biography": biography,
                        "appearance": appearance,
                    },
                )
            )
        return results
