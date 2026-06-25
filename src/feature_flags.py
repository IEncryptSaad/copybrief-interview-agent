"""Small environment-driven feature flag helpers.

Flags default to ``False`` so the free MVP stays functional with no paid APIs,
no database, and no optional services.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    """Feature switches for premium-ready extension points."""

    enable_claude: bool = Field(default=False)
    enable_persistence: bool = Field(default=False)
    enable_analytics: bool = Field(default=False)
    enable_auth: bool = Field(default=False)
    enable_pdf_export: bool = Field(default=False)


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}
