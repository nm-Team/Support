"""Recursive scanning of the docs directory tree."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from nmteam_support.frontmatter import parse_page
from nmteam_support.models import DocEntry, PageMetadata

# Directories copied verbatim into the output (never scanned or indexed).
SKIP_DIRS = frozenset({"img"})

# Internal directories that are never published to the site.
INTERNAL_DIRS = frozenset({"superpowers"})


@dataclass
class ScannedDir:
    """Everything the plugin needs to know about one directory under docs/."""

    rel_path: str  # path relative to the docs root; "" for the root itself
    has_index: bool
    index_meta: PageMetadata  # metadata from index.md (or name-derived defaults)
    index_body: str  # index.md body after frontmatter ("" when absent/empty)
    docs: list[DocEntry] = field(default_factory=list)  # non-index .md files
    subdirs: list[ScannedDir] = field(default_factory=list)
    other_files: list[str] = field(default_factory=list)  # non-.md files, relative paths
    image_dirs: list[str] = field(default_factory=list)  # dirs named "img", relative paths


@dataclass(frozen=True)
class SourcePage:
    """One parsed Markdown source plus the filesystem stamp used for reuse."""

    path: str
    text: str
    metadata: PageMetadata
    body: str
    stamp: tuple[int, int]


@dataclass(frozen=True)
class DocumentCatalog:
    """A scanned document tree with reusable page content."""

    docs_dir: Path
    root: ScannedDir
    pages: dict[str, SourcePage]
    changed_paths: frozenset[str]


def scan_docs(docs_dir: Path) -> ScannedDir:
    """Scan ``docs_dir`` recursively and return the resulting tree."""
    return refresh_catalog(docs_dir).root


def refresh_catalog(docs_dir: Path, previous: DocumentCatalog | None = None) -> DocumentCatalog:
    """Refresh the source catalog, reading only new or modified Markdown files."""
    resolved = docs_dir.resolve()
    previous_pages = previous.pages if previous and previous.docs_dir == resolved else {}
    pages: dict[str, SourcePage] = {}
    changed: set[str] = set()
    root = _scan(resolved, "", previous_pages, pages, changed)
    changed.update(previous_pages.keys() - pages.keys())
    return DocumentCatalog(resolved, root, pages, frozenset(changed))


def _scan(
    dir_path: Path,
    rel_path: str,
    previous_pages: dict[str, SourcePage],
    pages: dict[str, SourcePage],
    changed: set[str],
) -> ScannedDir:
    docs: list[DocEntry] = []
    subdirs: list[ScannedDir] = []
    other_files: list[str] = []
    image_dirs: list[str] = []
    index_meta = PageMetadata(title=dir_path.name, description="")
    index_body = ""
    has_index = False

    for name in sorted(os.listdir(dir_path)):  # deterministic order, cross-platform
        entry = dir_path / name
        child_rel = f"{rel_path}/{name}" if rel_path else name
        if entry.is_dir():
            if name in SKIP_DIRS:
                image_dirs.append(child_rel)
            elif name in INTERNAL_DIRS:
                continue
            else:
                subdirs.append(_scan(entry, child_rel, previous_pages, pages, changed))
        elif name.endswith(".md"):
            stat = entry.stat()
            stamp = (stat.st_mtime_ns, stat.st_size)
            source = previous_pages.get(child_rel)
            if source is None or source.stamp != stamp:
                text = entry.read_text(encoding="utf-8", errors="ignore")
                changed.add(child_rel)
                if not text:
                    continue
                meta, body = parse_page(text, name)
                source = SourcePage(child_rel, text, meta, body, stamp)
            pages[child_rel] = source
            meta = source.metadata
            body = source.body
            if name == "index.md":
                has_index = True
                index_meta = meta
                index_body = _index_body(source.text, body)
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
