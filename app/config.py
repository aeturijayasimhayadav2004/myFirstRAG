from functools import lru_cache

try:  # Pydantic v2 ships BaseSettings in pydantic-settings
    from pydantic_settings import BaseSettings
except Exception:  # pragma: no cover - fallback for pydantic v1 or the v2 compatibility shim
    try:
        from pydantic import BaseSettings  # type: ignore
    except Exception:  # pragma: no cover
        from pydantic.v1 import BaseSettings  # type: ignore


class Settings(BaseSettings):
    app_name: str = "RAG Job Matcher"
    secret_key: str = "super-secret-key"
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./jobrag.db"
    scheduler_interval_seconds: int = 60
    embedding_dim: int = 128
    linkedin_api_key: str = ""
    indeed_api_key: str = ""
    naukri_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
