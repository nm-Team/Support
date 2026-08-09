"""End-to-end documentation generation orchestration."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from nmteam_support.contributing import render_contributing_note, should_hide_contributing_note
from nmteam_support.frontmatter import split_frontmatter
from nmteam_support.index import render_index_page
from nmteam_support.nav import build_nav_yaml
from nmteam_support.redirects import load_redirects, render_redirects_js
from nmteam_support.scanner import ScannedDir, scan_docs
from nmteam_support.template import render_mkdocs_yml


@dataclass(frozen=True)
class GeneratorOptions:
    """All paths the generator touches; tests inject tmp_path-based values."""

    docs_dir: Path
    assets_dir: Path
    template_path: Path
    redirects_path: Path
    cache_dir: Path
    generated_dir: Path
    mkdocs_yml_path: Path


def default_options(root: Path | None = None) -> GeneratorOptions:
    root = root or Path.cwd()
    return GeneratorOptions(
        docs_dir=root / "docs",
        assets_dir=root / "assets",
        template_path=root / "mkdocs-template.yml",
        redirects_path=root / "redirects.json",
        cache_dir=root / "cache",
        generated_dir=root / "generated",
        mkdocs_yml_path=root / "mkdocs.yml",
    )


def generate(options: GeneratorOptions) -> None:
    """Regenerate ``cache/``, ``generated/`` and ``mkdocs.yml`` from ``docs/``."""
    print("Generating documentation...")
    cache_dir = options.cache_dir
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir()

    root = scan_docs(options.docs_dir)

    _write_tree(options.docs_dir, cache_dir, root)
    _write_indexes(cache_dir, root)
    if options.assets_dir.exists():
        shutil.copytree(options.assets_dir, cache_dir / "assets", dirs_exist_ok=True)

    nav_yaml = build_nav_yaml(root)
    template = options.template_path.read_text(encoding="UTF-8", errors="ignore")
    options.mkdocs_yml_path.write_text(render_mkdocs_yml(template, nav_yaml), encoding="UTF-8")

    redirects = load_redirects(options.redirects_path)
    if redirects is None:
        print("Warning: redirects.json not found. Skipping redirects generation.")
    else:
        assets_js = cache_dir / "assets" / "js"
        assets_js.mkdir(parents=True, exist_ok=True)
        (assets_js / "redirects.js").write_text(render_redirects_js(redirects), encoding="utf-8")
        print("Redirects script generated.")

    if options.generated_dir.exists():
        shutil.rmtree(options.generated_dir)
    shutil.copytree(cache_dir, options.generated_dir)
    print("Documentation generated.")


def _write_tree(docs_dir: Path, cache_dir: Path, scan: ScannedDir) -> None:
    for doc in scan.docs:
        source = docs_dir / doc.path
        target = cache_dir / doc.path
        target.parent.mkdir(parents=True, exist_ok=True)
        if should_hide_contributing_note(doc):
            shutil.copyfile(source, target)
        else:
            text = source.read_text(encoding="UTF-8", errors="ignore")
            target.write_text(render_doc_file(text, doc.path), encoding="UTF-8")
    for rel in scan.other_files:
        source = docs_dir / rel
        target = cache_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for rel in scan.image_dirs:
        target = cache_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(docs_dir / rel, target)
    for sub in scan.subdirs:
        _write_tree(docs_dir, cache_dir, sub)


def render_doc_file(text: str, doc_path: str) -> str:
    """Return ``text`` with the contributing note injected after the first heading."""
    metadata_raw, body = split_frontmatter(text)
    note = render_contributing_note(doc_path)
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            lines.insert(i + 1, note)
            break
    else:
        return (f"---{metadata_raw}---" if metadata_raw else "") + note + body
    return (f"---{metadata_raw}---" if metadata_raw else "") + "\n".join(lines)


def _write_indexes(cache_dir: Path, scan: ScannedDir) -> None:
    target = cache_dir / scan.rel_path / "index.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_index_page(scan), encoding="UTF-8")
    for sub in scan.subdirs:
        _write_indexes(cache_dir, sub)
