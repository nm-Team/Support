"""Check internal URLs against the files and anchors in a production build."""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit


class LinkCheckError(ValueError):
    """The build or site URL cannot be inspected reliably."""


@dataclass(frozen=True)
class LinkIssue:
    """One broken reference in a generated HTML file."""

    source: str
    line: int
    url: str
    reason: str


@dataclass(frozen=True)
class LinkReport:
    """Counts and diagnostics from one offline link check."""

    pages: int
    checked: int
    issues: tuple[LinkIssue, ...]


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()
        self.links: list[tuple[str, int]] = []
        self.base: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if (anchor := attributes.get("id")) is not None:
            self.anchors.add(anchor)
        if tag == "a" and (anchor := attributes.get("name")) is not None:
            self.anchors.add(anchor)
        if tag == "base" and self.base is None:
            self.base = attributes.get("href")
        names = []
        if tag in {"a", "area", "link"}:
            names.append("href")
        if tag in {"audio", "embed", "iframe", "img", "input", "script", "source", "video"}:
            names.append("src")
        if tag == "video":
            names.append("poster")
        if tag == "object":
            names.append("data")
        for name in names:
            if (url := attributes.get(name)) is not None:
                self.links.append((url, self.getpos()[0]))


def _read_page(path: Path) -> _Page:
    page = _Page()
    try:
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
    except (OSError, UnicodeError) as error:
        raise LinkCheckError(f"Cannot read HTML file {path}: {error}") from error
    return page


def _site_location(site_url: str) -> tuple[str, tuple[str, int | None], str]:
    try:
        parsed = urlsplit(site_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "expected an absolute HTTP(S) URL without credentials, query or fragment"
            )
        host = _host(site_url)
        path = unquote(parsed.path, errors="strict").rstrip("/") + "/"
    except (ValueError, UnicodeError) as error:
        raise LinkCheckError(f"Invalid site_url {site_url!r}: {error}") from error
    return site_url.rstrip("/") + "/", host, path


def _host(url: str) -> tuple[str, int | None]:
    parsed = urlsplit(url)
    port = parsed.port
    if port == {"http": 80, "https": 443}.get(parsed.scheme):
        port = None
    return parsed.hostname or "", port


def _target_path(url_path: str, site_path: str, files: set[str]) -> str | None:
    decoded = unquote(url_path, errors="strict")
    path = posixpath.normpath(decoded)
    if decoded.endswith("/") and path != "/":
        path += "/"
    if path == site_path.rstrip("/"):
        relative = ""
    elif path.startswith(site_path):
        relative = path[len(site_path) :]
    else:
        return None
    if relative and not relative.endswith("/") and relative in files:
        return relative
    index = relative.rstrip("/") + "/index.html" if relative else "index.html"
    return index if index in files else None


def check_internal_links(site_dir: Path, site_url: str) -> LinkReport:
    """Check href/src references offline, including URLs on the site's own host.

    File lookup is case-sensitive on every OS. Directory URLs require an index
    file; neither a custom 404 page nor a client-side redirect makes one exist.
    Fragments are checked against HTML IDs and legacy named anchors. Other hosts
    and non-HTTP schemes are never requested.
    """
    base_url, site_host, site_path = _site_location(site_url)
    site_dir = site_dir.resolve()
    if not site_dir.is_dir():
        raise LinkCheckError(f"No production build in {site_dir}; run `nmteam build` first.")
    paths = {
        path.relative_to(site_dir).as_posix(): path
        for path in site_dir.rglob("*")
        if path.is_file()
    }
    files = set(paths)
    if "index.html" not in files:
        raise LinkCheckError(f"No production build in {site_dir}; run `nmteam build` first.")
    pages = {
        name: _read_page(path)
        for name, path in sorted(paths.items())
        if path.suffix.lower() == ".html"
    }
    checked = 0
    issues: list[LinkIssue] = []
    for source, page in pages.items():
        page_url = urljoin(base_url, quote(source))
        seen: set[str] = set()
        for href, line in page.links:
            if href in seen:
                continue
            seen.add(href)
            try:
                url = urljoin(urljoin(page_url, page.base or ""), href)
                parsed = urlsplit(url)
                if parsed.scheme not in {"http", "https"} or _host(url) != site_host:
                    continue
                checked += 1
                target = _target_path(parsed.path, site_path, files)
                if target is None:
                    reason = f"missing target: {parsed.path}"
                elif target in pages:
                    # Text-fragment directives don't name an element. Browsers
                    # also accept an empty fragment or #top to reach the top.
                    fragment = unquote(parsed.fragment, errors="strict").split(":~:", 1)[0]
                    if (
                        not fragment
                        or fragment.lower() == "top"
                        or fragment in pages[target].anchors
                    ):
                        continue
                    reason = f"missing anchor #{fragment} in {target}"
                else:
                    continue
            except (ValueError, UnicodeError) as error:
                reason = f"invalid URL: {error}"
            issues.append(LinkIssue(source, line, href, reason))
    return LinkReport(len(pages), checked, tuple(issues))
