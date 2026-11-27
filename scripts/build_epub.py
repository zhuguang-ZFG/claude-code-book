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
DEFAULT_EPUB_INKS = {
    "--ink": "#26221B",
    "--ink-2": "#5C5448",
    "--ink-3": "#675F4F",
    "--bronze": "#43392B",
    "--bronze-2": "#8A7D68",
    "--bronze-3": "#5A5040",
    "--cinnabar": "#B4472F",
    "--jade": "#4E6E5D",
    "--sky": "#4C7093",
    "--sans": '"PingFang SC","Microsoft YaHei","Segoe UI",system-ui,-apple-system,sans-serif',
    "--serif": '"Noto Serif SC","Source Han Serif SC",Georgia,serif',
    "--mono": '"JetBrains Mono","Cascadia Code",Consolas,Menlo,monospace',
}
CSS = """
/* yuyu collected reader edition — light first, dark overrides last */
html{color:#26221B;background:#FBF7EF}
body{font-family:"Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",Georgia,"Times New Roman",serif;line-height:1.7;margin:1em}
h1,h2,h3,h4{line-height:1.35;break-after:avoid}
h1{font-size:1.45em;margin:.2em 0 .6em}
h2{font-size:1.22em;margin:1.8em 0 .6em;padding:0 0 .25em .6em;border-left:3px solid #B4472F;border-bottom:1px solid #E3D8C1}
h3{font-size:1.1em;margin:1.4em 0 .45em;color:#5A5040}
h4{font-size:1em;margin:1.2em 0 .4em;color:#5C5448}
p{orphans:2;widows:2;margin:0 0 .68em;text-align:justify;line-break:strict}
strong{font-weight:700}
em{font-family:"Kaiti SC","STKaiti","KaiTi","楷体",serif;font-style:normal;color:#5A5040}
li{margin:.25em 0}
hr{border:none;border-top:1px solid #E3D8C1;margin:1.5em 0}
article,section.part-divider{break-before:page}
img{max-width:100%;height:auto;object-fit:contain}
figure{margin:1.5em 0;break-inside:avoid}
figcaption{font-size:.85em;color:#5C5448;text-align:center;margin-top:.55em;line-height:1.6}
.fig-no{color:#B4472F;font-weight:700;margin-right:.35em}
.diagram-frame,.illu-frame{background:#FFFDF8;border:1px solid #E3D8C1;border-radius:6px;padding:.65em}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.8em;line-height:1.6;margin:0;padding:.9em 1em;background:#211E19;color:#EDE6D6;border-radius:6px}
code{font-family:"JetBrains Mono","Cascadia Code","SF Mono",Consolas,Menlo,monospace;overflow-wrap:anywhere;font-size:.88em;background:#F3EAD8;color:#5A5040;padding:.06em .3em;border-radius:4px}
pre code,.codehilite code{background:none;color:inherit;padding:0;font-size:inherit;border-radius:0}
.codehilite{margin:1.2em 0;border:1px solid #3A352C;border-radius:6px;overflow:hidden;background:#211E19}
table{border-collapse:collapse;max-width:100%;font-size:.82em;margin:1.2em 0;font-variant-numeric:tabular-nums}
td,th{border:1px solid #D2C4A6;padding:.42em .6em;overflow-wrap:anywhere;vertical-align:top}
th{background:#F3EAD8;color:#5A5040;font-weight:700;text-align:left;border-bottom:2px solid #8A7D68}
tbody tr:nth-child(2n){background:#F7F1E4}
a{color:#B4472F}
blockquote{border-inline-start:3px solid #8A7D68;margin-inline:0;padding:.55em 1em;background:#F5EFE2;border-radius:0 6px 6px 0;color:#5C5448}
.chapter-body > blockquote:first-child:not(.callout){border-inline-start:none;border-top:1px solid #E3D8C1;border-bottom:1px solid #E3D8C1;background:none;border-radius:0;padding:.6em 0;text-align:right;color:#5A5040}
/* chapter opener */
.chapter-head{margin:0 0 1.6em;padding:1.1em 0 1em;border-bottom:2px solid #E3D8C1}
.eyebrow{font-size:.8em;letter-spacing:.12em;color:#675F4F;margin:0 0 .7em}
.vol-tag{color:#B4472F;font-weight:700}
.ch-seal{display:block;font-size:2.3em;font-weight:700;line-height:1;color:#E3D8C1;margin:.05em 0 .1em}
.ch-title{margin:.1em 0 .2em}
.ch-emblem{display:block;margin:.3em 0 .8em;text-align:center}
.ch-emblem img{width:4em;height:4em;object-fit:contain;mix-blend-mode:multiply}
.kp-art img,.pd-art img,.cover-art img,.diagram-frame img,.illu-frame img{mix-blend-mode:multiply}
/* one-line summary */
.lead-band{margin:1.3em 0;padding:.85em 1em .95em;background:#F3EAD8;border-left:4px solid #B4472F;border-radius:0 6px 6px 0}
.lb-tag{margin:0 0 .35em;font-weight:700;color:#B4472F;font-size:.9em;letter-spacing:.06em}
.lb-plain{margin:0}
.lb-analogy{margin:.4em 0 0;color:#5C5448;font-size:.95em}
.lb-a-tag{font-weight:700}
/* chapter compass */
.compass{margin:1.3em 0}
.compass-card{margin:.8em 0;padding:.7em .95em;background:#FFFDF8;border:1px solid #E3D8C1;border-left:4px solid #4E6E5D;border-radius:6px}
.compass-card.question{border-left-color:#B4472F}
.compass-card.boundary{border-left-color:#675F4F}
.compass-card p{margin:0}
.cc-tag{margin:0 0 .3em;font-size:.85em;font-weight:700;letter-spacing:.08em;color:#4E6E5D}
.compass-card.question .cc-tag{color:#B4472F}
.compass-card.boundary .cc-tag{color:#675F4F}
.cc-src{margin:.8em 0 0;font-size:.85em;color:#675F4F;text-align:left}
.source-chip{display:inline-block;margin:.2em .4em .2em 0;padding:.05em .6em;border:1px solid #D2C4A6;border-radius:999px;background:#F3EAD8;color:#5A5040;text-decoration:none}
/* section tier chips */
.sec-tier{display:inline-block;margin-left:.45em;padding:.1em .6em;border-radius:999px;font-size:.68em;font-weight:700;letter-spacing:.08em;vertical-align:.2em;color:#FBF7EF;background:#8A7D68}
.t-start{background:#4E6E5D}
.t-core{background:#B4472F}
.t-deep{background:#675F4F}
/* callouts */
.callout{margin:1.2em 0;padding:.7em 1em .5em;background:#F3EAD8;border:1px solid #E3D8C1;border-left:4px solid #8A7D68;border-radius:6px}
.callout p{margin:0 0 .5em}
.callout-tag{font-weight:700;color:#43392B}
.callout-info{border-left-color:#43392B}
.callout-tip{border-left-color:#4E6E5D}
.callout-tip .callout-tag{color:#4E6E5D}
.callout-warning{border-left-color:#B4472F}
.callout-warning .callout-tag{color:#B4472F}
.callout-concept{border-left-color:#4C7093}
.callout-concept .callout-tag{color:#4C7093}
/* chapter end */
.ch-close{margin-top:2.2em;padding-top:1.2em;border-top:1px solid #E3D8C1}
.keeper{margin:1.1em 0;padding:.1em 1em .4em;background:#F3EAD8;border-radius:6px}
.keeper-note{margin:0;color:#5C5448;border-inline-start:2px solid #8A7D68;padding-inline-start:.9em}
/* back-of-chapter asides */
.chapter-notes,.new-terms{margin:1.8em 0;padding:0 .95em .4em;background:#F3EAD8;border-radius:6px}
.chapter-notes h4,.new-terms h4{margin:.8em 0 .4em;font-size:.85em;letter-spacing:.1em;color:#8A7D68}
.chapter-notes ol,.new-terms ul{margin:.2em 0 .6em}
.nt-term{font-weight:700}
/* ornaments */
.hr-rule{height:1px;border:none;background:#E3D8C1;margin:2em auto;width:60%}
/* part and volume dividers */
section.part-divider{padding-top:2.5em}
.pd-no{font-size:.85em;letter-spacing:.4em;color:#B4472F;font-weight:700;margin:0 0 .6em}
.pd-title{font-size:1.7em;margin:.2em 0 .4em}
.pd-count{color:#675F4F;margin:.2em 0 1em}
.cover-rule{height:2px;border:none;background:#D2C4A6;margin:1.6em 0;width:33%}
.pd-motto,.pd-goal{color:#5C5448}
.pd-motto{font-style:italic}
.pd-list{margin:1em 0}
/* front matter */
.front-page{padding-top:1.5em}
.page-title{font-size:1.55em;margin:0 0 .85em;padding-bottom:.3em;border-bottom:2px solid #B4472F;color:#5A5040}
.cover{text-align:center;padding-top:2.2em}
.cover .book-title{font-size:2em;margin:.4em 0 .3em}
.cover-art img{max-width:88%}
.cover-kicker{letter-spacing:.3em;color:#675F4F;font-size:.82em}
.book-sub,.book-epi{color:#5C5448}
.cover-seal{display:inline-block;margin:.6em 0;padding:.25em .6em;background:#B4472F;color:#FBF7EF;border-radius:4px;font-weight:700;letter-spacing:.15em}
.cover-foot{margin-top:1.2em;padding-top:.8em;border-top:1px solid #E3D8C1;color:#675F4F;font-size:.85em}
.imprint-list{margin:0 0 1.4em}
.ip-row{padding:.45em 0;border-bottom:1px solid #E3D8C1}
.ip-row dt{font-size:.82em;font-weight:700;letter-spacing:.12em;color:#43392B;margin:0}
.ip-row dd{margin:.15em 0 0}
.ip-notice-t{font-size:.95em;color:#B4472F;margin:1.2em 0 .35em}
.ip-notice{border-left:3px solid #D2C4A6;padding-left:.85em;color:#5C5448;font-size:.92em}
.rev-v{font-size:1.05em;color:#5A5040;border-bottom:1px solid #E3D8C1;padding-bottom:.2em;margin:1.2em 0 .4em}
.rev-d{font-size:.8em;color:#675F4F;margin-left:.6em;font-weight:400}
.route-card{margin:.75em 0;padding:.75em .95em;background:#FFFDF8;border:1px solid #E3D8C1;border-top:2.5px solid #8A7D68;border-radius:6px}
.route-card h3{margin:0 0 .3em;font-size:.95em;color:#B4472F}
.route-card p{margin:0;font-size:.9em;color:#5C5448}
.route-parts{list-style:none;padding:0;margin:1em 0}
.route-parts li{padding:.45em 0;border-bottom:1px solid #E3D8C1}
.route-goal{display:block;font-size:.88em;color:#675F4F;margin-top:.15em}
/* volume toc and backmatter */
.toc-vol{display:block;font-weight:700;margin:1.3em 0 .45em;padding-top:.65em;border-top:2px solid #D2C4A6}
.tp-no{color:#B4472F;margin-inline-end:.5em}
.toc-row{display:block;margin:.42em 0;text-decoration:none}
.toc-n{display:inline-block;min-width:1.9em;text-align:center;font-weight:700;font-size:.82em;padding:.05em .28em;border:1px solid #D2C4A6;border-radius:4px;margin-inline-end:.5em;color:#5A5040}
.toc-n-guide{color:#B4472F;border-color:#B4472F;background:#F3EAD8}
.toc-part{display:block;font-weight:700;margin:.95em 0 .35em}
.reg-kind{font-size:1em;color:#5A5040;border-bottom:1px solid #D2C4A6;padding-bottom:.25em;margin:1.5em 0 .6em}
.reg-list{list-style:none;padding:0;margin:0}
.reg-list li{padding:.65em .85em;margin:.5em 0;background:#FFFDF8;border:1px solid #E3D8C1;border-left:3px solid #8A7D68;border-radius:6px;break-inside:avoid}
.reg-no{font-weight:700;color:#B4472F;margin-inline-end:.5em}
.reg-auth{display:inline-block;font-size:.8em;padding:.05em .45em;background:#F3EAD8;border-radius:4px;color:#43392B;margin-inline:.35em}
.reg-meta{color:#675F4F;font-size:.85em;margin-top:.25em}
.reg-scope{font-size:.9em;color:#5C5448;margin-top:.25em}
.idx-letter{color:#B4472F;border-bottom:2px solid #8A7D68;display:inline-block;padding-bottom:.1em;margin:1.2em 0 .35em}
.idx-list,.pr-list,.kn-list{list-style:none;padding:0;margin:0}
.idx-row,.pr-row,.kn-row{padding:.38em 0;border-bottom:1px dotted #D2C4A6;break-inside:avoid}
.idx-term,.pr-term,.kn-head{font-weight:700;color:#5A5040;margin-right:.45em}
.pr-why,.kn-note{display:block;margin-top:.15em;padding-left:.6em;border-left:2px solid #8A7D68}
.pr-ana{display:block;margin-top:.15em;padding-left:.6em;color:#B4472F}
.colophon{margin-top:2em;padding-top:1em;border-top:1px solid #E3D8C1;text-align:center;font-size:.82em;color:#675F4F}
/* pygments — dark ground in both schemes */
.codehilite .c,.codehilite .cm,.codehilite .c1,.codehilite .cs{color:#93886F;font-style:italic}
.codehilite .k,.codehilite .kd,.codehilite .kn,.codehilite .kt{color:#D8B26A;font-weight:600}
.codehilite .nf,.codehilite .nc,.codehilite .fm{color:#E2C08D}
.codehilite .s,.codehilite .s1,.codehilite .s2,.codehilite .sb,.codehilite .sd{color:#A9C46C}
.codehilite .m,.codehilite .mi,.codehilite .mf,.codehilite .mh{color:#DFA878}
.codehilite .nt,.codehilite .tag{color:#8FB2D4}
.codehilite .na,.codehilite .attr{color:#C8A45C}
.codehilite .o,.codehilite .ow{color:#BDB4A2}
.codehilite .err{color:#E07B5F}
/* web-only furniture stays hidden */
.rail,.page-ref,.fig-hint,.gloss-pop,.tier-chip,.t-ruts{display:none}
.sheet{width:auto;max-width:100%;min-width:0;margin:0;padding:0}
svg{max-width:100%}
@media(prefers-color-scheme:dark){
html{color:#E9E4D8;background:#1E1D18}
a{color:#E07B5F}
h2{border-left-color:#E07B5F;border-bottom-color:#37342A}
h3{color:#E2DBCB}
h4{color:#BDB4A2}
em{color:#E2DBCB}
code{background:#22221C;color:#E2DBCB}
pre code,.codehilite code{background:none;color:inherit}
hr{border-top-color:#37342A}
figcaption,.lb-analogy,.pd-motto,.pd-goal,.book-sub,.book-epi,.cc-src,.keeper-note{color:#BDB4A2}
.eyebrow,.cover-kicker,.cover-foot,.reg-meta,.pd-count{color:#A59C8A}
td,th{border-color:#4A4536}
th{background:#22221C;color:#E2DBCB;border-bottom-color:#A89E8C}
tbody tr:nth-child(2n){background:#24231D}
blockquote{border-inline-start-color:#A89E8C;background:#22221C;color:#BDB4A2}
.chapter-body > blockquote:first-child:not(.callout){border-top-color:#37342A;border-bottom-color:#37342A;background:none;color:#E2DBCB}
.compass-card{background:#1E1D18;border-color:#37342A}
.diagram-frame,.illu-frame{background:#F5EFE2;border-color:#4A4536}
.diagram-frame img,.illu-frame img{mix-blend-mode:multiply}
.lead-band,.chapter-notes,.new-terms,.keeper,.callout{background:#22221C;border-color:#37342A}
.callout{border-left-color:#A89E8C}
.callout-tag,.toc-n,.source-chip{color:#E2DBCB}
.source-chip{border-color:#4A4536;background:#22221C}
.callout-info{border-left-color:#CFC6B4}
.callout-tip{border-left-color:#9DBFA9}
.callout-tip .callout-tag{color:#9DBFA9}
.callout-warning{border-left-color:#E07B5F}
.callout-warning .callout-tag{color:#E07B5F}
.callout-concept{border-left-color:#8FB2D4}
.callout-concept .callout-tag{color:#8FB2D4}
.lb-tag,.vol-tag,.pd-no,.tp-no,.reg-no,.ip-notice-t,.route-card h3,.idx-letter,.pr-ana{color:#E07B5F}
.cover-seal{background:#E07B5F;color:#1E1D18}
.page-title{color:#E2DBCB;border-bottom-color:#E07B5F}
.cover-foot,.ip-row,.rev-v,.route-parts li,.colophon{border-color:#37342A}
.ip-row dt,.rev-v,.reg-kind,.idx-term,.pr-term,.kn-head{color:#E2DBCB}
.ip-notice,.route-card p,.reg-scope,.route-goal{color:#BDB4A2}
.ip-notice,.toc-vol,.reg-kind,.idx-row,.pr-row,.kn-row{border-color:#4A4536}
.route-card,.reg-list li{background:#22221C;border-color:#37342A}
.route-card{border-top-color:#A89E8C}
.reg-list li{border-left-color:#A89E8C}
.reg-auth{background:#1E1D18;color:#CFC6B4}
.toc-n{border-color:#4A4536;color:#E2DBCB}
.toc-n-guide{color:#E07B5F;border-color:#E07B5F;background:#22221C}
.pr-why,.kn-note{border-left-color:#A89E8C}
.compass-card{border-left-color:#9DBFA9}
.compass-card.question{border-left-color:#E07B5F}
.compass-card.boundary{border-left-color:#BDB4A2}
.cc-tag{color:#9DBFA9}
.compass-card.question .cc-tag{color:#E07B5F}
.compass-card.boundary .cc-tag{color:#BDB4A2}
.sec-tier{background:#A89E8C;color:#1E1D18}
.t-start{background:#9DBFA9}
.t-core{background:#E07B5F}
.t-deep{background:#BDB4A2}
.fig-no,.chapter-notes h4,.new-terms h4{color:#A89E8C}
.fig-no{color:#E07B5F}
.ch-seal{color:#4A4536}
.ch-emblem img,.kp-art img,.pd-art img,.cover-art img{mix-blend-mode:screen;filter:invert(1) hue-rotate(180deg)}
.chapter-head,.ch-close{border-color:#37342A}
.hr-rule,.cover-rule{background:#4A4536}
.keeper-note{border-inline-start-color:#A89E8C}
}
"""


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
            raster.emulate_media(color_scheme="light", reduced_motion="reduce")
            for index in range(svg_count):
                node = page.locator(f'main svg[data-epub-svg="{index}"]')
                drawing = node.evaluate("""e => {
                    const style = getComputedStyle(e);
                    const rootStyle = getComputedStyle(document.documentElement);
                    const box = e.viewBox.baseVal;
                    const vars = {};
                    for (const name of [
                        '--ink', '--ink-2', '--ink-3',
                        '--bronze', '--bronze-2', '--bronze-3',
                        '--cinnabar', '--jade', '--sky',
                        '--sans', '--serif', '--mono'
                    ]) {
                        const val = (style.getPropertyValue(name) || rootStyle.getPropertyValue(name) || '').trim();
                        if (val) vars[name] = val;
                    }
                    return {svg:e.outerHTML, width:Math.min(1100, e.getBoundingClientRect().width || box.width),
                            ratio:box.width / box.height, color:style.color, font:style.fontFamily, vars:vars};
                }""")
                width = max(1, round(drawing["width"]))
                height = max(1, round(width / drawing["ratio"]))
                ink_vars = {
                    key: re.sub(r"[{}<>]", "", str(drawing.get("vars", {}).get(key) or default))
                    for key, default in DEFAULT_EPUB_INKS.items()
                }
                vars_css = ";".join(f"{key}:{val}" for key, val in ink_vars.items())
                raster.set_content('<html><body>' + drawing["svg"] + '</body></html>')
                raster.add_style_tag(content=(
                    f':root{{{vars_css}}}'
                    f'body{{margin:0;color:{drawing["color"]};font-family:{drawing["font"]}}}'
                    f'svg{{display:block!important;width:{width}px!important;height:{height}px!important;min-width:0!important;max-width:none!important}}'
                    'svg.il-cinnabar,svg .il-cinnabar{color:var(--cinnabar)}'
                    'svg.il-jade,svg .il-jade{color:var(--jade)}'
                    'svg.il-sky,svg .il-sky{color:var(--sky)}'
                    'svg.il-bronze,svg .il-bronze{color:var(--bronze)}'
                    'svg.il-bronze-2,svg .il-bronze-2{color:var(--bronze-2)}'
                    'svg.il-bronze-3,svg .il-bronze-3{color:var(--bronze-3)}'
                    'svg.il-muted,svg .il-muted{color:var(--ink-3)}'
                    'svg .frame-no{font-family:var(--sans);font-size:9px;fill:currentColor;opacity:.5;stroke:none}'
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
