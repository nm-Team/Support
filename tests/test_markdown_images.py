"""WebP-first Markdown image rendering tests."""

from xml.etree import ElementTree

from markdown import markdown

from nmteam_support.markdown_images import WebpPictureExtension


def _fragment(source: str) -> ElementTree.Element:
    html = markdown(source, extensions=["attr_list", WebpPictureExtension()])
    return ElementTree.fromstring(f"<root>{html}</root>")


def test_local_raster_image_renders_webp_before_original_fallback():
    root = _fragment('![配置页面](/assets/images/panel.png){ width="360" }')

    picture = root.find(".//picture")
    assert picture is not None
    source, fallback = list(picture)
    assert source.tag == "source"
    assert source.attrib == {
        "srcset": "/assets/images/panel.webp",
        "type": "image/webp",
    }
    assert fallback.tag == "img"
    assert fallback.attrib["src"] == "/assets/images/panel.png"
    assert fallback.attrib["alt"] == "配置页面"
    assert fallback.attrib["width"] == "360"


def test_external_and_vector_images_remain_plain_images():
    root = _fragment("![远程](https://example.com/image.png)\n\n![图标](/assets/icons/doc.svg)")

    assert root.findall(".//picture") == []
    assert [image.attrib["src"] for image in root.findall(".//img")] == [
        "https://example.com/image.png",
        "/assets/icons/doc.svg",
    ]
