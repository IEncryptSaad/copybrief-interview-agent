"""Free default provider using deterministic local rules."""
from __future__ import annotations

from src.answer_evaluator import evaluate_answer
from src.followup_generator import generate_followup
from src.models import AnswerEvaluation
from src.providers.base import InterviewProvider


class RuleBasedProvider(InterviewProvider):
    def evaluate_answer(self, answer: str) -> AnswerEvaluation:
        return evaluate_answer(answer)

    def generate_followup(self, section_key: str, evaluation: AnswerEvaluation) -> str:
        return generate_followup(section_key, evaluation)
