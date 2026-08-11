"""MkDocs plugin that renders derived content without staging directories."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from nmteam_support.contributing import (
    render_doc_body,
    render_doc_file,
    should_hide_contributing_note,
)
from nmteam_support.image_pipeline import RASTER_SUFFIXES, optimize_assets
from nmteam_support.index import render_index_body, render_index_page
from nmteam_support.llms import render_llms_txt
from nmteam_support.models import DocEntry
from nmteam_support.nav import build_nav, is_renderable
from nmteam_support.redirects import read_redirects, render_redirects_js
from nmteam_support.scanner import DocumentCatalog, ScannedDir, refresh_catalog


class SupportPluginConfig(Config):
    """The plugin intentionally has no user-facing options."""


class SupportPlugin(BasePlugin[SupportPluginConfig]):
    """Expose derived docs and assets through MkDocs' native build lifecycle."""

    def __init__(self) -> None:
        self._catalog: DocumentCatalog | None = None
        self._directories: dict[str, ScannedDir] = {}
        self._entries: dict[str, DocEntry] = {}
        self._command: Literal["build", "gh-deploy", "serve"] = "build"
        self._dirty = False

    def on_startup(self, *, command: Literal["build", "gh-deploy", "serve"], dirty: bool) -> None:
        self._command = command
        self._dirty = dirty

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        root = _project_root(config)
        for path in (root / "assets", root / "redirects.json"):
            value = str(path)
            if path.exists() and value not in config.watch:
                config.watch.append(value)
        return config

    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files:
        self._catalog = refresh_catalog(Path(config.docs_dir), self._catalog)
        self._directories = _directory_map(self._catalog.root)
        self._entries = _entry_map(self._catalog.root)
        config.nav = build_nav(self._catalog.root)

        for file in list(files):
            if file.src_uri == "superpowers" or file.src_uri.startswith("superpowers/"):
                files.remove(file)

        for source_uri, directory in self._directories.items():
            if not directory.has_index and is_renderable(directory):
                files.append(
                    File.generated(config, source_uri, content=render_index_page(directory))
                )

        root = _project_root(config)
        assets_dir = root / "assets"
        if assets_dir.is_dir():
            for source in sorted(assets_dir.rglob("*")):
                if source.is_file() and source.suffix.lower() not in RASTER_SUFFIXES:
                    source_uri = f"assets/{source.relative_to(assets_dir).as_posix()}"
                    files.append(File.generated(config, source_uri, abs_src_path=str(source)))

        redirects = read_redirects(root / "redirects.json")
        files.append(
            File.generated(
                config,
                "assets/js/redirects.js",
                content=render_redirects_js(redirects),
            )
        )
        files.append(
            File.generated(
                config,
                "llms.txt",
                content=render_llms_txt(self._catalog.root, config.site_url or ""),
            )
        )
        return files

    def on_page_markdown(
        self,
        markdown: str,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str:
        del config, files
        path = page.file.src_uri
        directory = self._directories.get(path)
        if directory is not None:
            page.meta["automatically_generated"] = (
                "Don't edit this file directly, it's generated at build time."
            )
            page.meta["title"] = directory.index_meta.title
            hidden = list(page.meta.get("hide", []))
            if "toc" not in hidden:
                hidden.append("toc")
            if directory.index_meta.hide_navigation and "navigation" not in hidden:
                hidden.append("navigation")
            page.meta["hide"] = hidden
            return render_index_body(directory)

        entry = self._entries.get(path)
        if entry is None or should_hide_contributing_note(entry):
            return markdown
        return render_doc_body(markdown, path)

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        root = _project_root(config)
        assets_dir = root / "assets"
        if assets_dir.is_dir():
            optimize_assets(
                assets_dir,
                Path(config.site_dir) / "assets",
                incremental=self._dirty,
            )
        if self._command != "serve" and self._catalog is not None:
            _write_markdown_copies(self._catalog, self._directories, self._entries, config)


def _project_root(config: MkDocsConfig) -> Path:
    if config.config_file_path:
        return Path(config.config_file_path).resolve().parent
    return Path.cwd()


def _directory_map(root: ScannedDir) -> dict[str, ScannedDir]:
    result: dict[str, ScannedDir] = {}

    def collect(directory: ScannedDir) -> None:
        path = f"{directory.rel_path}/index.md" if directory.rel_path else "index.md"
        result[path] = directory
        for child in directory.subdirs:
            collect(child)

    collect(root)
    return result


def _entry_map(root: ScannedDir) -> dict[str, DocEntry]:
    result = {entry.path: entry for entry in root.docs}
    for child in root.subdirs:
        result.update(_entry_map(child))
    return result


def _write_markdown_copies(
    catalog: DocumentCatalog,
    directories: dict[str, ScannedDir],
    entries: dict[str, DocEntry],
    config: MkDocsConfig,
) -> None:
    site_dir = Path(config.site_dir)
    for path, source in catalog.pages.items():
        directory = directories.get(path)
        if directory is not None:
            content = render_index_page(directory)
        else:
            entry = entries[path]
            content = (
                source.text
                if should_hide_contributing_note(entry)
                else render_doc_file(source.text, path)
            )
        target = site_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
