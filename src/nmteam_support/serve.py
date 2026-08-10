"""Static file server that serves Markdown as ``text/plain; charset=utf-8``.

Standard-library only, so ``nmteam preview`` works on every platform without
extra dependencies. The MIME override matters because Python's ``mimetypes``
module maps ``.md`` to ``text/markdown`` on 3.13+, which some browsers and
clients download or render inconsistently; ``text/plain`` with an explicit
UTF-8 charset is the most interoperable way to expose the per-page Markdown
copies written into ``site/``.
"""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar

DEFAULT_PORT = 8124
DEFAULT_BIND = "127.0.0.1"


class MarkdownPlainHandler(SimpleHTTPRequestHandler):
    """Serve ``.md``/``.markdown`` files as plain UTF-8 text."""

    extensions_map: ClassVar[dict[str, str]] = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/plain; charset=utf-8",
        ".markdown": "text/plain; charset=utf-8",
    }


class QuietMarkdownPlainHandler(MarkdownPlainHandler):
    """Serve files without emitting one stderr line per request."""

    def log_message(self, format: str, *args: object) -> None:
        del format, args


def create_server(
    directory: Path,
    port: int = DEFAULT_PORT,
    bind: str = DEFAULT_BIND,
    verbose: bool = False,
) -> ThreadingHTTPServer:
    """Build a threaded HTTP server rooted at ``directory``."""
    resolved = directory.resolve()
    handler_type = MarkdownPlainHandler if verbose else QuietMarkdownPlainHandler
    handler = partial(handler_type, directory=str(resolved))
    return ThreadingHTTPServer((bind, port), handler)


def serve_site(
    directory: Path,
    port: int = DEFAULT_PORT,
    bind: str = DEFAULT_BIND,
    verbose: bool = False,
) -> None:
    """Serve ``directory`` statically until interrupted."""
    server = create_server(directory, port, bind, verbose)
    host, bound_port = server.server_address
    print(f"预览服务器: http://{host}:{bound_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
