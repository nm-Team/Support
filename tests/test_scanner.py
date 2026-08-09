"""Directory scanning tests."""

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
