from functools import lru_cache
from os import getenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_database_url() -> str:
    if settings.database_url:
        return settings.database_url

    database_url = getenv("DATABASE_URL")
    if database_url:
        return database_url

    raise RuntimeError("DATABASE_URL is required")
