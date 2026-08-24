"""Environment-backed application settings."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API and local infrastructure."""

    app_name: str = "ERP AI Analyst"
    app_env: str = "local"
    debug: bool = False
    database_url: str = "postgresql+psycopg://erp:erp@localhost:5432/erp_ai_analyst"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached process settings."""

    return Settings()
