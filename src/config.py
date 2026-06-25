"""Application configuration."""
from __future__ import annotations

import os
from functools import lru_cache

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from pydantic import BaseModel, Field

from src.feature_flags import FeatureFlags, parse_bool


class Settings(BaseModel):
    """Runtime settings loaded from environment and optional .env."""

    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    provider: str = Field(default="rule_based")
    anthropic_api_key: str | None = Field(default=None)
    storage_backend: str = Field(default="disabled")
    local_storage_path: str = Field(default=".copybrief_data")
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    @property
    def can_use_anthropic(self) -> bool:
        return self.features.enable_claude and bool(self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv(override=False)
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        provider=os.getenv("PROVIDER", "rule_based").strip().lower(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        storage_backend=os.getenv("STORAGE_BACKEND", "disabled").strip().lower(),
        local_storage_path=os.getenv("LOCAL_STORAGE_PATH", ".copybrief_data"),
        features=FeatureFlags(
            enable_claude=parse_bool(os.getenv("ENABLE_CLAUDE")),
            enable_persistence=parse_bool(os.getenv("ENABLE_PERSISTENCE")),
            enable_analytics=parse_bool(os.getenv("ENABLE_ANALYTICS")),
            enable_auth=parse_bool(os.getenv("ENABLE_AUTH")),
            enable_pdf_export=parse_bool(os.getenv("ENABLE_PDF_EXPORT")),
        ),
    )
