"""Directory index.md page generation."""

from __future__ import annotations

import yaml

from nmteam_support.docslist import render_docs_list
from nmteam_support.nav import folder_entries, sort_entries
from nmteam_support.scanner import ScannedDir


def _yaml_title_scalar(title: str) -> str:
    """Render ``title`` as a single valid YAML scalar, quoting only when needed."""
    out = yaml.safe_dump(title, default_flow_style=True, allow_unicode=True)
    # PyYAML >= 6.0.3 closes a plain root scalar with an explicit document-end
    # marker ("..."); it is not part of the scalar, so drop it.
    if out.endswith("\n...\n"):
        out = out[: -len("\n...\n")] + "\n"
    return out.strip()


def render_index_page(scan: ScannedDir) -> str:
    """Render the complete index.md content (frontmatter + body + docsList) for a directory."""
    head_lines = [
        "---",
        "automatically_generated: Don't edit this file directly, it's auto generated.",
        # safe_dump emits a properly quoted/escaped YAML scalar for any title.
        f"title: {_yaml_title_scalar(scan.index_meta.title)}",
        "",
        "hide:",
        "  - toc",
    ]
    if scan.index_meta.hide_navigation:
        head_lines.append("  - navigation")
    head_lines.append("---")
    head_lines.append("")
    head = "\n".join(head_lines) + "\n"

    content = scan.index_body or f"# {scan.index_meta.title}\n{scan.index_meta.description}\n"

    if not scan.index_meta.hide_docs_list:
        entries = sort_entries(scan.docs + folder_entries(scan))
        content += render_docs_list(entries)
    return head + content
