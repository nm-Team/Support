"""Static serve tests: Markdown is served as text/plain with UTF-8 charset."""

import threading
import urllib.request
from unittest.mock import Mock

import pytest

import nmteam_support.serve as serve


def _base_url(server) -> str:
    host, port = server.server_address
    return f"http://{host}:{port}"


def test_markdown_served_as_text_plain_utf8(tmp_path):
    (tmp_path / "page.md").write_text("# 标题\n", encoding="utf-8", newline="\n")
    (tmp_path / "index.html").write_text("<h1>hi</h1>", encoding="utf-8")

    server = serve.create_server(tmp_path, port=0)
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
        assert serve.MarkdownPlainHandler.extensions_map[ext] == ("text/plain; charset=utf-8")
    assert "text/markdown" not in serve.MarkdownPlainHandler.extensions_map.values()


def test_preview_suppresses_per_request_logs_by_default(tmp_path, capsys):
    (tmp_path / "index.html").write_text("<h1>hi</h1>", encoding="utf-8")
    server = serve.create_server(tmp_path, port=0, verbose=False)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"{_base_url(server)}/", timeout=5) as response:
            assert response.status == 200
    finally:
        server.shutdown()
        server.server_close()

    assert capsys.readouterr().err == ""


def test_serve_site_closes_server_and_propagates_interrupt(tmp_path, monkeypatch):
    server = Mock(server_address=("127.0.0.1", 8124))
    server.serve_forever.side_effect = KeyboardInterrupt
    monkeypatch.setattr(serve, "create_server", lambda *_args: server)

    with pytest.raises(KeyboardInterrupt):
        serve.serve_site(tmp_path)

    server.server_close.assert_called_once_with()
