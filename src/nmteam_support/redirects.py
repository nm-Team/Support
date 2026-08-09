"""Redirects.js generation from redirects.json."""

from __future__ import annotations

import json
from pathlib import Path


def load_redirects(path: Path) -> dict[str, str] | None:
    """Load the redirect map; return None when the file is missing or invalid."""
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)["redirects"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def render_redirects_js(redirects: dict[str, str]) -> str:
    """Render the redirects.js content for a redirect map."""
    return (
        "// 自动生成的重定向脚本\n"
        "(function() {\n"
        "    // 重定向映射\n"
        "    const redirects = " + json.dumps(redirects, ensure_ascii=False, indent=8) + ";\n"
        "\n"
        "    // 获取当前路径\n"
        "    const currentPath = window.location.pathname;\n"
        "    \n"
        "    // 检查是否需要重定向\n"
        "    for (const oldPath in redirects) {\n"
        "        if (currentPath === oldPath || currentPath.startsWith(oldPath)) {\n"
        "            const newPath = redirects[oldPath];\n"
        "            // 执行重定向\n"
        "            window.location.replace(newPath);\n"
        "            break;\n"
        "        }\n"
        "    }\n"
        "})();"
    )
