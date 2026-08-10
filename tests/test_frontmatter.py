"""Frontmatter parsing smoke tests."""

from nmteam_support.frontmatter import parse_page, split_frontmatter


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


def test_unterminated_frontmatter_does_not_crash():
    meta, body = parse_page("---\ntitle: X\n", "x.md")
    assert meta.title == "X"
    assert body == "---\ntitle: X\n"


def test_title_falls_back_to_heading():
    meta, _ = parse_page("---\ndescription: D\n---\n\n# 标题\n\n正文\n", "x.md")
    assert meta.title == "标题"


def test_title_falls_back_to_filename():
    meta, _ = parse_page("", "my-doc.md")
    assert meta.title == "My Doc"


def test_index_garbage_defaults_to_zero():
    meta, _ = parse_page("---\nindex: nope\n---\n\n# T\n", "x.md")
    assert meta.index == 0


def test_description_skips_images_html_and_admonitions():
    meta, _ = parse_page(
        '---\n---\n\n# T\n\n![图](./img/a.png)\n\n<center>HTML</center>\n\n!!! note "注"\n    内容\n\n正文第一句。\n',
        "x.md",
    )
    assert meta.description == "正文第一句。"


def test_description_truncates_at_100():
    meta, _ = parse_page("---\n---\n\n# T\n\n" + "字" * 120 + "\n", "x.md")
    assert meta.description == "字" * 100 + "..."


def test_hide_flags():
    meta, _ = parse_page(
        "---\nhide_docs_list: true\nhideContributingNote: true\nhide:\n  - navigation\n---\n\n# T\n",
        "x.md",
    )
    assert meta.hide_docs_list
    assert meta.hide_contributing_note
    assert meta.hide_navigation


def test_hide_contributing_note_is_case_insensitive():
    meta, _ = parse_page("---\nhidecontributingnote: true\n---\n\n# T\n", "x.md")
    assert meta.hide_contributing_note
