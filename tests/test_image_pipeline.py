"""Raster asset optimization tests."""

from __future__ import annotations

import os
import shutil
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

import nmteam_support.image_pipeline as image_pipeline


def _gradient(mode: str = "RGB") -> Image.Image:
    image = Image.new(mode, (32, 32))
    for y in range(32):
        for x in range(32):
            pixel = (x * 8, y * 8, (x + y) * 4)
            image.putpixel((x, y), (*pixel, (x * y) % 256) if mode == "RGBA" else pixel)
    return image


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "cache" / "images"


def test_optimize_assets_emits_webp_and_jpeg_fallback(tmp_path: Path, cache_dir: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _gradient().save(source / "photo.jpg", quality=95)

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1

    with Image.open(source / "photo.jpg") as decoded:
        expected_jpeg = BytesIO()
        decoded.save(expected_jpeg, "JPEG", quality=80, optimize=True, progressive=True)
        expected_webp = BytesIO()
        decoded.save(
            expected_webp,
            "WEBP",
            quality=image_pipeline.RASTER_QUALITY,
            method=image_pipeline.WEBP_METHOD,
        )
    assert (target / "photo.jpg").read_bytes() == expected_jpeg.getvalue()
    assert (target / "photo.webp").read_bytes() == expected_webp.getvalue()


def test_optimize_assets_quantizes_png_fallback_and_preserves_alpha_in_webp(
    tmp_path: Path, cache_dir: Path
):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _gradient("RGBA").save(source / "diagram.png")

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1

    with Image.open(target / "diagram.png") as fallback:
        assert fallback.mode == "P"
        assert fallback.getbands() == ("P",)
    with Image.open(target / "diagram.webp") as preferred:
        assert preferred.format == "WEBP"
        assert "A" in preferred.getbands()


def test_optimize_assets_republishes_from_cache_after_the_site_is_wiped(
    tmp_path: Path, cache_dir: Path
):
    """The cache outlives ``site/``, which MkDocs clears on every non-dirty build."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    Image.new("RGB", (16, 16), "red").save(source / "diagram.png")

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1
    webp = (target / "diagram.webp").read_bytes()

    shutil.rmtree(target)  # what MkDocs does to site/ before every non-dirty build

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 0
    assert (target / "diagram.webp").read_bytes() == webp
    assert (target / "diagram.png").is_file()


def test_optimize_assets_reencodes_when_content_changes_under_the_old_stamp(
    tmp_path: Path, cache_dir: Path
):
    """Entries are addressed by content, so a rewritten file cannot pass as unchanged."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    image = source / "diagram.png"
    Image.new("RGB", (16, 16), "red").save(image)
    stamp = image.stat().st_mtime_ns

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1
    original = (target / "diagram.webp").read_bytes()

    Image.new("RGB", (16, 16), "blue").save(image)
    os.utime(image, ns=(stamp, stamp))

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1
    assert (target / "diagram.webp").read_bytes() != original


def test_optimize_assets_reencodes_when_encoder_parameters_change(
    tmp_path: Path, cache_dir: Path, monkeypatch
):
    """Retuning the encoder must not keep publishing output from the previous settings."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    Image.new("RGB", (16, 16), "red").save(source / "diagram.png")

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1

    monkeypatch.setattr(image_pipeline, "_ENCODER", b"retuned")

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 1


def test_optimize_assets_publishes_only_completed_cache_entries(tmp_path: Path, cache_dir: Path):
    """Nothing partial may reach ``site/``: entries are staged before they are visible."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    Image.new("RGB", (16, 16), "red").save(source / "diagram.png")

    image_pipeline.optimize_assets(source, target, cache_dir=cache_dir)

    assert not list(cache_dir.glob("*.part"))
    assert not list(target.glob("*.part"))


def test_optimize_assets_ignores_non_raster_sources(tmp_path: Path, cache_dir: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    (source / "notes.txt").write_text("not an image", encoding="utf-8")

    assert image_pipeline.optimize_assets(source, target, cache_dir=cache_dir) == 0
    assert not target.exists()
