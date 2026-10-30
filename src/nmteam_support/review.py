"""Development-only review context and validated Markdown block locations."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from html import escape
from html.parser import HTMLParser

from markdown import Markdown

from nmteam_support.frontmatter import split_frontmatter_lines

REVIEW_ASSETS = frozenset({"assets/js/review.js", "assets/styles/review.css"})
_VOID_TAGS = frozenset(
    [
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]
)


class _ReviewText(HTMLParser):
    """Collect DOM text offsets and exclude generated content from source matching."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.matching: list[str] = []
        self.excluded: list[bool] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = (dict(attrs).get("class") or "").split()
        excluded = bool(self.excluded and self.excluded[-1]) or any(
            name in classes for name in ("docsList", "review-generated", "headerlink")
        )
        if tag not in _VOID_TAGS:
            self.excluded.append(excluded)

    def handle_endtag(self, tag: str) -> None:
        if self.excluded:
            self.excluded.pop()

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        pass

    def handle_data(self, data: str) -> None:
        self.parts.append(data)
        self.matching.append("\0" * len(data) if self.excluded and self.excluded[-1] else data)


def _normalized(text: str) -> tuple[str, list[int]]:
    characters: list[str] = []
    offsets: list[int] = []
    for offset, character in enumerate(text):
        if not character.isspace():
            characters.append(character)
            offsets.append(offset)
    return "".join(characters), offsets


def _block_locations(
    source: str, rendered: str, converter: Markdown, actual_text: str
) -> list[list[int]]:
    """Locate independently rendered source fragments, accepting complete matches only.

    Blank-line fragments are candidates, not a Markdown parser: the configured
    Markdown engine validates each candidate's visible text. A match always
    identifies its entire original source range. Long fragments claim their
    positions first. Repeated fragments are paired in order only when all their
    occurrences are accounted for. Context-dependent syntax that cannot be
    validated remains unlocated.
    """
    _, body = split_frontmatter_lines(source)
    first_line = source[: len(source) - len(body)].count("\n") + 1
    candidates: dict[str, list[tuple[int, int]]] = defaultdict(list)
    line = first_line
    for fragment in re.split(r"(\n[ \t]*\n)", body):
        content = fragment.strip()
        if content:
            parser = _ReviewText()
            parser.feed(converter.reset().convert(content))
            text, _ = _normalized("".join(parser.matching).replace("\0", ""))
            if text:
                start = line + fragment[: len(fragment) - len(fragment.lstrip())].count("\n")
                end = line + fragment[: len(fragment.rstrip())].count("\n")
                candidates[text].append((start, end))
        line += fragment.count("\n")

    target, offsets = _normalized(rendered)
    occupied = bytearray(len(target))
    ranges: list[tuple[int, int, int, int]] = []
    for text, locations in sorted(candidates.items(), key=lambda item: -len(item[0])):
        occurrences: list[int] = []
        cursor = 0
        while (position := target.find(text, cursor)) >= 0:
            end = position + len(text)
            if not any(occupied[position:end]):
                occurrences.append(position)
            cursor = position + 1
        if len(occurrences) != len(locations):
            continue
        for position, (line_start, line_end) in zip(occurrences, locations, strict=True):
            end = position + len(text)
            occupied[position:end] = b"\1" * len(text)
            ranges.append((position, end, line_start, line_end))

    # UTF-16 offsets match browser Range APIs, including astral characters.
    utf16 = [0]
    for character in actual_text:
        utf16.append(utf16[-1] + len(character.encode("utf-16-le")) // 2)
    mappings: list[list[int]] = []
    for start, end, line_start, line_end in sorted(ranges):
        real_start, real_end = offsets[start], offsets[end - 1] + 1
        mappings.append(
            [utf16[real_start], utf16[real_end] - utf16[real_start], line_start, line_end]
        )
    return mappings


def render_review_context(
    html: str,
    *,
    source: str | None,
    path: str,
    project: str,
    extensions: list[str] | None = None,
    extension_configs: dict[str, dict[str, object]] | None = None,
) -> str:
    """Embed inert source snapshots and validated block ranges in development HTML."""
    parser = _ReviewText()
    parser.feed(html)
    text = "".join(parser.parts)
    matching = "".join(parser.matching)
    converter = Markdown(
        extensions=extensions
        if extensions is not None
        else ["admonition", "tables", "fenced_code"],
        extension_configs=extension_configs or {},
    )
    mappings = _block_locations(source, matching, converter, text) if source is not None else []
    payload = (
        json.dumps(
            {
                "path": path,
                "project": project,
                "source": source,
                "text": text,
                "mappings": mappings,
            },
            ensure_ascii=False,
        )
        .replace("<", "\\u003c")
        .replace("&", "\\u0026")
    )
    return (
        f'<div class="review-document" data-review-path="{escape(path, quote=True)}">'
        f'{html}</div><script type="application/json" id="review-context">{payload}</script>'
    )
