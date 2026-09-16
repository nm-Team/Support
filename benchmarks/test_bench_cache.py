"""Cache addressing and the cost of the warm publish path."""

from __future__ import annotations

import shutil
from pathlib import Path

from nmteam_support.cache import content_digest
from nmteam_support.image_pipeline import optimize_assets


def test_content_digest_over_every_raster(benchmark, raster_payloads: list[bytes]):
    """Hashing is what a warm build pays for every asset it does not re-encode."""
    benchmark(lambda: [content_digest(b"image", payload) for payload in raster_payloads])


def test_content_digest_over_a_rendered_page(benchmark, page_html: list[str]):
    benchmark(lambda: [content_digest(b"html", html.encode("utf-8")) for html in page_html])


def test_warm_publish_path(benchmark, assets_dir: Path, tmp_path: Path):
    """A warm build: hash every raster, then copy the cached variants into ``site/``."""
    target = tmp_path / "site"
    cache_dir = tmp_path / "cache"
    optimize_assets(assets_dir, target, cache_dir=cache_dir)

    def wipe_site() -> None:
        shutil.rmtree(target, ignore_errors=True)

    benchmark.pedantic(
        lambda: optimize_assets(assets_dir, target, cache_dir=cache_dir),
        setup=wipe_site,
        rounds=5,
        iterations=1,
    )
