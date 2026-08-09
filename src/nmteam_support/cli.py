"""Cross-platform command-line interface for the documentation toolchain."""

from __future__ import annotations

import shutil
import subprocess
import sys
import threading
from pathlib import Path

import typer

from nmteam_support.generator import GeneratorOptions, default_options, generate
from nmteam_support.redirects import (
    RedirectConfigError,
    read_redirects,
    write_redirects,
)

app = typer.Typer(invoke_without_command=True)
redirects_app = typer.Typer(no_args_is_help=True)
app.add_typer(redirects_app, name="redirects")

QUALITY_COMMANDS = (
    ["ruff", "check", "."],
    ["ruff", "format", "--check", "."],
    ["pytest"],
    ["mdformat", "--check", "README.md", "docs/"],
)


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
            [
                sys.executable,
                "-m",
                "mkdocs",
                "serve",
                "--dirtyreload",
                "--dev-addr",
                "127.0.0.1:8000",
            ]
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
            try:
                generate(options)
            except Exception as error:
                print(f"⚠️ 文档生成失败，继续监听: {error}", file=sys.stderr)


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


def cmd_check(options: GeneratorOptions) -> int:
    """Run repository quality checks and a strict documentation build."""
    for command in QUALITY_COMMANDS:
        code = subprocess.call(command)
        if code:
            return code
    return cmd_build(options)


def _exit_on_error(code: int) -> None:
    if code:
        raise typer.Exit(code=code)


def _managed_redirects() -> tuple[Path, dict[str, str]]:
    path = default_options().redirects_path
    try:
        return path, read_redirects(path)
    except RedirectConfigError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


@app.callback()
def root(context: typer.Context) -> None:
    """Manage the nmTeam Support documentation site."""
    if context.invoked_subcommand is None:
        typer.echo(context.get_help())


@app.command("generate")
def generate_command() -> None:
    """Generate documentation configuration and derived files."""
    generate(default_options())


@app.command("dev")
def dev_command() -> None:
    """Serve the site and regenerate derived files after changes."""
    _exit_on_error(cmd_dev(default_options()))


@app.command("build")
def build_command() -> None:
    """Generate and build the production documentation site."""
    _exit_on_error(cmd_build(default_options()))


@app.command("clean")
def clean_command() -> None:
    """Remove generated documentation output."""
    _exit_on_error(cmd_clean(default_options()))


@app.command("install")
def install_command() -> None:
    """Install project dependencies with uv."""
    _exit_on_error(cmd_install())


@app.command("check")
def check_command() -> None:
    """Run linting, tests, formatting checks, and a strict build."""
    _exit_on_error(cmd_check(default_options()))


@redirects_app.command("list")
def list_redirects_command() -> None:
    """List configured redirects."""
    _, redirects = _managed_redirects()
    if not redirects:
        typer.echo("当前没有配置任何重定向")
        return
    for old_path, new_path in redirects.items():
        typer.echo(f"{old_path} -> {new_path}")


@redirects_app.command("add")
def add_redirect_command(old_path: str, new_path: str) -> None:
    """Add or replace a redirect."""
    path, redirects = _managed_redirects()
    redirects[old_path] = new_path
    write_redirects(path, redirects)
    typer.echo(f"已添加重定向: {old_path} -> {new_path}")


@redirects_app.command("remove")
def remove_redirect_command(old_path: str) -> None:
    """Remove an existing redirect."""
    path, redirects = _managed_redirects()
    if old_path not in redirects:
        typer.echo(f"未找到重定向: {old_path}", err=True)
        raise typer.Exit(code=1)
    del redirects[old_path]
    write_redirects(path, redirects)
    typer.echo(f"已删除重定向: {old_path}")


def main() -> None:
    app()
