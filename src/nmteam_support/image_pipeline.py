"""Documentation asset staging and raster optimization."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

RASTER_QUALITY = 80
_RASTER_SUFFIXES = {".jpg", ".jpeg", ".png"}


def stage_assets(source_dir: Path, target_dir: Path) -> None:
    """Stage assets, emitting optimized fallbacks and WebP raster variants."""
    for source in sorted(source_dir.rglob("*")):
        relative = source.relative_to(source_dir)
        target = target_dir / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.suffix.lower() in _RASTER_SUFFIXES:
            target.parent.mkdir(parents=True, exist_ok=True)
            _optimize_raster(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _optimize_raster(source: Path, fallback: Path) -> None:
    with Image.open(source) as image:
        image.load()
        webp = fallback.with_suffix(".webp")
        image.save(webp, "WEBP", quality=RASTER_QUALITY, method=6)
        if fallback.suffix.lower() == ".png":
            _quantize_png(image).save(fallback, "PNG", optimize=True)
        else:
            jpeg = image if image.mode in {"RGB", "L", "CMYK"} else image.convert("RGB")
            jpeg.save(
                fallback,
                "JPEG",
                quality=RASTER_QUALITY,
                optimize=True,
                progressive=True,
            )


def _quantize_png(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        return image.convert("RGBA").quantize(
            colors=256,
            method=Image.Quantize.FASTOCTREE,
        )
    return image.convert("RGB").quantize(
        colors=256,
        method=Image.Quantize.MEDIANCUT,
    )
