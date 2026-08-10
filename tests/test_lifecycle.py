"""Real production lifecycle integration tests."""

import json

from nmteam_support.cli import build_site


def test_build_reads_docs_directly_and_writes_only_final_outputs(tmp_path, docs_dir):
    (tmp_path / "assets" / "styles").mkdir(parents=True)
    (tmp_path / "assets" / "styles" / "site.css").write_text(
        "body { color: black; }\n", encoding="utf-8"
    )
    (tmp_path / "redirects.json").write_text(
        json.dumps({"redirects": {"/old/": "/new/"}}), encoding="utf-8"
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        "site_name: Test\n"
        "site_url: https://docs.example.test\n"
        "strict: true\n"
        "docs_dir: docs\n"
        "site_dir: site\n"
        "plugins:\n"
        "  - nmteam-support\n"
        "markdown_extensions:\n"
        "  - admonition\n",
        encoding="utf-8",
    )

    build_site(config)

    site = tmp_path / "site"
    assert (site / "index.html").exists()
    assert (site / "nmbot-telegram" / "mcp" / "index.html").exists()
    assert (site / "assets" / "styles" / "site.css").read_text(encoding="utf-8") == (
        "body { color: black; }\n"
    )
    assert '"/old/": "/new/"' in (site / "assets" / "js" / "redirects.js").read_text(
        encoding="utf-8"
    )
    assert "帮助我们改进此文档" in (site / "nmbot-telegram" / "mcp.md").read_text(encoding="utf-8")
    assert not (tmp_path / "cache").exists()
    assert not (tmp_path / "generated").exists()
