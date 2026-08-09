"""CLI command tests."""

from pathlib import Path

from typer.testing import CliRunner

import nmteam_support.cli as cli
from nmteam_support.cli import cmd_clean
from nmteam_support.generator import GeneratorOptions

runner = CliRunner()


def _options(tmp_path: Path) -> GeneratorOptions:
    return GeneratorOptions(
        docs_dir=tmp_path / "docs",
        template_path=tmp_path / "mkdocs-template.yml",
        redirects_path=tmp_path / "redirects.json",
        cache_dir=tmp_path / "cache",
        generated_dir=tmp_path / "generated",
        mkdocs_yml_path=tmp_path / "mkdocs.yml",
    )


def test_cmd_clean_removes_output_dirs(tmp_path):
    opts = _options(tmp_path)
    opts.cache_dir.mkdir()
    opts.generated_dir.mkdir()
    (tmp_path / "site").mkdir()
    assert cmd_clean(opts) == 0
    assert not opts.cache_dir.exists()
    assert not opts.generated_dir.exists()
    assert not (tmp_path / "site").exists()


def test_cli_without_command_displays_help():
    assert hasattr(cli, "app")
    result = runner.invoke(cli.app)
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "generate" in result.stdout


def test_generate_command_calls_generator(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "generate", lambda options: calls.append(options))

    result = runner.invoke(cli.app, ["generate"])

    assert result.exit_code == 0
    assert len(calls) == 1


def test_build_command_propagates_failure(monkeypatch):
    monkeypatch.setattr(cli, "cmd_build", lambda options: 17)

    result = runner.invoke(cli.app, ["build"])

    assert result.exit_code == 17


def test_watcher_continues_after_generation_error(tmp_path, monkeypatch, capsys):
    opts = _options(tmp_path)
    snapshots = iter([(), ((1, 1),), ((2, 2),)])
    generate_calls = 0

    class StopAfterTwoChanges:
        waits = 0

        def wait(self, _timeout):
            self.waits += 1
            return self.waits > 2

    def generate_once_then_succeed(_options):
        nonlocal generate_calls
        generate_calls += 1
        if generate_calls == 1:
            raise OSError("temporary failure")

    monkeypatch.setattr(cli, "_snapshot", lambda _options: next(snapshots))
    monkeypatch.setattr(cli, "generate", generate_once_then_succeed)

    cli._watch_and_regenerate(opts, StopAfterTwoChanges())

    assert generate_calls == 2
    assert "temporary failure" in capsys.readouterr().err
