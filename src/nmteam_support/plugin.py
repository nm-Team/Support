"""MkDocs plugin that renders derived content without staging directories."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Literal

from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from nmteam_support.cache import CACHE_DIR_NAME
from nmteam_support.contributing import (
    render_contributing_note,
    render_doc_body,
    render_doc_file,
    should_hide_contributing_note,
)
from nmteam_support.icon_elements import render_portable_markdown
from nmteam_support.image_pipeline import RASTER_SUFFIXES, optimize_assets
from nmteam_support.index import render_index_body, render_index_page, render_portable_index_page
from nmteam_support.llms import render_llms_txt
from nmteam_support.minify import render_minified_html
from nmteam_support.models import DocEntry
from nmteam_support.nav import build_nav, is_renderable
from nmteam_support.redirects import read_redirects, render_redirects_js
from nmteam_support.review import REVIEW_ASSETS, render_review_context
from nmteam_support.revisions import PageRevision, RevisionError, read_page_revisions
from nmteam_support.scanner import DocumentCatalog, ScannedDir, refresh_catalog


class SupportPluginConfig(Config):
    """The plugin intentionally has no user-facing options."""


class SupportPlugin(BasePlugin[SupportPluginConfig]):
    """Expose derived docs and assets through MkDocs' native build lifecycle."""

    def __init__(self) -> None:
        self._catalog: DocumentCatalog | None = None
        self._directories: dict[str, ScannedDir] = {}
        self._entries: dict[str, DocEntry] = {}
        self._revisions: dict[str, PageRevision] = {}
        self._command: Literal["build", "gh-deploy", "serve"] = "build"

    def on_startup(self, *, command: Literal["build", "gh-deploy", "serve"], dirty: bool) -> None:
        del dirty
        self._command = command

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        root = _project_root(config)
        config.extra["review_enabled"] = self._command == "serve"
        for asset in REVIEW_ASSETS:
            collection = config.extra_css if asset.endswith(".css") else config.extra_javascript
            collection[:] = [item for item in collection if str(item) != asset]
            if self._command == "serve":
                collection.append(asset)
        for path in (root / "assets", root / "redirects.json"):
            value = str(path)
            if path.exists() and value not in config.watch:
                config.watch.append(value)
        return config

    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files:
        self._catalog = refresh_catalog(Path(config.docs_dir), self._catalog)
        try:
            self._revisions = read_page_revisions(Path(config.docs_dir))
        except RevisionError as error:
            raise PluginError(str(error)) from error
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
                    if self._command != "serve" and source_uri in REVIEW_ASSETS:
                        continue
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
        page.meta.pop("page_revision", None)
        if path in self._catalog.pages and path in self._revisions:
            page.meta["page_revision"] = self._revisions[path]
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
        rendered = render_doc_body(markdown, path)
        if self._command == "serve":
            note = render_contributing_note(path)
            rendered = rendered.replace(
                note, '\n<div class="review-generated" markdown="1">\n' + note + "</div>\n"
            )
        return rendered

    def on_page_content(
        self, html: str, /, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str:
        del files
        if self._command != "serve":
            return html
        source = self._catalog.pages.get(page.file.src_uri) if self._catalog else None
        path = (
            Path(config.docs_dir).relative_to(_project_root(config)) / page.file.src_uri
        ).as_posix()
        return render_review_context(
            html,
            source=source.text if source else None,
            path=path,
            project=sha256(str(_project_root(config)).encode()).hexdigest()[:16],
            extensions=config.markdown_extensions,
            extension_configs=config.mdx_configs,
        )

    def on_post_page(self, output: str, /, *, page: Page, config: MkDocsConfig) -> str:
        del page
        # Review ranges use exact DOM text offsets, including inter-block whitespace.
        if self._command == "serve":
            return output
        return render_minified_html(output, cache_dir=_cache_dir(config, "html"))

    def on_post_template(
        self, output_content: str, /, *, template_name: str, config: MkDocsConfig
    ) -> str:
        if not template_name.endswith(".html"):
            return output_content
        return render_minified_html(output_content, cache_dir=_cache_dir(config, "html"))

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        root = _project_root(config)
        assets_dir = root / "assets"
        if assets_dir.is_dir():
            optimize_assets(
                assets_dir,
                Path(config.site_dir) / "assets",
                cache_dir=_cache_dir(config, "images"),
            )
        if self._command != "serve" and self._catalog is not None:
            _write_markdown_copies(self._catalog, self._directories, self._entries, config)


def _project_root(config: MkDocsConfig) -> Path:
    if config.config_file_path:
        return Path(config.config_file_path).resolve().parent
    return Path.cwd()


def _cache_dir(config: MkDocsConfig, namespace: str) -> Path:
    return _project_root(config) / CACHE_DIR_NAME / namespace


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
    """Write one Markdown copy per rendered page, at its docs-relative path.

    Every page the site renders gets a copy so the article actions can point at
    ``page.file.src_uri`` without any URL-to-file guessing.
    """
    copies = {
        path: render_portable_index_page(directory)
        for path, directory in directories.items()
        if path in catalog.pages or is_renderable(directory)
    }
    for path, source in catalog.pages.items():
        if path in directories:
            continue
        entry = entries[path]
        copies[path] = (
            source.text
            if should_hide_contributing_note(entry)
            else render_doc_file(source.text, path)
        )

    site_dir = Path(config.site_dir)
    for path, content in copies.items():
        target = site_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_portable_markdown(content), encoding="utf-8", newline="\n")
