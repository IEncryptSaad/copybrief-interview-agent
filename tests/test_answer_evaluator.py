from src.answer_evaluator import evaluate_answer
from src.models import AnswerQuality


def test_missing_answer():
    assert evaluate_answer(" ").quality == AnswerQuality.missing


def test_thin_answer():
    assert evaluate_answer("small business owners").quality in {AnswerQuality.missing, AnswerQuality.thin}


def test_strong_specific_answer():
    result = evaluate_answer("We help dentists increase booked consultations by 20% because we automate recall emails and follow-up texts for inactive patients.")
    assert result.quality in {AnswerQuality.medium, AnswerQuality.strong}
    assert result.score > 0.4
