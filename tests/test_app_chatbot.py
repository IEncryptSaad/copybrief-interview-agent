import ast
from pathlib import Path

import app


def test_chatbot_uses_messages_type():
    assert app.chatbot.type == "messages"


def test_launch_config_is_hugging_face_spaces_compatible():
    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    launch_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "launch"
    ]

    assert len(launch_calls) == 1
    launch_call = launch_calls[0]
    keywords = {keyword.arg: keyword.value for keyword in launch_call.keywords}
    assert ast.literal_eval(keywords["server_name"]) == "0.0.0.0"
    assert ast.literal_eval(keywords["server_port"]) == 7860
    assert "share" not in keywords


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
