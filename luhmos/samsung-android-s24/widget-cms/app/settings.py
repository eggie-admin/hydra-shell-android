from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    kai_env: str = Field(default="development", alias="KAI_ENV")
    kai_cms_db: str = Field(default="./kai_cms.sqlite3", alias="KAI_CMS_DB")
    kai_allowed_origins: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173", alias="KAI_ALLOWED_ORIGINS"
    )
    kai_admin_token: str = Field(default="dev-only-change-me", alias="KAI_ADMIN_TOKEN")

    @property
    def db_path(self) -> Path:
        return Path(self.kai_cms_db).expanduser().resolve()

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.kai_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
