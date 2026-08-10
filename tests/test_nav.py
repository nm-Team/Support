"""Nav YAML generation tests."""

from nmteam_support.models import DocEntry
from nmteam_support.nav import build_nav, sort_entries
from nmteam_support.scanner import scan_docs


def _entry(path, name, index=0, kind="doc"):
    return DocEntry(title=name, description="", path=path, name=name, index=index, kind=kind)


def test_sort_index_ascending_then_folders_first_then_scan_order():
    entries = [
        _entry("doc2.md", "doc2", index=0),
        _entry("folder1", "folder1", index=0, kind="folder"),
        _entry("doc1.md", "doc1", index=-1),
        _entry("folder2", "folder2", index=5, kind="folder"),
        _entry("doc0.md", "doc0", index=0),
    ]
    assert [e.name for e in sort_entries(entries)] == ["doc1", "folder1", "doc2", "doc0", "folder2"]


def test_build_nav_shape(docs_dir):
    assert build_nav(scan_docs(docs_dir)) == [
        {"nmTeam 支持": "index.md"},
        {
            "nmBot Telegram": [
                {"nmBot Telegram": "nmbot-telegram/index.md"},
                {"MCP 配置": "nmbot-telegram/mcp.md"},
            ]
        },
        {
            "联系我们": [
                {"联系我们": "contact-us/index.md"},
                {"论坛": "contact-us/forum.md"},
            ]
        },
        {"关于": "about.md"},
    ]


def test_empty_folder_skipped(docs_dir):
    (docs_dir / "nmbot-telegram" / "empty-dir").mkdir()
    nav = build_nav(scan_docs(docs_dir))
    assert "empty-dir" not in str(nav)


def test_folder_with_empty_index_skipped(docs_dir):
    d = docs_dir / "nmbot-telegram" / "notes"
    d.mkdir()
    (d / "index.md").write_text("---\n---\n", encoding="utf-8")
    nav = build_nav(scan_docs(docs_dir))
    assert "notes" not in str(nav)


def test_folder_index_comes_from_its_index_md(docs_dir):
    # contact-us/index.md has index: 100 -> folder sorts after nmbot-telegram (0)
    nav = build_nav(scan_docs(docs_dir))
    assert str(nav).index("nmbot-telegram") < str(nav).index("contact-us")


def test_negative_index_doc_precedes_default_index_doc(docs_dir):
    # forum.md has index: -1 -> sorts before a same-level default-index (0) doc,
    # while the folder's index.md overview still renders first.
    (docs_dir / "contact-us" / "support.md").write_text(
        "---\ntitle: 支持文档\nindex: 0\n---\n\n# 支持文档\n",
        encoding="utf-8",
    )
    nav = str(build_nav(scan_docs(docs_dir)))
    assert (
        nav.index("contact-us/index.md")
        < nav.index("contact-us/forum.md")
        < nav.index("contact-us/support.md")
    )
