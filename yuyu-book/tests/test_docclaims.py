"""Every count the repository docs claim, recomputed from the files they describe.

These numbers move whenever the manuscript or a registry moves, and they rot
silently: one audit found the README describing a 100-entry glossary beside a
file holding 122 entries, a STRUCTURE row still saying "24 份图" after the
twenty-fifth drawing shipped, and a doc row promising that `extra` terms reach
the chapter panel when the panel has always been the marked set. Each claim is
one regex against one doc line, checked against a value computed from data, so
a reworded sentence fails as "claim missing" instead of passing vacuously.
"""
import re
import sys
import unittest
from pathlib import Path

if not __package__:  # direct run: see tests/__init__.py for the real bootstrap
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import plain
from yuyu_book.core import (BOOK_DIR, REPO_ROOT, extract_mermaid, load_json,
                            read_text, unit_stream)
from yuyu_book.plain import prose_lines

SEP_ROW = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+\s*:?\s*$")
ASCII = re.compile(r"[A-Za-z]")


class Data(unittest.TestCase):
    """Counts taken straight from the manuscript and the registries."""

    def setUp(self):
        self.manifest = load_json(BOOK_DIR / "manifest.json")
        self.units = [(u, k) for u, k, _p in unit_stream(self.manifest)]
        self.glosses = load_json(BOOK_DIR / "glosses.json")

    def unit_path(self, lang: str) -> list[str]:
        return [u[lang] for u, _k in self.units]

    def plates(self, lang: str) -> int:
        n = 0
        for rel in self.unit_path(lang):
            _body, blocks, _langs = extract_mermaid(read_text(REPO_ROOT / rel),
                                                    rel)
            n += len(blocks)
        return n

    def glossary_rows(self, lang: str) -> int:
        """Rows of the appendix D tables, headers excluded.

        Fence-aware: appendix D opens with a mermaid concept map whose
        `subgraph 核心架构["核心架构概念"]` lines look table-ish to a plain scan.
        """
        apxd = next(a for a in self.manifest["appendices"] if a["id"] == "apxd")
        lines = prose_lines(read_text(REPO_ROOT / apxd[lang]))
        order = sorted(lines)
        rows = 0
        for i, ln in enumerate(order):
            s = lines[ln].strip()
            if not s.startswith("|") or SEP_ROW.match(s):
                continue
            if i + 1 < len(order) and SEP_ROW.match(lines[order[i + 1]].strip()):
                continue          # this is a header row
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 5 or not ASCII.search(cells[0]):
                continue
            rows += 1
        return rows

    def drawings(self) -> int:
        return len(list((BOOK_DIR / "illustrations").glob("*.svg")))

    def index(self) -> list[dict]:
        return load_json(BOOK_DIR / "subject-index.json")

    def kinds(self) -> dict:
        out = {}
        for s in load_json(BOOK_DIR / "sources.json").values():
            out[s["kind"]] = out.get(s["kind"], 0) + 1
        return out

    def core_terms(self) -> int:
        return sum(1 for g in self.glosses.values()
                   if g.get("priority") == "core")

    def why_terms(self) -> int:
        return sum(1 for g in self.glosses.values()
                   if (g.get("why") or {}).get("zh"))

    def suite(self) -> int:
        loader = unittest.TestLoader()
        s = loader.discover(str(BOOK_DIR / "tests"))
        if loader.errors:
            raise AssertionError(f"discovery failed: {loader.errors[:2]}")
        return s.countTestCases()


class ShippedCounts(Data):
    """The docs quote these; the data is the only authority."""

    def setUp(self):
        super().setUp()
        plates_zh, plates_en = self.plates("zh"), self.plates("en")
        src = str(len(load_json(BOOK_DIR / "sources.json")))
        g = str(len(self.glosses))
        d = str(self.drawings())
        self.claims = [
            ("README.md", r"\*\*术语表\*\* — (\d+) 条中英对照术语",
             [str(self.glossary_rows("zh"))]),
            ("en/README.md", r"\*\*Glossary\*\* — (\d+) bilingual term",
             [str(self.glossary_rows("en"))]),
            ("STRUCTURE.md", r"术语白话注，当前 (\d+) 条（(\d+) 个 core",
             [g, str(self.core_terms())]),
            # the reason layer is quoted in all three docs, and its size is a
            # fact about glosses.json rather than about the core count
            ("STRUCTURE.md", r"`why` \+ `why_evidence`（原理句与它的出处，"
                             r"(\d+) 个 core 各配一对",
             [str(self.core_terms())]),
            ("README.md", r"(\d+) 个主干术语的原理", [str(self.why_terms())]),
            ("en/README.md", r"the (\d+) core terms' reasons",
             [str(self.why_terms())]),
            ("STRUCTURE.md", r"主题索引（生成物，当前 (\d+) 个词条 = "
                             r"(\d+) 条英文原名 \+ (\d+) 条中文译名）",
             [str(len(self.index())), str(len([e for e in self.index()
                                               if e["letter"] != "中"])),
              str(len([e for e in self.index() if e["letter"] == "中"]))]),
            ("README.md", r"全书另有 (\d+) 份手写线描图——扉页一幅四马古车、"
                         r"(\d+) 枚章徽配在章名右侧、(\d+) 幅题刻",
             [d, str(len(self.units)), str(len(self.manifest["parts"]))]),
            ("STRUCTURE.md", r"\| `illustrations/` \| (\d+) 份手写 SVG",
             [d]),
            ("CREDITS.md", r"扉页一幅车图（共 (\d+) 份", [d]),
            ("STRUCTURE.md", r"以来源 id 为键的 (\d+) 条登记", [src]),
            ("CREDITS.md", r"sources\.json\)（(\d+) 条）", [src]),
            # the registry is also quoted by family, in a sentence and in four
            # section headings; both drift the moment one entry is added
            ("STRUCTURE.md", r"kind 分布：`docs` (\d+)、`github` (\d+)、"
                             r"`blog` (\d+)、`spec` (\d+)、`npm` (\d+)、"
                             r"`community` (\d+)；(\d+) 条全部被",
             [str(self.kinds()["docs"]), str(self.kinds()["github"]),
              str(self.kinds()["blog"]), str(self.kinds()["spec"]),
              str(self.kinds()["npm"]), str(self.kinds()["community"]), src]),
            ("CREDITS.md", r"## 二、官方文档（(\d+) 条）",
             [str(self.kinds()["docs"])]),
            ("CREDITS.md", r"## 三、GitHub 仓库与钉版（(\d+) 条）",
             [str(self.kinds()["github"])]),
            ("CREDITS.md", r"## 四、协议规范与工程博客（(\d+) 条）",
             [str(self.kinds()["spec"] + self.kinds()["blog"])]),
            ("CREDITS.md", r"## 五、npm（(\d+) 条）",
             [str(self.kinds()["npm"])]),
            ("README.md", r"每版 (\d+) 张（中英合计 (\d+)）",
             [str(plates_zh), str(plates_zh + plates_en)]),
            ("STRUCTURE.md", r"中英文各有 (\d+) 个 Mermaid 围栏（合计 (\d+)）",
             [str(plates_zh), str(plates_zh + plates_en)]),
            ("CREDITS.md", r"全书 (\d+) 张图（中英各 (\d+)）",
             [str(plates_zh + plates_en), str(plates_en)]),
            ("en/README.md", r"All (\d+) diagrams per edition \((\d+) across "
                            r"both\)", [str(plates_en),
                                        str(plates_zh + plates_en)]),
            ("README.md", r"`yuyu-book/` 把 (\d+) 个单元装配成",
             [str(len(self.units))]),
        ]

    def test_doc_counts_match_the_data(self):
        bad = []
        for doc, rx, want in self.claims:
            m = re.compile(rx, re.M).search(read_text(REPO_ROOT / doc))
            if not m:
                bad.append(f"{doc}: nothing matches {rx!r} — the sentence was "
                           "reworded; re-pin the claim if its numbers are "
                           "still facts")
                continue
            got = list(m.groups())
            if got != want:
                bad.append(f"{doc}: claims {got}, the data says {want}")
        self.assertEqual(bad, [], "\n  " + "\n  ".join(bad))

    def test_the_revision_note_closes_with_the_suite_it_shipped(self):
        """The newest note quotes the builder's own test count; the note is
        read as the version's summary, so the figure has to be current."""
        # the ledger is newest-first: the top entry is the version shipping
        entry = load_json(BOOK_DIR / "revisions.json")["entries"][0]
        want = str(self.suite())
        for lang, rx in (("zh", r"构建器测试 (\d+) 项全绿"),
                         ("en", r"(\d+) builder tests green")):
            m = re.search(rx, entry[lang][-1])
            self.assertIsNotNone(
                m, f"revisions.{lang}: the last note no longer states the "
                   "suite size — re-pin it")
            self.assertEqual(m.group(1), want,
                             f"revisions.{lang}: the note says {m.group(1)}, "
                             f"discovery says {want}")

    def test_extra_terms_stay_off_the_prose_and_the_panel(self):
        """STRUCTURE promises `extra` reaches neither the dashes nor the chapter
        panel; the panel is built from the marks, so one flag covers both."""
        leaked = [gid for gid, g in self.glosses.items()
                  if g.get("priority") == "extra" and plain.marks(g)]
        self.assertEqual(leaked, [],
                         f"marked but registered as extra: {leaked}")
        for lang in ("zh", "en"):
            self.assertTrue(plain.Matcher(self.glosses, lang).rx,
                            f"no markable form in {lang}")


if __name__ == "__main__":
    unittest.main()
