from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RAG Job Matcher"
    secret_key: str = "super-secret-key"
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./jobrag.db"
    scheduler_interval_seconds: int = 60
    embedding_dim: int = 128


@lru_cache
def get_settings() -> Settings:
    return Settings()
