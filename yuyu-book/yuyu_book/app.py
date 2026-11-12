"""Application services for assembling《御舆》offline editions.

``build.py`` owns argument parsing and process exit; this module owns the
edition pipeline so a different front end can call it without a CLI.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import art, audit, blocks, pages, plain, registry, render
from . import mermaid as mm
from .blocks import ID_RE
from .core import (
    BOOK_DIR,
    HAN_RE,
    INDEX_CN_LETTER,
    REPO_ROOT,
    BuildError,
    expected_ids,
    load_unit,
    read_text,
    unit_stream,
)
from .print_manifest import IndexRow, OutlineEntry, PrintManifest
from .style import CSS, key_mark, page, rut, trace, wheel


def glossary_to_index(manifest: dict) -> list[dict]:
    """Build the subject index from appendix D tables (both languages)."""
    apxd = next((a for a in manifest["appendices"]
                 if a["id"] == "apxd" or a["id"].endswith("-apxd")), None)
    if apxd is None:
        return []
    chapter_ids: dict[int, str] = {}
    for unit, _kind, _part in unit_stream(manifest):
        m = re.search(r"(?:^|-)ch(\d{1,2})$", unit["id"])
        if m:
            chapter_ids[int(m.group(1))] = unit["id"]
    max_chapter = max(chapter_ids) if chapter_ids else 15
    entries: dict[str, dict] = {}

    def add(term: str, lang: str, anchor: str, label: str):
        key = term.strip().lower()
        if not key or len(term) > 64:
            return
        e = entries.setdefault(key, {"key": key, "letter": "A", lang: {"term": term.strip(), "refs": []}})
        for lk in ("zh", "en"):
            e.setdefault(lk, {"term": term.strip(), "refs": []})
        first = re.search(r"[A-Za-z]", term)
        if first:
            e["letter"] = first.group(0).upper()
        refs = e[lang]["refs"]
        if not any(r["anchor"] == anchor for r in refs):
            refs.append({"anchor": anchor, "label": label})

    def add_alias(term: str, anchor: str, label: str):
        """A Chinese headword pointing at the same chapter. Appendix D files
        every term under its English name, which is the right heading for the
        English book and the wrong one for the Chinese: a reader who just met
        自动压缩 in ch 7 does not think to look under A."""
        key = term.strip().lower()
        if not key or len(term) > 64:
            return
        e = entries.setdefault(key, {"key": key, "letter": INDEX_CN_LETTER,
                                     "zh": {"term": term.strip(), "refs": []},
                                     "en": {"term": term.strip(), "refs": []}})
        if not any(r["anchor"] == anchor for r in e["zh"]["refs"]):
            e["zh"]["refs"].append({"anchor": anchor, "label": label})

    rx_zh = re.compile(r"第\s*(\d{1,2})\s*章")
    rx_en = re.compile(r"Chapter\s+(\d{1,2})", re.I)
    for lang in ("zh", "en"):
        if lang not in apxd:
            continue
        text = read_text(REPO_ROOT / apxd[lang])
        fence = None
        for line in text.split("\n"):
            m = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
            if m:
                token, info = m.group(1), m.group(2).strip()
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and not info:
                    fence = None
                continue
            if fence is not None or not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2 or set("".join(cells)) <= set("-: "):
                continue
            term = cells[0].strip("*` ")
            tail = " ".join(cells[2:])
            rx = rx_zh if lang == "zh" else rx_en
            nums = [int(n) for n in rx.findall(tail)
                    if 1 <= int(n) <= max_chapter]
            if not nums or len(term) < 2:
                continue
            for n in nums[:4]:
                add(term, lang, chapter_ids.get(n, f"ch{n:02d}"),
                    f"第 {n} 章" if lang == "zh" else f"Ch {n}")
            if lang == "zh" and len(cells) >= 5:
                # the 中文译名 column, split on the slash that lets one English
                # term carry several translations
                for part in re.split(r"\s*/\s*", cells[1].strip("*` ")):
                    if len(part) >= 2 and HAN_RE.search(part):
                        for n in nums[:4]:
                            add_alias(part, chapter_ids.get(n, f"ch{n:02d}"),
                                      f"第 {n} 章")
    out = sorted(entries.values(), key=lambda e: (e["letter"], e["key"]))
    return [e for e in out if e.get("zh", {}).get("refs")
            or e.get("en", {}).get("refs")]


@dataclass
class Assembly:
    """One book's assembled body, before the page shell is wrapped around it.

    A standalone edition and a volume inside a collected omnibus run the same
    assembly; they differ only in which furniture they emit and which prefix
    the back-matter anchors carry."""
    units: list
    payloads: list[dict]
    body: list[str]
    toc_entries: list[dict]
    outline: list[tuple[int, str, str]]
    rail: list[str]
    idx_entries: list | None
    n_diagrams: int
    expect_svgs: int | None = None


def assemble_book(lang: str, manifest: dict, sources: dict, *,
                  mode: str, browser: str | None, autolink: bool,
                  glosses: dict | None = None,
                  paths: dict | None = None,
                  notes: dict | None = None,
                  plain_layer: bool = True,
                  matter: bool = True,
                  key: str = "") -> Assembly:
    """Render one manifest into body fragments.

    ``matter=False`` drops the cover, imprint, revisions, how-to-read, contents
    and route map: a volume in an omnibus gets one divider from the outer book
    instead. ``key`` prefixes the four back-matter anchors (sources, index,
    principles, keeper notes), which otherwise repeat once per volume."""
    ids = expected_ids(manifest)
    mapping = {i: i for i in ids}
    glosses = glosses or {}
    paths = paths or {}
    notes = notes or {}
    layer = plain.Layer(glosses, lang)

    units = []
    for unit_def, kind, part in unit_stream(manifest):
        u = load_unit(unit_def, kind, lang, REPO_ROOT)
        u.part = part  # type: ignore[attr-defined]
        units.append(u)

    local_targets = {u.path: u.id for u in units}
    for u in units:
        alias = re.search(r"(?:^|-)(ch\d{2}|apx[a-d])$", u.id)
        if alias:
            mapping[alias.group(1)] = u.id

    all_blocks, caps = [], {}
    for u in units:
        caps.update(mm.captions_for(read_text(REPO_ROOT / u.path), u.blocks,
                                    fallback=pages.ui("plate_fallback", lang)))
        all_blocks.extend(u.blocks)
    if mode == "render":
        diagrams = mm.render_all(all_blocks, caps, browser)
        expect_svgs = len(diagrams)
    else:
        diagrams = mm.source_fallback(all_blocks, caps)
        expect_svgs = None

    payloads = []
    for u in units:
        payloads.append(render.render_unit(u, mapping, diagrams=diagrams,
                                           autolink=autolink, gloss=layer,
                                           tiers=paths.get(u.id),
                                           local_targets=local_targets))
    by_id = {p["unit"].id: p for p in payloads}
    layer.check_coverage()

    # ---------------- assemble ----------------
    body: list[str] = []
    if matter:
        body.append(pages.cover(manifest, lang))
        body.append(pages.imprint(manifest, lang))
        rev_name = manifest.get("revisions_registry", "revisions.json")
        loaded = registry.load(rev_name) if rev_name else None
        rev = loaded.get("entries", []) if isinstance(loaded, dict) else []
        body.append(pages.revisions_page(rev, lang))
        body.append(pages.how_to_read(manifest, lang, paths))

    front_id = manifest["front"]["id"]
    toc_entries: list[dict] = [
        {"kind": "row", "anchor": front_id, "no": pages.FRONT_NO,
         "title": by_id[front_id]["unit"].title}]
    outline: list[tuple[int, str, str]] = [
        (1, by_id[front_id]["unit"].display or pages.ui("front", lang),
         front_id)]
    rail = [f'<nav class="rail" aria-label="contents"><p class="rail-title">'
            f'<a href="#toc">{pages.ui("toc", lang)}</a></p>']
    rail.append(f'<a class="rail-map" href="#route-map">'
                f'{key_mark("wheel")}{pages.ui("route_map", lang)}</a>')
    rail.append(f'<a href="#{front_id}">{pages.ui("front", lang)}</a>')

    for p_idx, part in enumerate(manifest["parts"], 1):
        label = f'{part["no"][lang]} · {part["title"][lang]}'
        toc_entries.append({"kind": "part", "anchor": part["id"],
                            "no": pages._ROMAN[p_idx],
                            "title": part["title"][lang]})
        outline.append((1, label, part["id"]))
        rail.append(f'<p class="rail-part">{pages.esc(label)}</p>')
        for unit_def in part["units"]:
            u = by_id[unit_def["id"]]["unit"]
            toc_entries.append({"kind": "row", "anchor": unit_def["id"],
                                "no": u.no_plain, "title": u.title})
            outline.append((2, u.display, unit_def["id"]))
            rail.append(f'<a href="#{unit_def["id"]}">{pages.esc(u.no)} '
                        f'{pages.esc(u.title)}</a>')

    toc_entries.append({"kind": "hr"})
    rail.append(f'<p class="rail-part">{pages.ui("appendix", lang)}</p>')
    for apx in manifest["appendices"]:
        u = by_id[apx["id"]]["unit"]
        toc_entries.append({"kind": "row", "anchor": apx["id"],
                            "no": u.no_plain, "title": u.title})
        outline.append((1, u.display, apx["id"]))
        rail.append(f'<a href="#{apx["id"]}">{pages.esc(u.no)} '
                    f'{pages.esc(u.title)}</a>')

    idx_key = manifest.get("subject_index_registry", "subject-index.json")
    idx_entries: list | None = None
    if idx_key:
        index_path = BOOK_DIR / idx_key
        if index_path.exists():
            loaded_index = registry.load(idx_key)
            idx_entries = loaded_index if isinstance(loaded_index, list) else None

    why_groups = _principle_groups(glosses, units, lang)
    back: list[tuple[str, str]] = ([] if not why_groups
                                   else [(key + "principles",
                                          pages.ui("principles_page", lang))])
    if notes:
        back += [(key + "keeper-notes", pages.ui("notes_page", lang))]
    if sources:
        back += [(key + "sources", pages.ui("sources_page", lang))]
    back += [(key + "subject-index", pages.ui("index_page", lang))]
    for anchor, label in back:
        if anchor == key + "subject-index" and not idx_entries:
            continue
        toc_entries.append({"kind": "part", "anchor": anchor, "no": "",
                            "title": label})
        outline.append((1, label, anchor))
        if matter:
            rail.append(f'<a href="#{anchor}">{pages.esc(label)}</a>')

    if matter:
        body.append(pages.toc_html(toc_entries, lang))
        # the foreword has no chapter number of its own; the wheel at the head
        # of the road wears the same gutter number the contents row shows
        nos = {p["unit"].id: p["unit"].no_plain for p in payloads}
        nos[front_id] = nos[front_id] or pages.FRONT_NO
        body.append(pages.route_map_page(manifest, lang, nos))
    body.append(_article(by_id[front_id], manifest, sources, lang,
                         notes=notes, show_lead=plain_layer))
    for part in manifest["parts"]:
        rows = [(u["id"], by_id[u["id"]]["unit"].no_plain,
                 by_id[u["id"]]["unit"].title)
                for u in part["units"]]
        body.append(pages.part_divider(part, lang,
                                       manifest["parts"].index(part) + 1, rows))
        for unit_def in part["units"]:
            body.append(_article(by_id[unit_def["id"]], manifest, sources,
                                 lang, notes=notes, show_lead=plain_layer))
    for apx in manifest["appendices"]:
        body.append(_article(by_id[apx["id"]], manifest, sources, lang,
                             kind="appendix", notes=notes,
                             show_lead=plain_layer))

    if why_groups:
        body.append(pages.principles_page(why_groups, lang,
                                          anchor=key + "principles"))
    if notes:
        body.append(pages.notes_page(notes, units, lang,
                                     anchor=key + "keeper-notes"))
    if sources:
        body.append(pages.source_registry(sources, lang, anchor=key + "sources"))
    if idx_entries:
        body.append(pages.subject_index_page(idx_entries, lang,
                                             anchor=key + "subject-index"))

    n_diagrams = sum(p["n_diagrams"] for p in payloads)
    if matter:
        foot = pages.ui("diagrams", lang)
        body.append(f'<footer class="colophon">{wheel(34)}'
                    f'{pages.esc(manifest["title"][lang])} · v'
                    f'{pages.esc(manifest["version"])} · {n_diagrams} {foot}'
                    f'</footer>')
    return Assembly(units=units, payloads=payloads, body=body,
                    toc_entries=toc_entries, outline=outline, rail=rail,
                    idx_entries=idx_entries, n_diagrams=n_diagrams,
                    expect_svgs=expect_svgs)


def _audit(html_text: str, *, units, payloads, part_ids: list[str],
           notes: dict, lang: str, plain_layer: bool,
           expect_svgs: int | None, lead_units: int | None = None,
           guides: dict | None = None) -> dict:
    """Prove every drawn thing and every plain-layer mark reached the page."""
    audit.audit(html_text, n_units=len(units), expect_svgs=expect_svgs,
                expect_compass=sum(1 for u in units
                                   if (guides or {}).get(u.id)))

    # the dashed marks and the chapter panels come from the same hit list; if
    # they ever diverge, paper readers would chase underlines that are nowhere
    # explained (there is no hover in print)
    n_marks = html_text.count('<span class="gloss"')
    n_rows = html_text.count('<li class="nt-row">')
    n_chips = html_text.count('<span class="sec-tier')
    n_emblems = html_text.count('<span class="ch-emblem"')
    ids = [p["unit"].id for p in payloads]
    want_emblems = len(ids) - len(art.missing(ids))
    n_heads = html_text.count('<div class="pd-art"')
    want_heads = len(part_ids) - len(art.missing(part_ids))
    if n_emblems != want_emblems or n_heads != want_heads:
        raise BuildError(f"{n_emblems}/{want_emblems} emblems and "
                         f"{n_heads}/{want_heads} headpieces reached the book "
                         "— every drawing must reach its page")
    if n_marks != n_rows:
        raise BuildError(f"plain layer: {n_marks} dashed marks but {n_rows} "
                         f"panel rows — every mark must be restated on paper")
    n_keep = html_text.count('<div class="keeper">')
    n_kn = html_text.count('<li class="kn-row">')
    want_keep = sum(1 for u in units if (notes.get(u.id) or {}).get(lang))
    if notes and (n_keep != want_keep or n_kn != want_keep):
        raise BuildError(f"keeper layer: {n_keep} chapter notes and {n_kn} "
                         f"collection rows for {want_keep} authored — the "
                         "postman must sit at every rut and be listed once")
    n_lead = html_text.count('<div class="lead-band"')
    want_lead = (len(units) if lead_units is None else lead_units) \
        if plain_layer else 0
    if n_lead != want_lead:
        raise BuildError(f"plain layer: {n_lead} lead bands for {want_lead} "
                         "units — the band belongs to the layer, so --no-plain "
                         "has to drop it with everything else")
    return {"marks": n_marks, "chips": n_chips, "emblems": n_emblems,
            "heads": n_heads, "keeper": n_keep, "lead": n_lead}


def build_edition(lang: str, manifest: dict, sources: dict, *,
                  mode: str, browser: str | None, autolink: bool,
                  out_dir: Path, do_pdf: bool, edge: str | None,
                  glosses: dict | None = None,
                  paths: dict | None = None,
                  notes: dict | None = None,
                  plain_layer: bool = True) -> Path:
    asm = assemble_book(lang, manifest, sources, mode=mode, browser=browser,
                        autolink=autolink, glosses=glosses, paths=paths,
                        notes=notes, plain_layer=plain_layer, matter=True)
    # the break points go in here, over the whole assembled book rather than
    # unit by unit: the front and back matter never runs the unit pipeline, and
    # a revision note quoting getFeatureValue_CACHED_MAY_BE_STALE pushed the
    # document 37px past a 390px screen. This is also the last pass that reads
    # the text as words — term matching, the outline and the cross-references
    # have all already seen it uncut.
    body_html = render.soften_long_names("\n".join(asm.body))
    product = manifest.get("product", "book")
    body_class = f"lang-{lang}"
    if product in {"opencode", "deepseek", "hermes", "codex"}:
        body_class += f" agent-book agent-{product}"
    html_text = page(lang, f'{manifest["title"][lang]} — {manifest["author"]}',
                     CSS, body_class, body_html,
                     "\n".join(asm.rail) + "</nav>", "")
    counts = _audit(html_text, units=asm.units, payloads=asm.payloads,
                    part_ids=[f'part-{p["id"]}' for p in manifest["parts"]],
                    notes=notes or {}, lang=lang, plain_layer=plain_layer,
                    lead_units=sum(
                        1 for g in (manifest.get("guides") or {}).values()
                        if (g.get("plain") or {}).get(lang)),
                    guides=manifest.get("guides"),
                    expect_svgs=asm.expect_svgs)

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = manifest.get("output_prefix") or "yuyu-agent-harness"
    out = out_dir / f"{prefix}-{lang}.html"
    out.write_text(html_text, encoding="utf-8")
    stats = (f"{out.name}: {out.stat().st_size / 1e6:.1f} MB, "
             f"{len(asm.units)} units, {asm.n_diagrams} plates, "
             f"{sum(len(p['external']) for p in asm.payloads)} cited links, "
             f"{counts['marks']} glosses, {counts['lead']} lead bands, "
             f"{counts['chips']} tier chips, {counts['emblems']} emblems, "
             f"{counts['heads']} headpieces, {counts['keeper']} keeper notes")
    print("  " + stats)
    if do_pdf:
        from yuyu_book import pdf
        pmeta = pdf_meta(manifest, asm.outline, asm.toc_entries, lang,
                         asm.idx_entries)
        # paper has no hover and no locator chip that means anything without a
        # sheet number, so the index rows get their folios from a measuring
        # print and the book is printed again with the numbers in place
        folios = {}
        if pmeta.index_rows:
            dest = pdf.measure(out,
                               sorted({r.anchor for r in pmeta.index_rows}),
                               edge or browser)
            folios = {a: dest[a] + 1 for a in dest}
            out.write_text(pages.fill_index_folios(html_text, folios),
                           encoding="utf-8")
        p = pdf.build_pdf(out, pmeta, edge or browser, folios=folios)
        print(f"  {p.name}: {p.stat().st_size / 1e6:.1f} MB, "
              f"{pdf.sheet_count(p)} pages, {len(asm.outline)} bookmarks, "
              f"{len(folios)} index folios")
    return out


def build_collected(lang: str, spec: dict, volumes, *,
                    mode: str, browser: str | None, autolink: bool,
                    out_dir: Path, do_pdf: bool, edge: str | None,
                    plain_layer: bool = True) -> Path:
    """Bind the volumes into one document, one volume per door.

    Each volume keeps its own front matter, part dividers, apparatus and
    numbering; the collection adds the volume level and one contents page that
    opens on volumes rather than chapters."""
    body: list[str] = []
    body.append(pages.cover(spec, lang))
    body.append(pages.imprint(spec, lang))
    toc_entries: list[dict] = []
    outline: list[tuple[int, str, str]] = []
    rail = [f'<nav class="rail" aria-label="contents"><p class="rail-title">'
            f'<a href="#toc">{pages.ui("toc", lang)}</a></p>']
    units_all, payloads_all = [], []
    part_ids: list[str] = []
    notes_all: dict = {}
    index_rows: list = []
    n_diagrams = 0
    svgs = 0
    front_anchor = ""
    for n, vol in enumerate(volumes, 1):
        asm = assemble_book(lang, vol.manifest, vol.sources, mode=mode,
                            browser=browser, autolink=autolink,
                            glosses=vol.glosses, paths=vol.paths,
                            notes=vol.notes, plain_layer=plain_layer,
                            matter=False, key=vol.id + "-")
        if not front_anchor:
            front_anchor = vol.manifest["front"]["id"]
        for row in vol.manifest["parts"]:
            part_ids.append(f'part-{row["id"]}')
        units_all.extend(asm.units)
        payloads_all.extend(asm.payloads)
        notes_all.update(vol.notes)
        n_diagrams += asm.n_diagrams
        svgs += asm.expect_svgs or 0
        if asm.idx_entries:
            index_rows += [(e[lang]["term"], e[lang]["refs"][0]["anchor"])
                           for e in asm.idx_entries if e[lang]["refs"]]

        toc_entries.append({"kind": "part", "anchor": vol.id,
                            "no": vol.no[lang], "title": vol.title[lang]})
        outline.append((1, vol.label(lang), vol.id))
        rail.append(f'<p class="rail-part">{pages.esc(vol.label(lang))}</p>')
        skip = {vol.id + name for name in
                ("principles", "keeper-notes", "sources", "subject-index")}
        for entry in asm.toc_entries:
            if entry.get("anchor") in skip:
                continue
            toc_entries.append(entry)
            if entry["kind"] in ("part", "row"):
                rail.append(f'<a href="#{entry["anchor"]}">'
                            f'{pages.esc(entry["title"])}</a>')
        for level, label, anchor in asm.outline:
            if anchor in skip:
                continue
            outline.append((level + 1, label, anchor))

        rows = [(p["id"], p["no"][lang], p["title"][lang])
                for p in vol.manifest["parts"]]
        body.append(pages.volume_divider(
            {"id": vol.id, "no": vol.no, "title": vol.title,
             "motto": {"zh": vol.manifest.get("subtitle", {}).get(lang, "")},
             "goal": {}}, lang, n, rows))
        product = vol.manifest.get("product", "book")
        extra = (f" agent-book agent-{product}"
                 if product in {"opencode", "deepseek", "hermes", "codex"} else "")
        body.append(f'<section class="volume{extra}" data-volume="{vol.id}">')
        body.extend(asm.body)
        body.append("</section>")

    foot = pages.ui("diagrams", lang)
    body.append(f'<footer class="colophon">{wheel(34)}'
                f'{pages.esc(spec["title"][lang])} · v'
                f'{pages.esc(spec["version"])} · {len(volumes)} 卷 · '
                f'{len(units_all)} units · {n_diagrams} {foot}</footer>')
    body.insert(2, pages.toc_html(toc_entries, lang))

    body_html = render.soften_long_names("\n".join(body))
    html_text = page(lang, f'{spec["title"][lang]} — {spec["author"]}',
                     CSS, f"lang-{lang}", body_html,
                     "\n".join(rail) + "</nav>", "")
    guide_units = sum(
        1 for vol in volumes
        for guide in (vol.manifest.get("guides") or {}).values()
        if (guide.get("plain") or {}).get(lang))
    # a volume may ship no guides at all (`plain_optional`); the compass count
    # is then the number of units that really carry one, not the unit total
    guides_all = {uid: guide for vol in volumes
                  for uid, guide in (vol.manifest.get("guides") or {}).items()}
    counts = _audit(html_text, units=units_all, payloads=payloads_all,
                    part_ids=part_ids, notes=notes_all, lang=lang,
                    plain_layer=plain_layer, lead_units=guide_units,
                    guides=guides_all,
                    expect_svgs=svgs if mode == "render" else None)

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = spec.get("output_prefix") or "yuyu-collected"
    out = out_dir / f"{prefix}-{lang}.html"
    out.write_text(html_text, encoding="utf-8")
    print(f"  {out.name}: {out.stat().st_size / 1e6:.1f} MB, "
          f"{len(volumes)} volumes, {len(units_all)} units, "
          f"{n_diagrams} plates, {counts['marks']} glosses, "
          f"{counts['lead']} lead bands, {counts['keeper']} keeper notes")
    if do_pdf:
        from yuyu_book import pdf
        pmeta = PrintManifest(
            outline=tuple(OutlineEntry(*entry) for entry in outline),
            toc_rows=tuple(e["anchor"] for e in toc_entries
                           if e["kind"] in ("row", "part")),
            index_rows=tuple(IndexRow(term, anchor)
                             for term, anchor in index_rows),
            toc_title=pages.ui("toc", lang),
            title=spec["title"][lang],
            subtitle=spec["subtitle"][lang],
            author=spec["author"],
            keywords=f'v{spec["version"]} {spec["date"]}',
            lang=lang,
            front_anchor=front_anchor)
        folios = {}
        if pmeta.index_rows:
            dest = pdf.measure(out,
                               sorted({r.anchor for r in pmeta.index_rows}),
                               edge or browser)
            folios = {a: dest[a] + 1 for a in dest}
            out.write_text(pages.fill_index_folios(html_text, folios),
                           encoding="utf-8")
        p = pdf.build_pdf(out, pmeta, edge or browser, folios=folios)
        print(f"  {p.name}: {p.stat().st_size / 1e6:.1f} MB, "
              f"{pdf.sheet_count(p)} pages, {len(outline)} bookmarks, "
              f"{len(folios)} index folios")
    return out


def pdf_meta(manifest, outline, toc_entries, lang, idx_entries=()) -> PrintManifest:
    """Everything the PDF pass needs that the HTML cannot say for itself:
    bookmarks, the contents rows it must number, and the index rows it must
    number once the measuring print says where each unit lands. Running heads
    are derived from the outline, so a part divider cannot be left out of the
    head map without also disappearing from the bookmark tree."""
    return PrintManifest(
        # every bookmark opens a section, parts included: leaving the part
        # dividers out made those pages wear the previous chapter's head
        outline=tuple(OutlineEntry(*entry) for entry in outline),
        toc_rows=tuple(e["anchor"] for e in toc_entries
                       if e["kind"] in ("row", "part")),
        # a folio is written into the row it belongs to, keyed by the anchor
        # the row links to — the terms are here so a test can prove this list
        # is the index in the order the page puts it down: an entry this
        # edition has no chip for prints no row and gets no folio
        index_rows=tuple(IndexRow(e[lang]["term"],
                                  e[lang]["refs"][0]["anchor"])
                         for e in (idx_entries or ()) if e[lang]["refs"]),
        toc_title=pages.ui("toc", lang),
        title=manifest["title"][lang],
        subtitle=manifest["subtitle"][lang],
        author=manifest["author"],
        keywords=f'v{manifest["version"]} {manifest["date"]}',
        lang=lang,
        front_anchor=manifest["front"]["id"])


def _principle_groups(glosses: dict, units, lang: str) -> list[dict]:
    """The why lines, filed under the chapter that argues for them.

    A term's own chapter is decided by its `why_evidence` pointer rather than by
    where the word first appears: the reason lives where the reason is given,
    which is not always the first mention.
    """
    by_path = {u.path: u for u in units}
    order = {u.id: n for n, u in enumerate(units)}
    block_unit = {}
    for u in units:
        for block in blocks.parse_blocks(read_text(REPO_ROOT / u.path),
                                         u.id, u.lang):
            if block.block_id:
                block_unit[block.block_id] = u
    groups: dict[str, dict] = {}
    for gid, g in sorted(glosses.items(), key=lambda kv: kv[1]["term"][lang]):
        why = (g.get("why") or {}).get(lang)
        if not why:
            continue
        unit = None
        for ref in g.get("why_evidence") or []:
            if ID_RE.match(str(ref)):
                unit = block_unit.get(str(ref))
            else:
                unit = by_path.get(str(ref).rsplit(":", 1)[0]
                                   .replace("\\", "/"))
            if unit is not None:
                break
        if unit is None:
            raise BuildError(f"gloss {gid}: why_evidence points outside the book")
        groups.setdefault(unit.id, {"anchor": unit.anchor,
                                    "head": unit.display, "terms": []})
        groups[unit.id]["terms"].append(
            {"term": g["term"][lang], "why": why,
             "analogy": (g.get("analogy") or {}).get(lang, "")})
    return [groups[k] for k in sorted(groups, key=lambda k: order.get(k, 99))]


def _article(payload, manifest, sources, lang, kind=None, notes=None,
             show_lead=True):
    u = payload["unit"]
    kind = kind or u.kind
    guide = (manifest.get("guides") or {}).get(u.id, {})
    part = getattr(u, "part", None)
    eyebrow = []
    if part:
        eyebrow.append(f'{part["no"][lang]} {part["title"][lang]}')
    if kind != "front":
        eyebrow.append(u.eyebrow)
    label = u.display
    if kind == "chapter" and u.no:
        digits = "".join(c for c in u.no if c.isdigit())
        seal = f'<span class="ch-seal" aria-hidden="true">{digits.zfill(2)}</span>'
        label = u.title
    elif kind == "appendix":
        seal = f'<span class="ch-seal" aria-hidden="true">{u.id[-1].upper()}</span>'
        label = u.title
    else:
        seal = ""
    # the emblem rides at the end of the head row, so the top of every unit is
    # title + seal + drawing rather than a wide empty band over the sheet
    emblem = art.emblem(u.id)
    title_html = (f'{seal}<h1 class="ch-title">{pages.esc(label)}</h1>{emblem}')
    if seal or emblem:
        title_html = f'<div class="ch-head-row">{title_html}</div>'
    # the foreword is the one unit whose number-free title is the eyebrow text,
    # so it renders no eyebrow at all rather than "前言" twice above the H1
    eyebrow_html = (f'<p class="eyebrow">{pages.esc(" · ".join(eyebrow))}</p>'
                    if eyebrow else "")
    # the head closes on a drawn wire rather than a ruled line: same job, and it
    # carries the unit id so no two chapters run the same trace
    head = (f'<header class="chapter-head">{eyebrow_html}{title_html}'
            f'{trace(u.id)}</header>')
    cls = "chapter" if kind == "chapter" else ("unit" if kind == "front"
                                               else "unit appendix")
    # the band's text lives in the manifest, not in the glossary, so it is the
    # one device the empty layer cannot swallow by itself
    lead = pages.lead_band(guide, lang) if show_lead else ""
    compass = pages.compass(u, guide, sources, lang) if guide else ""
    panel = pages.new_terms_panel(payload.get("new_terms") or [], lang, kind)
    # keep rendered body but drop its own H1 (re-synthesised above)
    body_html = re.sub(r"<h1 [^>]*>.*?</h1>|<h1>.*?</h1>", "", payload["html"],
                       count=1)
    # the ruts go inside the body, glued to the block they close: left as a
    # trailing sibling they can fall alone onto a sheet the next unit's forced
    # page break then empties
    keeper = ((notes or {}).get(u.id) or {}).get(lang)
    closer = (f'<div class="keeper">{art.keeper()}'
              f'<p class="keeper-note">{pages.esc(keeper)}</p></div>'
              if keeper else "") + rut(u.id)
    body_html = render.glue_closer(body_html, closer)
    # the card of new terms trails the chapter rather than opening it: it is
    # the tallest block on the opener, and ahead of the prose it spent the
    # whole first sheet on furniture so that a chapter's first sentence landed
    # on page two. The ruts stay the last ink of the argument; the card is the
    # apparatus that closes it.
    return (f'<article class="{cls}" id="{u.id}">{head}'
            f'{lead}{compass}<div class="chapter-body">{body_html}{panel}</div>'
            f'</article>')

