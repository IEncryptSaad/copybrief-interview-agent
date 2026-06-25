"""Interview orchestration independent from UI."""
from __future__ import annotations

import logging
import re

from src.brief_generator import generate_brief
from src.config import get_settings
from src.discovery_schema import DISCOVERY_SECTIONS
from src.models import InterviewState, InterviewTurn, SectionAnswer
from src.providers.anthropic_provider import AnthropicProvider
from src.providers.base import InterviewProvider
from src.providers.rule_based import RuleBasedProvider

logger = logging.getLogger(__name__)


def build_provider() -> InterviewProvider:
    settings = get_settings()
    if settings.effective_provider == "anthropic":
        return AnthropicProvider(settings.anthropic_api_key)
    return RuleBasedProvider()


class InterviewController:
    def __init__(self, provider: InterviewProvider | None = None) -> None:
        self.provider = provider or build_provider()

    def initial_state(self) -> InterviewState:
        return InterviewState()

    def first_message(self) -> str:
        return "Hi! I’ll help turn your client discovery into a copywriting brief. " + DISCOVERY_SECTIONS[0].question

    def progress(self, state: InterviewState) -> str:
        return f"{len(state.completed_sections)}/{len(DISCOVERY_SECTIONS)} sections complete"

    def handle_answer(self, answer: str, state: InterviewState | None = None) -> InterviewTurn:
        state = state or self.initial_state()
        if state.finished:
            return InterviewTurn(message="The interview is complete. You can generate the brief or reset to start over.", state=state, progress=self.progress(state), brief=generate_brief(state))

        section = DISCOVERY_SECTIONS[state.current_index]
        section_answer = state.sections.get(section.key, SectionAnswer(section_key=section.key))
        section_answer.answers.append(answer.strip())
        combined = section_answer.combined_answer
        evaluation = self.provider.evaluate_answer(combined)
        section_answer.evaluation = evaluation
        state.sections[section.key] = section_answer
        self._capture_phrases(answer, state)

        followups = state.followup_counts.get(section.key, 0)
        if not evaluation.is_good_enough and followups < 1:
            state.followup_counts[section.key] = followups + 1
            logger.info("Asking follow-up for %s: %s", section.key, evaluation.quality)
            return InterviewTurn(message=self.provider.generate_followup(section.key, evaluation), state=state, progress=self.progress(state))

        if section.key not in state.completed_sections:
            state.completed_sections.append(section.key)
        state.current_index += 1
        if state.current_index >= len(DISCOVERY_SECTIONS):
            state.finished = True
            brief = generate_brief(state)
            return InterviewTurn(message="Great — the discovery interview is complete. Click generate/download brief to save the Markdown brief.", state=state, progress=self.progress(state), brief=brief)

        next_question = DISCOVERY_SECTIONS[state.current_index].question
        return InterviewTurn(message=next_question, state=state, progress=self.progress(state))

    def generate_brief(self, state: InterviewState) -> str:
        return generate_brief(state)

    @staticmethod
    def _capture_phrases(answer: str, state: InterviewState) -> None:
        quoted = re.findall(r"[\"“](.*?)[\"”]", answer)
        candidates = quoted + re.findall(r"\b(?:I|we|our|my) [^.?!]{12,90}", answer, flags=re.I)
        for phrase in candidates:
            clean = phrase.strip()
            if clean and clean not in state.exact_phrases:
                state.exact_phrases.append(clean)
