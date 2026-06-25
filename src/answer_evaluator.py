"""Rule-based answer quality evaluation."""
from __future__ import annotations

import re
from src.models import AnswerEvaluation, AnswerQuality

VAGUE_TERMS = {"good", "great", "best", "quality", "people", "everyone", "stuff", "things", "etc", "nice", "better", "help"}
SPECIFIC_PATTERNS = [r"\$\d", r"\d+%", r"\b\d+\b", r"because\b", r"for example\b", r"such as\b", r"instead of\b"]


def evaluate_answer(answer: str) -> AnswerEvaluation:
    text = answer.strip()
    if not text:
        return AnswerEvaluation(quality=AnswerQuality.missing, score=0, reasons=["No answer provided."])

    words = re.findall(r"[A-Za-z0-9'$%.-]+", text.lower())
    unique_words = set(words)
    vague_hits = sorted(unique_words & VAGUE_TERMS)
    specific_hits = [p for p in SPECIFIC_PATTERNS if re.search(p, text, flags=re.I)]

    score = min(len(words) / 45, 0.55)
    score += min(len(unique_words) / 35, 0.2)
    score += min(len(specific_hits) * 0.1, 0.25)
    score -= min(len(vague_hits) * 0.05, 0.2)
    score = max(0, min(score, 1))

    reasons: list[str] = []
    if len(words) < 4:
        quality = AnswerQuality.missing
        reasons.append("Answer is too short to use.")
    elif len(words) < 12:
        quality = AnswerQuality.thin
        reasons.append("Answer needs more detail.")
    elif vague_hits and not specific_hits and len(words) < 35:
        quality = AnswerQuality.vague
        reasons.append(f"Answer uses broad language: {', '.join(vague_hits)}.")
    elif score >= 0.72 or (len(words) >= 35 and specific_hits):
        quality = AnswerQuality.strong
        reasons.append("Answer includes useful detail and specificity.")
    else:
        quality = AnswerQuality.medium
        reasons.append("Answer is usable but could be richer.")

    return AnswerEvaluation(quality=quality, score=round(score, 2), reasons=reasons)
