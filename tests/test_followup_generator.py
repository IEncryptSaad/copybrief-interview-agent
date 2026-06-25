from src.followup_generator import generate_followup
from src.models import AnswerEvaluation, AnswerQuality


def test_followup_is_section_specific():
    question = generate_followup("offer", AnswerEvaluation(quality=AnswerQuality.thin, score=0.2))
    assert "offer" in question.lower()
    assert "included" in question.lower()
