"""Nav YAML generation tests."""

from nmteam_support.models import DocEntry
from nmteam_support.nav import build_nav_yaml, sort_entries
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


def test_build_nav_yaml_shape(docs_dir):
    nav = build_nav_yaml(scan_docs(docs_dir))
    assert nav == (
        "  - nmTeam 支持: 'index.md'\n"
        "  - nmBot Telegram:\n"
        "    - nmBot Telegram: 'nmbot-telegram/index.md'\n"
        "    - MCP 配置: 'nmbot-telegram/mcp.md'\n"
        "  - 联系我们:\n"
        "    - 联系我们: 'contact-us/index.md'\n"
        "    - 论坛: 'contact-us/forum.md'\n"
        "  - 关于: 'about.md'"
    )


def test_empty_folder_skipped(docs_dir):
    (docs_dir / "nmbot-telegram" / "empty-dir").mkdir()
    nav = build_nav_yaml(scan_docs(docs_dir))
    assert "empty-dir" not in nav


def test_folder_with_empty_index_skipped(docs_dir):
    d = docs_dir / "nmbot-telegram" / "notes"
    d.mkdir()
    (d / "index.md").write_text("---\n---\n", encoding="utf-8")
    nav = build_nav_yaml(scan_docs(docs_dir))
    assert "notes" not in nav
