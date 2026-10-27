"""Readable heading URLs and legacy-fragment compatibility tests."""

from xml.etree import ElementTree

import pytest
from markdown import Markdown


def _renderer(*, readable: bool = True) -> Markdown:
    extensions = ["toc", "attr_list", "footnotes", "md_in_html"]
    if readable:
        extensions.append("nmteam_support.heading_anchors")
    return Markdown(extensions=extensions, extension_configs={"toc": {"permalink": "#"}})


def _tree(renderer: Markdown, source: str) -> ElementTree.Element:
    return ElementTree.fromstring(f"<div>{renderer.convert(source)}</div>")


@pytest.mark.parametrize("level", range(1, 7))
def test_chinese_headings_keep_readable_text_at_every_level(level):
    renderer = _renderer()
    tree = _tree(renderer, f"{'#' * level} 如何启动 nmBot 面板？")

    heading = tree.find(f"h{level}")
    assert heading is not None
    assert heading.get("id") == "如何启动-nmbot-面板"
    assert heading.find("a").get("href") == "#如何启动-nmbot-面板"
    assert renderer.toc_tokens[0]["id"] == "如何启动-nmbot-面板"
    assert renderer.toc_tokens[0]["name"] == "如何启动 nmBot 面板？"


def test_legacy_ids_still_target_the_same_heading_with_repeats_and_inline_markup():
    source = (
        "# 中文标题\n\n## **中文标题**\n\n### 中文标题\n\n"
        "## <nmbot-plus-icon></nmbot-plus-icon> nmBot+ 功能\n\n"
        "## A &amp; B 中文[^1]\n\n## 😀\n\n## Hello\n\n## Hello\n\n"
        "[^1]: Note\n"
    )
    old, new = _tree(_renderer(readable=False), source), _tree(_renderer(), source)
    before = [el for el in old if el.tag.startswith("h")]
    after = [el for el in new if el.tag.startswith("h")]

    for legacy, current in zip(before, after, strict=True):
        if legacy.get("id") == current.get("id"):
            continue
        alias = current.find("span[@class='legacy-heading-anchor']")
        assert alias is not None
        assert alias.get("id") == legacy.get("id")
        assert alias.get("aria-hidden") == "true"
    assert [heading.get("id") for heading in after[:3]] == [
        "中文标题",
        "中文标题_1",
        "中文标题_2",
    ]
    assert [heading.get("id") for heading in after[-2:]] == ["hello", "hello_1"]


def test_explicit_ids_and_legacy_fragments_are_reserved_before_new_ids():
    source = (
        "# 中文\n\n## Other {#中文}\n\n"
        "## 帮助\n\n## 帮助\n\n## Other {#帮助_1}\n\n"
        "## _1\n\n## Fixed {#fixed}\n"
    )
    old, new = _tree(_renderer(readable=False), source), _tree(_renderer(), source)
    old_ids = {el.attrib["id"] for el in old.iter() if "id" in el.attrib}
    new_ids = [el.attrib["id"] for el in new.iter() if "id" in el.attrib]

    assert old_ids <= set(new_ids)
    assert len(new_ids) == len(set(new_ids))
    assert new.find("h1").get("id") == "中文_1"
    assert new.find("h2[@id='fixed']") is not None
    assert new.find("h2[@id='fixed']/span") is None


def test_raw_html_ids_cannot_collide_with_readable_anchors():
    tree = _tree(_renderer(), '<div id="中文"></div>\n\n# 中文')

    assert tree.find("h1").get("id") == "中文_1"


def test_toc_labels_and_reset_do_not_change_anchor_text_or_numbering():
    renderer = _renderer()
    source = '# 标题 {data-toc-label="目录名称"}\n\n## 标题\n\n[TOC]'
    first = renderer.convert(source)

    assert renderer.toc_tokens[0]["id"] == "标题"
    assert renderer.toc_tokens[0]["name"] == "目录名称"
    assert 'href="#标题"' in renderer.toc
    assert 'href="#标题_1"' in renderer.toc
    renderer.reset()
    assert renderer.convert(source) == first
