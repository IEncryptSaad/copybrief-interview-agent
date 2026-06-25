"""Storage interfaces and free adapters for interviews and briefs."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from src.models import InterviewState


class InterviewStorage(ABC):
    @abstractmethod
    def save_session(self, session_id: str, state: InterviewState) -> None: ...

    @abstractmethod
    def load_session(self, session_id: str) -> InterviewState | None: ...

    @abstractmethod
    def save_brief(self, session_id: str, markdown: str) -> None: ...

    @abstractmethod
    def load_brief(self, session_id: str) -> str | None: ...


class DisabledStorage(InterviewStorage):
    """No-op adapter used when persistence is off."""

    def save_session(self, session_id: str, state: InterviewState) -> None:
        return None

    def load_session(self, session_id: str) -> InterviewState | None:
        return None

    def save_brief(self, session_id: str, markdown: str) -> None:
        return None

    def load_brief(self, session_id: str) -> str | None:
        return None


class InMemoryStorage(InterviewStorage):
    def __init__(self) -> None:
        self.sessions: dict[str, InterviewState] = {}
        self.briefs: dict[str, str] = {}

    def save_session(self, session_id: str, state: InterviewState) -> None:
        self.sessions[session_id] = state.model_copy(deep=True)

    def load_session(self, session_id: str) -> InterviewState | None:
        state = self.sessions.get(session_id)
        return state.model_copy(deep=True) if state else None

    def save_brief(self, session_id: str, markdown: str) -> None:
        self.briefs[session_id] = markdown

    def load_brief(self, session_id: str) -> str | None:
        return self.briefs.get(session_id)


class LocalJsonStorage(InterviewStorage):
    """Simple file adapter; future DB adapters can implement the same methods."""

    def __init__(self, root: str | Path = ".copybrief_data") -> None:
        self.root = Path(root)
        self.sessions_dir = self.root / "sessions"
        self.briefs_dir = self.root / "briefs"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.briefs_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_id: str, state: InterviewState) -> None:
        (self.sessions_dir / f"{session_id}.json").write_text(state.model_dump_json(indent=2), encoding="utf-8")

    def load_session(self, session_id: str) -> InterviewState | None:
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            return None
        return InterviewState.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def save_brief(self, session_id: str, markdown: str) -> None:
        (self.briefs_dir / f"{session_id}.md").write_text(markdown, encoding="utf-8")

    def load_brief(self, session_id: str) -> str | None:
        path = self.briefs_dir / f"{session_id}.md"
        return path.read_text(encoding="utf-8") if path.exists() else None
