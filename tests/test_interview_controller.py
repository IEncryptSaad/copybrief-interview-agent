from src.interview_controller import InterviewController


def test_interview_asks_followup_for_thin_answer():
    controller = InterviewController()
    state = controller.initial_state()
    turn = controller.handle_answer("coaching", state)
    assert "more detail" in turn.message.lower() or "fill that in" in turn.message.lower()
    assert state.current_index == 0


def test_interview_advances_after_good_answer():
    controller = InterviewController()
    state = controller.initial_state()
    turn = controller.handle_answer("We sell a $500 launch strategy intensive for solo SaaS founders who need a clear offer, landing page angle, and launch emails within 10 days because they are stuck rewriting copy.", state)
    assert state.current_index == 1
    assert "ideal customer" in turn.message.lower()
