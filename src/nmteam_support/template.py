"""mkdocs-template.yml nav injection."""

from __future__ import annotations

import re

NAV_START = "# NAV_ARIA_START"
NAV_END = "# NAV_ARIA_END"

_NAV_PATTERN = re.compile(r"# NAV_ARIA_START.*# NAV_ARIA_END", re.S)
_SITE_URL_PATTERN = re.compile(r"^\s*site_url:\s*(\S+)\s*$", re.M)


def render_mkdocs_yml(template: str, nav_yaml: str) -> str:
    """Replace the nav placeholder block with ``nav_yaml``."""
    block = f"{NAV_START}\n{nav_yaml}\n{NAV_END}" if nav_yaml else f"{NAV_START}\n{NAV_END}"
    # Callable replacement: re.sub otherwise interprets backslash escapes in the
    # replacement string (e.g. "\1" -> group reference), mangling literal nav text.
    return _NAV_PATTERN.sub(lambda _m: block, template)


def extract_site_url(template: str, fallback: str = "https://support.nmteam.xyz") -> str:
    """Read ``site_url:`` from the template, falling back when absent."""
    match = _SITE_URL_PATTERN.search(template)
    return match.group(1).strip().rstrip("/") if match else fallback
