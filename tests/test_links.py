"""Offline checks of rendered URLs, files, and HTML anchors."""

from html import escape
from pathlib import Path

import pytest

from nmteam_support.cli import build_site
from nmteam_support.links import LinkCheckError, check_internal_links

SITE_URL = "https://docs.example.test/"


@pytest.fixture
def built_site(tmp_path: Path) -> Path:
    site = tmp_path / "site"
    (site / "guide").mkdir(parents=True)
    (site / "assets").mkdir()
    (site / "index.html").write_text('<h1 id="home">Home</h1>', encoding="utf-8")
    (site / "guide/index.html").write_text(
        '<h1 id="使用说明">Guide</h1><span id="_1"></span><a name="legacy"></a>',
        encoding="utf-8",
    )
    (site / "assets/diagram one.png").write_bytes(b"image")
    (site / "assets/site.css").write_text("body {}", encoding="utf-8")
    (site / "assets/site.js").write_text("", encoding="utf-8")
    (site / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return site


@pytest.mark.parametrize(
    "href",
    [
        "/guide/",
        "/guide",
        "guide/index.html",
        "./guide/?q=one&other=two",
        "https://docs.example.test/guide/",
        "https://DOCS.example.test:443/guide/",
        "http://docs.example.test/guide/",
        "//docs.example.test/guide/",
        "/guide/#使用说明",
        "/guide/#%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E",
        "/guide/#_1",
        "/guide/#legacy",
        "/guide/#使用说明:~:text=Guide",
        "/guide/#:~:text=Guide",
        "/guide/#TOP",
        "#home",
        "#",
        "",
        "/assets/diagram%20one.png?v=2",
        "/guide.md",
    ],
)
def test_existing_internal_urls_pass(built_site: Path, href: str):
    (built_site / "index.html").write_text(
        f'<h1 id="home">Home</h1><a href="{escape(href, quote=True)}">Link</a>',
        encoding="utf-8",
    )

    report = check_internal_links(built_site, SITE_URL)

    assert report.pages == 2
    assert report.checked == 1
    assert report.issues == ()


@pytest.mark.parametrize(
    ("href", "reason"),
    [
        ("/missing/", "missing target"),
        ("https://docs.example.test/missing/", "missing target"),
        ("//docs.example.test/missing/", "missing target"),
        ("/Guide/", "missing target"),
        ("/guide.html", "missing target"),
        ("/guide.md/", "missing target"),
        ("/guide/#missing", "missing anchor #missing"),
        ("#HOME", "missing anchor #HOME"),
        ("/assets/missing.png", "missing target"),
        ("https://docs.example.test:invalid/guide/", "invalid URL"),
        ("/guide/%ff", "invalid URL"),
    ],
)
def test_broken_internal_urls_report_the_original_reference(
    built_site: Path, href: str, reason: str
):
    (built_site / "index.html").write_text(
        f'<h1 id="home">Home</h1>\n<a href="{escape(href, quote=True)}">Link</a>',
        encoding="utf-8",
    )

    report = check_internal_links(built_site, SITE_URL)

    assert len(report.issues) == 1
    issue = report.issues[0]
    assert issue.source == "index.html"
    assert issue.line == 2
    assert issue.url == href
    assert reason in issue.reason


def test_relative_urls_resolve_from_the_rendered_page(built_site: Path):
    (built_site / "guide/index.html").write_text(
        '<a href="../assets/diagram%20one.png">Image</a>'
        '<a href="../?q=1#home">Home</a><a href="./missing/">Missing</a>',
        encoding="utf-8",
    )

    report = check_internal_links(built_site, SITE_URL)

    assert report.checked == 3
    assert [(issue.source, issue.url) for issue in report.issues] == [
        ("guide/index.html", "./missing/")
    ]


def test_external_urls_protocols_and_escaped_examples_are_ignored(built_site: Path):
    (built_site / "index.html").write_text(
        '<a href="https://external.example/missing/">External</a>'
        '<a href="//external.example/missing/">External</a>'
        '<a href="https://docs.example.test.evil.example/missing/">Other host</a>'
        '<a href="https://docs.example.test:8443/missing/">Other port</a>'
        '<a href="mailto:help@example.test">Mail</a><a href="tg://user?id=1">Telegram</a>'
        '<a href="javascript:void(0)">Action</a><img src="data:image/png;base64,AAAA">'
        '<!-- <a href="/comment/">Comment</a> -->'
        '<code>&lt;a href="/example/"&gt;Example&lt;/a&gt;</code>'
        "<script>const example = '<a href=\"/script/\">';</script>",
        encoding="utf-8",
    )

    report = check_internal_links(built_site, SITE_URL)

    assert report.checked == 0
    assert report.issues == ()


def test_asset_references_and_self_closing_tags_are_checked(built_site: Path):
    (built_site / "index.html").write_text(
        '<link rel="stylesheet" href="/assets/site.css" />'
        '<script src="/assets/site.js"></script><img src="/assets/diagram%20one.png" />'
        '<img src="/assets/missing.png" /><iframe src="/missing/"></iframe>',
        encoding="utf-8",
    )

    report = check_internal_links(built_site, SITE_URL)

    assert report.checked == 5
    assert [issue.url for issue in report.issues] == ["/assets/missing.png", "/missing/"]


def test_base_url_and_site_subdirectory_are_respected(built_site: Path):
    (built_site / "index.html").write_text(
        '<base href="/support/guide/">'
        '<a href="#使用说明">Guide</a><a href="../guide.md">Markdown</a>'
        '<a href="https://docs.example.test/support/guide/">Absolute</a>'
        '<a href="/guide/">Outside the configured site</a>',
        encoding="utf-8",
    )

    report = check_internal_links(built_site, "https://docs.example.test/support")

    assert report.checked == 4
    assert [issue.url for issue in report.issues] == ["/guide/"]


def test_percent_encoded_unicode_paths_and_dot_segments(built_site: Path):
    (built_site / "中文").mkdir()
    (built_site / "中文/index.html").write_text('<h1 id="标题">Title</h1>', encoding="utf-8")
    (built_site / "index.html").write_text(
        '<a href="/%E4%B8%AD%E6%96%87/#%E6%A0%87%E9%A2%98">Encoded</a>'
        '<a href="/中文/#标题">Unicode</a><a href="/guide/../中文/">Dot segments</a>',
        encoding="utf-8",
    )

    assert check_internal_links(built_site, SITE_URL).issues == ()


def test_directories_without_an_index_and_client_redirects_do_not_hide_missing_pages(
    built_site: Path,
):
    (built_site / "empty").mkdir()
    (built_site / "404.html").write_text(
        '<script>window.location.replace("/guide/");</script>', encoding="utf-8"
    )
    (built_site / "index.html").write_text(
        '<a href="/empty/">Empty</a><a href="/old/">Redirect</a>', encoding="utf-8"
    )

    report = check_internal_links(built_site, SITE_URL)

    assert [issue.url for issue in report.issues] == ["/empty/", "/old/"]


def test_repeated_references_are_reported_once_per_page(built_site: Path):
    (built_site / "index.html").write_text(
        '<a href="/missing/">First</a><a href="/missing/">Again</a>', encoding="utf-8"
    )

    report = check_internal_links(built_site, SITE_URL)

    assert report.checked == 1
    assert len(report.issues) == 1


@pytest.mark.parametrize(
    "site_url", ["", "/support/", "ftp://docs.example.test/", "https://docs.example.test/?q=1"]
)
def test_invalid_site_url_fails_explicitly(built_site: Path, site_url: str):
    with pytest.raises(LinkCheckError, match="Invalid site_url"):
        check_internal_links(built_site, site_url)


def test_missing_build_fails_instead_of_checking_zero_pages(tmp_path: Path):
    with pytest.raises(LinkCheckError, match="run `nmteam build` first"):
        check_internal_links(tmp_path, SITE_URL)


def test_unreadable_html_fails_with_the_file_name(built_site: Path):
    (built_site / "guide/index.html").write_bytes(b"\xff")

    with pytest.raises(LinkCheckError, match=r"guide.*index\.html"):
        check_internal_links(built_site, SITE_URL)


def test_real_mkdocs_build_checks_generated_navigation_and_heading_aliases(
    tmp_path: Path, docs_dir: Path
):
    (docs_dir / "about.md").write_text(
        "# About\n\n"
        "[Unicode](https://docs.example.test/nmbot-telegram/mcp/#使用说明)\n\n"
        "[Legacy](/nmbot-telegram/mcp/#_1)\n\n[Broken](/missing-page/)\n",
        encoding="utf-8",
    )
    (docs_dir / "nmbot-telegram/mcp.md").write_text("# 使用说明\n", encoding="utf-8")
    (docs_dir / "nmbot-telegram/update-log").mkdir()
    (docs_dir / "nmbot-telegram/update-log/entry.md").write_text(
        "# Entry\n\n[Wrong](../../contact-us/) [Right](../../contact-us/index.md)\n",
        encoding="utf-8",
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        "site_name: Test\nsite_url: https://docs.example.test\ndocs_dir: docs\n"
        "theme:\n  name: material\nplugins:\n  - nmteam-support\n"
        "markdown_extensions:\n  - toc:\n      permalink: '#'\n"
        "  - nmteam_support.heading_anchors\n",
        encoding="utf-8",
    )

    build_site(config)
    report = check_internal_links(tmp_path / "site", SITE_URL)

    assert report.pages >= 6
    assert [(issue.source, issue.url) for issue in report.issues] == [
        ("about/index.html", "/missing-page/"),
        ("nmbot-telegram/update-log/entry/index.html", "../../contact-us/"),
    ]
