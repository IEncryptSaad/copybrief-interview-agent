from src.brief_generator import generate_brief
from src.models import InterviewState, SectionAnswer


def test_brief_contains_required_sections():
    state = InterviewState(sections={"offer": SectionAnswer(section_key="offer", answers=["A course for freelancers."])}, completed_sections=["offer"], exact_phrases=["charge more with confidence"])
    brief = generate_brief(state)
    assert "## Business Summary" in brief
    assert "## Recommended Copy Angles" in brief
    assert '"charge more with confidence"' in brief
    assert "## Missing Information" in brief
