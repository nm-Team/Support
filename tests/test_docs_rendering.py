"""Consumer-visible Markdown rendering regression tests."""

from html.parser import HTMLParser
from pathlib import Path

from markdown import markdown
from mkdocs.config import load_config

from nmteam_support.frontmatter import parse_page

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
MKDOCS_CONFIG = load_config(config_file=str(REPO_ROOT / "mkdocs.yml"))


class _FragmentGraph(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.fragments: set[str] = set()

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if element_id := attributes.get("id"):
            self.ids.add(element_id)
        if (href := attributes.get("href")) and href.startswith("#"):
            self.fragments.add(href[1:])


def _render(relative_path: str) -> str:
    source = (DOCS_ROOT / relative_path).read_text(encoding="utf-8")
    _metadata, body = parse_page(source, Path(relative_path).name)
    return markdown(
        body,
        extensions=MKDOCS_CONFIG.markdown_extensions,
        extension_configs=MKDOCS_CONFIG.mdx_configs,
    )


def test_message_template_renders_all_footnotes():
    output = _render("nmbot-telegram/message-template.md")

    assert 'id="fn:1"' in output
    assert 'id="fn:2"' in output
    assert 'id="fn:3"' in output
    assert "%E7%9B%AE%E5%89%8D" not in output


def test_message_template_preserves_literal_telegram_syntax():
    output = _render("nmbot-telegram/message-template.md")

    for spelling in (r"\~", r"\=", r"\|"):
        assert f"<code>{spelling}</code>" in output
    for entity in ("&amp;lt;", "&amp;gt;", "&amp;amp;"):
        assert f"<code>{entity}</code>" in output


def test_panel_troubleshooting_lists_render_bold_labels():
    access = _render("nmbot-telegram/faq/cannot-access-panel.md")
    login = _render("nmbot-telegram/faq/cannot-log-in-to-panel.md")

    for label in (
        "检查网络连接：",
        "清除浏览器缓存：",
        "尝试使用其他浏览器：",
        "检查防火墙设置：",
        "查看 nmBot 面板服务状态：",
    ):
        assert f"<strong>{label}</strong>" in access
    for label in (
        "检查网络连接：",
        "确认你可以访问 Telegram：",
        "清除浏览器缓存：",
        "更新浏览器：",
        "禁用浏览器插件：",
        "使用其他浏览器或设备：",
        "联系技术支持：",
    ):
        assert f"<strong>{label}</strong>" in login
    assert "\\*\\*" not in access
    assert "\\*\\*" not in login


def test_same_page_links_target_rendered_heading_ids():
    paths = (
        "nmbot-telegram/faq/why-my-message-deleted.md",
        "nmbot-telegram/panel/how-to-launch-panel.md",
    )

    for path in paths:
        graph = _FragmentGraph()
        graph.feed(_render(path))
        assert graph.fragments <= graph.ids, f"{path}: {graph.fragments - graph.ids}"


def test_update_logs_preserve_literal_notes_and_list_structure():
    july = _render("nmbot-telegram/update-log/2024-07.md")
    previous = _render("nmbot-telegram/update-log/previous-log.md")
    april = _render("nmbot-telegram/update-log/2025-04.md")

    assert "* 部分功能需要用户的 Telegram App 版本支持。" in july
    assert "* 通过 nmBot 面板修改关键词回复时" in previous
    assert "* 通过 nmBot 面板修改群组配置时" in previous
    assert "<li>nmBot 面板现在将提示使用 Internet Explorer" in april
    assert "<li>\n<h2>" not in april
