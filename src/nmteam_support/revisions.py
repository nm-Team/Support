"""Read page update times from committed Git history without date fallbacks."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger("mkdocs.plugins.nmteam_support.revisions")
DISPLAY_TIMEZONE = timezone(timedelta(hours=8))


class RevisionError(RuntimeError):
    """Git history could not be read reliably."""


@dataclass(frozen=True)
class PageRevision:
    """A machine-readable timestamp and its fixed-timezone display value."""

    iso: str
    display: str


def read_page_revisions(docs_dir: Path) -> dict[str, PageRevision]:
    """Read the latest commit touching each source file in one Git traversal."""
    docs_dir = docs_dir.resolve()
    if shutil.which("git") is None or not any(
        (parent / ".git").exists() for parent in (docs_dir, *docs_dir.parents)
    ):
        logger.info("Git history is unavailable; page update times will be hidden.")
        return {}
    head = _git(docs_dir, "rev-parse", "--verify", "--quiet", "HEAD", success_codes=(0, 1)).strip()
    if not head:
        logger.info("The repository has no commits; page update times will be hidden.")
        return {}
    _complete_history(docs_dir, head)
    tracked_paths = set(_git(docs_dir, "ls-files", "-z", "--", ".").split("\0"))
    history = _git(
        docs_dir,
        "log",
        "--format=%x00%ct",
        "--name-only",
        "-z",
        "--no-renames",
        "--no-show-signature",
        "--no-color",
        "--relative",
        "--",
        ".",
    )
    revisions: dict[str, PageRevision] = {}
    revision = None
    first_path = False
    for field in history.split("\0"):
        if not field:
            revision = None
        elif revision is None:
            try:
                date = datetime.fromtimestamp(int(field), tz=DISPLAY_TIMEZONE)
            except (ValueError, OverflowError, OSError) as error:
                raise RevisionError(f"Invalid Git commit timestamp: {field!r}") from error
            revision = PageRevision(iso=date.isoformat(), display=date.strftime("%Y-%m-%d %H:%M"))
            first_path = True
        else:
            # Git inserts one LF before the first NUL-delimited path in each commit.
            path = field.removeprefix("\n") if first_path else field
            first_path = False
            if path in tracked_paths:
                revisions.setdefault(path, revision)
    return revisions


def _complete_history(docs_dir: Path, head: str) -> None:
    """Fetch the checked-out commit's ancestors without changing the checkout."""
    if _git(docs_dir, "rev-parse", "--is-shallow-repository").strip() != "true":
        return
    remotes = _git(docs_dir, "remote").splitlines()
    if "origin" in remotes:
        remote = "origin"
    elif len(remotes) == 1:
        remote = remotes[0]
    else:
        raise RevisionError(
            "Cannot complete shallow Git history: configure an origin remote "
            "or run `git fetch --unshallow <remote>` before building."
        )
    logger.info("Fetching complete Git history from %s for page update times.", remote)
    _git(
        docs_dir,
        "-c",
        "credential.interactive=false",
        "fetch",
        "--unshallow",
        "--no-tags",
        "--no-recurse-submodules",
        "--no-write-fetch-head",
        "--",
        remote,
        head,
        timeout=120,
    )
    if _git(docs_dir, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise RevisionError(
            "Git history is still shallow after fetching. The build remote must provide "
            "the complete history of the checked-out commit."
        )


def _git(
    docs_dir: Path, *args: str, success_codes: tuple[int, ...] = (0,), timeout: int = 30
) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(docs_dir), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as error:
        raise RevisionError(f"Cannot read Git history in {docs_dir}: {error}") from error
    if result.returncode not in success_codes:
        raise RevisionError(
            f"Cannot read Git history in {docs_dir}: {result.stderr.strip()} "
            f"(exit {result.returncode})"
        )
    return result.stdout
