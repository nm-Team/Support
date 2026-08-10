"""Contributing-note injection for rendered documents."""

from __future__ import annotations

import re

from nmteam_support.frontmatter import split_frontmatter
from nmteam_support.models import DocEntry

GITHUB_EDIT_BASE = "https://github.com/nm-Team/Support/edit/main/docs/"

# Path prefixes that never receive a contributing note.
EXCLUDED_PATH_PATTERNS = (
    r"^legal/",
    r"/legal/",
    r"/update-log/",
)


def render_contributing_note(doc_path: str) -> str:
    """Return the '帮助我们改进此文档' admonition for ``doc_path`` (relative to docs/)."""
    github_edit_url = f"{GITHUB_EDIT_BASE}{doc_path}"
    return (
        "\n"
        f'!!! tip "帮助我们改进此文档"\n'
        "    发现文档有错误或需要改进的地方？您可以：\n"
        "\n"
        f"    - [在 GitHub 上直接编辑此页面]({github_edit_url})\n"
        "    - [提交 Issue 报告问题](https://github.com/nm-Team/Support/issues/new)\n"
        "    - [加入我们的讨论](https://github.com/nm-Team/Support/discussions)\n"
        "\n"
        "    您的贡献将帮助更多用户获得更好的体验！\n"
        "\n"
    )


def should_hide_contributing_note(entry: DocEntry) -> bool:
    """True when a doc must be copied verbatim (no note injected)."""
    if entry.hide_contributing_note:
        return True
    if entry.name == "index.md":
        return True
    return any(re.search(pattern, entry.path) for pattern in EXCLUDED_PATH_PATTERNS)


def render_doc_body(markdown: str, doc_path: str) -> str:
    """Inject the contributing note into a Markdown body."""
    note = render_contributing_note(doc_path)
    lines = markdown.split("\n")
    for index, line in enumerate(lines):
        if line.strip().startswith("#"):
            lines.insert(index + 1, note)
            return "\n".join(lines)
    return note + markdown


def render_doc_file(text: str, doc_path: str) -> str:
    """Inject the note while preserving the source frontmatter."""
    metadata, body = split_frontmatter(text)
    prefix = f"---{metadata}---" if metadata else ""
    return prefix + render_doc_body(body, doc_path)
