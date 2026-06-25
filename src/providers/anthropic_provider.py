"""Safe optional Anthropic adapter placeholder.

The MVP never requires Anthropic. This adapter intentionally falls back to the
rule-based provider unless a future implementation adds the SDK and explicit API calls.
"""
from __future__ import annotations

import logging
from src.providers.rule_based import RuleBasedProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(RuleBasedProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        if not api_key:
            logger.info("ANTHROPIC_API_KEY missing; using rule-based behavior.")
        else:
            logger.info("Anthropic key configured; MVP adapter still uses safe rule-based behavior.")
