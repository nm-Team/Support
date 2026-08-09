"""Frontmatter parsing and metadata extraction.

Mirrors the behavior of the original generate.py while fixing two defects:
- an unterminated frontmatter fence no longer crashes (old code raised IndexError);
- description extraction is bounded and deterministic (old code could loop forever
  and produced concatenated garbage for pages without a ``description:`` field).
"""

from __future__ import annotations

import re

from nmteam_support.models import PageMetadata

_MARKDOWN_CHARS = re.compile(r"[\[\]\(\)#`>*_]|\|")


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split ``text`` into ``(metadata_raw, body)``.

    Mirrors the original ``text.split("---", 2)`` behavior used when injecting
    contributing notes: only a leading ``---`` triggers a split, and an
    unterminated fence degrades to ``("", text)``.
    """
    if not text.startswith("---"):
        return ("", text)
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ("", text)
    return (parts[1], parts[2])


def split_frontmatter_lines(text: str) -> tuple[str, str]:
    """Line-based split used for metadata extraction.

    Returns ``(metadata_raw, body)``; ``body`` is everything after the closing
    fence (or the whole text when there is no leading fence).
    """
    lines = text.split("\n")
    if not lines or not lines[0].startswith("---"):
        return ("", text)
    i = 1
    while i < len(lines) and not lines[i].startswith("---"):
        i += 1
    if i >= len(lines):
        return ("", text)
    metadata_raw = "\n".join(lines[1:i])
    return (metadata_raw, "\n".join(lines[i + 1 :]))


def extract_title(metadata_raw: str, body: str, filename: str) -> str:
    """Title from ``title:`` frontmatter, else the first ``#`` heading, else the file name."""
    if metadata_raw:
        match = re.search(r"title: (.*)", metadata_raw)
        if match:
            return match.group(1).strip()
    match = re.search(r"# (.*)", body)
    if match:
        return match.group(1).strip()
    return filename.replace(".md", "").replace("-", " ").title()


def extract_description(metadata_raw: str, body: str) -> str:
    """Description from ``description:`` frontmatter, else the first prose line of the body."""
    if metadata_raw:
        match = re.search(r"description: (.*)", metadata_raw)
        if match:
            return match.group(1).strip()
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "![", "<", "!!!")):
            continue
        text = _MARKDOWN_CHARS.sub("", line).strip()
        if not text:
            continue
        return text[:100] + "..." if len(text) > 100 else text
    return ""


def extract_index(metadata_raw: str) -> int:
    if metadata_raw:
        match = re.search(r"index: (.*)", metadata_raw)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return 0
    return 0


def extract_hide_docs_list(metadata_raw: str) -> bool:
    match = re.search(r"hide_docs_list: (.*)", metadata_raw)
    return bool(match and match.group(1).strip() == "true")


def extract_hide_contributing_note(metadata_raw: str) -> bool:
    return bool(metadata_raw and re.search(r"hideContributingNote", metadata_raw, re.IGNORECASE))


def extract_hide_navigation(metadata_raw: str) -> bool:
    return bool(metadata_raw and re.search(r"- navigation", metadata_raw))


def parse_page(text: str, filename: str) -> tuple[PageMetadata, str]:
    """Parse a full markdown page into its metadata and body (after frontmatter)."""
    metadata_raw, body = split_frontmatter_lines(text)
    return (
        PageMetadata(
            title=extract_title(metadata_raw, body, filename),
            description=extract_description(metadata_raw, body),
            index=extract_index(metadata_raw),
            hide_docs_list=extract_hide_docs_list(metadata_raw),
            hide_contributing_note=extract_hide_contributing_note(metadata_raw),
            hide_navigation=extract_hide_navigation(metadata_raw),
        ),
        body,
    )
