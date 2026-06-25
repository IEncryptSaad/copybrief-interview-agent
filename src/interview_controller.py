"""Interview orchestration independent from UI."""
from __future__ import annotations

import logging
import re

from src.brief_generator import generate_brief
from src.config import get_settings
from src.discovery_schema import DISCOVERY_SECTIONS, DiscoverySection, get_discovery_sections
from src.exporters import BriefExporter, MarkdownExporter
from src.models import InterviewState, InterviewTurn, SectionAnswer
from src.providers.base import InterviewProvider
from src.providers.registry import build_provider as build_registered_provider
from src.storage import DisabledStorage, InterviewStorage, LocalJsonStorage

logger = logging.getLogger(__name__)


def build_provider() -> InterviewProvider:
    return build_registered_provider(get_settings())


def build_storage() -> InterviewStorage:
    settings = get_settings()
    if not settings.features.enable_persistence:
        return DisabledStorage()
    if settings.storage_backend == "local_json":
        return LocalJsonStorage(settings.local_storage_path)
    return DisabledStorage()


class InterviewController:
    def __init__(
        self,
        provider: InterviewProvider | None = None,
        storage: InterviewStorage | None = None,
        exporter: BriefExporter | None = None,
        template_key: str = "copywriting",
    ) -> None:
        self.provider = provider or build_provider()
        self.storage = storage or build_storage()
        self.exporter = exporter or MarkdownExporter()
        self.template_key = template_key
        self.sections: list[DiscoverySection] = get_discovery_sections(template_key)

    def initial_state(self) -> InterviewState:
        return InterviewState()

    def first_message(self) -> str:
        return (
            "Hi — I’m CopyBrief, your copywriting discovery assistant. I’ll ask focused questions about the offer, "
            "buyer, pain points, proof, voice, objections, and CTA, then turn your answers into a practical Markdown brief. "
            "Use the client's exact wording when you have it; I’ll preserve strong phrases for hooks and messaging. "
            f"{self.sections[0].question}"
        )

    def progress(self, state: InterviewState) -> str:
        return f"{len(state.completed_sections)}/{len(self.sections)} sections complete"

    def handle_answer(self, answer: str, state: InterviewState | None = None) -> InterviewTurn:
        state = state or self.initial_state()
        answer = (answer or "").strip()
        if not answer:
            logger.info("Ignoring empty answer in controller")
            return InterviewTurn(
                message="Please share a short answer, even if it is rough. A few specific details are enough to keep building the brief.",
                state=state,
                progress=self.progress(state),
            )
        if state.finished:
            return InterviewTurn(message="The interview is complete. You can generate the brief or reset to start over.", state=state, progress=self.progress(state), brief=self.generate_brief(state))

        section = self.sections[state.current_index]
        section_answer = state.sections.get(section.key, SectionAnswer(section_key=section.key))
        section_answer.answers.append(answer)
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
        if state.current_index >= len(self.sections):
            state.finished = True
            brief = self.generate_brief(state)
            return InterviewTurn(message="Great — the discovery interview is complete. Click generate/download brief to save the Markdown brief.", state=state, progress=self.progress(state), brief=brief)

        next_question = self.sections[state.current_index].question
        return InterviewTurn(message=next_question, state=state, progress=self.progress(state))

    def generate_brief(self, state: InterviewState) -> str:
        logger.info("Generating brief with %s completed sections", len(state.completed_sections))
        brief = generate_brief(state, self.sections)
        self.storage.save_brief("latest", brief)
        return self.exporter.export_text(brief)

    def save_session(self, session_id: str, state: InterviewState) -> None:
        self.storage.save_session(session_id, state)

    def load_session(self, session_id: str) -> InterviewState | None:
        return self.storage.load_session(session_id)

    @staticmethod
    def _capture_phrases(answer: str, state: InterviewState) -> None:
        quoted = re.findall(r"[\"“](.*?)[\"”]", answer)
        candidates = quoted + re.findall(r"\b(?:I|we|our|my) [^.?!]{12,90}", answer, flags=re.I)
        for phrase in candidates:
            clean = phrase.strip()
            if clean and clean not in state.exact_phrases:
                state.exact_phrases.append(clean)
