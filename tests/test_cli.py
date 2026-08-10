"""CLI command tests."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import nmteam_support.cli as cli
from nmteam_support.generator import GeneratorOptions

runner = CliRunner()


def _options(tmp_path: Path) -> GeneratorOptions:
    return GeneratorOptions(
        docs_dir=tmp_path / "docs",
        assets_dir=tmp_path / "assets",
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
    assert cli.cmd_clean(opts) == 0
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


def test_redirects_add_persists_quoted_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli.app, ["redirects", "add", "/old path/", "/new path/"])

    assert result.exit_code == 0
    payload = json.loads((tmp_path / "redirects.json").read_text(encoding="utf-8"))
    assert payload == {"redirects": {"/old path/": "/new path/"}}


def test_redirects_list_displays_existing_rules(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "redirects.json").write_text(
        json.dumps({"redirects": {"/old/": "/new/"}}), encoding="utf-8"
    )

    result = runner.invoke(cli.app, ["redirects", "list"])

    assert result.exit_code == 0
    assert "/old/ -> /new/" in result.stdout


def test_serve_command_serves_site_with_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "site").mkdir()
    captured = {}
    monkeypatch.setattr(
        cli,
        "serve_site",
        lambda directory, port, bind: captured.update(directory=directory, port=port, bind=bind),
    )

    result = runner.invoke(cli.app, ["serve"])

    assert result.exit_code == 0
    assert captured["directory"] == tmp_path / "site"
    assert captured["port"] == 8124
    assert captured["bind"] == "127.0.0.1"


def test_serve_command_rejects_missing_site(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli.app, ["serve"])

    assert result.exit_code != 0
    assert "site/ 不存在" in result.stderr


def test_redirects_remove_deletes_existing_rule(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "redirects.json").write_text(
        json.dumps({"redirects": {"/old/": "/new/"}}), encoding="utf-8"
    )

    result = runner.invoke(cli.app, ["redirects", "remove", "/old/"])

    assert result.exit_code == 0
    payload = json.loads((tmp_path / "redirects.json").read_text(encoding="utf-8"))
    assert payload == {"redirects": {}}


def test_redirects_remove_reports_missing_rule(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli.app, ["redirects", "remove", "/missing/"])

    assert result.exit_code == 1
    assert "未找到重定向" in result.stderr


def test_redirects_add_preserves_malformed_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "redirects.json"
    path.write_text("{ invalid", encoding="utf-8")

    result = runner.invoke(cli.app, ["redirects", "add", "/old/", "/new/"])

    assert result.exit_code == 1
    assert "无法读取重定向配置" in result.stderr
    assert path.read_text(encoding="utf-8") == "{ invalid"


def test_check_runs_complete_pipeline_in_order(tmp_path, monkeypatch):
    options = _options(tmp_path)
    commands = []
    build_options = []
    monkeypatch.setattr(cli.subprocess, "call", lambda command: commands.append(command) or 0)
    monkeypatch.setattr(cli, "cmd_build", lambda received: build_options.append(received) or 0)

    assert cli.cmd_check(options) == 0
    assert commands == [
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
    ]
    assert build_options == [options]


def test_check_stops_after_first_failed_command(tmp_path, monkeypatch):
    calls = []

    def run(command):
        calls.append(command)
        return 9 if command[:2] == ["ruff", "format"] else 0

    monkeypatch.setattr(cli.subprocess, "call", run)
    monkeypatch.setattr(
        cli,
        "cmd_build",
        lambda options: pytest.fail(f"build must not run: {options}"),
    )

    assert cli.cmd_check(_options(tmp_path)) == 9
    assert calls == [["ruff", "check", "."], ["ruff", "format", "--check", "."]]


def test_check_command_propagates_failure(monkeypatch):
    monkeypatch.setattr(cli, "cmd_check", lambda options: 13)

    result = runner.invoke(cli.app, ["check"])

    assert result.exit_code == 13


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


def test_snapshot_changes_when_asset_changes(tmp_path):
    opts = _options(tmp_path)
    opts.assets_dir.mkdir()
    before = cli._snapshot(opts)

    (opts.assets_dir / "site.css").write_text("body {}\n", encoding="utf-8")

    assert cli._snapshot(opts) != before
