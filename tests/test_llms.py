"""llms.txt generation tests."""

from nmteam_support.llms import render_llms_txt
from nmteam_support.scanner import scan_docs

BASE_URL = "https://support.nmteam.xyz"


def test_llms_txt_has_header_and_summary(docs_dir):
    content = render_llms_txt(scan_docs(docs_dir), BASE_URL)
    assert content.startswith("# nmTeam Support\n")
    assert "> 支持中心。" in content
    assert content.endswith("\n")


def test_llms_txt_sections_and_links(docs_dir):
    content = render_llms_txt(scan_docs(docs_dir), BASE_URL)
    assert "## nmTeam 支持" in content  # root section
    assert "## nmBot Telegram" in content
    assert "## 联系我们" in content
    assert "- [MCP 配置](https://support.nmteam.xyz/nmbot-telegram/mcp.md): 配置 MCP。" in content
    assert "- [关于](https://support.nmteam.xyz/about.md): 了解此文档。" in content
    assert "- [nmTeam 支持](https://support.nmteam.xyz/index.md): 支持中心。" in content


def test_llms_txt_index_entries_use_index_paths(docs_dir):
    content = render_llms_txt(scan_docs(docs_dir), BASE_URL)
    assert "- [nmBot Telegram](https://support.nmteam.xyz/nmbot-telegram/index.md)" in content
    assert "- [联系我们](https://support.nmteam.xyz/contact-us/index.md)" in content


def test_llms_txt_links_use_base_url(docs_dir):
    content = render_llms_txt(scan_docs(docs_dir), "https://docs.example.org/sub")
    assert "https://docs.example.org/sub/nmbot-telegram/mcp.md" in content
    assert "support.nmteam.xyz" not in content


def test_llms_txt_empty_tree(tmp_path):
    (tmp_path / "docs").mkdir()
    content = render_llms_txt(scan_docs(tmp_path / "docs"), BASE_URL)
    assert content.startswith("# nmTeam Support\n")
    assert "## " not in content
