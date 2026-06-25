"""Discovery sections and section-specific prompts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoverySection:
    key: str
    label: str
    question: str


DISCOVERY_SECTIONS: list[DiscoverySection] = [
    DiscoverySection("offer", "Offer", "To start, what are you selling, and what does the client get?"),
    DiscoverySection("audience", "Audience / Avatar", "Who is the ideal customer or buyer for this offer?"),
    DiscoverySection("pain_points", "Pain Points", "What problems, frustrations, or urgent pains are they dealing with now?"),
    DiscoverySection("desired_transformation", "Desired Transformation", "What outcome or transformation do they want most?"),
    DiscoverySection("origin_story", "Origin Story", "What is the story behind this offer or business?"),
    DiscoverySection("objections", "Objections", "What doubts or objections might stop someone from buying?"),
    DiscoverySection("proof_results", "Proof / Results", "What proof, results, testimonials, credentials, or case studies can we mention?"),
    DiscoverySection("brand_voice", "Brand Voice", "How should the copy sound: tone, style, words to use or avoid?"),
    DiscoverySection("competitors", "Competitors", "Who are your main competitors or alternatives customers compare you with?"),
    DiscoverySection("cta", "CTA", "What is the primary call to action or next step?"),
    DiscoverySection("guarantees", "Guarantees / Risk Reversal", "Do you offer any guarantee, refund policy, trial, or other risk reversal?"),
    DiscoverySection("constraints", "Constraints", "Any deadlines, legal claims to avoid, required phrases, channels, or other constraints?"),
]

SECTION_BY_KEY = {section.key: section for section in DISCOVERY_SECTIONS}
