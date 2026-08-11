"""MkDocs nav YAML generation from a scanned docs tree."""

from __future__ import annotations

from nmteam_support.models import DocEntry
from nmteam_support.scanner import ScannedDir

type NavItem = dict[str, str | list["NavItem"]]


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


def build_nav(root: ScannedDir) -> list[NavItem]:
    """Build the native MkDocs nav structure without serializing YAML."""
    return _build(root)


def _build(scan: ScannedDir) -> list[NavItem]:
    items: list[NavItem] = []
    if scan.index_body:
        path = f"{scan.rel_path}/index.md" if scan.rel_path else "index.md"
        items.append({scan.index_meta.title: path})
    for entry in sort_entries(scan.docs + folder_entries(scan)):
        if entry.kind == "folder":
            sub = next(child for child in scan.subdirs if child.rel_path == entry.path)
            children = _build(sub)
            if children:
                items.append({entry.title: children})
        else:
            items.append({entry.title: entry.path})
    return items
