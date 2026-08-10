"""Raster asset optimization tests."""

from io import BytesIO
from pathlib import Path

from PIL import Image

from nmteam_support.image_pipeline import stage_assets


def _gradient(mode: str = "RGB") -> Image.Image:
    image = Image.new(mode, (32, 32))
    for y in range(32):
        for x in range(32):
            pixel = (x * 8, y * 8, (x + y) * 4)
            image.putpixel((x, y), (*pixel, (x * y) % 256) if mode == "RGBA" else pixel)
    return image


def test_stage_assets_emits_quality_80_webp_and_jpeg_fallback(tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    image = _gradient()
    image.save(source / "photo.jpg", quality=95)

    stage_assets(source, target)

    with Image.open(source / "photo.jpg") as decoded:
        expected_jpeg = BytesIO()
        decoded.save(expected_jpeg, "JPEG", quality=80, optimize=True, progressive=True)
        expected_webp = BytesIO()
        decoded.save(expected_webp, "WEBP", quality=80, method=6)
    assert (target / "photo.jpg").read_bytes() == expected_jpeg.getvalue()
    assert (target / "photo.webp").read_bytes() == expected_webp.getvalue()


def test_stage_assets_quantizes_png_fallback_and_preserves_alpha_in_webp(tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _gradient("RGBA").save(source / "diagram.png")

    stage_assets(source, target)

    with Image.open(target / "diagram.png") as fallback:
        assert fallback.mode == "P"
        assert fallback.getbands() == ("P",)
    with Image.open(target / "diagram.webp") as preferred:
        assert preferred.format == "WEBP"
        assert "A" in preferred.getbands()


def test_stage_assets_copies_non_raster_resources(tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    (source / "icons").mkdir(parents=True)
    (source / "icons" / "doc.svg").write_text("<svg></svg>\n", encoding="utf-8")
    (source / "site.css").write_text("body {}\n", encoding="utf-8")

    stage_assets(source, target)

    assert (target / "icons" / "doc.svg").read_text(encoding="utf-8") == "<svg></svg>\n"
    assert (target / "site.css").read_text(encoding="utf-8") == "body {}\n"
