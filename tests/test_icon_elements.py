"""Portable product icon rendering tests."""

import yaml

from nmteam_support.frontmatter import split_frontmatter
from nmteam_support.icon_elements import render_portable_markdown


def test_render_portable_markdown_replaces_both_icon_elements():
    source = (
        "---\n"
        "title: <nmbot-plus-icon></nmbot-plus-icon> nmBot+\n"
        "---\n\n"
        "# <nmbot-plus-icon></nmbot-plus-icon> nmBot+\n\n"
        "<nmbot-intelligence-icon></nmbot-intelligence-icon> 智能功能\n"
    )

    output = render_portable_markdown(source)

    metadata_raw, _body = split_frontmatter(output)
    assert yaml.safe_load(metadata_raw)["title"] == "nmBot+"
    assert "![nmBot+ Logo](https://websiteres.nmteam.xyz/nmBot/plus.svg) nmBot+" in output
    assert (
        "![nmBot Intelligence Logo](https://websiteres.nmteam.xyz/"
        "pintroimg/nmBot-Telegram/v2/nmbot-intelligence.svg) 智能功能" in output
    )
    assert "<nmbot-" not in output


def test_render_portable_markdown_leaves_unknown_elements_unchanged():
    source = "# <product-icon></product-icon> Product\n"

    assert render_portable_markdown(source) == source
