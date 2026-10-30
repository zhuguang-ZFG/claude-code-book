# -*- coding: utf-8 -*-
"""ch04 short-v1: Claude/Codex/Agent fun personas + guess beat + hard A/V sync. No publish."""
from __future__ import annotations
import asyncio, html, json, math, struct, subprocess, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHORT = ROOT / "short"
ASSETS = SHORT / "assets"
COMP = SHORT / "compositions"
OUT = ROOT.parent / "out" / "ch04-short-v1.mp4"
SAMPLE = ROOT.parent / "assets" / "sample-short.txt"
HOOK = 5.0
FPS = 30


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def ensure() -> None:
    for d in (SHORT, ASSETS, ASSETS / "sfx", COMP, ROOT.parent / "out", SHORT / ".hf-tmpdir"):
        d.mkdir(parents=True, exist_ok=True)


def synth_sfx() -> None:
    out = ASSETS / "sfx"
    specs = {
        "whoosh": (0.28, 900, 180),
        "impact": (0.22, 80, 40),
        "rein_snap": (0.12, 2200, 600),
        "gallop": (0.55, 120, 90),
        "ui_blip": (0.08, 1400, 1100),
        "punch": (0.18, 60, 30),
        "glitch": (0.15, 400, 1200),
        "tick": (0.06, 1800, 1600),
    }
    for name, (dur, f0, f1) in specs.items():
        path = out / f"{name}.wav"
        if path.exists() and path.stat().st_size > 500:
            continue
        sr = 44100
        n = int(sr * dur)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            env = math.exp(-t * (8 if name != "whoosh" else 4))
            if name == "whoosh":
                freq = f0 + (f1 - f0) * (t / max(dur, 1e-6))
                sample = env * 0.45 * math.sin(2 * math.pi * freq * t)
            elif name == "gallop":
                hit = 0.0
                for k in (0.0, 0.18, 0.36):
                    dt = t - k
                    if 0 <= dt < 0.08:
                        hit += math.exp(-dt * 40) * math.sin(2 * math.pi * f0 * dt)
                sample = 0.55 * hit
            elif name in ("rein_snap", "glitch"):
                noise = ((i * 1103515245 + 12345) & 0x7FFF) / 32768.0 - 0.5
                sample = env * (0.35 * math.sin(2 * math.pi * f0 * t) + 0.4 * noise)
            elif name == "tick":
                sample = env * 0.5 * math.sin(2 * math.pi * f0 * t)
            else:
                sample = env * 0.6 * math.sin(2 * math.pi * f0 * t)
            sample = max(-1.0, min(1.0, sample))
            frames += struct.pack("<h", int(sample * 30000))
        with wave.open(str(path), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(frames)


def split_phrases(text: str) -> list[str]:
    """Split on CN/EN punctuation; keep English tokens + 「」 quotes intact."""
    parts: list[str] = []
    buf = ""
    seps = set("，。；、！？,.!;:")
    in_quote = False
    for ch in text:
        if ch == "「":
            in_quote = True
            buf += ch
            continue
        if ch == "」":
            buf += ch
            in_quote = False
            continue
        buf += ch
        if (not in_quote) and ch in seps:
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    merged: list[str] = []
    for p in parts:
        stripped = p.strip()
        if not stripped:
            continue
        # fold pure punctuation / tiny fragments into previous
        if merged and (len(stripped) <= 2 or stripped in "。！？.!?"):
            merged[-1] += p
        else:
            merged.append(p)
    return [p for p in merged if p.strip()]


def allocate_phrase_times(sent_start: float, sent_end: float, phrases: list[str]) -> list[dict]:
    # weight by visible char count (CJK=1, latin run=1 unit per 3 chars)
    def weight(s: str) -> float:
        w = 0.0
        i = 0
        while i < len(s):
            o = ord(s[i])
            if s[i].isspace() or s[i] in "，。；、！？,.!;:「」·":
                i += 1
                continue
            if o < 128:
                j = i
                while j < len(s) and ord(s[j]) < 128 and not s[j].isspace():
                    j += 1
                w += max(1.0, (j - i) / 3.0)
                i = j
            else:
                w += 1.0
                i += 1
        return max(w, 1.0)

    weights = [weight(p) for p in phrases]
    total_w = sum(weights) or 1.0
    span = max(sent_end - sent_start, 0.2)
    t = sent_start
    out = []
    for p, w in zip(phrases, weights):
        dur = span * (w / total_w)
        out.append({"start": round(t, 3), "end": round(t + dur, 3), "text": p.strip()})
        t += dur
    if out:
        out[-1]["end"] = round(sent_end, 3)
    return out


async def make_vo() -> tuple[float, list[dict], list[dict]]:
    import edge_tts

    text = SAMPLE.read_text(encoding="utf-8").strip()
    raw = ASSETS / "short-vo-raw.mp3"
    sentences: list[dict] = []
    communicate = edge_tts.Communicate(text, "zh-CN-YunyangNeural", rate="-10%", pitch="-5Hz")
    with open(raw, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                s = chunk["offset"] / 10_000_000
                e = s + chunk["duration"] / 10_000_000
                sentences.append({"start": s, "end": e, "text": chunk["text"]})

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw)],
        capture_output=True, text=True, check=True,
    )
    vo_dur = float(probe.stdout.strip())

    silence = ASSETS / "silence5.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(HOOK),
         "-c:a", "libmp3lame", "-q:a", "4", str(silence)],
        check=True, capture_output=True,
    )
    vo = ASSETS / "short-vo.mp3"
    concat = ASSETS / "vo-concat.txt"
    concat.write_text(f"file '{silence.name}'\nfile '{raw.name}'\n", encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c:a", "libmp3lame", "-q:a", "2", str(vo)],
        check=True, capture_output=True,
    )

    phrases: list[dict] = []
    sent_shifted: list[dict] = []
    for sent in sentences:
        s0, e0 = sent["start"] + HOOK, sent["end"] + HOOK
        sent_shifted.append({"start": round(s0, 3), "end": round(e0, 3), "text": sent["text"]})
        ph = split_phrases(sent["text"])
        phrases.extend(allocate_phrase_times(s0, e0, ph))

    (ASSETS / "short-caps.json").write_text(json.dumps(phrases, ensure_ascii=False, indent=2), encoding="utf-8")
    (ASSETS / "short-sents.json").write_text(json.dumps(sent_shifted, ensure_ascii=False, indent=2), encoding="utf-8")
    return HOOK + vo_dur, phrases, sent_shifted


def sfx_on_phrases(phrases: list[dict], total: float) -> list[tuple[float, str, float]]:
    kinds = ["tick", "ui_blip", "whoosh", "impact", "punch", "glitch", "rein_snap"]
    ev = [
        (0.10, "whoosh", 0.62),
        (0.28, "ui_blip", 0.50),
        (0.46, "ui_blip", 0.50),
        (0.70, "tick", 0.45),
        (1.15, "glitch", 0.55),
        (1.70, "impact", 0.68),
        (1.85, "punch", 0.62),
        (2.15, "rein_snap", 0.55),
        (2.40, "punch", 0.60),
        (3.40, "whoosh", 0.55),
        (4.15, "impact", 0.65),
        (4.55, "punch", 0.58),
    ]
    for i, p in enumerate(phrases):
        t = p["start"]
        if t >= total - 0.15:
            continue
        name = kinds[i % len(kinds)]
        vol = 0.38 + (i % 3) * 0.05
        if "Claude" in p["text"] or "Codex" in p["text"] or "Agent" in p["text"] or "猜" in p["text"]:
            name, vol = "punch", 0.58
        if "假双手" in p["text"] or "锤子" in p["text"] or "干等" in p["text"]:
            name, vol = "impact", 0.62
        if "马" in p["text"] or "缰" in p["text"] or "活扣" in p["text"]:
            name, vol = "rein_snap", 0.62
        if "Harness" in p["text"] or "双手" in p["text"] or "Streaming" in p["text"]:
            name, vol = "punch", 0.55
        ev.append((t, name, vol))
        if "马" in p["text"] or "驭" in p["text"]:
            ev.append((t + 0.25, "gallop", 0.50))
    # dedupe close hits
    ev.sort(key=lambda x: x[0])
    out = []
    last = -1.0
    for t, n, v in ev:
        if t - last < 0.08:
            continue
        out.append((t, n, v))
        last = t
    return out


def write_dense(total: float, sents: list[dict], phrases: list[dict]) -> None:
    # Map scenes hard to sentence windows (absolute times already include HOOK)
    # s0 anti, s1 alerts, s2 vs, s3 chariot, s4 cta
    while True:
        if len(sents) >= 5:
            break
        # pad if TTS merged oddly
        sents = sents + [{"start": total - 0.5, "end": total, "text": ""}]
        break

    # Ensure 5 scene anchors even if TTS SentenceBoundary < 5
    while len(sents) < 5:
        last = sents[-1] if sents else {"start": HOOK, "end": HOOK + 1}
        gap = max(1.2, (total - last["end"]) / max(2, 6 - len(sents)))
        sents.append({"start": min(last["end"] + 0.05, total - 0.8), "end": min(last["end"] + gap, total)})
    # Prefer phrase-aligned anchors when we have clear phrase groups
    phrases_by_scene = phrases  # already absolute
    t_anti = sents[0]["start"]
    t_alert = sents[1]["start"]
    t_vs = sents[2]["start"]
    t_cart = sents[3]["start"]
    t_cta = sents[4]["start"]
    # If only 4 TTS sents, split body for alert/vs using phrase starts
    if len([s for s in sents if s.get("_pad")]) >= 0 and len(phrases) >= 6:
        # anti: 假双手 / Bash / 锤子
        # alert/guess: 猜一猜 / 五要素 / 五十五
        for ph in phrases:
            if "猜一猜" in ph["text"] or "四道闸" in ph["text"] or "不是一扇" in ph["text"] or "真护栏" in ph["text"]:
                t_alert = ph["start"]; break
        for ph in phrases:
            if "校验输入" in ph["text"] or "规则匹配" in ph["text"] or "deny" in ph["text"] or "交互确认" in ph["text"]:
                t_vs = ph["start"]; break
        for ph in phrases:
            if "五种模式" in ph["text"] or "default" in ph["text"] or "bypass" in ph["text"] or "门禁" in ph["text"]:
                t_cart = ph["start"]; break
        for ph in phrases:
            if "完整版" in ph["text"] or "B 站" in ph["text"] or "合集" in ph["text"] or "纵深防御" in ph["text"]:
                t_cta = ph["start"]; break

    
    # phrase onsets inside alert sentence for card pops
    alert_phrases = [p for p in phrases if t_alert - 0.05 <= p["start"] < t_vs]
    # expect ~ 超时 / 格式错 / 权限乱 / 上下文 / 理想假设 / 打破
    alert_times = [p["start"] for p in alert_phrases[:6]]
    while len(alert_times) < 4:
        alert_times.append(t_alert + 1.2 * (len(alert_times) + 1))

    # vs micro-beats from phrases in vs sentence
    vs_phrases = [p for p in phrases if t_vs - 0.05 <= p["start"] < t_cart]
    cart_phrases = [p for p in phrases if t_cart - 0.05 <= p["start"] < t_cta]

    def flash_js(t: float) -> str:
        return f"flash({t:.3f});"

    # Build dense GSAP driven by phrase list for kinetic hits
    kinetic_lines = []
    for i, p in enumerate(phrases):
        txt = p["text"].replace('"', "")
        # skip ultra short punctuation-only
        core = txt.strip("，。；、！？,.!;:「」 ")
        if len(core) < 2:
            continue
        color = ["#6cf", "#f8a", "#ff6", "#9f8", "#fc6"][i % 5]
        kinetic_lines.append(
            f'tl.fromTo("#kx", {{opacity:0, scale:0.7, y:30}}, {{opacity:1, scale:1.05, y:0, duration:0.12}}, {p["start"]:.3f});'
        )
        kinetic_lines.append(
            f'tl.call(() => {{ const el=document.getElementById("kx"); if(el){{ el.textContent={json.dumps(core[:18], ensure_ascii=False)}; el.style.color="{color}"; }} }}, null, {p["start"]:.3f});'
        )
        kinetic_lines.append(
            f'tl.to("#kx", {{opacity:0, y:-24, duration:0.15}}, {max(p["end"]-0.08, p["start"]+0.12):.3f});'
        )

    alert_tl = []
    ids = ["#a1", "#a2", "#a3", "#a4"]
    for i, sel in enumerate(ids):
        tt = alert_times[i]
        alert_tl.append(
            f'tl.fromTo("{sel}", {{opacity:0, x:90, scale:0.8}}, {{opacity:1, x:0, scale:1, duration:0.22}}, {tt:.3f});'
        )
        alert_tl.append(flash_js(tt))

    # shake bg subtly on each phrase start in body
    shake_lines = []
    for p in phrases:
        shake_lines.append(
            f'tl.fromTo("#root", {{x:0}}, {{x:6, duration:0.04, yoyo:true, repeat:1}}, {p["start"]:.3f});'
        )

    # v3: load external persona template (fun Claude/Codex/Agent + 猜一猜)
    tpl_path = COMP / "dense-short-v3.tpl.html"
    tpl = tpl_path.read_text(encoding="utf-8")
    guess_pad = 2.05
    alert_tl = []
    ids = ["#a1", "#a2", "#a3", "#a4"]
    for i, sel in enumerate(ids):
        tt = alert_times[i] + guess_pad
        if tt >= t_vs - 0.3:
            tt = t_alert + guess_pad + 0.35 * (i + 1)
        alert_tl.append(
            f'tl.fromTo("{sel}", {{opacity:0, x:90, scale:0.8, rotation:6}}, {{opacity:1, x:0, scale:1, rotation:0, duration:0.22}}, {tt:.3f});'
        )
        alert_tl.append(flash_js(tt))
    # extra fun SFX-synced pops already in template timeline
    doc = tpl
    for k, v in {
        "$TOTAL$": f"{total:.3f}",
        "$FPS$": str(FPS),
        "$T_ANTI$": f"{t_anti:.3f}",
        "$T_ALERT$": f"{t_alert:.3f}",
        "$T_VS$": f"{t_vs:.3f}",
        "$T_CART$": f"{t_cart:.3f}",
        "$T_CTA$": f"{t_cta:.3f}",
        "$ALERT_TL$": "\n".join(alert_tl),
        "$KINETIC$": "\n".join(kinetic_lines),
        "$SHAKE$": "\n".join(shake_lines),
    }.items():
        doc = doc.replace(k, v)
    (COMP / "dense-short.html").write_text(doc, encoding="utf-8")


def write_captions(caps: list[dict], total: float) -> None:
    lines = []
    tl_lines = []
    for i, c in enumerate(caps):
        lines.append(f'<div class="cap" id="cap{i}">{esc(c["text"])}</div>')
        s, e = c["start"], c["end"]
        # hard sync: appear at phrase start, hold through phrase, fade just before next
        tl_lines.append(f'tl.set("#cap{i}", {{opacity:0, scale:0.92}}, 0);')
        tl_lines.append(
            f'tl.to("#cap{i}", {{opacity:1, scale:1, duration:0.08}}, {s:.3f});'
        )
        tl_lines.append(
            f'tl.to("#cap{i}", {{opacity:0, scale:0.96, duration:0.08}}, {max(e - 0.04, s + 0.08):.3f});'
        )
    html_doc = f'''<!doctype html>
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
<div id="root" class="clip" data-composition-id="captions-zh" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
  <div class="wrap">{chr(10).join(lines)}</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
window.__timelines["captions-zh"] = tl;
</script></body></html>
'''
    (COMP / "captions-zh.html").write_text(html_doc, encoding="utf-8")


def write_index(total: float, sfx: list[tuple[float, str, float]]) -> None:
    durs = {"whoosh": 0.30, "impact": 0.24, "rein_snap": 0.14, "gallop": 0.58, "ui_blip": 0.10, "punch": 0.20, "glitch": 0.16, "tick": 0.07}
    tags = []
    for i, (t, name, vol) in enumerate(sfx):
        tags.append(
            f'<audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.wav" data-start="{t:.3f}" '
            f'data-duration="{durs.get(name,0.25):.3f}" data-track-index="{20+(i%8)}" data-volume="{vol:.2f}"></audio>'
        )
    index = f'''<!doctype html>
<html lang="zh-CN" data-resolution="portrait"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
<div class="clip" data-composition-id="dense-short" data-composition-src="compositions/dense-short.html" data-start="0" data-duration="{total:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>
<div class="clip" data-composition-id="captions-zh" data-composition-src="compositions/captions-zh.html" data-start="0" data-duration="{total:.3f}" data-track-index="10" data-track-kind="captions" style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>
<audio id="a-roll-audio" src="assets/short-vo.mp3" data-start="0" data-duration="{total:.3f}" data-track-index="2" data-volume="1"></audio>
{chr(10).join(tags)}
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>
'''
    (SHORT / "index.html").write_text(index, encoding="utf-8")


def write_meta() -> None:
    (SHORT / "package.json").write_text(json.dumps({
        "name": "ch04-short", "private": True, "type": "module",
        "scripts": {"render": "npx --yes hyperframes@0.8.210 render", "check": "npx --yes hyperframes@0.8.210 check"},
    }, indent=2), encoding="utf-8")
    (SHORT / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}, "authoringSkill": "hyperframes", "registryItems": [],
    }, indent=2), encoding="utf-8")
    (SHORT / "meta.json").write_text(json.dumps({"id": "ch03-short", "name": "ch04-short"}, indent=2), encoding="utf-8")


def main() -> None:
    ensure()
    synth_sfx()
    total, phrases, sents = asyncio.run(make_vo())
    sfx = sfx_on_phrases(phrases, total)
    write_dense(total, sents, phrases)
    write_captions(phrases, total)
    write_index(total, sfx)
    write_meta()
    meta = {
        "total": total, "caps": len(phrases), "sents": len(sents), "sfx": len(sfx),
        "hook": HOOK, "out": str(OUT),
        "sent_starts": [s["start"] for s in sents],
        "phrase_texts": [p["text"] for p in phrases],
    }
    (SHORT / "short-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    # sync verification table
    lines = ["# short A/V sync map", "", "| t | scene | phrase |", "|---|---|---|"]
    scene = "hook"
    cuts = []
    if len(sents) >= 5:
        cuts = [
            (sents[0]["start"], "anti"),
            (sents[1]["start"], "alert"),
            (sents[2]["start"], "vs"),
            (sents[3]["start"], "cart"),
            (sents[4]["start"], "cta"),
        ]
    for p in phrases:
        sc = "body"
        for ct, name in cuts:
            if p["start"] + 1e-6 >= ct:
                sc = name
        lines.append(f"| {p['start']:.2f}–{p['end']:.2f} | {sc} | {p['text']} |")
    (SHORT / "SYNC-MAP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK short assembled total={total:.3f}s caps={len(phrases)} sents={len(sents)} sfx={len(sfx)}")
    print("phrases:", [p["text"] for p in phrases])


if __name__ == "__main__":
    main()