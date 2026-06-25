"""Pydantic models for interview state and outputs."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class AnswerQuality(str, Enum):
    strong = "strong"
    medium = "medium"
    thin = "thin"
    vague = "vague"
    missing = "missing"


class AnswerEvaluation(BaseModel):
    quality: AnswerQuality
    score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)

    @property
    def is_good_enough(self) -> bool:
        return self.quality in {AnswerQuality.strong, AnswerQuality.medium}


class SectionAnswer(BaseModel):
    section_key: str
    answers: list[str] = Field(default_factory=list)
    evaluation: AnswerEvaluation | None = None

    @property
    def combined_answer(self) -> str:
        return "\n".join(answer.strip() for answer in self.answers if answer.strip())


class InterviewState(BaseModel):
    current_index: int = 0
    sections: dict[str, SectionAnswer] = Field(default_factory=dict)
    exact_phrases: list[str] = Field(default_factory=list)
    completed_sections: list[str] = Field(default_factory=list)
    followup_counts: dict[str, int] = Field(default_factory=dict)
    finished: bool = False


class InterviewTurn(BaseModel):
    message: str
    state: InterviewState
    progress: str
    brief: str | None = None
