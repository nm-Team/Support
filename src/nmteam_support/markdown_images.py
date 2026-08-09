"""WebP-first Markdown image rendering."""

from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree

from markdown import Markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

_RASTER_SUFFIXES = {".jpg", ".jpeg", ".png"}


class WebpPictureTreeprocessor(Treeprocessor):
    """Wrap local raster images in WebP-first ``picture`` elements."""

    def run(self, root: ElementTree.Element) -> None:
        for parent in list(root.iter()):
            for index, image in enumerate(list(parent)):
                if image.tag != "img" or not _is_local_raster(image.get("src", "")):
                    continue
                source = ElementTree.Element(
                    "source",
                    {
                        "srcset": _webp_url(image.attrib["src"]),
                        "type": "image/webp",
                    },
                )
                picture = ElementTree.Element("picture")
                picture.tail = image.tail
                image.tail = None
                picture.extend((source, image))
                parent[index] = picture


class WebpPictureExtension(Extension):
    """Register WebP-first rendering after ``attr_list`` processing."""

    def extendMarkdown(self, md: Markdown) -> None:
        md.treeprocessors.register(WebpPictureTreeprocessor(md), "webp_picture", 7)


def _is_local_raster(url: str) -> bool:
    parsed = urlsplit(url)
    return (
        not parsed.scheme
        and not parsed.netloc
        and PurePosixPath(parsed.path).suffix.lower() in _RASTER_SUFFIXES
    )


def _webp_url(url: str) -> str:
    parsed = urlsplit(url)
    path = str(PurePosixPath(parsed.path).with_suffix(".webp"))
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))


def makeExtension(**kwargs) -> WebpPictureExtension:
    """Load the extension from MkDocs/Python-Markdown configuration."""
    return WebpPictureExtension(**kwargs)
