"""Typer command line interface for the documentation lifecycle."""

from __future__ import annotations

import logging
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from mkdocs.commands.build import build as mkdocs_build
from mkdocs.commands.serve import serve as mkdocs_serve
from mkdocs.config import load_config
from mkdocs.exceptions import Abort, ConfigurationError, PluginError

from nmteam_support.redirects import RedirectConfigError, read_redirects, write_redirects
from nmteam_support.serve import DEFAULT_BIND, DEFAULT_PORT, serve_site

app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode="markdown",
    help="Manage the nmTeam Support documentation site.",
)
redirects_app = typer.Typer(no_args_is_help=True, help="Manage URL redirects.")
app.add_typer(redirects_app, name="redirects")

QUALITY_COMMANDS = (
    ["ruff", "check", "."],
    ["ruff", "format", "--check", "."],
    ["pytest"],
    [
        "mdformat",
        "--check",
        "--exclude",
        "docs/superpowers/**",
        "README.md",
        "docs/",
    ],
)


@dataclass(frozen=True)
class CliState:
    """Options shared by all commands."""

    verbose: bool = False


class LifecycleError(RuntimeError):
    """A user-facing lifecycle failure with actionable context."""


@app.callback()
def root(
    context: typer.Context,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed MkDocs output."),
    ] = False,
) -> None:
    """Manage the nmTeam Support documentation site."""
    context.obj = CliState(verbose=verbose)


def build_site(config_path: Path, verbose: bool = False) -> None:
    """Build the site in-process so plugins and errors share one lifecycle."""
    _configure_logging(verbose)
    config = None
    try:
        config = load_config(config_file=str(config_path), strict=True)
        config.plugins.on_startup(command="build", dirty=False)
        mkdocs_build(config)
    except (Abort, ConfigurationError, OSError, PluginError) as error:
        raise LifecycleError(f"构建失败: {error}") from error
    finally:
        if config is not None:
            config.plugins.on_shutdown()


def dev_site(
    config_path: Path,
    host: str,
    port: int,
    open_browser: bool,
    verbose: bool,
) -> None:
    """Run MkDocs' native dirty-reload lifecycle without an extra watcher."""
    _configure_logging(verbose)
    if not verbose:
        logging.getLogger("mkdocs.commands.build").setLevel(logging.ERROR)
    typer.echo(f"开发服务器: http://{host}:{port}")
    try:
        mkdocs_serve(
            config_file=str(config_path),
            build_type="dirty",
            dev_addr=f"{host}:{port}",
            open_in_browser=open_browser,
        )
    except (Abort, ConfigurationError, OSError, PluginError) as error:
        raise LifecycleError(f"开发服务器启动失败: {error}") from error


def preview_site(
    directory: Path,
    port: int,
    host: str,
    verbose: bool,
) -> None:
    """Preview an existing production build."""
    if not directory.is_dir():
        raise LifecycleError("site/ 不存在，请先运行 `nmteam build`。")
    serve_site(directory, port, host, verbose)


def check_site(config_path: Path, verbose: bool = False) -> None:
    """Run repository checks followed by the production build lifecycle."""
    for command in QUALITY_COMMANDS:
        code = subprocess.call(command)
        if code:
            raise LifecycleError(f"检查失败 ({code}): {' '.join(command)}")
    build_site(config_path, verbose)


def _configure_logging(verbose: bool) -> None:
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s - %(message)s", force=True)
    logging.getLogger("mkdocs.commands.build").setLevel(logging.NOTSET)


def _execute(action: Callable[[], None]) -> None:
    try:
        action()
    except LifecycleError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


def _state(context: typer.Context) -> CliState:
    return context.ensure_object(CliState)


def _config_path() -> Path:
    return Path.cwd() / "mkdocs.yml"


@app.command("dev")
def dev_command(
    context: typer.Context,
    host: Annotated[
        str,
        typer.Option("--host", help="Address for the development server."),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", min=1, max=65535, help="Development server port."),
    ] = 8000,
    open_browser: Annotated[
        bool,
        typer.Option("--open", help="Open the site in the default browser."),
    ] = False,
) -> None:
    """Run local development with incremental reloads."""
    state = _state(context)
    _execute(lambda: dev_site(_config_path(), host, port, open_browser, state.verbose))


@app.command("build")
def build_command(context: typer.Context) -> None:
    """Build the production site."""
    state = _state(context)
    started = time.perf_counter()
    _execute(lambda: build_site(_config_path(), state.verbose))
    typer.echo(f"构建完成: site/ ({time.perf_counter() - started:.2f}s)")


@app.command("preview")
def preview_command(
    context: typer.Context,
    port: Annotated[
        int,
        typer.Option("--port", "-p", min=1, max=65535, help="Preview server port."),
    ] = DEFAULT_PORT,
    host: Annotated[
        str,
        typer.Option("--host", help="Address for the preview server."),
    ] = DEFAULT_BIND,
) -> None:
    """Preview the built site with browser-friendly Markdown responses."""
    state = _state(context)
    _execute(lambda: preview_site(Path.cwd() / "site", port, host, state.verbose))


@app.command("check")
def check_command(context: typer.Context) -> None:
    """Run linting, tests, formatting checks, and a strict build."""
    state = _state(context)
    _execute(lambda: check_site(_config_path(), state.verbose))


def _managed_redirects() -> tuple[Path, dict[str, str]]:
    path = Path.cwd() / "redirects.json"
    try:
        return path, read_redirects(path)
    except RedirectConfigError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


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
    """Remove a redirect."""
    path, redirects = _managed_redirects()
    if old_path not in redirects:
        typer.echo(f"未找到重定向: {old_path}", err=True)
        raise typer.Exit(code=1)
    del redirects[old_path]
    write_redirects(path, redirects)
    typer.echo(f"已删除重定向: {old_path}")


def main() -> None:
    """Run the command-line application."""
    app()


if __name__ == "__main__":
    main()
