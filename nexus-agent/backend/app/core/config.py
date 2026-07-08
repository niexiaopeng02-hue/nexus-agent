from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "NexusAgent"
    environment: str = "development"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_url: str = "postgresql+psycopg://nexus:nexus@postgres:5432/nexusagent"
    openai_api_key: str | None = None
    llm_provider: str = "mock"
    upload_max_bytes: int = 5_000_000
    allowed_upload_extensions: str = ".pdf,.docx,.txt,.md,.markdown"
    log_level: str = "INFO"
    secret_key: str = Field(default="demo-only-change-me", min_length=8)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_upload_extensions.split(",")}


@lru_cache
def get_settings() -> Settings:
    return Settings()
