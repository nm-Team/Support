"""Content-addressed cache shared by the build's expensive, deterministic transforms."""

from __future__ import annotations

import os
from hashlib import blake2b
from pathlib import Path

# Cache root, relative to the project root. It deliberately lives outside ``site/``:
# MkDocs wipes the site directory on every non-dirty build, so a cache placed there
# would never survive long enough to be hit. The directory is disposable — deleting it
# only costs one cold build.
CACHE_DIR_NAME = ".cache"

_DIGEST_SIZE = 20
_LENGTH_SIZE = 8


def content_digest(*parts: bytes) -> str:
    """Address one cache entry by the exact inputs that determine its output.

    Callers must pass everything the output depends on, including the parameters of
    the transform, so that tuning it invalidates the entries produced by the old one.
    Parts are length-prefixed, so splitting an input differently cannot collide.
    """
    digest = blake2b(digest_size=_DIGEST_SIZE)
    for part in parts:
        digest.update(len(part).to_bytes(_LENGTH_SIZE, "big"))
        digest.update(part)
    return digest.hexdigest()


def staged_path(path: Path) -> Path:
    """A process-unique sibling used to publish a cache entry without partial content.

    Two builds of this checkout can overlap, so entries are written to a private name
    and moved into place, making a half-written file impossible to observe.
    """
    return path.with_name(f"{path.name}.{os.getpid()}.part")
