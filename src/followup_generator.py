"""Generate targeted follow-up questions."""
from __future__ import annotations

from src.discovery_schema import SECTION_BY_KEY
from src.models import AnswerEvaluation, AnswerQuality

FOLLOWUPS = {
    "offer": "What makes the offer valuable or different, and what exactly is included?",
    "audience": "Can you describe a specific ideal buyer: role, situation, goals, and what they already believe?",
    "pain_points": "What is the most painful moment they experience before looking for this solution?",
    "desired_transformation": "What concrete result would make them feel this purchase worked?",
    "origin_story": "What personal insight, frustration, or event led to creating this?",
    "objections": "What is the biggest reason they might hesitate, delay, or choose a competitor?",
    "proof_results": "Can you share any numbers, testimonials, credentials, examples, or before/after results?",
    "brand_voice": "Name 2-3 brands or adjectives that capture the tone, plus anything to avoid.",
    "competitors": "Which alternatives do buyers compare against, and why do they choose you instead?",
    "cta": "What exact action should readers take, and where should that action send them?",
    "guarantees": "How can you reduce buyer risk: guarantee, trial, refund, demo, or proof before payment?",
    "constraints": "What claims, words, deadlines, formats, or compliance limits should the copy respect?",
}


def generate_followup(section_key: str, evaluation: AnswerEvaluation) -> str:
    section = SECTION_BY_KEY[section_key]
    prefix = "Thanks — I need a little more detail." if evaluation.quality != AnswerQuality.missing else "No problem — let's fill that in."
    return f"{prefix} For {section.label.lower()}: {FOLLOWUPS.get(section_key, section.question)}"
