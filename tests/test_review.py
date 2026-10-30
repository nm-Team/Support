"""Development review source locations and production isolation."""

import json
from html.parser import HTMLParser

import markdown
import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

from nmteam_support.review import render_review_context


class _Context(HTMLParser):
    def __init__(self):
        super().__init__()
        self.payload = ""
        self.in_context = False

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "review-context":
            self.in_context = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_context = False

    def handle_data(self, data):
        if self.in_context:
            self.payload += data


def _context(html, source):
    output = render_review_context(html, source=source, path="docs/test.md", project="test")
    parser = _Context()
    parser.feed(output)
    return json.loads(parser.payload)


def _source_range(context, rendered_offset):
    for start, size, line_start, line_end in context["mappings"]:
        if start <= rendered_offset < start + size:
            return line_start, line_end
    return None


def test_locations_include_frontmatter_and_distinguish_repeated_text():
    source = "---\ntitle: Test\n---\n# Heading\n\nFirst **same** text.\n\nSecond **same** text.\n"
    html = "<h1>Heading</h1>\n<p>First <strong>same</strong> text.</p>\n<p>Second <strong>same</strong> text.</p>"
    context = _context(html, source)
    text = "Heading\nFirst same text.\nSecond same text."
    first = _source_range(context, text.index("same"))
    second = _source_range(context, text.rindex("same"))
    assert first == (6, 6)
    assert second == (8, 8)


def test_generated_text_is_never_assigned_a_source_location():
    source = "# Heading\n\nOriginal text.\n"
    html = (
        '<h1>Heading<a class="headerlink">¶</a></h1>'
        '<div class="review-generated"><p>Original text.</p></div>'
        '<p>Original text.</p><div class="docsList"><p>Original text.</p></div>'
    )
    context = _context(html, source)
    text = "Heading¶Original text.Original text.Original text."
    assert _source_range(context, text.index("Original")) is None
    assert _source_range(context, text.index("Original", text.index("Original") + 1)) is not None
    assert _source_range(context, text.rindex("Original")) is None


def test_offsets_use_browser_utf16_units_including_excluded_emoji():
    source = "# 😀标题\n\n😀原文\n"
    context = _context('<h1>😀标题</h1><div class="docsList">😀</div><p>😀原文</p>', source)
    rendered_offset = len("😀标题😀😀".encode("utf-16-le")) // 2
    assert _source_range(context, rendered_offset) == (3, 3)


def test_context_escapes_script_terminators_and_paths():
    source = '# Test\n\n</script><script>alert("x")</script>\n'
    output = render_review_context(
        "<p>Test</p>", source=source, path='docs/"<test>.md', project="test"
    )
    assert output.count("</script>") == 1
    assert 'data-review-path="docs/&quot;&lt;test&gt;.md"' in output
    assert _context("<p>Test</p>", source)["source"] == source


def test_generated_page_has_no_fabricated_source():
    context = _context("<h1>Generated</h1>", None)
    assert context["source"] is None
    assert context["mappings"] == []


@pytest.mark.parametrize("command", ["build", "serve"])
def test_real_lifecycle_loads_review_only_in_development(tmp_path, docs_dir, command):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Test\ndocs_dir: docs\nsite_dir: site\n"
        f"theme:\n  name: material\n  custom_dir: {root / 'overrides'}\n"
        "plugins:\n  - nmteam-support\n"
        "markdown_extensions:\n  - md_in_html\n  - admonition\n",
        encoding="utf-8",
    )
    for path in ("js/review.js", "styles/review.css"):
        target = tmp_path / "assets" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((root / "assets" / path).read_text(encoding="utf-8"), encoding="utf-8")
    config = load_config(config_file=str(tmp_path / "mkdocs.yml"), strict=True)
    config.plugins.on_startup(command=command, dirty=False)
    try:
        build(config)
    finally:
        config.plugins.on_shutdown()
    output = (tmp_path / "site/nmbot-telegram/mcp/index.html").read_text(encoding="utf-8")
    enabled = command == "serve"
    assert ('id="review-context"' in output) == enabled
    assert ('id="review-open"' in output) == enabled
    assert ("assets/js/review.js" in output) == enabled
    assert (tmp_path / "site/assets/js/review.js").exists() == enabled
    assert (tmp_path / "site/assets/styles/review.css").exists() == enabled
    if enabled:
        parser = _Context()
        parser.feed(output)
        payload = json.loads(parser.payload)
        assert payload["path"] == "docs/nmbot-telegram/mcp.md"
        assert payload["source"] == (docs_dir / "nmbot-telegram/mcp.md").read_text(encoding="utf-8")
        assert '<div class="review-generated">' in output
        assert "帮助我们改进此文档" in output
        assert "!!! tip" not in output


def test_markdown_tables_code_and_nested_admonitions_keep_exact_text_mapping():
    source = (
        '# Heading\n\n!!! note "注意"\n    多个 **格式** 与 [链接](https://example.test)。\n\n'
        "| 列名 |\n| --- |\n| 单元格 |\n\n```text\ncode <value>\n```\n"
    )
    html = markdown.markdown(source, extensions=["admonition", "tables", "fenced_code"])
    context = _context(html, source)
    text = _Text()
    text.feed(html)
    rendered = "".join(text.parts)
    for term in ["注意", "格式", "链接", "单元格", "code <value>"]:
        line_start, line_end = _source_range(context, rendered.index(term))
        assert term in "\n".join(source.splitlines()[line_start - 1 : line_end])


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("# Heading\n\nfoo\n\nfoo\n", [(3, 3), (5, 5)]),
        ("# Heading\n\n![foo](foo.png)\n\nfoo\n", [(5, 5)]),
    ],
)
def test_repeated_blocks_and_invisible_image_alt_keep_correct_lines(source, expected):
    html = markdown.markdown(source)
    context = _context(html, source)
    text = context["text"]
    offsets = [index for index in range(len(text)) if text.startswith("foo", index)]
    assert [_source_range(context, index) for index in offsets] == expected


def test_generated_heading_permalink_is_not_a_source_location():
    source = "# Heading\n"
    html = markdown.markdown(
        source, extensions=["toc"], extension_configs={"toc": {"permalink": "Link"}}
    )
    output = render_review_context(
        html,
        source=source,
        path="docs/test.md",
        project="test",
        extensions=["toc"],
        extension_configs={"toc": {"permalink": "Link"}},
    )
    parser = _Context()
    parser.feed(output)
    context = json.loads(parser.payload)
    assert _source_range(context, context["text"].index("Heading")) == (1, 1)
    assert _source_range(context, context["text"].index("Link")) is None


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)
