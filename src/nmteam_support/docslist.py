"""docsList HTML card generation for directory index pages."""

from __future__ import annotations

import html

from nmteam_support.models import DocEntry


def render_docs_list(entries: list[DocEntry]) -> str:
    """Render the docsList card HTML for already-sorted ``entries``."""
    html_parts = ['\n\n\n<div class="docsList">']
    for entry in entries:
        html_parts.append(
            '\n    <div class="docsItem">\n'
            '        <i class="icon {type}" aria-hidden="true"></i>\n'
            '        <div class="text">\n'
            '            <a class="link" href="{path}">{title}</a>\n'
            '            <p class="description">{description}</p>\n'
            "        </div>\n"
            "    </div>".format(
                path=html.escape("/" + entry.path.replace(".md", "")),
                title=html.escape(entry.title),
                description=html.escape(entry.description),
                type=entry.kind,
            )
        )
    html_parts.append("\n</div>")
    return "".join(html_parts)
