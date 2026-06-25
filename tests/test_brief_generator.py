from src.brief_generator import generate_brief
from src.models import InterviewState, SectionAnswer


def test_brief_contains_required_sections():
    state = InterviewState(sections={"offer": SectionAnswer(section_key="offer", answers=["A course for freelancers."])}, completed_sections=["offer"], exact_phrases=["charge more with confidence"])
    brief = generate_brief(state)
    assert "## Business Summary" in brief
    assert "## Recommended Copy Angles" in brief
    assert '"charge more with confidence"' in brief
    assert "## Missing Information" in brief


def test_partial_brief_lists_missing_and_preserves_available_content():
    state = InterviewState(
        sections={"offer": SectionAnswer(section_key="offer", answers=["We sell landing page copy for SaaS founders who say \"launch without second guessing\"."])},
        exact_phrases=["launch without second guessing"],
    )
    brief = generate_brief(state)
    assert "This is a partial brief" in brief
    assert "We sell landing page copy" in brief
    assert '"launch without second guessing"' in brief
    assert "Offer: partial answer captured" in brief
    assert "Audience / Avatar: no answer captured yet" in brief
