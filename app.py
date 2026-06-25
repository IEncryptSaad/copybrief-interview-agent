"""Gradio UI for CopyBrief Interview Agent."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import gradio as gr

from src.interview_controller import InterviewController
from src.logging_config import configure_logging
from src.config import get_settings
from src.models import InterviewState

settings = get_settings()
configure_logging(settings.log_level)
controller = InterviewController()


def start() -> tuple[list[dict[str, str]], InterviewState, str, str | None]:
    state = controller.initial_state()
    return ([{"role": "assistant", "content": controller.first_message()}], state, controller.progress(state), None)


def respond(message: str, history: list[dict[str, str]], state: InterviewState | None) -> tuple[str, list[dict[str, str]], InterviewState, str, str | None]:
    if not message.strip():
        return "", history, state or controller.initial_state(), controller.progress(state or controller.initial_state()), None
    current = state or controller.initial_state()
    turn = controller.handle_answer(message, current)
    history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": turn.message}]
    return "", history, turn.state, turn.progress, turn.brief


def make_brief_file(state: InterviewState | None) -> tuple[str, str]:
    current = state or controller.initial_state()
    brief = controller.generate_brief(current)
    path = Path(tempfile.gettempdir()) / "copybrief.md"
    path.write_text(brief, encoding="utf-8")
    return brief, str(path)


with gr.Blocks(title="CopyBrief Interview Agent") as demo:
    gr.Markdown("# CopyBrief Interview Agent\nFree, rule-based, Claude-ready copywriting discovery interviews.")
    chatbot = gr.Chatbot(label="Interview")
    state = gr.State()
    progress = gr.Markdown()
    msg = gr.Textbox(label="Your answer", placeholder="Type your response and press Enter")
    with gr.Row():
        reset = gr.Button("Reset Interview")
        brief_btn = gr.Button("Generate / Download Markdown Brief")
    brief_md = gr.Markdown(label="Generated brief")
    brief_file = gr.File(label="Download brief")

    demo.load(start, outputs=[chatbot, state, progress, brief_file])
    msg.submit(respond, inputs=[msg, chatbot, state], outputs=[msg, chatbot, state, progress, brief_md])
    reset.click(start, outputs=[chatbot, state, progress, brief_file])
    brief_btn.click(make_brief_file, inputs=[state], outputs=[brief_md, brief_file])

if __name__ == "__main__":
    demo.launch()
