"""docsList HTML tests."""

from nmteam_support.docslist import render_docs_list, render_markdown_docs_list
from nmteam_support.models import DocEntry


def test_render_docs_list_structure():
    entries = [DocEntry(title="A", description="d", path="a.md", name="a.md", kind="doc")]
    out = render_docs_list(entries)
    assert out.startswith('\n\n\n<div class="docsList">')
    assert out.endswith("\n</div>")
    assert '<a class="link" href="/a">A</a>' in out
    assert '<i class="icon doc" aria-hidden="true"></i>' in out


def test_render_docs_list_strips_md_and_escapes():
    entries = [
        DocEntry(title="A&B", description='say "hi"', path="n/b.md", name="b.md", kind="doc")
    ]
    out = render_docs_list(entries)
    assert 'href="/n/b"' in out
    assert "A&amp;B" in out
    assert "say &quot;hi&quot;" in out


def test_render_docs_list_folder_icon():
    entries = [DocEntry(title="F", description="", path="nm", name="nm", kind="folder")]
    assert '<i class="icon folder" aria-hidden="true"></i>' in render_docs_list(entries)


def test_render_docs_list_displays_product_icon_in_title():
    entries = [
        DocEntry(
            title="<nmbot-plus-icon></nmbot-plus-icon> nmBot+",
            description="",
            path="plus",
            name="plus",
            kind="folder",
        )
    ]

    output = render_docs_list(entries)

    assert '<img class="nmbot-product-icon"' in output
    assert 'alt="nmBot+ Logo"' in output
    assert "&lt;nmbot-plus-icon&gt;" not in output


def test_render_markdown_docs_list_preserves_links_and_descriptions():
    entries = [
        DocEntry(title="A", description="Description", path="n/a.md", name="a.md"),
        DocEntry(title="Folder", description="", path="n/folder", name="folder", kind="folder"),
    ]

    output = render_markdown_docs_list(entries)

    assert output.startswith("\n\n## 相关文档\n\n")
    assert "- [A](/n/a)：Description" in output
    assert "- [Folder](/n/folder)" in output


def test_render_markdown_docs_list_omits_empty_section():
    assert render_markdown_docs_list([]) == ""
