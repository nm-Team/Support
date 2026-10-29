"""Redirects generation tests."""

import json
import shutil
import subprocess

import pytest

import nmteam_support.redirects as redirects_module


@pytest.mark.parametrize(
    ("incoming", "destination", "expected"),
    [
        ("/old/", "/new/", "/new/"),
        ("/old", "/new/", "/new/"),
        ("/old.html?ref=share#details", "/new/", "/new/?ref=share#details"),
        ("/old.md#_3", "/new/", "/new/#_3"),
        ("/old/child/?view=full#part", "/new/", "/new/?view=full#part"),
        ("/old/?ref=share#before", "/new/#after", "/new/?ref=share#after"),
        ("/old/?ref=share#before", "/new/?ref=target#after", "/new/?ref=target#after"),
        ("/old/#%E4%B8%AD%E6%96%87", "/new/", "/new/#%E4%B8%AD%E6%96%87"),
        ("/old-other/", "/new/", None),
        ("/unmoved/?ref=share#details", "/new/", None),
    ],
)
def test_generated_script_resolves_legacy_links(incoming, destination, expected):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to execute the generated browser JavaScript")
    script = redirects_module.render_redirects_js({"/old/": destination})
    harness = """
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const location = new URL(input.url);
let redirect = null;
location.replace = value => { redirect = value; };
vm.runInNewContext(input.script, { window: { location }, URL, console: { log() {} } });
process.stdout.write(JSON.stringify(redirect));
"""
    result = subprocess.run(
        [node, "-e", harness],
        input=json.dumps({"url": "https://support.nmteam.xyz" + incoming, "script": script}),
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == (
        "https://support.nmteam.xyz" + expected if expected else None
    )


def test_render_redirects_js_contains_mapping():
    js = redirects_module.render_redirects_js({"/old/": "/new/"})
    assert "const redirects = {" in js
    assert '"/old/": "/new/"' in js
    assert "window.location.replace(target.href);" in js


def test_render_redirects_js_keeps_unicode():
    js = redirects_module.render_redirects_js({"/旧/": "/新/"})
    assert "/旧/" in js


def test_load_redirects_missing_file(tmp_path):
    assert redirects_module.load_redirects(tmp_path / "nope.json") is None


def test_load_redirects_reads_map(tmp_path):
    p = tmp_path / "redirects.json"
    p.write_text(json.dumps({"redirects": {"/a/": "/b/"}}), encoding="utf-8")
    assert redirects_module.load_redirects(p) == {"/a/": "/b/"}


def test_load_redirects_invalid_json(tmp_path):
    p = tmp_path / "redirects.json"
    p.write_text("{ not valid json", encoding="utf-8")
    assert redirects_module.load_redirects(p) is None


def test_load_redirects_missing_key(tmp_path):
    p = tmp_path / "redirects.json"
    p.write_text(json.dumps({"foo": 1}), encoding="utf-8")
    assert redirects_module.load_redirects(p) is None


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
