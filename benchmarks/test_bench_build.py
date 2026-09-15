"""End-to-end timings for the shipped command.

Unlike the other benchmarks these measure the real entry point in its own process, so
the numbers include interpreter start-up and are directly comparable to what a developer
sees. They build into the repository's own ``site/`` and reuse its ``.cache/``.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _build(repo_root: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "nmteam_support", "build"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )


def test_build_cold_cache(benchmark, repo_root: Path):
    """A clean checkout, or CI: every raster is encoded and every page minified."""
    benchmark.pedantic(
        lambda: _build(repo_root),
        setup=lambda: shutil.rmtree(repo_root / ".cache", ignore_errors=True),
        rounds=3,
        iterations=1,
    )


def test_build_warm_cache(benchmark, repo_root: Path):
    """The common local loop, where only the edited page has changed."""
    _build(repo_root)
    benchmark.pedantic(lambda: _build(repo_root), rounds=5, iterations=1)
