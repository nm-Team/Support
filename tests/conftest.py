"""Shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    """A minimal docs tree: root page + two product folders."""
    docs = tmp_path / "docs"
    (docs / "nmbot-telegram").mkdir(parents=True)
    (docs / "contact-us").mkdir()
    (docs / "index.md").write_text(
        "---\ntitle: nmTeam 支持\ndescription: 支持中心。\nhide_docs_list: true\n---\n\n# nmTeam 支持\n\n正文。\n",
        encoding="utf-8",
    )
    (docs / "about.md").write_text(
        "---\ntitle: 关于\nindex: 200\ndescription: 了解此文档。\n---\n\n# 关于\n",
        encoding="utf-8",
    )
    (docs / "nmbot-telegram" / "index.md").write_text(
        "---\ntitle: nmBot Telegram\n---\n\n# nmBot\n\n简介。\n",
        encoding="utf-8",
    )
    (docs / "nmbot-telegram" / "mcp.md").write_text(
        "---\ntitle: MCP 配置\ndescription: 配置 MCP。\n---\n\n# MCP 配置\n\n正文。\n",
        encoding="utf-8",
    )
    (docs / "contact-us" / "index.md").write_text(
        "---\ntitle: 联系我们\nindex: 100\n---\n\n# 联系\n\n方式。\n",
        encoding="utf-8",
    )
    (docs / "contact-us" / "forum.md").write_text(
        "---\ntitle: 论坛\nindex: -1\n---\n\n# 论坛\n",
        encoding="utf-8",
    )
    return docs
