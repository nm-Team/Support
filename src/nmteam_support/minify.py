"""HTML minification of rendered pages, cached by the exact input that produced it."""

from __future__ import annotations

from pathlib import Path

import htmlmin

from nmteam_support.cache import content_digest, staged_path

# The options the site has always minified with. Quoting and empty attributes are
# deliberately preserved: MkDocs Material's navigation binds its behaviour to
# ``label[tabindex]``, so a minifier that drops empty attributes would silently break it.
_OPTIONS: dict[str, bool] = {
    "remove_comments": True,
    "remove_optional_attribute_quotes": False,
    "reduce_empty_attributes": False,
}

# Bump when the minifier output changes in a way ``_OPTIONS`` cannot express.
_CACHE_VERSION = 1
_MINIFIER = f"v{_CACHE_VERSION}|htmlmin2|{sorted(_OPTIONS.items())}".encode()


def render_minified_html(html: str, *, cache_dir: Path) -> str:
    """Minify one rendered page, reusing the cached result of an identical input.

    htmlmin is pure Python and costs about 0.7s for the whole site, while the pages it
    receives repeat byte for byte across builds whenever the documentation tree is
    unchanged — see ``benchmarks/test_bench_minify.py``.
    """
    digest = content_digest(_MINIFIER, html.encode("utf-8"))
    cached = cache_dir / digest
    if cached.is_file():
        return cached.read_text(encoding="utf-8")
    minified = _minify(html)
    cache_dir.mkdir(parents=True, exist_ok=True)
    staged = staged_path(cached)
    staged.write_text(minified, encoding="utf-8")
    staged.replace(cached)
    return minified


def _minify(html: str) -> str:
    return htmlmin.minify(html, **_OPTIONS)
