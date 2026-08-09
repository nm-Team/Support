"""Command-line interface: generate / dev / build / clean / install."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from nmteam_support.generator import GeneratorOptions, default_options, generate


def _rm(path: Path) -> None:
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def cmd_clean(options: GeneratorOptions) -> int:
    """Remove cache/, generated/ and site/."""
    for path in (options.cache_dir, options.generated_dir, options.mkdocs_yml_path.parent / "site"):
        _rm(path)
    print("✅ 清理完成")
    return 0


def cmd_build(options: GeneratorOptions) -> int:
    """Regenerate and build the static site into site/."""
    generate(options)
    return subprocess.call([sys.executable, "-m", "mkdocs", "build", "--strict", "--clean"])


def cmd_dev(options: GeneratorOptions) -> int:
    """Regenerate, then serve with live-reload and auto-regeneration."""
    generate(options)
    stop = threading.Event()
    watcher = threading.Thread(target=_watch_and_regenerate, args=(options, stop), daemon=True)
    watcher.start()
    try:
        return subprocess.call(
            [sys.executable, "-m", "mkdocs", "serve", "--dirtyreload", "--dev-addr", "127.0.0.1:8000"]
        )
    finally:
        stop.set()


def _watch_and_regenerate(options: GeneratorOptions, stop: threading.Event) -> None:
    """Regenerate when docs/ or the template changes; mkdocs live-reloads the rest."""
    last = _snapshot(options)
    while not stop.wait(1.0):
        current = _snapshot(options)
        if current != last:
            last = current
            print("🔄 检测到变更，重新生成...")
            generate(options)


def _snapshot(options: GeneratorOptions) -> tuple[tuple[int, int], ...]:
    stamps: list[tuple[int, int]] = []
    for root in (options.docs_dir, options.template_path):
        if root.is_file():
            stamps.append((root.stat().st_mtime_ns, root.stat().st_size))
        elif root.is_dir():
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    stamps.append((path.stat().st_mtime_ns, path.stat().st_size))
    return tuple(stamps)


def cmd_install() -> int:
    """Install dependencies via uv (equivalent to ``uv sync``)."""
    return subprocess.call(["uv", "sync"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nmteam", description="nmTeam Support 文档站工具链")
    parser.add_argument(
        "command",
        nargs="?",
        default="generate",
        choices=["generate", "dev", "build", "clean", "install"],
    )
    args = parser.parse_args(argv)
    options = default_options()
    if args.command == "generate":
        generate(options)
        return 0
    if args.command == "dev":
        return cmd_dev(options)
    if args.command == "build":
        return cmd_build(options)
    if args.command == "clean":
        return cmd_clean(options)
    return cmd_install()
