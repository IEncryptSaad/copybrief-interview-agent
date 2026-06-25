"""Provider interface for future LLM-backed features."""
from __future__ import annotations

from abc import ABC, abstractmethod
from src.models import AnswerEvaluation


class InterviewProvider(ABC):
    @abstractmethod
    def evaluate_answer(self, answer: str) -> AnswerEvaluation: ...

    @abstractmethod
    def generate_followup(self, section_key: str, evaluation: AnswerEvaluation) -> str: ...
