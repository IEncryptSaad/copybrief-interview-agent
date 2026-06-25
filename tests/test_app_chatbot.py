import inspect

import app


def test_chatbot_uses_messages_type_when_gradio_supports_it():
    if "type" in inspect.signature(app.gr.Chatbot).parameters:
        assert app.chatbot_message_type_kwargs() == {"type": "messages"}
        assert app.chatbot.type == "messages"
    else:
        assert app.chatbot_message_type_kwargs() == {}
