"""Gradio UI for CopyBrief Interview Agent."""
from __future__ import annotations

import inspect
import logging
import tempfile
from pathlib import Path

import gradio as gr

from src.config import get_settings
from src.interview_controller import InterviewController
from src.logging_config import configure_logging
from src.models import InterviewState

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)
controller = InterviewController()

EMPTY_MESSAGE_RESPONSE = "No problem — send a few words when you're ready. If you're unsure, share your best guess and I'll help turn it into useful copy brief inputs."


def chatbot_message_type_kwargs() -> dict[str, str]:
    if "type" in inspect.signature(gr.Chatbot).parameters:
        return {"type": "messages"}
    return {}


def start() -> tuple[list[dict[str, str]], InterviewState, str, str | None]:
    logger.info("Starting interview session")
    state = controller.initial_state()
    return ([{"role": "assistant", "content": controller.first_message()}], state, controller.progress(state), None)


def reset_interview() -> tuple[list[dict[str, str]], InterviewState, str, str, str | None]:
    history, state, progress, file_path = start()
    logger.info("Reset interview session")
    return history, state, progress, "", file_path


def respond(message: str, history: list[dict[str, str]] | None, state: InterviewState | None) -> tuple[str, list[dict[str, str]], InterviewState, str, str | None]:
    history = history or []
    current = state or controller.initial_state()
    cleaned = (message or "").strip()
    if not cleaned:
        logger.info("Received empty interview message")
        return "", history + [{"role": "assistant", "content": EMPTY_MESSAGE_RESPONSE}], current, controller.progress(current), None

    try:
        turn = controller.handle_answer(cleaned, current)
        updated_history = history + [{"role": "user", "content": cleaned}, {"role": "assistant", "content": turn.message}]
        logger.info("Handled answer; progress=%s", turn.progress)
        return "", updated_history, turn.state, turn.progress, turn.brief
    except Exception:
        logger.exception("Failed to handle interview answer")
        safe_message = "Sorry — something went wrong while processing that answer. Your session is still open, so please try rephrasing or click Generate Brief for what we have so far."
        return "", history + [{"role": "assistant", "content": safe_message}], current, controller.progress(current), None


def make_brief_file(state: InterviewState | None) -> tuple[str, str | None]:
    current = state or controller.initial_state()
    try:
        brief = controller.generate_brief(current)
        path = Path(tempfile.gettempdir()) / "copybrief.md"
        path.write_text(brief, encoding="utf-8")
        logger.info("Generated brief file at %s", path)
        return brief, str(path)
    except Exception:
        logger.exception("Failed to generate brief")
        return "Sorry — the brief could not be generated. Please try again or reset the interview.", None


with gr.Blocks(title="CopyBrief Interview Agent") as demo:
    gr.Markdown("# CopyBrief Interview Agent\nFree, rule-based, Claude-ready copywriting discovery interviews.")
    chatbot = gr.Chatbot(label="Interview", **chatbot_message_type_kwargs())
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
    reset.click(reset_interview, outputs=[chatbot, state, progress, brief_md, brief_file])
    brief_btn.click(make_brief_file, inputs=[state], outputs=[brief_md, brief_file])

if __name__ == "__main__":
    demo.launch()
