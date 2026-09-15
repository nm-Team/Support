"""Shared build cache tests."""

from __future__ import annotations

from pathlib import Path

from nmteam_support.cache import content_digest, staged_path


def test_content_digest_is_stable_for_the_same_inputs():
    assert content_digest(b"encoder", b"payload") == content_digest(b"encoder", b"payload")


def test_content_digest_changes_with_every_part_it_is_given():
    baseline = content_digest(b"encoder", b"payload")

    assert content_digest(b"other-encoder", b"payload") != baseline
    assert content_digest(b"encoder", b"other-payload") != baseline
    assert content_digest(b"encoderpayload") != baseline


def test_staged_path_is_a_unique_sibling_of_the_entry(tmp_path: Path):
    entry = tmp_path / "abc123"

    staged = staged_path(entry)

    assert staged.parent == entry.parent
    assert staged != entry
    assert staged.name.startswith("abc123.")
    assert staged.name.endswith(".part")
