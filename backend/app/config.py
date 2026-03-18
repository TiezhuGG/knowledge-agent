from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Knowledge Agent"
    app_env: str = "dev"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    top_k_chunks: int = 4
    max_chunk_chars: int = 800
    enable_live_llm: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

