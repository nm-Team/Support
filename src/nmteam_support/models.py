"""Core data models shared across the generator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageMetadata:
    """Metadata parsed from a page's YAML frontmatter (or derived defaults)."""

    title: str
    description: str = ""
    index: int = 0
    hide_docs_list: bool = False
    hide_contributing_note: bool = False
    hide_navigation: bool = False


@dataclass(frozen=True)
class DocEntry:
    """A single nav/docsList entry: a document or a sub-folder.

    ``path`` is relative to the docs root, e.g. ``nmbot-telegram/mcp.md``
    (documents) or ``nmbot-telegram/panel`` (folders).
    """

    title: str
    description: str
    path: str
    name: str  # file name or folder name
    index: int = 0
    kind: str = "doc"  # "doc" | "folder"
    hide_contributing_note: bool = False
