"""Markdown brief generation."""
from __future__ import annotations

from src.discovery_schema import DISCOVERY_SECTIONS, DiscoverySection
from src.models import InterviewState


def _answer(state: InterviewState, key: str) -> str:
    item = state.sections.get(key)
    return item.combined_answer if item and item.combined_answer else "_Missing._"


def _bullets(text: str) -> str:
    if not text or text == "_Missing._":
        return "- _Missing._"
    parts = [p.strip(" -") for p in text.replace("\n", ". ").split(".") if p.strip()]
    return "\n".join(f"- {p}" for p in parts[:6])


def _missing_items(state: InterviewState, sections: list[DiscoverySection]) -> list[str]:
    missing: list[str] = []
    for section in sections:
        answer = state.sections.get(section.key)
        if not answer or not answer.combined_answer:
            missing.append(f"{section.label}: no answer captured yet")
        elif section.key not in state.completed_sections:
            missing.append(f"{section.label}: partial answer captured; needs confirmation or more detail")
    return missing


def _safe_snippet(text: str, fallback: str, limit: int = 100) -> str:
    if not text or text == "_Missing._":
        return fallback
    return text[:limit]


def generate_brief(state: InterviewState, sections: list[DiscoverySection] | None = None) -> str:
    active_sections = sections or DISCOVERY_SECTIONS
    missing = _missing_items(state, active_sections)
    offer = _answer(state, "offer")
    audience = _answer(state, "audience")
    pain = _answer(state, "pain_points")
    transformation = _answer(state, "desired_transformation")
    phrases = state.exact_phrases or []

    angles = [
        f"Position the offer around moving from {_safe_snippet(pain, 'the buyer’s current pain')} to {_safe_snippet(transformation, 'the desired result')}.",
        "Use proof, specificity, and risk reversal close to the CTA to reduce hesitation.",
        "Mirror the client's own language in headlines, lead sections, bullets, and CTA microcopy.",
    ]
    hooks = [
        f"Still dealing with {_safe_snippet(pain, 'the same costly problem', 90)}?",
        f"A clearer path to {_safe_snippet(transformation, 'the result your buyer wants', 90)}",
        f"For {_safe_snippet(audience, 'the right buyer', 90)} who want a better way",
    ]

    completion_note = (
        "This brief is based on a completed discovery interview."
        if not missing
        else "This is a partial brief. It is usable for an MVP/demo, but the Missing Information section lists what to confirm before final copy."
    )

    return f"""# Copywriting Brief

> {completion_note}

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
