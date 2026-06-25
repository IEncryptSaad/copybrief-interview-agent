"""Provider registry/factory for interview LLM adapters."""
from __future__ import annotations

import logging
from collections.abc import Callable

from src.config import Settings
from src.providers.anthropic_provider import AnthropicProvider
from src.providers.base import InterviewProvider
from src.providers.rule_based import RuleBasedProvider

logger = logging.getLogger(__name__)
ProviderBuilder = Callable[[Settings], InterviewProvider]


class ProviderRegistry:
    """Minimal registry so new providers do not touch controllers."""

    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}

    def register(self, name: str, builder: ProviderBuilder) -> None:
        self._builders[name] = builder

    def create(self, settings: Settings) -> InterviewProvider:
        requested = settings.provider
        builder = self._builders.get(requested)
        if requested == "anthropic" and not settings.can_use_anthropic:
            logger.info("Anthropic disabled or missing API key; falling back to rule_based provider.")
            builder = self._builders["rule_based"]
        elif builder is None:
            logger.warning("Unknown provider '%s'; falling back to rule_based provider.", requested)
            builder = self._builders["rule_based"]
        return builder(settings)


registry = ProviderRegistry()
registry.register("rule_based", lambda _settings: RuleBasedProvider())
registry.register("anthropic", lambda settings: AnthropicProvider(settings.anthropic_api_key))


def build_provider(settings: Settings) -> InterviewProvider:
    return registry.create(settings)
