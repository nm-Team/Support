"""Redirects generation tests."""

import json

import pytest

import nmteam_support.redirects as redirects_module
from nmteam_support.redirects import load_redirects, render_redirects_js


def test_render_redirects_js_contains_mapping():
    js = render_redirects_js({"/old/": "/new/"})
    assert "const redirects = {" in js
    assert '"/old/": "/new/"' in js
    assert "window.location.replace(newPath);" in js


def test_render_redirects_js_keeps_unicode():
    js = render_redirects_js({"/旧/": "/新/"})
    assert "/旧/" in js


def test_load_redirects_missing_file(tmp_path):
    assert load_redirects(tmp_path / "nope.json") is None


def test_load_redirects_reads_map(tmp_path):
    p = tmp_path / "redirects.json"
    p.write_text(json.dumps({"redirects": {"/a/": "/b/"}}), encoding="utf-8")
    assert load_redirects(p) == {"/a/": "/b/"}


def test_load_redirects_invalid_json(tmp_path):
    p = tmp_path / "redirects.json"
    p.write_text("{ not valid json", encoding="utf-8")
    assert load_redirects(p) is None


def test_load_redirects_missing_key(tmp_path):
    p = tmp_path / "redirects.json"
    p.write_text(json.dumps({"foo": 1}), encoding="utf-8")
    assert load_redirects(p) is None


def test_read_redirects_rejects_invalid_json_without_overwriting(tmp_path):
    assert hasattr(redirects_module, "read_redirects")
    path = tmp_path / "redirects.json"
    original = "{ invalid"
    path.write_text(original, encoding="utf-8")

    with pytest.raises(redirects_module.RedirectConfigError):
        redirects_module.read_redirects(path)

    assert path.read_text(encoding="utf-8") == original


def test_read_redirects_missing_file_returns_empty_map(tmp_path):
    assert hasattr(redirects_module, "read_redirects")
    assert redirects_module.read_redirects(tmp_path / "redirects.json") == {}


def test_read_redirects_rejects_non_string_mapping(tmp_path):
    assert hasattr(redirects_module, "read_redirects")
    path = tmp_path / "redirects.json"
    path.write_text(json.dumps({"redirects": {"/old/": 3}}), encoding="utf-8")

    with pytest.raises(redirects_module.RedirectConfigError):
        redirects_module.read_redirects(path)


def test_write_redirects_round_trips_unicode(tmp_path):
    assert hasattr(redirects_module, "write_redirects")
    path = tmp_path / "redirects.json"

    redirects_module.write_redirects(path, {"/旧/": "/新/"})

    assert redirects_module.read_redirects(path) == {"/旧/": "/新/"}
