"""Directory index.md page generation."""

from __future__ import annotations

from nmteam_support.docslist import render_docs_list
from nmteam_support.nav import folder_entries, sort_entries
from nmteam_support.scanner import ScannedDir


def render_index_page(scan: ScannedDir) -> str:
    """Render the complete index.md content (frontmatter + body + docsList) for a directory."""
    head_lines = [
        "---",
        "automatically_generated: Don't edit this file directly, it's auto generated.",
        f"title: {scan.index_meta.title}",
        "",
        "hide:",
        "  - toc",
    ]
    if scan.index_meta.hide_navigation:
        head_lines.append("  - navigation")
    head_lines.append("---")
    head_lines.append("")
    head = "\n".join(head_lines) + "\n"

    if scan.index_body:
        content = scan.index_body
    else:
        content = f"# {scan.index_meta.title}\n{scan.index_meta.description}\n"

    if not scan.index_meta.hide_docs_list:
        entries = sort_entries(scan.docs + folder_entries(scan))
        content += render_docs_list(entries)
    return head + content
