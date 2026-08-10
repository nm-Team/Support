"""Static serve tests: Markdown is served as text/plain with UTF-8 charset."""

import threading
import urllib.request

from nmteam_support.serve import MarkdownPlainHandler, create_server


def _base_url(server) -> str:
    host, port = server.server_address
    return f"http://{host}:{port}"


def test_markdown_served_as_text_plain_utf8(tmp_path):
    (tmp_path / "page.md").write_text("# 标题\n", encoding="utf-8", newline="\n")
    (tmp_path / "index.html").write_text("<h1>hi</h1>", encoding="utf-8")

    server = create_server(tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = _base_url(server)
        with urllib.request.urlopen(f"{base}/page.md", timeout=5) as response:
            assert response.headers.get_content_type() == "text/plain"
            assert response.headers.get_content_charset() == "utf-8"
            assert response.read().decode("utf-8") == "# 标题\n"
        with urllib.request.urlopen(f"{base}/index.html", timeout=5) as response:
            assert response.headers.get_content_type() == "text/html"
    finally:
        server.shutdown()
        server.server_close()


def test_markdown_extension_map_excludes_text_markdown():
    for ext in (".md", ".markdown"):
        assert MarkdownPlainHandler.extensions_map[ext] == "text/plain; charset=utf-8"
    assert "text/markdown" not in MarkdownPlainHandler.extensions_map.values()
