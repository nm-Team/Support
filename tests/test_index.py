"""Index page generation tests."""

from nmteam_support.index import render_index_page
from nmteam_support.scanner import scan_docs


def test_index_page_frontmatter_and_no_docs_list(docs_dir):
    root = scan_docs(docs_dir)
    page = render_index_page(root)
    assert page.startswith(
        "---\nautomatically_generated: Don't edit this file directly, it's auto generated.\n"
        "title: nmTeam 支持\n\nhide:\n  - toc\n---"
    )
    assert "正文。" in page
    # root index.md sets hide_docs_list: true -> no card list
    assert '<div class="docsList">' not in page


def test_index_page_docs_list_for_subdir(docs_dir):
    root = scan_docs(docs_dir)
    nmbot = next(s for s in root.subdirs if s.rel_path == "nmbot-telegram")
    page = render_index_page(nmbot)
    assert '<div class="docsList">' in page
    assert 'href="/nmbot-telegram/mcp"' in page


def test_index_page_navigation_hide(docs_dir):
    (docs_dir / "nmbot-telegram" / "index.md").write_text(
        "---\ntitle: nmBot\nhide:\n  - navigation\n---\n\n# nmBot\n", encoding="utf-8"
    )
    root = scan_docs(docs_dir)
    nmbot = next(s for s in root.subdirs if s.rel_path == "nmbot-telegram")
    assert "  - navigation" in render_index_page(nmbot)


def test_index_page_default_content_without_index_md(tmp_path):
    d = tmp_path / "docs2"
    d.mkdir()
    page = render_index_page(scan_docs(d))
    assert "# docs2\n" in page
    assert '<div class="docsList">' in page  # empty list div is still emitted
