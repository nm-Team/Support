"""Recursive scanning of the docs directory tree."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from nmteam_support.frontmatter import parse_page
from nmteam_support.models import DocEntry, PageMetadata

# Directories copied verbatim into the output (never scanned or indexed).
SKIP_DIRS = frozenset({"img"})

# Internal directories that are never published to the generated site.
INTERNAL_DIRS = frozenset({"superpowers"})


@dataclass
class ScannedDir:
    """Everything the generator needs to know about one directory under docs/."""

    rel_path: str  # path relative to the docs root; "" for the root itself
    has_index: bool
    index_meta: PageMetadata  # metadata from index.md (or name-derived defaults)
    index_body: str  # index.md body after frontmatter ("" when absent/empty)
    docs: list[DocEntry] = field(default_factory=list)  # non-index .md files
    subdirs: list["ScannedDir"] = field(default_factory=list)
    other_files: list[str] = field(default_factory=list)  # non-.md files, relative paths
    image_dirs: list[str] = field(default_factory=list)  # dirs named "img", relative paths


def scan_docs(docs_dir: Path) -> ScannedDir:
    """Scan ``docs_dir`` recursively and return the resulting tree."""
    return _scan(docs_dir, "")


def _scan(dir_path: Path, rel_path: str) -> ScannedDir:
    docs: list[DocEntry] = []
    subdirs: list[ScannedDir] = []
    other_files: list[str] = []
    image_dirs: list[str] = []
    index_meta = PageMetadata(title=dir_path.name, description="")
    index_body = ""
    has_index = False

    for name in os.listdir(dir_path):  # keep listdir order for stable ties
        entry = dir_path / name
        child_rel = f"{rel_path}/{name}" if rel_path else name
        if entry.is_dir():
            if name in SKIP_DIRS:
                image_dirs.append(child_rel)
            elif name in INTERNAL_DIRS:
                continue
            else:
                subdirs.append(_scan(entry, child_rel))
        elif name.endswith(".md"):
            text = entry.read_text(encoding="utf-8", errors="ignore")
            if not text:  # empty files are skipped entirely
                continue
            meta, body = parse_page(text, name)
            if name == "index.md":
                has_index = True
                index_meta = meta
                index_body = _index_body(text, body)
            else:
                docs.append(
                    DocEntry(
                        title=meta.title,
                        description=meta.description,
                        path=child_rel,
                        name=name,
                        index=meta.index,
                        kind="doc",
                        hide_contributing_note=meta.hide_contributing_note,
                    )
                )
        else:
            other_files.append(child_rel)

    return ScannedDir(
        rel_path=rel_path,
        has_index=has_index,
        index_meta=index_meta,
        index_body=index_body,
        docs=docs,
        subdirs=subdirs,
        other_files=other_files,
        image_dirs=image_dirs,
    )


def _index_body(text: str, body: str) -> str:
    """index.md body: only kept when at least one non-empty line survives."""
    if not text.startswith("---"):
        return text  # whole file is the body
    return body if any(line for line in body.split("\n")) else ""
