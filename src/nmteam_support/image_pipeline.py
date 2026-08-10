"""Direct-to-site raster optimization."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

RASTER_QUALITY = 80
RASTER_SUFFIXES = frozenset({".jpg", ".jpeg", ".png"})
MAX_IMAGE_WORKERS = 4


def optimize_assets(source_dir: Path, target_dir: Path, *, incremental: bool = False) -> int:
    """Write raster variants directly to ``target_dir`` and return the processed count."""
    tasks = [
        (source, target_dir / source.relative_to(source_dir))
        for source in sorted(source_dir.rglob("*"))
        if source.is_file() and source.suffix.lower() in RASTER_SUFFIXES
    ]
    if incremental:
        tasks = [(source, target) for source, target in tasks if _is_stale(source, target)]
    if not tasks:
        return 0
    worker_count = min(MAX_IMAGE_WORKERS, len(tasks), os.cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        list(executor.map(lambda paths: _optimize_raster(*paths), tasks))
    return len(tasks)


def _is_stale(source: Path, fallback: Path) -> bool:
    webp = fallback.with_suffix(".webp")
    if not fallback.exists() or not webp.exists():
        return True
    source_mtime = source.stat().st_mtime_ns
    return fallback.stat().st_mtime_ns < source_mtime or webp.stat().st_mtime_ns < source_mtime


def _optimize_raster(source: Path, fallback: Path) -> None:
    fallback.parent.mkdir(parents=True, exist_ok=True)
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
