"""Contributing note tests."""

from nmteam_support.contributing import render_contributing_note, should_hide_contributing_note
from nmteam_support.models import DocEntry


def _entry(path: str, hide: bool = False) -> DocEntry:
    name = path.rsplit("/", 1)[-1]
    return DocEntry(title="t", description="", path=path, name=name, hide_contributing_note=hide)


def test_render_contributing_note_contains_edit_url():
    note = render_contributing_note("nmbot-telegram/mcp.md")
    assert "https://github.com/nm-Team/Support/edit/main/docs/nmbot-telegram/mcp.md" in note
    assert '!!! tip "帮助我们改进此文档"' in note


def test_hide_when_flag_set():
    assert should_hide_contributing_note(_entry("a/b.md", hide=True))


def test_hide_for_index_md():
    assert should_hide_contributing_note(_entry("contact-us/index.md"))


def test_hide_for_legal_and_update_log():
    assert should_hide_contributing_note(_entry("legal/terms.md"))
    assert should_hide_contributing_note(_entry("nmbot-telegram/legal/terms.md"))
    assert should_hide_contributing_note(_entry("nmbot-telegram/update-log/2026-01.md"))


def test_show_for_normal_doc():
    assert not should_hide_contributing_note(_entry("nmbot-telegram/mcp.md"))
