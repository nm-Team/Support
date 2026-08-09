"""Redirects.js generation from redirects.json."""

from __future__ import annotations

import json
from pathlib import Path


class RedirectConfigError(ValueError):
    """Raised when redirects.json cannot be safely managed."""


def read_redirects(path: Path) -> dict[str, str]:
    """Read and validate redirects for management commands."""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        redirects = payload["redirects"]
    except (json.JSONDecodeError, KeyError, OSError, TypeError) as error:
        raise RedirectConfigError(f"无法读取重定向配置: {error}") from error
    if not isinstance(redirects, dict) or not all(
        isinstance(old, str) and isinstance(new, str) for old, new in redirects.items()
    ):
        raise RedirectConfigError("redirects 必须是字符串到字符串的映射")
    return redirects


def write_redirects(path: Path, redirects: dict[str, str]) -> None:
    """Write a validated redirect map with stable UTF-8 formatting."""
    payload = json.dumps({"redirects": redirects}, ensure_ascii=False, indent=2)
    path.write_text(payload + "\n", encoding="utf-8")


def load_redirects(path: Path) -> dict[str, str] | None:
    """Load the redirect map; return None when the file is missing or invalid."""
    if not path.is_file():
        return None
    try:
        return read_redirects(path)
    except RedirectConfigError:
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
