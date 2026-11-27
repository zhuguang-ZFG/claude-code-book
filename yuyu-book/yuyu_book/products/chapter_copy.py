"""Chapter copy shared by the knowledge cards and the sample chapter.

The hook is a quote whose bold lead-in names it. The recap is structural: the
last quote with exactly three circled checks, with or without the legacy
label. Removing a visible slogan from the book must not break derivative pages.
"""
import re
from pathlib import Path

from ..paths import BOOK_DIR

HOOK = {"zh": "开门一句话", "en": "In one line"}
RECAP = {"zh": "三句话带走", "en": "Three sentences to keep"}

_CIRCLED = re.compile(r"[①②③④⑤]")


def _quote_block(unit, marker: str) -> str:
    for section in unit.sections:
        for block in section.blocks:
            if block.kind == "quote" and marker in block.text:
                return block.text
    return ""


def _after_label(text: str, label: str) -> str:
    flat = " ".join(line.lstrip("> ").strip() for line in text.splitlines())
    flat = flat.replace("**", "")
    index = flat.find(label)
    if index < 0:
        return ""
    rest = re.sub(r"^\s*[：:]\s*", "", flat[index + len(label):])
    return rest.strip()


def hook(unit, lang: str) -> str:
    """The one-line door opener that starts the chapter."""
    label = HOOK[lang]
    text = _after_label(_quote_block(unit, label), label)
    if not text:
        raise ValueError(f"{unit.id}: no '{label}' quote in {lang}")
    return text


def recap(unit, lang: str) -> list[str]:
    """The chapter's three closing checks, independent of a visible label."""
    legacy = RECAP[lang]
    for section in reversed(unit.sections):
        for block in reversed(section.blocks):
            if block.kind != "quote":
                continue
            text = _after_label(block.text, legacy) if legacy in block.text \
                else " ".join(line.lstrip("> ").strip() for line in block.text.splitlines())
            items = [part.strip() for part in _CIRCLED.split(text) if part.strip()]
            if len(items) == 3:
                return items
    raise ValueError(f"{unit.id}: expected 3 closing checks in {lang}")


def content_plate(unit_id: str) -> Path | None:
    """The chapter's own content plate, when the drawing shelf has one."""
    plates = sorted(BOOK_DIR.joinpath("illustrations").glob(f"{unit_id}-*.svg"))
    return plates[0] if plates else None
