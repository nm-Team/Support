"""Portable product icon rendering tests."""

from nmteam_support.icon_elements import render_icon_elements_html, render_portable_markdown


def test_render_portable_markdown_replaces_both_icon_elements():
    source = (
        "---\n"
        "title: <nmbot-plus-icon></nmbot-plus-icon> nmBot+\n"
        "---\n\n"
        "# <nmbot-plus-icon></nmbot-plus-icon> nmBot+\n\n"
        "<nmbot-intelligence-icon></nmbot-intelligence-icon> 智能功能\n"
    )

    output = render_portable_markdown(source)

    assert output.startswith("# ![nmBot+ Logo]")
    assert "title:" not in output
    assert "![nmBot+ Logo](https://websiteres.nmteam.xyz/nmBot/plus.svg) nmBot+" in output
    assert (
        "![nmBot Intelligence Logo](https://websiteres.nmteam.xyz/"
        "pintroimg/nmBot-Telegram/v2/nmbot-intelligence.svg) 智能功能" in output
    )
    assert "<nmbot-" not in output


def test_render_portable_markdown_strips_generated_frontmatter():
    source = (
        "---\n"
        "automatically_generated: Don't edit this file directly.\n"
        "title: Product\n"
        "\n"
        "hide:\n"
        "  - toc\n"
        "---\n\n"
        "# Product\n"
    )

    assert render_portable_markdown(source) == "# Product\n"


def test_render_portable_markdown_leaves_unknown_elements_unchanged():
    source = "# <product-icon></product-icon> Product\n"

    assert render_portable_markdown(source) == source


def test_render_icon_elements_html_only_allows_known_icons():
    source = (
        "<nmbot-plus-icon></nmbot-plus-icon> Plus & "
        "<nmbot-intelligence-icon></nmbot-intelligence-icon> Intelligence "
        "<script>alert(1)</script>"
    )

    output = render_icon_elements_html(source)

    assert output.count('class="nmbot-product-icon"') == 2
    assert 'alt="nmBot+ Logo"' in output
    assert 'alt="nmBot Intelligence Logo"' in output
    assert "Plus &amp;" in output
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in output
