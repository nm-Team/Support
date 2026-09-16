"""Encoder effort and concurrency, measured on the site's real rasters."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import nmteam_support.image_pipeline as image_pipeline


@pytest.mark.parametrize("method", [4, 5, 6])
def test_cold_encode_pass_by_webp_method(
    benchmark, monkeypatch, assets_dir: Path, tmp_path: Path, method: int
):
    """What ``WEBP_METHOD`` buys: encode effort against bytes and wall clock."""
    cache_dir = tmp_path / f"cache-m{method}"
    target = tmp_path / f"site-m{method}"
    monkeypatch.setattr(image_pipeline, "WEBP_METHOD", method)

    benchmark.pedantic(
        lambda: image_pipeline.optimize_assets(assets_dir, target, cache_dir=cache_dir),
        setup=lambda: shutil.rmtree(cache_dir, ignore_errors=True),
        rounds=3,
        iterations=1,
    )


@pytest.mark.parametrize("workers", [1, 4, 8])
def test_cold_encode_pass_by_worker_count(
    benchmark, monkeypatch, assets_dir: Path, tmp_path: Path, workers: int
):
    """Whether the thread pool actually scales: Pillow's encoder releases the GIL."""
    cache_dir = tmp_path / f"cache-w{workers}"
    target = tmp_path / f"site-w{workers}"
    monkeypatch.setattr(image_pipeline, "MAX_IMAGE_WORKERS", workers)

    benchmark.pedantic(
        lambda: image_pipeline.optimize_assets(assets_dir, target, cache_dir=cache_dir),
        setup=lambda: shutil.rmtree(cache_dir, ignore_errors=True),
        rounds=3,
        iterations=1,
    )
