"""docsList HTML tests."""

from nmteam_support.docslist import render_docs_list
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
