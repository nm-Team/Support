"""Shared fixtures for the performance suite.

These benchmarks intentionally run against the real repository: the encoder settings,
cache layout and minifier choices they compare were made for this site's actual mix of
screenshots, diagrams and rendered pages, so synthetic inputs would measure the wrong
work.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

from nmteam_support import plugin as plugin_module
from nmteam_support.image_pipeline import RASTER_SUFFIXES

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def assets_dir() -> Path:
    return REPO_ROOT / "assets"


@pytest.fixture(scope="session")
def raster_paths() -> list[Path]:
    assets = REPO_ROOT / "assets"
    return [
        path
        for path in sorted(assets.rglob("*"))
        if path.is_file() and path.suffix.lower() in RASTER_SUFFIXES
    ]


@pytest.fixture(scope="session")
def raster_payloads(raster_paths: list[Path]) -> list[bytes]:
    """Every raster's bytes, read once so no benchmark measures filesystem reads."""
    return [path.read_bytes() for path in raster_paths]


@pytest.fixture(scope="session")
def page_html(tmp_path_factory: pytest.TempPathFactory) -> list[str]:
    """The HTML the site hands to the minifier, captured from a real build.

    The build runs with the minify hook replaced by the identity function, so these are
    the minifier's inputs rather than its outputs.
    """
    site_dir = tmp_path_factory.mktemp("unminified-site")
    config = load_config(config_file=str(REPO_ROOT / "mkdocs.yml"), strict=True)
    config.site_dir = str(site_dir)
    original = plugin_module.render_minified_html
    plugin_module.render_minified_html = lambda html, *, cache_dir: html
    try:
        config.plugins.on_startup(command="build", dirty=False)
        build(config)
    finally:
        plugin_module.render_minified_html = original
    return [path.read_text(encoding="utf-8") for path in sorted(site_dir.rglob("*.html"))]
