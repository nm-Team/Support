"""Cross-platform launcher behavior tests."""

import os
import subprocess
from pathlib import Path


def test_shell_launcher_forwards_arguments_from_repository_root(tmp_path):
    repository_root = Path(__file__).parents[1]
    capture_dir = tmp_path / "capture"
    capture_dir.mkdir()
    executable_dir = tmp_path / "bin"
    executable_dir.mkdir()
    fake_uv = executable_dir / "uv"
    fake_uv.write_text(
        "#!/bin/sh\n"
        'printf "%s\\n" "$PWD" > "$CAPTURE_DIR/cwd"\n'
        'printf "%s\\n" "$@" > "$CAPTURE_DIR/args"\n'
        "exit 23\n",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)
    environment = os.environ | {
        "CAPTURE_DIR": str(capture_dir),
        "PATH": f"{executable_dir}{os.pathsep}{os.environ['PATH']}",
    }

    result = subprocess.run(
        [
            "sh",
            str(repository_root / "scripts" / "nmteam.sh"),
            "redirects",
            "add",
            "/old path/",
            "/new path/",
        ],
        cwd=tmp_path,
        env=environment,
        check=False,
    )

    assert result.returncode == 23
    assert (capture_dir / "cwd").read_text(encoding="utf-8").strip() == str(repository_root)
    assert (capture_dir / "args").read_text(encoding="utf-8").splitlines() == [
        "run",
        "nmteam",
        "redirects",
        "add",
        "/old path/",
        "/new path/",
    ]
