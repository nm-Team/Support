"""Real production lifecycle integration tests."""

import json
import threading
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from nmteam_support.cli import build_site
from nmteam_support.serve import create_server

REPO_ROOT = Path(__file__).resolve().parents[1]


class _ArticleActions(HTMLParser):
    """Collect the Markdown paths advertised by a rendered page."""

    def __init__(self) -> None:
        super().__init__()
        self.md_paths: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag == "div" and "ai-tools" in classes and attributes.get("data-md-path"):
            self.md_paths.append(str(attributes["data-md-path"]))


def test_build_reads_docs_directly_and_writes_only_final_outputs(tmp_path, docs_dir):
    (tmp_path / "assets" / "styles").mkdir(parents=True)
    (tmp_path / "assets" / "styles" / "site.css").write_text(
        "body { color: black; }\n", encoding="utf-8"
    )
    (tmp_path / "redirects.json").write_text(
        json.dumps({"redirects": {"/old/": "/new/"}}), encoding="utf-8"
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        "site_name: Test\n"
        "site_url: https://docs.example.test\n"
        "strict: true\n"
        "docs_dir: docs\n"
        "site_dir: site\n"
        "plugins:\n"
        "  - nmteam-support\n"
        "markdown_extensions:\n"
        "  - admonition\n",
        encoding="utf-8",
    )

    build_site(config)

    site = tmp_path / "site"
    assert (site / "index.html").exists()
    assert (site / "nmbot-telegram" / "mcp" / "index.html").exists()
    assert (site / "assets" / "styles" / "site.css").read_text(encoding="utf-8") == (
        "body { color: black; }\n"
    )
    assert '"/old/": "/new/"' in (site / "assets" / "js" / "redirects.js").read_text(
        encoding="utf-8"
    )
    assert "帮助我们改进此文档" in (site / "nmbot-telegram" / "mcp.md").read_text(encoding="utf-8")
    assert not (tmp_path / "cache").exists()
    assert not (tmp_path / "generated").exists()


def test_every_rendered_page_advertises_a_served_markdown_copy(tmp_path, docs_dir):
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        "site_name: Test\n"
        "site_url: https://docs.example.test\n"
        "strict: true\n"
        "docs_dir: docs\n"
        "site_dir: site\n"
        "theme:\n"
        "  name: material\n"
        f"  custom_dir: {REPO_ROOT / 'overrides'}\n"
        "plugins:\n"
        "  - nmteam-support\n",
        encoding="utf-8",
    )

    build_site(config)

    site = tmp_path / "site"
    advertised: dict[str, list[str]] = {}
    for page in sorted(site.rglob("*.html")):
        if page.name == "404.html":
            continue
        parser = _ArticleActions()
        parser.feed(page.read_text(encoding="utf-8"))
        advertised[page.relative_to(site).as_posix()] = parser.md_paths

    # The home page hides the actions on purpose; every other page advertises one copy.
    assert advertised.pop("index.html") == []
    assert set(advertised) == {
        "about/index.html",
        "contact-us/forum/index.html",
        "contact-us/index.html",
        "nmbot-telegram/index.html",
        "nmbot-telegram/mcp/index.html",
    }
    assert advertised["nmbot-telegram/index.html"] == ["nmbot-telegram/index.md"]

    server = create_server(site, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[0], server.server_address[1]
        for page, paths in advertised.items():
            assert len(paths) == 1, page
            with urllib.request.urlopen(f"http://{host}:{port}/{paths[0]}", timeout=5) as response:
                assert response.status == 200, page
                assert response.headers.get_content_type() == "text/plain", page
                served = response.read().decode("utf-8")
            assert served == (site / paths[0]).read_text(encoding="utf-8"), page
            # Build output stays byte-identical across platforms, so copies use LF.
            assert b"\r" not in (site / paths[0]).read_bytes(), page
    finally:
        server.shutdown()
        server.server_close()
