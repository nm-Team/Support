"""Production build configuration tests."""

from pathlib import Path
from xml.etree import ElementTree

import yaml
from markdown import markdown
from mkdocs.config import load_config


def test_every_heading_level_has_a_copyable_permalink():
    repo_root = Path(__file__).resolve().parents[1]
    config = load_config(config_file=str(repo_root / "mkdocs.yml"))
    source = "\n\n".join(f"{'#' * level} Section {level}" for level in range(1, 7))

    output = markdown(
        source,
        extensions=config.markdown_extensions,
        extension_configs=config.mdx_configs,
    )

    headings = list(ElementTree.fromstring(f"<div>{output}</div>"))
    assert [heading.tag for heading in headings] == [f"h{level}" for level in range(1, 7)]
    for heading in headings:
        link = heading.find("a[@class='headerlink']")
        assert link is not None
        assert link.get("href") == f"#{heading.attrib['id']}"
        assert link.get("title") == "复制章节链接"
        assert heading.text.startswith("Section ")


def test_mkdocs_reads_sources_directly_through_support_plugin():
    repo_root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((repo_root / "mkdocs.yml").read_text(encoding="utf-8"))

    assert config["docs_dir"] == "docs"
    assert "nmteam-support" in config["plugins"]
    assert not config.get("strict", False)
    assert "nav" not in config
    assert not (repo_root / "mkdocs-template.yml").exists()


def test_markdown_renderer_preserves_mdformat_hard_breaks():
    repo_root = Path(__file__).resolve().parents[1]
    config = load_config(config_file=str(repo_root / "mkdocs.yml"))

    output = markdown(
        "发布日期：2026 年 8 月 11 日\\\n更新日期：2026 年 8 月 12 日",
        extensions=config.markdown_extensions,
        extension_configs=config.mdx_configs,
    )

    assert output == ("<p>发布日期：2026 年 8 月 11 日<br />\n更新日期：2026 年 8 月 12 日</p>")
