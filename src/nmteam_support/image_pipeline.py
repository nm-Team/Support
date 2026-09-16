"""Content-addressed raster optimization with a persistent build cache."""

from __future__ import annotations

import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from nmteam_support.cache import content_digest, staged_path

RASTER_QUALITY = 80
RASTER_SUFFIXES = frozenset({".jpg", ".jpeg", ".png"})
PNG_COLORS = 256

# Pillow's WebP ``method`` trades encoding effort for a few percent of bytes. Measured on
# this repository's rasters, dropping from ``6`` to ``5`` costs 1.7% more bytes and takes
# roughly a quarter of the encode time — see ``benchmarks/test_bench_image_pipeline.py``.
WEBP_METHOD = 5

# Encoding runs in Pillow's C encoder, which releases the GIL, so threads scale with cores.
# The same benchmark measures the full pass at 2.7s / 1.0s / 0.7s for 1 / 4 / 8 workers.
MAX_IMAGE_WORKERS = 8

# Bump when the encoder pipeline changes in a way ``_ENCODER`` cannot express, otherwise
# the parameters below would keep matching stale cache entries.
CACHE_VERSION = 1

_ENCODER = (
    f"v{CACHE_VERSION}|webp:{RASTER_QUALITY}:{WEBP_METHOD}"
    f"|png:{PNG_COLORS}|jpeg:{RASTER_QUALITY}:progressive"
).encode()


@dataclass(frozen=True)
class RasterJob:
    """One source raster plus the cache and output paths derived from its content."""

    source: Path
    target: Path
    cache_dir: Path
    digest: str

    @property
    def outputs(self) -> tuple[tuple[Path, Path], ...]:
        """``(cached, published)`` pairs: WebP first, original-format fallback second."""
        return (
            (self.cache_dir / f"{self.digest}.webp", self.target.with_suffix(".webp")),
            (self.cache_dir / f"{self.digest}{self.target.suffix.lower()}", self.target),
        )


def optimize_assets(source_dir: Path, target_dir: Path, *, cache_dir: Path) -> int:
    """Publish optimized rasters into ``target_dir`` and return how many were encoded.

    A raster is only encoded when its cache entry is missing, so a warm build is a
    content hash plus a file copy per asset. The return value lets callers and tests
    tell a cold build from a warm one.
    """
    jobs = _collect(source_dir, target_dir, cache_dir)
    misses = [job for job in jobs if not _is_cached(job)]
    if misses:
        with ThreadPoolExecutor(max_workers=_worker_count(len(misses))) as executor:
            list(executor.map(_encode, misses))
    for job in jobs:
        for cached, published in job.outputs:
            published.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cached, published)
    return len(misses)


def _collect(source_dir: Path, target_dir: Path, cache_dir: Path) -> list[RasterJob]:
    return [
        RasterJob(
            source=source,
            target=target_dir / source.relative_to(source_dir),
            cache_dir=cache_dir,
            digest=_digest(source),
        )
        for source in sorted(source_dir.rglob("*"))
        if source.is_file() and source.suffix.lower() in RASTER_SUFFIXES
    ]


def _digest(source: Path) -> str:
    """Content address over the source bytes and the encoder parameters."""
    return content_digest(_ENCODER, source.read_bytes())


def _is_cached(job: RasterJob) -> bool:
    return all(cached.is_file() for cached, _ in job.outputs)


def _worker_count(pending: int) -> int:
    return max(1, min(MAX_IMAGE_WORKERS, pending, (os.cpu_count() or 1) - 1))


def _encode(job: RasterJob) -> None:
    """Encode one source into the cache; published files are always copies of it."""
    job.cache_dir.mkdir(parents=True, exist_ok=True)
    webp, fallback = (cached for cached, _ in job.outputs)
    with Image.open(job.source) as image:
        image.load()
        _save(image, webp, "WEBP", quality=RASTER_QUALITY, method=WEBP_METHOD)
        if fallback.suffix == ".png":
            _save(_quantize_png(image), fallback, "PNG", optimize=True)
        else:
            _save(
                _jpeg_ready(image),
                fallback,
                "JPEG",
                quality=RASTER_QUALITY,
                optimize=True,
                progressive=True,
            )


def _save(image: Image.Image, path: Path, image_format: str, **options: bool | int) -> None:
    """Stage through a process-unique file so a parallel build never reads a partial image."""
    staged = staged_path(path)
    image.save(staged, image_format, **options)
    staged.replace(path)


def _jpeg_ready(image: Image.Image) -> Image.Image:
    return image if image.mode in {"RGB", "L", "CMYK"} else image.convert("RGB")


def _quantize_png(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        return image.convert("RGBA").quantize(
            colors=PNG_COLORS,
            method=Image.Quantize.FASTOCTREE,
        )
    return image.convert("RGB").quantize(
        colors=PNG_COLORS,
        method=Image.Quantize.MEDIANCUT,
    )
