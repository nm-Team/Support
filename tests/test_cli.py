"""Typer lifecycle and command tests."""

import json

from typer.testing import CliRunner

import nmteam_support.cli as cli

runner = CliRunner()


def test_help_exposes_only_current_lifecycle_commands():
    result = runner.invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    for command in ("dev", "build", "preview", "check", "check-links", "redirects"):
        assert command in result.stdout
    for removed in ("generate", "clean", "install", "serve"):
        removed_result = runner.invoke(cli.app, [removed])
        assert removed_result.exit_code != 0
        assert "No such command" in removed_result.stderr


def test_dev_command_maps_typer_options_to_lifecycle(tmp_path, monkeypatch):
    assert hasattr(cli, "dev_site")
    monkeypatch.chdir(tmp_path)
    calls = []
    monkeypatch.setattr(cli, "dev_site", lambda *args: calls.append(args))

    result = runner.invoke(
        cli.app,
        ["--verbose", "dev", "--host", "0.0.0.0", "--port", "9000", "--open"],
    )

    assert result.exit_code == 0
    assert calls == [(tmp_path / "mkdocs.yml", "0.0.0.0", 9000, True, True)]


def test_dev_site_uses_mkdocs_dirtyreload_without_a_second_watcher(tmp_path, monkeypatch):
    assert hasattr(cli, "dev_site")
    calls = []
    monkeypatch.setattr(cli, "mkdocs_serve", lambda **kwargs: calls.append(kwargs))

    cli.dev_site(tmp_path / "mkdocs.yml", "127.0.0.1", 8100, False, False)

    assert calls == [
        {
            "config_file": str(tmp_path / "mkdocs.yml"),
            "build_type": "dirty",
            "dev_addr": "127.0.0.1:8100",
            "open_in_browser": False,
        }
    ]


def test_build_command_reports_lifecycle_failure(monkeypatch):
    assert hasattr(cli, "LifecycleError")
    monkeypatch.setattr(
        cli,
        "build_site",
        lambda *_args: (_ for _ in ()).throw(cli.LifecycleError("构建失败: broken")),
    )

    result = runner.invoke(cli.app, ["build"])

    assert result.exit_code == 1
    assert "构建失败: broken" in result.stderr


def test_preview_command_serves_site_quietly_by_default(tmp_path, monkeypatch):
    assert hasattr(cli, "preview_site")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "site").mkdir()
    calls = []
    monkeypatch.setattr(cli, "serve_site", lambda *args: calls.append(args))

    result = runner.invoke(cli.app, ["preview", "--port", "9001"])

    assert result.exit_code == 0
    assert calls == [(tmp_path / "site", 9001, "127.0.0.1", False)]


def test_preview_rejects_missing_site(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli.app, ["preview"])

    assert result.exit_code == 1
    assert "site/ 不存在" in result.stderr


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


def test_redirects_remove_deletes_existing_rule(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "redirects.json").write_text(
        json.dumps({"redirects": {"/old/": "/new/"}}), encoding="utf-8"
    )

    result = runner.invoke(cli.app, ["redirects", "remove", "/old/"])

    assert result.exit_code == 0
    payload = json.loads((tmp_path / "redirects.json").read_text(encoding="utf-8"))
    assert payload == {"redirects": {}}


def test_redirects_add_preserves_malformed_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "redirects.json"
    path.write_text("{ invalid", encoding="utf-8")

    result = runner.invoke(cli.app, ["redirects", "add", "/old/", "/new/"])

    assert result.exit_code == 1
    assert "无法读取重定向配置" in result.stderr
    assert path.read_text(encoding="utf-8") == "{ invalid"


def test_check_runs_tools_then_the_same_build_lifecycle(tmp_path, monkeypatch):
    assert hasattr(cli, "check_site")
    commands = []
    builds = []
    monkeypatch.setattr(cli.subprocess, "call", lambda command: commands.append(command) or 0)
    monkeypatch.setattr(cli, "build_site", lambda *args: builds.append(args))

    cli.check_site(tmp_path / "mkdocs.yml", verbose=True)

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
    assert builds == [(tmp_path / "mkdocs.yml", True)]


def _link_check_project(tmp_path):
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Test\nsite_url: https://docs.example.test\nplugins: []\n", encoding="utf-8"
    )
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text(
        '<a href="#home">Home</a><h1 id="home">Home</h1>', encoding="utf-8"
    )
    return site


def test_check_links_builds_by_default_and_checks_real_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Test\nsite_url: https://docs.example.test\nplugins: []\n", encoding="utf-8"
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/index.md").write_text("# Home\n", encoding="utf-8")

    result = runner.invoke(cli.app, ["check-links"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "site/index.html").is_file()
    assert "内部链接检查通过" in result.stdout


def test_check_links_no_build_uses_existing_output_and_reports_broken_links(tmp_path, monkeypatch):
    site = _link_check_project(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/index.md").write_text("# Home\n", encoding="utf-8")
    (site / "index.html").write_text('<a href="/missing/">Broken</a>', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli.app, ["check-links", "--no-build"])

    assert result.exit_code == 1
    assert "index.html:1:" in result.stderr
    assert "/missing/" in result.stderr
    assert "missing target" in result.stderr
    assert "发现 1 个失效的内部链接" in result.stderr
    assert not (site / "sitemap.xml").exists()


def test_check_links_no_build_fails_without_output(tmp_path, monkeypatch):
    (tmp_path / "docs").mkdir()
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Test\nsite_url: https://docs.example.test\nplugins: []\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli.app, ["check-links", "--no-build"])

    assert result.exit_code == 1
    assert "nmteam build" in result.stderr
