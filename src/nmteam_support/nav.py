"""MkDocs nav YAML generation from a scanned docs tree."""

from __future__ import annotations

from nmteam_support.models import DocEntry
from nmteam_support.scanner import ScannedDir


def sort_entries(entries: list[DocEntry]) -> list[DocEntry]:
    """Order entries: index ascending, folders before docs, then scan order (stable)."""
    return sorted(entries, key=lambda e: (e.index, 0 if e.kind == "folder" else 1))


def folder_entries(scan: ScannedDir) -> list[DocEntry]:
    """Folder entries of ``scan`` that are renderable (have a non-empty nav block)."""
    return [
        DocEntry(
            title=sub.index_meta.title,
            description=sub.index_meta.description,
            path=sub.rel_path,
            name=sub.rel_path.rsplit("/", 1)[-1],
            index=sub.index_meta.index,
            kind="folder",
        )
        for sub in scan.subdirs
        if is_renderable(sub)
    ]


def is_renderable(scan: ScannedDir) -> bool:
    """A directory produces output when it has an index body, docs, or renderable subdirs."""
    return bool(scan.index_body or scan.docs or any(is_renderable(sub) for sub in scan.subdirs))


def build_nav_yaml(root: ScannedDir) -> str:
    """Render the nav block (without the ``nav:`` key) for the whole tree."""
    return _render(root, 0)


def _render(scan: ScannedDir, depth: int) -> str:
    indent = "  " * (depth + 1)
    lines: list[str] = []
    if scan.index_body:
        link = "" if scan.rel_path == "" else scan.rel_path + "/"
        lines.append(f"{indent}- {scan.index_meta.title}: '{link}index.md'")
    for entry in sort_entries(scan.docs + folder_entries(scan)):
        if entry.kind == "folder":
            sub = next(s for s in scan.subdirs if s.rel_path == entry.path)
            sub_block = _render(sub, depth + 1)
            if sub_block:  # empty folders are skipped entirely
                lines.append(f"{indent}- {entry.title}:")
                lines.append(sub_block)
        else:
            lines.append(f"{indent}- {entry.title}: '{entry.path}'")
    return "\n".join(lines)
