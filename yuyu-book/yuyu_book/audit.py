"""Post-build audit of the generated book HTML: structural guarantees
checked before a build is allowed to land in dist/."""
from __future__ import annotations

import re
from html.parser import HTMLParser

from .core import BuildError

VOID = {"br", "img", "hr", "meta", "input", "link", "wbr"}


def named_svg(attrs: dict[str, str]) -> bool:
    """A graphic is either named or explicitly hidden; `role` is neither.

    `role="graphics-document"` with no label is exactly the unlabelled stop a
    screen reader cannot announce, so it does not count as a name.
    """
    if attrs.get("aria-hidden") == "true":
        return True
    return any((attrs.get(k) or "").strip()
               for k in ("aria-label", "aria-labelledby"))


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.svgs = 0
        self.unnamed: list[str] = []
        self.scripts = 0
        self.imgs_external = 0
        self.classes: dict[str, int] = {}
        self.open_stack: list[str] = []
        self.hidden_stack: list[bool] = []
        self.svg_frames: list[dict] = []
        self.stray: list[str] = []
        self.nested: int = 0

    def handle_starttag(self, tag, attrs):
        # HTMLParser hands back `str | None` for a bare attribute; the empty
        # string keeps the reads below simple and means the same thing here
        a = {k: (v or "") for k, v in attrs}
        if a.get("id"):
            self.ids.append(a["id"])
        if a.get("href", "").startswith("#"):
            self.hrefs.append(a["href"][1:])
        if tag == "svg":
            self.svgs += 1
            # A `<title>` child names the drawing just as well as aria-label,
            # so the verdict waits for the closing tag.
            self.svg_frames.append({"class": a.get("class", "<no class>"),
                                    "hidden": any(self.hidden_stack),
                                    "named": named_svg(a), "title": ""})
        if tag == "script":
            self.scripts += 1
        if tag == "img" and not a.get("src", "").startswith("data:"):
            self.imgs_external += 1
        cls = a.get("class", "")
        for c in cls.split():
            self.classes[c] = self.classes.get(c, 0) + 1
        if tag not in VOID:
            if tag in ("figure", "div", "h1", "h2", "h3", "ul", "ol", "table") \
                    and ("pre" in self.open_stack or "code" in self.open_stack):
                self.nested += 1
            self.open_stack.append(tag)
            self.hidden_stack.append(a.get("aria-hidden") == "true")

    def handle_data(self, data):
        if self.svg_frames and self.open_stack and self.open_stack[-1] == "title":
            self.svg_frames[-1]["title"] += data

    def _finalize_svg(self):
        if not self.svg_frames:
            return
        frame = self.svg_frames.pop()
        if not frame["hidden"] and not frame["named"] and not frame["title"].strip():
            self.unnamed.append(frame["class"])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, [kv for kv in attrs])
        if tag not in VOID and self.open_stack and self.open_stack[-1] == tag:
            self.open_stack.pop()
            self.hidden_stack.pop()
        if tag == "svg":
            self._finalize_svg()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.open_stack and self.open_stack[-1] == tag:
            self.open_stack.pop()
            self.hidden_stack.pop()
        elif tag in self.open_stack:
            while self.open_stack and self.open_stack[-1] != tag:
                dropped = self.open_stack.pop()
                self.hidden_stack.pop()
                if dropped == "svg":
                    self._finalize_svg()
                self.stray.append(dropped)
            if self.open_stack:
                self.open_stack.pop()
                self.hidden_stack.pop()
        else:
            self.stray.append(tag)
        if tag == "svg":
            self._finalize_svg()


def exposed_svgs(html_text: str) -> list[str]:
    """The exposed `<svg>` roots that neither name themselves nor are hidden."""
    p = _Parser()
    p.feed(html_text)
    return p.unnamed


def audit(html_text: str, *, n_units: int, expect_svgs: int | None,
          expect_compass: int | None = None) -> None:
    """Refuse a document that lost a structural promise.

    ``expect_compass`` defaults to one card per unit; a volume that ships
    without guides (`plain_optional`) declares how many units actually carry
    one, so the count is exact rather than waived."""
    p = _Parser()
    p.feed(html_text)

    errors = []
    dupes = {i for i in p.ids if p.ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate ids: {sorted(dupes)[:10]}")
    idset = set(p.ids)
    broken = sorted({h for h in p.hrefs if h and h not in idset})
    if broken:
        errors.append(f"broken anchors ({len(broken)}): {broken[:10]}")
    if p.scripts:
        errors.append(f"{p.scripts} <script> tags — book must be JS-free")
    if p.imgs_external:
        errors.append(f"{p.imgs_external} non-data <img> — offline guarantee")
    if p.classes.get("chapter", 0) + p.classes.get("unit", 0) < n_units:
        errors.append(f"only {p.classes} articles for {n_units} units")
    if expect_svgs is not None and p.svgs < expect_svgs:
        errors.append(f"svg count {p.svgs} < expected {expect_svgs}")
    if p.unnamed:
        errors.append(f"{len(p.unnamed)} exposed <svg> roots carry no name and "
                      f"no aria-hidden — a screen reader announces them as "
                      f"unnamed graphics: {sorted(set(p.unnamed))[:6]}")
    if "mermaid-missing" in p.classes:
        errors.append(f'{p.classes["mermaid-missing"]} missing diagrams')
    if p.stray:
        errors.append(f"unbalanced closing tags: {p.stray[:8]}")
    if p.nested:
        errors.append(f"{p.nested} block elements nested inside <pre>/<code> "
                      "(an unclosed fence is swallowing the text)")
    if "@@MM:" in html_text:
        errors.append(f"{html_text.count('@@MM:')} unresolved mermaid placeholders")
    if "@@ILL:" in html_text:
        errors.append(f"{html_text.count('@@ILL:')} unresolved drawing "
                      "placeholders")
    fence_residue = re.findall(r"^ {0,3}`{3,}", html_text, re.M)
    if fence_residue:
        errors.append(f"{len(fence_residue)} stray markdown fences left in output")
    want_compass = n_units if expect_compass is None else expect_compass
    if p.classes.get("compass", 0) < want_compass:
        errors.append(f'compass cards: {p.classes.get("compass", 0)} < '
                      f'{want_compass}')
    md_links = [u for u in re.findall(r'href="([^"]{0,120}\.md)(?=["#])', html_text)
                if "://" not in u]
    if md_links:
        errors.append(f"{len(md_links)} residual .md links: {md_links[:3]}")
    if errors:
        raise BuildError("audit failed:\n  " + "\n  ".join(errors))
