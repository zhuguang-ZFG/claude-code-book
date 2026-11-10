"""Karaoke caption and watermark render inputs for the video factory.

Ported verbatim from the ch01 dense-v4 production script so the pipeline
regenerates the exact render inputs the shipped videos were burned with.
Given the recorded cue track, the generated pages are byte-identical to the
legacy artifacts; the legacy files therefore become witnesses rather than
build inputs.
"""
from __future__ import annotations

import html
from pathlib import Path

FONT = """
@font-face { font-family: 'Noto Sans SC'; src: local('Noto Sans SC'), local('NotoSansSC-Regular'), local('Microsoft YaHei'); font-weight: 100 900; }
@font-face { font-family: 'Microsoft YaHei'; src: local('Microsoft YaHei'), local('Microsoft YaHei UI'); }
"""


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def tokenize_zh(text: str) -> list[str]:
    """Split for karaoke: CJK char-by-char; latin/digit runs kept together."""
    tokens = []
    buf = []
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf":
            if buf:
                tokens.append("".join(buf))
                buf = []
            tokens.append(ch)
        elif ch.isspace():
            if buf:
                tokens.append("".join(buf))
                buf = []
            if tokens and not tokens[-1].endswith(" "):
                # soft space marker kept as own token for layout
                tokens.append(" ")
        else:
            buf.append(ch)
    if buf:
        tokens.append("".join(buf))
    return [token for token in tokens if token != ""]


def karaoke_captions_html(cues: list[dict], total_s: float) -> str:
    """The karaoke caption page burned into the shipped long renders."""
    parts = []
    anim = []
    for i, cue in enumerate(cues):
        text = (cue.get("text") or "").strip()
        if not text:
            continue
        start = max(0.1, float(cue["start"]))
        end = float(cue["end"])
        if end <= start:
            end = start + 1.2
        cid = f"c{i}"
        dur = end - start
        toks = tokenize_zh(text)
        if not toks:
            continue
        # weight: CJK=1, latin run=max(1,len/2), space=0.3
        weights = []
        for tok in toks:
            if tok == " ":
                weights.append(0.35)
            elif all("\u4e00" <= c <= "\u9fff" or "\u3400" <= c <= "\u4dbf"
                     for c in tok):
                weights.append(1.0)
            else:
                weights.append(max(1.0, len(tok) * 0.45))
        tw = sum(weights) or 1.0
        # leave tiny head/tail so fade works
        usable = max(0.35, dur - 0.22)
        spans = []
        cursor = 0.0
        local_anim = [
            f'tl.set("#{cid}-in", {{opacity:0}}, 0);',
            f'tl.to("#{cid}-in", {{opacity:1, duration:0.10}}, {start:.3f});',
            f'tl.to("#{cid}-in", {{opacity:0, duration:0.12}}, '
            f'{max(start, end - 0.12):.3f});',
        ]
        for ki, tok in enumerate(toks):
            kid = f"{cid}-k{ki}"
            spans.append(f'<span class="kw" id="{kid}">{esc(tok)}</span>')
            t_on = start + 0.08 + usable * (cursor / tw)
            step = max(0.045, usable * (weights[ki] / tw) * 0.85)
            local_anim.append(
                f'tl.fromTo("#{kid}", {{color:"#7a8799"}}, '
                f'{{color:"#ffe08a", duration:{step:.3f}, ease:"none"}}, '
                f'{t_on:.3f});'
            )
            cursor += weights[ki]
        parts.append(
            f'<div id="{cid}" class="cap-clip clip" data-start="{start:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="10">'
            f'<div class="cap-inner" id="{cid}-in">{"".join(spans)}</div></div>'
        )
        anim.extend(local_anim)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>{FONT}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:transparent}}
.cap-clip{{position:absolute;left:0;right:0;bottom:72px;display:flex;justify-content:center;pointer-events:none;z-index:55}}
.cap-inner{{max-width:1600px;padding:14px 28px;border-radius:10px;background:rgba(8,10,14,.78);color:#7a8799;font-size:34px;line-height:1.5;text-align:center;opacity:0;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;text-shadow:0 2px 8px rgba(0,0,0,.55);white-space:pre-wrap}}
.kw{{display:inline;color:#7a8799;transition:none}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-track-kind="captions" data-start="0" data-duration="{total_s:.3f}" data-width="1920" data-height="1080" data-fps="30" style="position:relative;width:1920px;height:1080px;background:transparent">
{"".join(parts)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(anim)}
window.__timelines["captions-zh"] = tl;
</script></body></html>"""


def short_captions_html(cues: list[dict], total_s: float,
                        fps: int = 30) -> str:
    """The karaoke pill caption page burned into the shipped short renders.

    Ported verbatim from the shipped short production script (vertical
    1080x1920 layout, one phrase pill at a time).
    """
    lines = []
    for i, cue in enumerate(cues):
        lines.append(f'<div class="cap" id="cap{i}" style="opacity:0">'
                     f'{esc(cue.get("text") or "")}</div>')
    tl_lines = []
    for i, cue in enumerate(cues):
        start = float(cue["start"])
        end = float(cue["end"])
        tl_lines.append(f'tl.set("#cap{i}", {{opacity:0}}, 0);')
        tl_lines.append(
            f'tl.fromTo("#cap{i}", {{opacity:0, y:18, scale:0.92}}, '
            f'{{opacity:1, y:0, scale:1, duration:0.12}}, {start:.3f});'
        )
        tl_lines.append(
            f'tl.to("#cap{i}", {{opacity:0, y:-10, duration:0.12}}, '
            f'{max(end - 0.05, start + 0.05):.3f});'
        )
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:transparent}}
.wrap{{position:absolute;left:40px;right:40px;bottom:160px;text-align:center;z-index:55;pointer-events:none}}
.cap{{position:absolute;left:0;right:0;bottom:0;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;
  font-size:40px;font-weight:800;color:#fff;padding:14px 22px;
  text-shadow:0 2px 10px #000,0 0 16px #000a;
  background:linear-gradient(90deg,#1a90ffcc,#7a3dffcc);border-radius:999px;
  display:inline-block;margin:0 auto;width:fit-content;max-width:100%;
  left:50%;transform:translateX(-50%)}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-start="0" data-duration="{total_s:.3f}" data-width="1080" data-height="1920" data-fps="{fps}">
  <div class="wrap">
    {chr(10).join(lines)}
  </div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
window.__timelines["captions-zh"] = tl;
</script></body></html>
'''


def _short_lines(cues: list[dict]) -> tuple[list[str], list[str]]:
    """Body lines and GSAP lines shared by the pill-caption variants."""
    lines = []
    tl_lines = []
    for i, cue in enumerate(cues):
        lines.append(f'<div class="cap" id="cap{i}">{esc(cue.get("text") or "")}'
                     f'</div>')
        start = float(cue["start"])
        end = float(cue["end"])
        tl_lines.append(f'tl.set("#cap{i}", {{opacity:0, scale:0.92}}, 0);')
        tl_lines.append(
            f'tl.to("#cap{i}", {{opacity:1, scale:1, duration:0.08}}, '
            f'{start:.3f});')
        tl_lines.append(
            f'tl.to("#cap{i}", {{opacity:0, scale:0.96, duration:0.08}}, '
            f'{max(end - 0.04, start + 0.08):.3f});')
    return lines, tl_lines


def short_captions_v2_html(cues: list[dict], total_s: float,
                           fps: int = 30) -> str:
    """The ch02-ch04 short pill caption page (centered, 38px)."""
    lines, tl_lines = _short_lines(cues)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:transparent}}
.wrap{{position:absolute;left:36px;right:36px;bottom:150px;text-align:center;z-index:55;pointer-events:none;height:120px}}
.cap{{position:absolute;left:50%;bottom:0;transform:translateX(-50%);font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;
  font-size:38px;font-weight:800;color:#fff;padding:14px 26px;opacity:0;
  text-shadow:0 2px 10px #000,0 0 16px #000a;white-space:nowrap;max-width:100%;
  background:linear-gradient(90deg,#1a90ffee,#7a3dffee);border-radius:999px}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-start="0" data-duration="{total_s:.3f}" data-width="1080" data-height="1920" data-fps="{fps}">
  <div class="wrap">{chr(10).join(lines)}</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
window.__timelines["captions-zh"] = tl;
</script></body></html>
'''


def short_captions_ch05_html(cues: list[dict], total_s: float,
                             fps: int = 30) -> str:
    """The ch05 short pill caption page (fit-content auto margins)."""
    lines, tl_lines = _short_lines(cues)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}}
@font-face{{font-family:'Microsoft YaHei';src:local('Microsoft YaHei'),local('Noto Sans SC');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:transparent}}
.wrap{{position:absolute;left:40px;right:40px;bottom:150px;text-align:center;z-index:55;pointer-events:none;height:120px}}
.cap{{position:absolute;left:0;right:0;bottom:0;margin:auto;width:fit-content;max-width:100%;
  font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;
  font-size:38px;font-weight:800;color:#fff;padding:14px 26px;opacity:0;
  text-shadow:0 2px 10px #000,0 0 16px #000a;white-space:nowrap;
  background:linear-gradient(90deg,#1a90ffee,#7a3dffee);border-radius:999px}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-start="0" data-duration="{total_s:.3f}" data-width="1080" data-height="1920" data-fps="{fps}">
  <div class="wrap">{chr(10).join(lines)}</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
window.__timelines["captions-zh"] = tl;
</script></body></html>
'''


SHORT_CAPTION_WRITERS = {
    "ch01": short_captions_html,
    "ch02": short_captions_v2_html,
    "ch03": short_captions_v2_html,
    "ch04": short_captions_v2_html,
    "ch05": short_captions_ch05_html,
}


def watermark_html(total_s: float) -> str:
    """The static brand watermark burned into the shipped long renders."""
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>{FONT}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:transparent}}
.wm{{position:absolute;top:28px;right:36px;z-index:60;text-align:right;opacity:0.70;pointer-events:none;
  font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;letter-spacing:.06em}}
.wm-brand{{font-size:22px;font-weight:700;color:#e8ecf1;text-shadow:0 1px 6px rgba(0,0,0,.65)}}
.wm-series{{font-size:18px;color:#f0a050;margin-top:4px;text-shadow:0 1px 4px rgba(0,0,0,.55)}}
.wm-mark{{font-size:12px;color:#7a8799;margin-top:6px;letter-spacing:.18em}}
</style></head><body>
<div id="root" class="clip" data-composition-id="watermark" data-start="0" data-duration="{total_s:.3f}" data-width="1920" data-height="1080" data-fps="30" style="position:relative;width:1920px;height:1080px;background:transparent">
  <div class="wm" id="wm" data-layout-ignore="true">
    <div class="wm-brand">小电讲电路</div>
    <div class="wm-series">驭者 · Agent Harness</div>
  </div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
tl.set("#wm", {{opacity:0.70}}, 0);
window.__timelines["watermark"] = tl;
</script></body></html>"""


def write_render_inputs(base: Path, episode: dict, cues: list[dict],
                        fmt: str = "long") -> dict[str, str]:
    """Regenerate the render inputs under the render tree.

    ``base`` is the render project directory (the legacy index parent).
    For ``long`` writes ``compositions/captions-zh.html`` and
    ``compositions/watermark.html``; for ``short`` writes
    ``short/compositions/captions-zh.html``. Returns SHA-256 digests.
    """
    import hashlib

    total_s = float(episode["formats"][fmt]["duration_s"])
    written = {}

    def _write(path: Path, body: str) -> None:
        # The shipped artifacts were written through Windows text mode, so
        # pin CRLF to stay byte-identical to them on every platform.
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8", newline="\r\n")
        written[path.relative_to(base).as_posix()] = hashlib.sha256(
            path.read_bytes()).hexdigest()

    if fmt == "long":
        _write(base / "compositions" / "captions-zh.html",
               karaoke_captions_html(cues, total_s))
        _write(base / "compositions" / "watermark.html",
               watermark_html(total_s))
    else:
        writer = SHORT_CAPTION_WRITERS.get(
            episode.get("id", ""), short_captions_v2_html)
        _write(base / "short" / "compositions" / "captions-zh.html",
               writer(cues, total_s))
    return written
