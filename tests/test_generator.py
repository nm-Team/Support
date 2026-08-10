"""End-to-end generator tests."""

from pathlib import Path

import pytest
from PIL import Image

from nmteam_support.generator import (
    GeneratorOptions,
    generate,
    render_doc_file,
    stage_markdown_copies,
)


def _full_options(tmp_path: Path, docs_dir: Path, redirects: str | None = None) -> GeneratorOptions:
    (tmp_path / "mkdocs-template.yml").write_text(
        "site_name: Test\nnav:\n# NAV_ARIA_START\n# NAV_ARIA_END\n", encoding="utf-8"
    )
    if redirects is not None:
        (tmp_path / "redirects.json").write_text(redirects, encoding="utf-8")
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir(exist_ok=True)
    return GeneratorOptions(
        docs_dir=docs_dir,
        assets_dir=assets_dir,
        template_path=tmp_path / "mkdocs-template.yml",
        redirects_path=tmp_path / "redirects.json",
        cache_dir=tmp_path / "cache",
        generated_dir=tmp_path / "generated",
        mkdocs_yml_path=tmp_path / "mkdocs.yml",
    )


def test_generate_writes_all_outputs(tmp_path, docs_dir):
    options = _full_options(tmp_path, docs_dir, redirects='{"redirects": {"/old/": "/new/"}}')
    generate(options)
    assert (options.generated_dir / "index.md").exists()
    assert (options.generated_dir / "nmbot-telegram" / "mcp.md").exists()
    mkdocs_yml = options.mkdocs_yml_path.read_text(encoding="utf-8")
    assert "NAV_ARIA_START" in mkdocs_yml
    assert "nmbot-telegram/mcp.md" in mkdocs_yml


def test_generate_stages_centralized_assets(tmp_path, docs_dir):
    options = _full_options(tmp_path, docs_dir)
    stylesheet = options.assets_dir / "styles" / "site.css"
    stylesheet.parent.mkdir(parents=True)
    stylesheet.write_text("body { color: black; }\n", encoding="utf-8")

    generate(options)

    assert (options.generated_dir / "assets" / "styles" / "site.css").read_text(
        encoding="utf-8"
    ) == stylesheet.read_text(encoding="utf-8")


def test_generate_emits_optimized_raster_variants(tmp_path, docs_dir):
    options = _full_options(tmp_path, docs_dir)
    image_path = options.assets_dir / "images" / "diagram.png"
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (16, 16), "red").save(image_path)

    generate(options)

    assert (options.generated_dir / "assets" / "images" / "diagram.png").exists()
    assert (options.generated_dir / "assets" / "images" / "diagram.webp").exists()


def test_generate_injects_contributing_note(tmp_path, docs_dir):
    options = _full_options(tmp_path, docs_dir)
    generate(options)
    content = (options.generated_dir / "nmbot-telegram" / "mcp.md").read_text(encoding="utf-8")
    assert "帮助我们改进此文档" in content


def test_generate_skips_contributing_note_for_update_log(tmp_path, docs_dir):
    d = docs_dir / "nmbot-telegram" / "update-log"
    d.mkdir()
    (d / "2026-01.md").write_text(
        "---\nindex: -2601\n---\n\n# 2026-01\n\n内容。\n", encoding="utf-8"
    )
    options = _full_options(tmp_path, docs_dir)
    generate(options)
    content = (options.generated_dir / "nmbot-telegram" / "update-log" / "2026-01.md").read_text(
        encoding="utf-8"
    )
    assert "帮助我们改进此文档" not in content


def test_generate_writes_redirects_before_copy(tmp_path, docs_dir):
    """Regression: redirects.js must land in generated/, not only in cache/."""
    options = _full_options(tmp_path, docs_dir, redirects='{"redirects": {"/a/": "/b/"}}')
    generate(options)
    js = options.generated_dir / "assets" / "js" / "redirects.js"
    assert js.exists()
    assert "/a/" in js.read_text(encoding="utf-8")


def test_generate_writes_llms_txt(tmp_path, docs_dir):
    options = _full_options(tmp_path, docs_dir)
    generate(options)
    llms = options.generated_dir / "llms.txt"
    assert llms.exists()
    content = llms.read_text(encoding="utf-8")
    assert content.startswith("# nmTeam Support\n")
    assert "nmbot-telegram/mcp.md" in content
    assert "https://support.nmteam.xyz/nmbot-telegram/mcp.md" in content


def test_stage_markdown_copies_mirrors_cache(tmp_path, docs_dir):
    options = _full_options(tmp_path, docs_dir)
    generate(options)
    site_dir = tmp_path / "site"
    stage_markdown_copies(options.cache_dir, site_dir)
    twin = site_dir / "nmbot-telegram" / "mcp.md"
    assert twin.exists()
    cached = options.cache_dir / "nmbot-telegram" / "mcp.md"
    assert twin.read_text(encoding="utf-8") == cached.read_text(encoding="utf-8")
    assert (site_dir / "index.md").exists()


def test_generate_skips_superpowers_in_output(tmp_path, docs_dir):
    internal = docs_dir / "superpowers"
    internal.mkdir()
    (internal / "plan.md").write_text("# 计划\n", encoding="utf-8")
    options = _full_options(tmp_path, docs_dir)
    generate(options)
    assert not (options.generated_dir / "superpowers").exists()


def test_render_doc_file_no_heading():
    out = render_doc_file("---\ntitle: X\n---\n\n正文。\n", "x.md")
    assert "帮助我们改进此文档" in out
    assert out.startswith("---\ntitle: X\n---")


def test_generate_real_docs_tree(tmp_path):
    """Generate from the repository's actual docs/ tree into a temp output (must not hang)."""
    repo_root = Path(__file__).resolve().parents[1]
    docs = repo_root / "docs"
    if not docs.is_dir():
        pytest.skip("docs/ not present")
    options = GeneratorOptions(
        docs_dir=docs,
        assets_dir=repo_root / "assets",
        template_path=repo_root / "mkdocs-template.yml",
        redirects_path=repo_root / "redirects.json",
        cache_dir=tmp_path / "cache",
        generated_dir=tmp_path / "generated",
        mkdocs_yml_path=tmp_path / "mkdocs.yml",
    )
    generate(options)
    assert list(options.generated_dir.rglob("index.md"))
    assert (options.generated_dir / "assets" / "js" / "redirects.js").exists()
    assert not (options.generated_dir / "superpowers").exists()
