"""Page update times are derived from real per-file Git history."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from nmteam_support.cli import build_site
from nmteam_support.revisions import PageRevision, RevisionError, read_page_revisions


def _git(root: Path, *args: str, date: str | None = None) -> str:
    env = os.environ.copy()
    if date is not None:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    ).stdout


@pytest.fixture
def git_docs(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.name", "Documentation Tests")
    _git(tmp_path, "config", "user.email", "docs@example.test")
    _git(tmp_path, "config", "commit.gpgsign", "false")
    _git(tmp_path, "config", "core.hooksPath", str(tmp_path / ".git" / "no-hooks"))
    docs = tmp_path / "docs"
    docs.mkdir()
    return docs


def _commit(docs: Path, date: str) -> None:
    _git(docs.parent, "add", "--all")
    _git(docs.parent, "commit", "-m", "Update documents", date=date)


def test_each_page_uses_its_last_commit_and_survives_unrelated_changes(git_docs):
    (git_docs / "first.md").write_text("# First\n", encoding="utf-8")
    (git_docs / "中文 page.md").write_text("# Second\n", encoding="utf-8")
    _commit(git_docs, "2023-01-02T03:04:05+00:00")
    (git_docs / "first.md").write_text("# First updated\n", encoding="utf-8")
    _commit(git_docs, "2024-06-07T08:09:10-04:00")

    expected = {
        "first.md": PageRevision("2024-06-07T20:09:10+08:00", "2024-06-07 20:09"),
        "中文 page.md": PageRevision("2023-01-02T11:04:05+08:00", "2023-01-02 11:04"),
    }
    assert read_page_revisions(git_docs) == expected

    (git_docs.parent / "README.md").write_text("Unrelated\n", encoding="utf-8")
    _commit(git_docs, "2025-01-01T00:00:00+00:00")
    (git_docs / "first.md").write_text("# Uncommitted edit\n", encoding="utf-8")
    (git_docs / "untracked.md").write_text("# New\n", encoding="utf-8")
    os.utime(git_docs / "中文 page.md", (1_800_000_000, 1_800_000_000))

    assert read_page_revisions(git_docs) == expected


def test_uses_committer_time_instead_of_author_time(git_docs):
    (git_docs / "page.md").write_text("# Page\n", encoding="utf-8")
    _git(git_docs.parent, "add", "--all")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = "2020-01-01T00:00:00+00:00"
    env["GIT_COMMITTER_DATE"] = "2024-01-01T00:00:00+00:00"
    subprocess.run(
        ["git", "-C", str(git_docs.parent), "commit", "-m", "Commit an older draft"],
        check=True,
        capture_output=True,
        env=env,
    )

    assert read_page_revisions(git_docs)["page.md"].iso == "2024-01-01T08:00:00+08:00"


def test_rename_has_a_real_commit_time_and_removed_paths_are_not_reused(git_docs):
    (git_docs / "old.md").write_text("# Original\n", encoding="utf-8")
    _commit(git_docs, "2020-01-01T00:00:00+00:00")
    _git(git_docs.parent, "mv", "docs/old.md", "docs/new.md")
    _commit(git_docs, "2021-01-01T00:00:00+00:00")

    revisions = read_page_revisions(git_docs)
    assert revisions["new.md"].iso == "2021-01-01T08:00:00+08:00"
    assert "old.md" not in revisions
    (git_docs / "old.md").write_text("# New untracked page at an old path\n", encoding="utf-8")
    assert "old.md" not in read_page_revisions(git_docs)


@pytest.mark.skipif(os.name == "nt", reason="Windows does not allow LF in filenames")
def test_nul_delimited_paths_preserve_whitespace_and_newlines(git_docs):
    for name in (" leading.md", "line\nbreak.md", "\nfirst.md"):
        (git_docs / name).write_text("# Page\n", encoding="utf-8")
    _commit(git_docs, "2020-01-01T00:00:00+00:00")

    assert set(read_page_revisions(git_docs)) == {" leading.md", "line\nbreak.md", "\nfirst.md"}


def test_unborn_repository_has_no_fabricated_dates(git_docs, caplog):
    (git_docs / "new.md").write_text("# New\n", encoding="utf-8")
    with caplog.at_level(logging.INFO):
        assert read_page_revisions(git_docs) == {}
    assert "no commits" in caplog.text


def test_source_archive_has_no_fabricated_dates(tmp_path, caplog):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "page.md").write_text("# Page\n", encoding="utf-8")
    with caplog.at_level(logging.INFO):
        assert read_page_revisions(docs) == {}
    assert "update times will be hidden" in caplog.text


def test_missing_git_hides_dates_with_an_explanation(git_docs, monkeypatch, caplog):
    monkeypatch.setattr(shutil, "which", lambda _command: None)
    with caplog.at_level(logging.INFO):
        assert read_page_revisions(git_docs) == {}
    assert "Git history is unavailable" in caplog.text


def test_shallow_history_fails_instead_of_assigning_the_clone_boundary_date(git_docs, tmp_path):
    (git_docs / "older.md").write_text("# Older\n", encoding="utf-8")
    _commit(git_docs, "2020-01-01T00:00:00+00:00")
    (git_docs / "newer.md").write_text("# Newer\n", encoding="utf-8")
    _commit(git_docs, "2021-01-01T00:00:00+00:00")
    clone = tmp_path / "shallow"
    _git(tmp_path, "clone", "--depth=1", git_docs.parent.as_uri(), str(clone))

    with pytest.raises(RevisionError, match="fetch-depth: 0"):
        read_page_revisions(clone / "docs")


def test_git_errors_are_reported_with_context(git_docs, monkeypatch):
    def fail(*_args, **_kwargs):
        return subprocess.CompletedProcess([], 128, stdout="", stderr="History is unreadable")

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(RevisionError, match="History is unreadable"):
        read_page_revisions(git_docs)


def test_git_timeouts_are_reported_with_context(git_docs, monkeypatch):
    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired("git", 30)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(RevisionError, match="Cannot read Git history"):
        read_page_revisions(git_docs)


def test_material_footer_shows_per_page_times_and_hides_unknown_dates(git_docs):
    (git_docs / "index.md").write_text("# Home\n", encoding="utf-8")
    (git_docs / "older.md").write_text("# Older\n", encoding="utf-8")
    (git_docs / "newer.md").write_text("# Newer\n", encoding="utf-8")
    generated_dir = git_docs / "generated"
    generated_dir.mkdir()
    (generated_dir / "child.md").write_text("# Child\n", encoding="utf-8")
    _commit(git_docs, "2020-01-01T00:00:00+00:00")
    (git_docs / "newer.md").write_text("# Updated\n", encoding="utf-8")
    _commit(git_docs, "2022-02-02T00:00:00+00:00")
    (git_docs / "untracked.md").write_text("# Untracked\n", encoding="utf-8")
    overrides = Path(__file__).resolve().parents[1] / "overrides"
    config = git_docs.parent / "mkdocs.yml"
    config.write_text(
        "site_name: Test\ndocs_dir: docs\nsite_dir: site\n"
        f"theme:\n  name: material\n  custom_dir: {overrides.as_posix()}\n"
        "plugins:\n  - nmteam-support\nmarkdown_extensions:\n  - admonition\n",
        encoding="utf-8",
    )

    build_site(config)

    site = git_docs.parent / "site"
    older = (site / "older/index.html").read_text(encoding="utf-8")
    newer = (site / "newer/index.html").read_text(encoding="utf-8")
    assert '<time datetime="2020-01-01T08:00:00+08:00">2020-01-01 08:00</time>' in older
    assert '<time datetime="2022-02-02T08:00:00+08:00">2022-02-02 08:00</time>' in newer
    assert "上次更新：" in newer
    assert "UTC+8" in newer
    assert newer.index("帮助我们改进此文档") < newer.index("上次更新：")
    for relative in ("untracked/index.html", "generated/index.html", "404.html"):
        assert "上次更新：" not in (site / relative).read_text(encoding="utf-8")
    assert "上次更新：" not in (site / "newer.md").read_text(encoding="utf-8")

    # A rebuild and a file mtime change must leave the committed time intact.
    os.utime(git_docs / "older.md", (1_800_000_000, 1_800_000_000))
    build_site(config)
    assert (site / "older/index.html").read_text(encoding="utf-8") == older


def test_material_footer_stays_hidden_in_a_source_archive(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n", encoding="utf-8")
    overrides = Path(__file__).resolve().parents[1] / "overrides"
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        "site_name: Test\ndocs_dir: docs\nsite_dir: site\n"
        f"theme:\n  name: material\n  custom_dir: {overrides.as_posix()}\n"
        "plugins:\n  - nmteam-support\n",
        encoding="utf-8",
    )

    build_site(config)

    assert "上次更新：" not in (tmp_path / "site/index.html").read_text(encoding="utf-8")
