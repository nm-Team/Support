"""Minification cost, cold against cached."""

from __future__ import annotations

import shutil
from pathlib import Path

from nmteam_support.minify import render_minified_html


def test_minify_every_page_cold(benchmark, page_html: list[str], tmp_path: Path):
    """The full-price pass, which is what a clean checkout or CI pays."""
    cache_dir = tmp_path / "cache"

    benchmark.pedantic(
        lambda: [render_minified_html(html, cache_dir=cache_dir) for html in page_html],
        setup=lambda: shutil.rmtree(cache_dir, ignore_errors=True),
        rounds=3,
        iterations=1,
    )


def test_minify_every_page_warm(benchmark, page_html: list[str], tmp_path: Path):
    """The same pass once the cache holds every page, which is the common local build."""
    cache_dir = tmp_path / "cache"
    for html in page_html:
        render_minified_html(html, cache_dir=cache_dir)

    benchmark(lambda: [render_minified_html(html, cache_dir=cache_dir) for html in page_html])


def test_minify_single_page_cold(benchmark, page_html: list[str], tmp_path: Path):
    """One page re-rendered: the only work a single-page edit should ever repeat."""
    cache_dir = tmp_path / "cache"
    page = max(page_html, key=len)

    benchmark.pedantic(
        lambda: render_minified_html(page, cache_dir=cache_dir),
        setup=lambda: shutil.rmtree(cache_dir, ignore_errors=True),
        rounds=5,
        iterations=1,
    )
