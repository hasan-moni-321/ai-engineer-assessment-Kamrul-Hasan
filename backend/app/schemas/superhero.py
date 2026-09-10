from typing import Any
from pydantic import BaseModel


class SuperheroResult(BaseModel):
    source_type: str = "superhero"
    source_name: str
    title: str
    content: str
    metadata: dict[str, Any]
