from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Engineer Assessment"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: str = Field(default="")
    router_model: str = "gpt-5.6-luna"
    answer_model: str = "gpt-5.6-terra"
    embedding_model: str = "text-embedding-3-large"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "docker_kubernetes_v1"

    chunk_target_tokens: int = 500
    chunk_min_tokens: int = 200
    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 75

    rag_top_k: int = 8
    rag_final_context_k: int = 5
    rag_score_threshold: float = 0.35

    openai_timeout: float = 30.0
    qdrant_timeout: float = 5.0
    superhero_timeout: float = 10.0
    max_question_length: int = 4000

    superhero_api_base_url: str = "https://superheroapi.com/api"
    superhero_api_token: str = ""

    cors_origins: str = "http://localhost:5000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
