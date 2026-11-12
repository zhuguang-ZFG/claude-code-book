"""A collected edition: several finished books bound as volumes of one book.

Each volume keeps its own manifest, sources, plain-language registries and
apparatus. The collection only adds the level above them — a volume door, a
volume-level contents, and one document that carries them in order.

Manifest ids are already unique across products (`front`/`p1`/`apxa` vs
`codex-front`/`codex-p1`/`codex-apxa`, `ch01` vs `omp-ch01`), so the collection
does not rename anything upstream of the furniture. The four back-matter
anchors each volume repeats (`sources`, `subject-index`, `principles`,
`keeper-notes`) are scoped by the caller with a volume key.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import plain
from .config import load_configs
from .core import BuildError


@dataclass
class Volume:
    id: str
    no: dict[str, str]
    title: dict[str, str]
    manifest: dict
    sources: dict
    glosses: dict
    paths: dict
    notes: dict

    def label(self, lang: str) -> str:
        return f'{self.no[lang]} · {self.title[lang]}'


def load_collection(spec: dict) -> list[Volume]:
    """Load every volume in manifest order and refuse a shared anchor."""
    volumes: list[Volume] = []
    for raw in spec.get("volumes") or ():
        manifest, sources = load_configs(raw["manifest"], raw["sources"])
        glosses, paths = plain.load_plain(manifest)
        notes = plain.load_notes(manifest)
        volumes.append(Volume(id=raw["id"], no=raw["no"], title=raw["title"],
                              manifest=manifest, sources=sources,
                              glosses=glosses, paths=paths, notes=notes))
    if not volumes:
        raise BuildError("collected: the manifest declares no volumes")
    seen_volumes: set[str] = set()
    seen_anchors: dict[str, str] = {}
    for volume in volumes:
        if volume.id in seen_volumes:
            raise BuildError(f"collected: duplicate volume id {volume.id!r}")
        seen_volumes.add(volume.id)
        manifest = volume.manifest
        anchors = [manifest["front"]["id"]]
        anchors += [u["id"] for part in manifest["parts"] for u in part["units"]]
        anchors += [p["id"] for p in manifest["parts"]]
        anchors += [a["id"] for a in manifest["appendices"]]
        for anchor in anchors:
            other = seen_anchors.get(anchor)
            if other is not None:
                raise BuildError(
                    f"collected: anchor {anchor!r} appears in both {other!r} "
                    f"and {volume.id!r} — two volumes would share a page")
            seen_anchors[anchor] = volume.id
    return volumes
