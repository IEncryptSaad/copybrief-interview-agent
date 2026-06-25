"""Export interfaces for generated briefs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BriefExporter(ABC):
    @abstractmethod
    def export_text(self, markdown: str) -> str: ...

    @abstractmethod
    def export_file(self, markdown: str, path: str | Path) -> Path: ...


class MarkdownExporter(BriefExporter):
    """Default free exporter; future PDF/Docs/CRM exporters can share this interface."""

    def export_text(self, markdown: str) -> str:
        return markdown

    def export_file(self, markdown: str, path: str | Path) -> Path:
        output = Path(path)
        output.write_text(markdown, encoding="utf-8")
        return output
