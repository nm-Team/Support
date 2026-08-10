"""Production HTML minification configuration tests."""

from pathlib import Path

import htmlmin
import yaml


def test_html_minification_preserves_attribute_quotes_and_removes_comments():
    repo_root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((repo_root / "mkdocs.yml").read_text(encoding="utf-8"))
    minify = next(plugin["minify"] for plugin in config["plugins"] if "minify" in plugin)
    source = (
        '<footer class="md-footer" data-empty=""><!-- internal --><div>Copyright</div></footer>'
    )

    output = htmlmin.minify(source, **minify["htmlmin_opts"])

    assert 'class="md-footer"' in output
    assert 'data-empty=""' in output
    assert "internal" not in output
    assert len(output) < len(source)


def test_mkdocs_reads_sources_directly_through_support_plugin():
    repo_root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((repo_root / "mkdocs.yml").read_text(encoding="utf-8"))

    assert config["docs_dir"] == "docs"
    assert "nmteam-support" in config["plugins"]
    assert not config.get("strict", False)
    assert "nav" not in config
    assert not (repo_root / "mkdocs-template.yml").exists()
