"""Frontmatter parsing smoke tests."""

from nmteam_support.frontmatter import parse_page, split_frontmatter, split_frontmatter_lines


def test_split_frontmatter_roundtrip():
    text = "---\ntitle: X\n---\n\n# Body\n"
    metadata_raw, body = split_frontmatter(text)
    assert "title: X" in metadata_raw
    assert body == "\n\n# Body\n"


def test_split_frontmatter_without_fence():
    assert split_frontmatter("no frontmatter\n") == ("", "no frontmatter\n")


def test_parse_page_extracts_metadata():
    meta, body = parse_page("---\ntitle: T\ndescription: D\nindex: 5\n---\n\n# T\n", "x.md")
    assert meta.title == "T"
    assert meta.description == "D"
    assert meta.index == 5
    assert body == "\n# T\n"
