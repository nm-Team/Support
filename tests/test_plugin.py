"""MkDocs plugin integration tests."""

import importlib
import importlib.util
import json
from pathlib import Path

from mkdocs.config import load_config
from mkdocs.structure.files import Files, get_files
from mkdocs.structure.pages import Page
from PIL import Image


def _plugin_module():
    assert importlib.util.find_spec("nmteam_support.plugin") is not None
    return importlib.import_module("nmteam_support.plugin")


def _context(tmp_path: Path, docs_dir: Path):
    module = _plugin_module()
    config_path = tmp_path / "mkdocs.yml"
    config_path.write_text(
        "site_name: Test\nsite_url: https://docs.example.test\ndocs_dir: docs\nsite_dir: site\n",
        encoding="utf-8",
    )
    assets = tmp_path / "assets"
    (assets / "styles").mkdir(parents=True)
    (assets / "styles" / "site.css").write_text("body {}\n", encoding="utf-8")
    (tmp_path / "redirects.json").write_text(
        json.dumps({"redirects": {"/old/": "/new/"}}), encoding="utf-8"
    )
    plugin = module.SupportPlugin()
    errors, warnings = plugin.load_config({}, config_file_path=str(config_path))
    assert errors == []
    assert warnings == []
    config = load_config(config_file=str(config_path))
    config.plugins["nmteam-support"] = plugin
    config.plugins.on_startup(command="build", dirty=False)
    config = config.plugins.on_config(config)
    files = config.plugins.on_files(get_files(config), config=config)
    assert isinstance(files, Files)
    return plugin, config, files


def test_plugin_builds_navigation_and_virtual_static_files(tmp_path, docs_dir):
    internal = docs_dir / "superpowers"
    internal.mkdir()
    (internal / "plan.md").write_text("# Internal\n", encoding="utf-8")
    _plugin, config, files = _context(tmp_path, docs_dir)

    assert config.nav == [
        {"nmTeam 支持": "index.md"},
        {
            "nmBot Telegram": [
                {"nmBot Telegram": "nmbot-telegram/index.md"},
                {"MCP 配置": "nmbot-telegram/mcp.md"},
            ]
        },
        {
            "联系我们": [
                {"联系我们": "contact-us/index.md"},
                {"论坛": "contact-us/forum.md"},
            ]
        },
        {"关于": "about.md"},
    ]
    assert files.get_file_from_path("assets/styles/site.css") is not None
    redirects = files.get_file_from_path("assets/js/redirects.js").content_string
    assert "const redirects =" in redirects
    assert '"/old/": "/new/"' in redirects
    assert "nmbot-telegram/mcp.md" in files.get_file_from_path("llms.txt").content_string
    assert files.get_file_from_path("superpowers/plan.md") is None
    assert not (tmp_path / "cache").exists()
    assert not (tmp_path / "generated").exists()


def test_plugin_transforms_only_page_markdown_at_render_time(tmp_path, docs_dir):
    plugin, config, files = _context(tmp_path, docs_dir)
    doc_file = files.get_file_from_path("nmbot-telegram/mcp.md")
    doc_page = Page(None, doc_file, config)
    doc_page.meta = {}

    rendered_doc = plugin.on_page_markdown(
        "# MCP 配置\n\n正文。\n", page=doc_page, config=config, files=files
    )

    assert "帮助我们改进此文档" in rendered_doc

    index_file = files.get_file_from_path("nmbot-telegram/index.md")
    index_page = Page(None, index_file, config)
    index_page.meta = {}
    rendered_index = plugin.on_page_markdown(
        "# nmBot\n\n简介。\n", page=index_page, config=config, files=files
    )

    assert '<div class="docsList">' in rendered_index
    assert index_page.meta["hide"] == ["toc"]


def test_plugin_writes_final_images_and_markdown_copies_without_staging(tmp_path, docs_dir):
    image_path = tmp_path / "assets" / "images" / "diagram.png"
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (16, 16), "red").save(image_path)
    plugin, config, _files = _context(tmp_path, docs_dir)
    Path(config.site_dir).mkdir()

    plugin.on_post_build(config=config)

    assert (Path(config.site_dir) / "assets" / "images" / "diagram.png").exists()
    assert (Path(config.site_dir) / "assets" / "images" / "diagram.webp").exists()
    markdown_copy = Path(config.site_dir) / "nmbot-telegram" / "mcp.md"
    assert "帮助我们改进此文档" in markdown_copy.read_text(encoding="utf-8")
    assert not (tmp_path / "cache").exists()
    assert not (tmp_path / "generated").exists()
