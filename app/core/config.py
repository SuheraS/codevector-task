from functools import lru_cache
from os import getenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_database_url() -> str:
    # Prefer pydantic-loaded value first
    url = settings.database_url or getenv("DATABASE_URL")

    if not url:
        raise RuntimeError("DATABASE_URL is required")

    # 🔥 CRITICAL FIX: force SQLAlchemy to use psycopg v3 (NOT psycopg2)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://")

    return url