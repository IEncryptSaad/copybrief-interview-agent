"""Application configuration."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings loaded from environment and optional .env."""

    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    provider: Literal["rule_based", "anthropic"] = Field(default="rule_based")
    anthropic_api_key: str | None = Field(default=None)

    @property
    def effective_provider(self) -> Literal["rule_based", "anthropic"]:
        if self.provider == "anthropic" and self.anthropic_api_key:
            return "anthropic"
        return "rule_based"


@lru_cache
def get_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv(override=False)
    raw_provider = os.getenv("PROVIDER", "rule_based")
    provider: Literal["rule_based", "anthropic"] = "anthropic" if raw_provider == "anthropic" else "rule_based"
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        provider=provider,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
    )
