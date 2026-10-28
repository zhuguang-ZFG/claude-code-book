# -*- coding: utf-8 -*-
"""Parse docs/video/ch01/long-script.md into timed VO chunks with slide keys."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # repo root if under video/ch01/assets/build
# Actually this file will live at video/ch01/assets/build/parse_script.py -> parents[4] = repo
SCRIPT = ROOT / "docs" / "video" / "ch01" / "long-script.md"
OUT = Path(__file__).resolve().parent / "chunks.json"

MARKER_RE = re.compile(r"^\[(ANIM|CODE):([a-z0-9\-]+)\]\s*$")
SECTION_RE = re.compile(r"^##\s+")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
META_LINE_RE = re.compile(r"^>\s*")

def clean_line(line: str) -> str:
    line = BOLD_RE.sub(r"\1", line)
    line = INLINE_CODE_RE.sub(r"\1", line)
    return line.strip()

def is_skip(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("#"):
        return True
    if s.startswith(">"):
        return True
    if s.startswith("---"):
        return True
    if s.startswith("|") and "|" in s[1:]:
        return True
    if s.startswith("```"):
        return True
    return False

def parse(text: str) -> list[dict]:
    lines = text.splitlines()
    chunks: list[dict] = []
    section = "intro"
    section_idx = 0
    slide = "title"
    buf: list[str] = []
    in_code = False

    def flush():
        nonlocal buf
        body = "".join(buf).strip()
        buf = []
        if not body:
            return
        # drop pure whitespace / punctuation-only leftovers
        han = len(re.findall(r"[\u4e00-\u9fff]", body))
        if han < 8 and len(body) < 20:
            return
        chunks.append({
            "id": f"c{len(chunks):03d}",
            "section": section,
            "section_idx": section_idx,
            "slide": slide,
            "text": body,
            "hanzi": han,
        })

    for raw in lines:
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = SECTION_RE.match(raw)
        if m:
            flush()
            section_idx += 1
            section = raw.lstrip("#").strip()
            # map section to default slide
            if section_idx == 1:
                slide = "open"
            elif section_idx == 2:
                slide = "paradigm"
            elif section_idx == 3:
                slide = "architecture"
            elif section_idx == 4:
                slide = "principles"
            elif section_idx == 5:
                slide = "practice"
            elif section_idx == 6:
                slide = "outro"
            else:
                slide = f"sec{section_idx}"
            continue
        mm = MARKER_RE.match(raw.strip())
        if mm:
            flush()
            slide = mm.group(2)
            continue
        if is_skip(raw):
            continue
        cleaned = clean_line(raw)
        if not cleaned:
            continue
        buf.append(cleaned)
        # keep paragraph cohesion: flush on empty next handled by skip; also soft-split long paras later
        if cleaned.endswith(("。", "！", "？", "；")) and sum(len(re.findall(r"[\u4e00-\u9fff]", x)) for x in buf) >= 180:
            flush()

    flush()
    return chunks

def main():
    text = SCRIPT.read_text(encoding="utf-8")
    chunks = parse(text)
    # soft-split any remaining very long chunks
    final = []
    for c in chunks:
        if c["hanzi"] <= 280:
            final.append(c)
            continue
        # split by sentence
        parts = re.split(r"(?<=[。！？])", c["text"])
        acc = ""
        for p in parts:
            if not p.strip():
                continue
            if len(re.findall(r"[\u4e00-\u9fff]", acc + p)) > 220 and acc:
                final.append({**c, "id": f"c{len(final):03d}", "text": acc, "hanzi": len(re.findall(r"[\u4e00-\u9fff]", acc))})
                acc = p
            else:
                acc += p
        if acc.strip():
            final.append({**c, "id": f"c{len(final):03d}", "text": acc, "hanzi": len(re.findall(r"[\u4e00-\u9fff]", acc))})
    # re-id
    for i, c in enumerate(final):
        c["id"] = f"c{i:03d}"
    total_han = sum(c["hanzi"] for c in final)
    OUT.write_text(json.dumps({"chunks": final, "total_hanzi": total_han, "count": len(final)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"chunks={len(final)} total_hanzi={total_han} -> {OUT}")

if __name__ == "__main__":
    main()

