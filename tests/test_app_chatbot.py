import inspect

import app


def test_chatbot_uses_messages_type_when_gradio_supports_it():
    if "type" in inspect.signature(app.gr.Chatbot).parameters:
        assert app.chatbot_message_type_kwargs() == {"type": "messages"}
        assert app.chatbot.type == "messages"
    else:
        assert app.chatbot_message_type_kwargs() == {}


def test_empty_message_gets_graceful_assistant_response():
    history, state, _progress, _file = app.start()
    textbox, updated_history, updated_state, progress, brief = app.respond("   ", history, state)
    assert textbox == ""
    assert updated_state == state
    assert "send a few words" in updated_history[-1]["content"].lower()
    assert progress.startswith("0/")
    assert brief is None


def test_reset_interview_clears_brief_preview_and_file():
    history, state, progress, brief_md, brief_file = app.reset_interview()
    assert history[0]["role"] == "assistant"
    assert state.current_index == 0
    assert progress.startswith("0/")
    assert brief_md == ""
    assert brief_file is None
