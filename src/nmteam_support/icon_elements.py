"""Portable representations for nmBot product icon elements."""

from __future__ import annotations

import html
from dataclasses import dataclass

from nmteam_support.frontmatter import split_frontmatter


@dataclass(frozen=True)
class IconElement:
    """A site-only custom element and its portable image representation."""

    tag: str
    alt: str
    url: str

    @property
    def element(self) -> str:
        return f"<{self.tag}></{self.tag}>"

    @property
    def markdown(self) -> str:
        return f"![{self.alt}]({self.url})"


ICON_ELEMENTS = (
    IconElement(
        tag="nmbot-plus-icon",
        alt="nmBot+ Logo",
        url="https://websiteres.nmteam.xyz/nmBot/plus.svg",
    ),
    IconElement(
        tag="nmbot-intelligence-icon",
        alt="nmBot Intelligence Logo",
        url="https://websiteres.nmteam.xyz/pintroimg/nmBot-Telegram/v2/nmbot-intelligence.svg",
    ),
)


def render_portable_markdown(markdown: str) -> str:
    """Remove build metadata and replace site-only icon elements."""
    metadata_raw, body = split_frontmatter(markdown)
    content = body.lstrip("\n") if metadata_raw else markdown
    return _replace_icons(content)


def render_icon_elements_html(text: str) -> str:
    """Escape a title while rendering known icon elements as inline images."""
    rendered = html.escape(text)
    for icon in ICON_ELEMENTS:
        image = (
            '<img class="nmbot-product-icon" '
            f'src="{html.escape(icon.url, quote=True)}" '
            f'alt="{html.escape(icon.alt, quote=True)}">'
        )
        rendered = rendered.replace(html.escape(icon.element), image)
    return rendered


def _replace_icons(text: str) -> str:
    for icon in ICON_ELEMENTS:
        text = text.replace(icon.element, icon.markdown)
    return text
