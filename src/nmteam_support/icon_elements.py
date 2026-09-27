"""Portable representations for nmBot product icon elements."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

import yaml

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

_TITLE_LINE = re.compile(r"^(?P<prefix>title:\s*)(?P<value>.*)$", re.MULTILINE)


def strip_icon_elements(text: str) -> str:
    """Remove known icon elements from a plain-text value."""
    for icon in ICON_ELEMENTS:
        text = text.replace(icon.element, "")
    return " ".join(text.split())


def render_portable_markdown(markdown: str) -> str:
    """Replace site-only icon elements while preserving valid front matter."""
    metadata_raw, body = split_frontmatter(markdown)
    if not metadata_raw:
        return _replace_icons(markdown)

    metadata_raw = _TITLE_LINE.sub(_render_plain_title, metadata_raw)
    return f"---{metadata_raw}---{_replace_icons(body)}"


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


def _render_plain_title(match: re.Match[str]) -> str:
    raw_value = match.group("value")
    try:
        value = yaml.safe_load(raw_value)
    except yaml.YAMLError:
        value = raw_value
    if not isinstance(value, str):
        return match.group(0)

    title = strip_icon_elements(value)
    scalar = yaml.safe_dump(title, allow_unicode=True, default_flow_style=True).strip()
    if scalar.endswith("\n..."):
        scalar = scalar[: -len("\n...")]
    return f"{match.group('prefix')}{scalar}"
