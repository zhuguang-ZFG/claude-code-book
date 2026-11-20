#!/usr/bin/env python3
"""Convert a validated offline HTML edition into a scriptless reflowable EPUB.

This is a format post-pass, not a second manuscript parser. Chromium rasterizes
SVG (including Mermaid foreignObject labels) before XHTML serialization. All
images are bundled, internal anchors retained, and the ZIP is written atomically.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import re
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))
from yuyu_book.core import BuildError
from yuyu_book.pdf import _launch

XHTML = "http://www.w3.org/1999/xhtml"
EPUB = "http://www.idpf.org/2007/ops"
OPF = "http://www.idpf.org/2007/opf"
DC = "http://purl.org/dc/elements/1.1/"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCK = {"article", "section", "main", "aside", "header", "footer", "figure", "figcaption", "div", "p", "pre", "blockquote", "ul", "ol", "li", "dl", "dt", "dd", "table", "thead", "tbody", "tfoot", "tr", "td", "th", "caption", "colgroup", "h1", "h2", "h3", "h4", "h5", "h6", "nav", "hr", "br", "img", "a", "span", "strong", "em", "b", "i", "s", "small", "sub", "sup", "code", "kbd", "samp", "var", "abbr", "cite", "time", "mark", "q", "wbr"}
ATTR = {"id", "class", "href", "src", "alt", "title", "colspan", "rowspan", "scope", "start", "value", "datetime", "lang", "dir"}
CSS = """html{color:#26221B;background:#FBF7EF}body{font-family:serif;line-height:1.65;margin:1em}h1,h2,h3,h4{line-height:1.35;break-after:avoid}article,section.part-divider{break-before:page}p{orphans:2;widows:2}img{max-width:100%;height:auto;object-fit:contain}figure{margin:1em 0;break-inside:avoid}figcaption{font-size:.85em;color:#5C5448}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.8em}code{font-family:monospace;overflow-wrap:anywhere}table{border-collapse:collapse;max-width:100%;font-size:.8em}td,th{border:1px solid #D2C4A6;padding:.35em;overflow-wrap:anywhere}a{color:#B4472F}blockquote{border-inline-start:2px solid #D2C4A6;margin-inline:0;padding-inline-start:1em}.rail,.page-ref,.fig-hint,.gloss-pop,.tier-chip,.t-ruts{display:none}.sheet{width:auto;max-width:100%;min-width:0;margin:0;padding:0}svg{max-width:100%}@media(prefers-color-scheme:dark){html{color:#E9E4D8;background:#1E1D18}a{color:#E07B5F}}"""


def _text(parent, value: str) -> None:
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
    if len(parent):
        child = parent[-1]
        child.tail = (child.tail or "") + value
    else:
        parent.text = (parent.text or "") + value


class XHTMLBody(HTMLParser):
    def __init__(self, resources: dict, base: Path):
        super().__init__(convert_charrefs=True)
        self.root = ET.Element(f"{{{XHTML}}}body")
        self.stack = [("body", self.root)]
        self.resources = resources
        self.base = base

    def handle_starttag(self, tag, attributes):
        original = tag
        tag = tag if tag in BLOCK else ("div" if tag in {"details", "summary", "form"} else "span")
        attrs = {key: value for key, value in attributes if key in ATTR and value is not None}
        if tag == "img":
            src = attrs.get("src", "")
            if src.startswith("data:"):
                header, data = src.split(",", 1)
                mime = header[5:].split(";", 1)[0]
                blob = base64.b64decode(data) if ";base64" in header else urllib.parse.unquote_to_bytes(data)
            else:
                parsed = urllib.parse.urlsplit(src)
                if parsed.scheme or parsed.netloc:
                    raise BuildError(f"EPUB: external image is not allowed: {src}")
                path = (self.base / urllib.parse.unquote(parsed.path)).resolve()
                blob = path.read_bytes()
                mime = mimetypes.guess_type(path.name)[0]
            extensions = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
            if mime not in extensions:
                raise BuildError(f"EPUB: unsupported image media type {mime}")
            name = "images/" + hashlib.sha256(blob).hexdigest() + extensions[mime]
            self.resources[name] = (mime, blob)
            attrs["src"] = name
            attrs.setdefault("alt", "")
        element = ET.SubElement(self.stack[-1][1], f"{{{XHTML}}}{tag}", attrs)
        if original not in VOID:
            self.stack.append((original, element))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        _text(self.stack[-1][1], data)


def _document(title: str, lang: str, body: ET.Element) -> bytes:
    root = ET.Element(f"{{{XHTML}}}html", {"lang": lang, "{http://www.w3.org/XML/1998/namespace}lang": lang})
    head = ET.SubElement(root, f"{{{XHTML}}}head")
    ET.SubElement(head, f"{{{XHTML}}}title").text = title
    ET.SubElement(head, f"{{{XHTML}}}link", {"rel": "stylesheet", "type": "text/css", "href": "book.css"})
    root.append(body)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _navigation(body: ET.Element, lang: str, ids: set[str]) -> tuple[ET.Element, list[str]]:
    nav_body = ET.Element(f"{{{XHTML}}}body")
    nav = ET.SubElement(nav_body, f"{{{XHTML}}}nav", {f"{{{EPUB}}}type": "toc", "id": "toc"})
    ET.SubElement(nav, f"{{{XHTML}}}h1").text = "目录" if lang.startswith("zh") else "Contents"
    listing = ET.SubElement(nav, f"{{{XHTML}}}ol")
    headings = []
    parent_item = None
    child_listing = None
    for element in body.iter():
        if element.tag not in (f"{{{XHTML}}}h1", f"{{{XHTML}}}h2"):
            continue
        is_chapter = element.tag == f"{{{XHTML}}}h1"
        if is_chapter:
            parent_item = None
            child_listing = None
        anchor = element.get("id")
        if not anchor:
            anchor = f"epub-heading-{len(headings) + 1}"
            while anchor in ids:
                anchor += "-x"
            element.set("id", anchor)
            ids.add(anchor)
        label = "".join(element.itertext()).strip()
        if not label:
            continue
        headings.append(anchor)
        item = ET.Element(f"{{{XHTML}}}li")
        ET.SubElement(item, f"{{{XHTML}}}a", {"href": "#" + anchor}).text = label
        if is_chapter:
            listing.append(item)
            parent_item = item
            child_listing = None
        elif parent_item is not None:
            if child_listing is None:
                child_listing = ET.SubElement(parent_item, f"{{{XHTML}}}ol")
            child_listing.append(item)
        else:
            listing.append(item)
    return nav_body, headings


DOC_STEM = re.compile(r"[a-z0-9][a-z0-9-]*")
HEADINGS = (f"{{{XHTML}}}h1", f"{{{XHTML}}}h2")


def _has_content(block: ET.Element) -> bool:
    """A stripped jump bar leaves an empty wrapper; it is not a document."""
    if any(element.tag == f"{{{XHTML}}}img" for element in block.iter()):
        return True
    return bool("".join(block.itertext()).strip())


def _blocks(body: ET.Element) -> list[ET.Element]:
    """Reading-order blocks: one per article, one per front or back page.

    A volume wrapper only groups its children for the online edition; the
    offline book flattens it so every article becomes its own document, the
    way the reference EPUBs ship one XHTML file per chapter."""
    blocks = []
    for child in body:
        if child.tag == f"{{{XHTML}}}section" and any(
                grand.tag == f"{{{XHTML}}}article" for grand in child):
            blocks.extend(grand for grand in child if _has_content(grand))
        elif _has_content(child):
            blocks.append(child)
    return blocks


def _documents(body: ET.Element) -> list[tuple[str, ET.Element]]:
    """Name every block after its anchor, or by position when it has none."""
    documents: list[tuple[str, ET.Element]] = []
    taken: set[str] = set()
    for index, block in enumerate(_blocks(body), 1):
        stem = block.get("id", "")
        if not DOC_STEM.fullmatch(stem) or stem in taken:
            stem = f"part-{index:03d}"
        taken.add(stem)
        documents.append((stem, block))
    return documents


def _anchor_owner(documents: list[tuple[str, ET.Element]]) -> dict[str, str]:
    owner: dict[str, str] = {}
    for stem, block in documents:
        for element in block.iter():
            anchor = element.get("id")
            if not anchor:
                continue
            if anchor in owner:
                raise BuildError(f"EPUB: duplicate anchor {anchor}")
            owner[anchor] = stem
    return owner


def _relink(element: ET.Element, stem: str, owner: dict[str, str]) -> None:
    href = element.get("href", "")
    if not href.startswith("#"):
        return
    anchor = urllib.parse.unquote(href[1:])
    target = owner.get(anchor)
    if target is None:
        raise BuildError(f"EPUB: dangling internal link {href}")
    element.set("href", href if target == stem else f"{target}.xhtml{href}")


def _document_title(block: ET.Element, fallback: str) -> str:
    for element in block.iter():
        if element.tag in HEADINGS:
            label = "".join(element.itertext()).strip()
            if label:
                return label
    return fallback


def build(html: Path, output: Path, lang: str, browser: str | None = None) -> dict:
    if not html.is_file():
        raise BuildError(f"EPUB: missing HTML edition {html}")
    from playwright.sync_api import sync_playwright
    resources = {}
    with sync_playwright() as playwright:
        launched = _launch(playwright, browser)
        try:
            page = launched.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5)
            page.route("http://**/*", lambda route: route.abort())
            page.route("https://**/*", lambda route: route.abort())
            page.goto(html.resolve().as_uri(), wait_until="load")
            page.emulate_media(color_scheme="light", reduced_motion="reduce")
            page.add_style_tag(content="*{animation:none!important;transition:none!important}svg *{opacity:1!important;stroke-dashoffset:0!important}svg{max-width:1100px!important;height:auto!important}main{display:block!important}")
            page.evaluate("document.fonts.ready")
            title = page.title()
            if not page.locator("main").count():
                raise BuildError("EPUB: validated edition must contain main")
            page.evaluate("""() => {
                // Mermaid keeps its paint rules inside the SVG. Preserve those
                // until rasterization; removing them here turns nodes/edges black.
                document.querySelectorAll('script,main button,main input,main svg[aria-hidden="true"],main .fig-hint,main .page-ref,main .no-print').forEach(e=>e.remove());
                document.querySelectorAll('main svg').forEach((e,i)=>e.dataset.epubSvg=String(i));
            }""")
            svg_count = page.locator("main svg").count()
            raster = launched.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1.5)
            for index in range(svg_count):
                node = page.locator(f'main svg[data-epub-svg="{index}"]')
                drawing = node.evaluate("""e => {
                    const style = getComputedStyle(e);
                    const box = e.viewBox.baseVal;
                    return {svg:e.outerHTML, width:Math.min(1100, e.getBoundingClientRect().width || box.width),
                            ratio:box.width / box.height, color:style.color, font:style.fontFamily};
                }""")
                width = max(1, round(drawing["width"]))
                height = max(1, round(width / drawing["ratio"]))
                raster.set_content('<html><body>' + drawing["svg"] + '</body></html>')
                raster.add_style_tag(content=(
                    f'body{{margin:0;color:{drawing["color"]};font-family:{drawing["font"]}}}'
                    f'svg{{display:block!important;width:{width}px!important;height:{height}px!important;min-width:0!important;max-width:none!important}}'
                    '*{animation:none!important;transition:none!important;scroll-behavior:auto!important}'))
                raster.evaluate("document.fonts.ready")
                image = raster.locator("svg").screenshot(type="png", animations="disabled", timeout=30000)
                encoded = base64.b64encode(image).decode("ascii")
                node.evaluate("""(e,src) => {const i=document.createElement('img');i.src=src;i.alt=e.getAttribute('aria-label')||e.closest('figure')?.querySelector('figcaption')?.textContent||e.querySelector('title')?.textContent||'Illustration';e.replaceWith(i)}""", "data:image/png;base64," + encoded)
            page.evaluate("document.querySelectorAll('main style').forEach(e=>e.remove())")
            markup = page.locator("main").inner_html()
            author = page.locator('meta[name="author"]').get_attribute("content") if page.locator('meta[name="author"]').count() else ""
        finally:
            launched.close()
    parser = XHTMLBody(resources, html.parent)
    parser.feed(markup)
    suffix = f" — {author}" if author else ""
    if suffix and title.endswith(suffix):
        title = title[:-len(suffix)]
    ids = {element.get("id") for element in parser.root.iter() if element.get("id")}
    for element in parser.root.iter():
        href = element.get("href", "")
        if href.startswith("#") and urllib.parse.unquote(href[1:]) not in ids:
            raise BuildError(f"EPUB: dangling internal link {href}")
    nav_body, headings = _navigation(parser.root, lang, ids)
    digest = hashlib.sha256(html.read_bytes()).hexdigest()
    package = ET.Element(f"{{{OPF}}}package", {"version": "3.0", "unique-identifier": "book-id"})
    documents = _documents(parser.root)
    if not documents:
        raise BuildError("EPUB: the edition has no content blocks")
    owner = _anchor_owner(documents)
    for stem, block in documents:
        for element in block.iter():
            _relink(element, stem, owner)
    for element in nav_body.iter():
        _relink(element, "", owner)
    cover_name = ""
    for stem, block in documents:
        if block.get("id") == "cover":
            cover_name = next((element.get("src", "") for element in block.iter()
                               if element.tag == f"{{{XHTML}}}img"), "")
            break
    metadata = ET.SubElement(package, f"{{{OPF}}}metadata")
    ET.SubElement(metadata, f"{{{DC}}}identifier", {"id": "book-id"}).text = "urn:sha256:" + digest
    ET.SubElement(metadata, f"{{{DC}}}title").text = title
    ET.SubElement(metadata, f"{{{DC}}}language").text = lang
    ET.SubElement(metadata, f"{{{DC}}}creator").text = author
    ET.SubElement(metadata, f"{{{DC}}}rights").text = "CC BY-NC-SA 4.0"
    modified = datetime.fromtimestamp(html.stat().st_mtime, timezone.utc)
    ET.SubElement(metadata, f"{{{OPF}}}meta", {"property": "dcterms:modified"}).text = modified.strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = ET.SubElement(package, f"{{{OPF}}}manifest")
    for stem, _block in documents:
        ET.SubElement(manifest, f"{{{OPF}}}item",
                      {"id": stem, "href": stem + ".xhtml",
                       "media-type": "application/xhtml+xml"})
    for key, href, mime, props in (("nav", "nav.xhtml", "application/xhtml+xml", "nav"), ("css", "book.css", "text/css", "")):
        attrs = {"id": key, "href": href, "media-type": mime}
        if props:
            attrs["properties"] = props
        ET.SubElement(manifest, f"{{{OPF}}}item", attrs)
    cover_id = ""
    for index, (name, (mime, _blob)) in enumerate(resources.items()):
        attrs = {"id": f"image-{index}", "href": name, "media-type": mime}
        if name == cover_name:
            attrs["properties"] = "cover-image"
            cover_id = attrs["id"]
        ET.SubElement(manifest, f"{{{OPF}}}item", attrs)
    # EPUB 3 declares the library thumbnail through cover-image; the legacy
    # meta name="cover" is deprecated and draws EPUBCheck warnings.
    spine = ET.SubElement(package, f"{{{OPF}}}spine")
    for stem, _block in documents:
        ET.SubElement(spine, f"{{{OPF}}}itemref", {"idref": stem})
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="yuyu-epub-", dir=output.parent) as temporary:
        staged = Path(temporary) / output.name
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            archive.writestr("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
            archive.writestr("EPUB/package.opf", ET.tostring(package, encoding="utf-8", xml_declaration=True))
            for stem, block in documents:
                document_body = ET.Element(f"{{{XHTML}}}body")
                document_body.append(block)
                archive.writestr(f"EPUB/{stem}.xhtml", _document(
                    _document_title(block, title), lang, document_body))
            archive.writestr("EPUB/nav.xhtml", _document(title, lang, nav_body))
            archive.writestr("EPUB/book.css", CSS)
            for name, (_mime, blob) in resources.items():
                archive.writestr("EPUB/" + name, blob)
        staged.replace(output)
    return {"output": str(output), "source_sha256": digest, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "images": len(resources), "rasterized_svg": svg_count, "navigation_entries": len(headings), "documents": len(documents), "cover_image": cover_id, "bytes": output.stat().st_size}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lang", choices=["zh", "en", "zh-CN"], required=True)
    parser.add_argument("--browser")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.html, args.output, args.lang, args.browser), ensure_ascii=False))
        return 0
    except (BuildError, OSError, ValueError) as exc:
        print(f"EPUB FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
