"""Home page Markdown rendering regression tests."""

from pathlib import Path

import markdown


def test_homepage_markdown_inside_html_sections_is_rendered():
    repo_root = Path(__file__).resolve().parents[1]
    source = (repo_root / "docs" / "index.md").read_text(encoding="utf-8")

    rendered = markdown.markdown(source, extensions=["md_in_html"])

    assert "## 关于帮助文档" not in rendered
    assert "### 参与改进 nmTeam 帮助文档" not in rendered
    assert "<h2>关于帮助文档</h2>" in rendered
    assert "<h3>参与改进 nmTeam 帮助文档</h3>" in rendered
    assert '<a href="./about.md">在此</a>' in rendered
