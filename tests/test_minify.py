"""HTML minification tests."""

from __future__ import annotations

from pathlib import Path

import pytest

import nmteam_support.minify as minify
from nmteam_support.minify import render_minified_html


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "cache" / "html"


def test_render_minified_html_removes_comments_and_keeps_attribute_quoting(cache_dir: Path):
    source = (
        '<footer class="md-footer" data-empty=""><!-- internal --><div>Copyright</div></footer>'
    )

    output = render_minified_html(source, cache_dir=cache_dir)

    assert 'class="md-footer"' in output
    assert 'data-empty=""' in output
    assert "internal" not in output
    assert len(output) < len(source)


def test_render_minified_html_keeps_the_empty_tabindex_navigation_hook(cache_dir: Path):
    """MkDocs Material binds its navigation state updates to ``label[tabindex]``.

    The theme renders ``tabindex=""`` for collapsible sections, so a minifier that
    drops empty attributes would silently detach that behaviour.
    """
    source = '<label class="md-nav__link" for="__nav_4" id="__nav_4_label" tabindex=""></label>'

    output = render_minified_html(source, cache_dir=cache_dir)

    assert 'tabindex=""' in output


def test_render_minified_html_reuses_the_cached_result(cache_dir: Path, monkeypatch):
    source = "<div>  spaced  </div>"
    first = render_minified_html(source, cache_dir=cache_dir)

    def explode(_: str) -> str:
        raise AssertionError("re-minified an input that was already cached")

    monkeypatch.setattr(minify, "_minify", explode)

    assert render_minified_html(source, cache_dir=cache_dir) == first


def test_render_minified_html_caches_distinct_inputs_separately(cache_dir: Path):
    assert render_minified_html("<p>a</p>", cache_dir=cache_dir) != render_minified_html(
        "<p>b</p>", cache_dir=cache_dir
    )

    assert len(list(cache_dir.iterdir())) == 2
