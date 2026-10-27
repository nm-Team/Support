"""Readable Unicode heading anchors with the original fragment IDs preserved."""

from __future__ import annotations

import html
import re
from copy import deepcopy
from html.parser import HTMLParser
from xml.etree import ElementTree

from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.toc import (
    TocTreeprocessor,
    remove_fnrefs,
    render_inner_html,
    slugify_unicode,
    strip_tags,
    unique,
)
from markdown.treeprocessors import Treeprocessor

_HEADING = re.compile(r"h[1-6]", re.IGNORECASE)


class _RawIds(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.add(value)


class HeadingAnchorsTreeprocessor(Treeprocessor):
    """Reserve legacy IDs before assigning readable anchors to Markdown headings."""

    def run(self, root: ElementTree.Element) -> None:
        toc = self.md.treeprocessors["toc"]
        if not isinstance(toc, TocTreeprocessor):
            raise TypeError("Readable heading anchors require the standard toc treeprocessor")

        # Let the existing TOC implementation reproduce its exact allocation,
        # including explicit IDs, repeated headings, inline HTML and footnotes.
        legacy_root = deepcopy(root)
        toc.run(legacy_root)
        headings = [
            el for el in root.iter() if isinstance(el.tag, str) and _HEADING.fullmatch(el.tag)
        ]
        legacy_headings = [
            el
            for el in legacy_root.iter()
            if isinstance(el.tag, str) and _HEADING.fullmatch(el.tag)
        ]
        used_ids = {el.attrib["id"] for el in legacy_root.iter() if "id" in el.attrib}
        raw_ids = _RawIds()
        for block in self.md.htmlStash.rawHtmlBlocks:
            raw_ids.feed(block if isinstance(block, str) else self.md.serializer(block))
        used_ids.update(raw_ids.ids)

        for heading, legacy_heading in zip(headings, legacy_headings, strict=True):
            if "id" in heading.attrib:
                continue
            text = html.unescape(strip_tags(render_inner_html(remove_fnrefs(heading), self.md)))
            readable_slug = slugify_unicode(text, toc.sep)
            legacy_id = legacy_heading.attrib["id"]
            # Preserve unchanged slugs, including repeated English headings.
            if readable_slug == toc.slugify(text, toc.sep):
                heading.set("id", legacy_id)
                continue
            heading.set("id", unique(readable_slug, used_ids))
            alias = ElementTree.Element(
                "span",
                {"id": legacy_id, "class": "legacy-heading-anchor", "aria-hidden": "true"},
            )
            heading.insert(0, alias)


class HeadingAnchorsExtension(Extension):
    """Assign IDs after inline/attribute processing and before TOC generation."""

    def extendMarkdown(self, md: Markdown) -> None:
        md.treeprocessors.register(HeadingAnchorsTreeprocessor(md), "heading_anchors", 5.5)


def makeExtension(**kwargs) -> HeadingAnchorsExtension:
    """Load the extension from MkDocs/Python-Markdown configuration."""
    return HeadingAnchorsExtension(**kwargs)
