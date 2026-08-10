"""llms.txt generation from the scanned docs tree."""

from __future__ import annotations

from nmteam_support.models import DocEntry
from nmteam_support.scanner import ScannedDir

SITE_TITLE = "nmTeam Support"

# Optional section skipped when a shorter context is needed (llmstxt.org spec).
OPTIONAL_SECTION = "Optional"


def render_llms_txt(root: ScannedDir, base_url: str) -> str:
    """Render the ``/llms.txt`` file following the llmstxt.org proposal.

    Every link points to the raw Markdown copy written next to the rendered
    page (same docs-relative path), so LLMs can fetch page bodies directly.
    """
    normalized_base_url = base_url.rstrip("/")
    lines = [f"# {SITE_TITLE}", ""]
    summary = root.index_meta.description or "nmTeam 官方支持文档站。"
    lines.append(f"> {summary}")
    lines.append("")
    lines.append("本文件面向语言模型，提供 nmTeam 支持文档的索引；")
    lines.append("每个链接指向对应页面的 Markdown 版本。")
    lines.append("")

    sections = _sections(root)
    if sections:
        for title, entries in sections:
            lines.append(f"## {title}")
            lines.append("")
            for entry in entries:
                lines.append(_render_entry(entry, normalized_base_url))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_entry(entry: DocEntry, base_url: str) -> str:
    line = f"- [{entry.title}]({base_url}/{entry.path})"
    if entry.description:
        line += f": {entry.description}"
    return line


def _sections(root: ScannedDir) -> list[tuple[str, list[DocEntry]]]:
    """Collect ``(section title, entries)`` pairs, one per directory with content."""
    sections: list[tuple[str, list[DocEntry]]] = []
    entries = _index_entry(root) + list(root.docs)
    if entries:
        title = root.index_meta.title or "站点"
        sections.append((title, _sorted(entries)))
    for sub in root.subdirs:
        sections.extend(_sections(sub))
    return sections


def _index_entry(scan: ScannedDir) -> list[DocEntry]:
    """The directory's own index.md as a DocEntry, when present."""
    if not scan.has_index:
        return []
    path = f"{scan.rel_path}/index.md" if scan.rel_path else "index.md"
    return [
        DocEntry(
            title=scan.index_meta.title,
            description=scan.index_meta.description or "目录索引",
            path=path,
            name="index.md",
        )
    ]


def _sorted(entries: list[DocEntry]) -> list[DocEntry]:
    return sorted(entries, key=lambda entry: (entry.index, entry.path))
