"""Directory scanning tests."""

import os

from nmteam_support import scanner
from nmteam_support.scanner import scan_docs


def test_scan_collects_docs_and_folders(docs_dir):
    root = scan_docs(docs_dir)
    assert root.rel_path == ""
    assert [d.name for d in root.docs] == ["about.md"]
    assert {s.rel_path for s in root.subdirs} == {"nmbot-telegram", "contact-us"}
    nmbot = next(s for s in root.subdirs if s.rel_path == "nmbot-telegram")
    assert {d.name for d in nmbot.docs} == {"mcp.md"}
    assert nmbot.index_meta.title == "nmBot Telegram"
    assert nmbot.index_body.startswith("\n# nmBot")


def test_scan_skips_img_dirs(docs_dir):
    img = docs_dir / "nmbot-telegram" / "img"
    img.mkdir()
    (img / "a.png").write_bytes(b"x")
    root = scan_docs(docs_dir)
    nmbot = next(s for s in root.subdirs if s.rel_path == "nmbot-telegram")
    assert nmbot.image_dirs == ["nmbot-telegram/img"]


def test_scan_skips_superpowers(docs_dir):
    internal = docs_dir / "superpowers"
    internal.mkdir()
    (internal / "plan.md").write_text("# 计划\n", encoding="utf-8")
    root = scan_docs(docs_dir)
    assert {s.rel_path for s in root.subdirs} == {"nmbot-telegram", "contact-us"}


def test_scan_skips_empty_md_files(docs_dir):
    (docs_dir / "empty.md").write_text("", encoding="utf-8")
    root = scan_docs(docs_dir)
    assert "empty.md" not in [d.name for d in root.docs]


def test_scan_sorts_when_listdir_order_is_unordered(monkeypatch, docs_dir):
    """Same-index docs keep alphabetical order even when the OS enumerates
    entries in a non-alphabetical order, so nav order is stable across platforms."""
    d = docs_dir / "nmbot-telegram"
    for name in ["alpha.md", "mike.md", "zeta.md"]:
        (d / name).write_text(f"---\ntitle: {name}\n---\n\n# {name}\n", encoding="utf-8")

    real_listdir = os.listdir
    monkeypatch.setattr(scanner.os, "listdir", lambda p: sorted(real_listdir(p), reverse=True))

    root = scan_docs(docs_dir)
    nmbot = next(s for s in root.subdirs if s.rel_path == "nmbot-telegram")
    assert [doc.name for doc in nmbot.docs] == ["alpha.md", "mcp.md", "mike.md", "zeta.md"]


def test_refresh_catalog_reuses_unchanged_pages_and_reports_only_changes(docs_dir):
    assert hasattr(scanner, "refresh_catalog")

    first = scanner.refresh_catalog(docs_dir)
    unchanged = scanner.refresh_catalog(docs_dir, first)

    assert unchanged.changed_paths == frozenset()
    assert unchanged.pages["about.md"] is first.pages["about.md"]

    mcp = docs_dir / "nmbot-telegram" / "mcp.md"
    mcp.write_text(mcp.read_text(encoding="utf-8") + "\n新增内容。\n", encoding="utf-8")
    changed = scanner.refresh_catalog(docs_dir, unchanged)

    assert changed.changed_paths == frozenset({"nmbot-telegram/mcp.md"})
    assert changed.pages["about.md"] is first.pages["about.md"]
    assert changed.pages["nmbot-telegram/mcp.md"] is not first.pages["nmbot-telegram/mcp.md"]
