"""Redirects generation tests."""

import json

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
