"""Markdown brief generation."""
from __future__ import annotations

from src.discovery_schema import DISCOVERY_SECTIONS
from src.models import InterviewState


def _answer(state: InterviewState, key: str) -> str:
    item = state.sections.get(key)
    return item.combined_answer if item and item.combined_answer else "_Missing._"


def _bullets(text: str) -> str:
    if not text or text == "_Missing._":
        return "- _Missing._"
    parts = [p.strip(" -") for p in text.replace("\n", ". ").split(".") if p.strip()]
    return "\n".join(f"- {p}" for p in parts[:6])


def generate_brief(state: InterviewState) -> str:
    missing = [s.label for s in DISCOVERY_SECTIONS if not state.sections.get(s.key) or s.key not in state.completed_sections]
    offer = _answer(state, "offer")
    audience = _answer(state, "audience")
    pain = _answer(state, "pain_points")
    transformation = _answer(state, "desired_transformation")
    phrases = state.exact_phrases or []

    angles = [
        f"Position the offer around moving from {pain[:120]} to {transformation[:120]}.",
        "Use proof and risk reversal close to the CTA to reduce hesitation.",
        "Mirror the client's own language in headlines and lead sections.",
    ]
    hooks = [
        f"Still dealing with {pain[:90]}?",
        f"A clearer path to {transformation[:90]}",
        f"For {audience[:90]} who want a better way",
    ]

    return f"""# Copywriting Brief

## Business Summary
{offer}

## Offer
{offer}

## Target Audience
{audience}

## Pain Points
{_bullets(pain)}

## Desired Transformation
{transformation}

## Origin Story
{_answer(state, 'origin_story')}

## Proof and Results
{_answer(state, 'proof_results')}

## Objections
{_bullets(_answer(state, 'objections'))}

## Competitors
{_answer(state, 'competitors')}

## Brand Voice
{_answer(state, 'brand_voice')}

## Exact Client Phrases
{chr(10).join(f'- "{phrase}"' for phrase in phrases[:12]) if phrases else '- _No standout exact phrases captured yet._'}

## Recommended Copy Angles
{chr(10).join(f'- {angle}' for angle in angles)}

## Suggested Hooks
{chr(10).join(f'- {hook}' for hook in hooks)}

## Missing Information
{chr(10).join(f'- {item}' for item in missing) if missing else '- None — all discovery sections completed.'}

## CTA / Next Step
{_answer(state, 'cta')}
"""
