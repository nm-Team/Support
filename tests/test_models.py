"""Model smoke tests."""

from nmteam_support.models import DocEntry, PageMetadata


def test_page_metadata_defaults():
    meta = PageMetadata(title="t")
    assert meta.description == ""
    assert meta.index == 0
    assert not meta.hide_docs_list
    assert not meta.hide_contributing_note
    assert not meta.hide_navigation


def test_doc_entry_fields():
    entry = DocEntry(title="A", description="d", path="a/b.md", name="b.md", index=3, kind="doc")
    assert entry.path == "a/b.md"
    assert entry.kind == "doc"
    assert not entry.hide_contributing_note
