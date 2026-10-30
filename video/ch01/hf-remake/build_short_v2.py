# -*- coding: utf-8 -*-
"""ch01 short-v2: dense motion + hard A/V sync (phrase-locked cuts/karaoke). No publish."""
from __future__ import annotations
import asyncio, html, json, math, struct, subprocess, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHORT = ROOT / "short-v2"
ASSETS = SHORT / "assets"
COMP = SHORT / "compositions"
OUT = ROOT.parent / "out" / "ch01-short-v2.mp4"
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
        (0.12, "whoosh", 0.55),
        (0.55, "ui_blip", 0.42),
        (1.1, "impact", 0.52),
        (1.8, "glitch", 0.42),
        (2.5, "ui_blip", 0.40),
        (3.3, "whoosh", 0.50),
        (3.9, "punch", 0.55),
        (4.55, "impact", 0.52),
    ]
    for i, p in enumerate(phrases):
        t = p["start"]
        if t >= total - 0.15:
            continue
        name = kinds[i % len(kinds)]
        vol = 0.38 + (i % 3) * 0.05
        if "马" in p["text"] or "缰" in p["text"] or "鞍" in p["text"]:
            name, vol = "rein_snap", 0.62
        if "Harness" in p["text"] or "整车" in p["text"]:
            name, vol = "punch", 0.55
        ev.append((t, name, vol))
        if "马" in p["text"]:
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

    t_anti = sents[0]["start"]
    t_alert = sents[1]["start"]
    t_vs = sents[2]["start"]
    t_cart = sents[3]["start"]
    t_cta = sents[4]["start"]

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

    doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#05070d}}
body{{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;color:#f4f7ff}}
#root{{position:absolute;inset:0;background:
  radial-gradient(ellipse at 40% 15%,#1a2744 0%,transparent 50%),
  radial-gradient(ellipse at 70% 80%,#2a1030 0%,transparent 45%),
  linear-gradient(165deg,#070b14,#0d1528 42%,#120a18)}}
.flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;z-index:50}}
.scene{{position:absolute;inset:0;opacity:0}}
.series{{position:absolute;top:72px;left:48px;font-size:26px;letter-spacing:.12em;color:#f0a050;opacity:0;z-index:8}}
.wm{{position:absolute;top:64px;right:40px;text-align:right;opacity:.72;z-index:60;pointer-events:none}}
.wm-b{{font-size:24px;font-weight:700;color:#e8ecf1;text-shadow:0 1px 6px #000a}}
.wm-s{{font-size:20px;color:#f0a050;margin-top:4px}}
.bubble{{position:absolute;padding:18px 26px;border-radius:22px;background:#1a2438;border:2px solid #4af;
  font-size:28px;font-weight:700;opacity:0;box-shadow:0 0 24px #4af6}}
.hand{{position:absolute;font-size:72px;opacity:0;filter:drop-shadow(0 8px 12px #000a)}}
.hub{{position:absolute;left:50%;top:40%;width:170px;height:170px;margin:-85px 0 0 -85px;border-radius:50%;
  background:radial-gradient(circle,#6cf,#148 60%,#062);box-shadow:0 0 70px #4af;opacity:0}}
.ray{{position:absolute;left:50%;top:40%;width:4px;height:240px;background:linear-gradient(#6cf,transparent);
  transform-origin:top center;opacity:0}}
.mod{{position:absolute;padding:14px 22px;border-radius:14px;background:#122038;border:2px solid #6cf;
  font-size:30px;font-weight:800;opacity:0}}
.title{{position:absolute;left:40px;right:40px;top:46%;text-align:center;font-size:68px;font-weight:900;
  letter-spacing:2px;text-shadow:0 0 40px #4af,0 6px 0 #000;opacity:0}}
.sub{{position:absolute;left:48px;right:48px;top:56%;text-align:center;font-size:34px;color:#9ecbff;opacity:0}}
.code{{position:absolute;left:48px;right:48px;top:360px;padding:32px;border-radius:24px;background:#0a101c;
  border:3px solid #3a5;font-family:Consolas,monospace;font-size:32px;line-height:1.55;opacity:0;
  white-space:pre-wrap;box-shadow:0 0 40px #3a56}}
.xmark{{position:absolute;left:50%;top:52%;transform:translate(-50%,-50%) scale(0);font-size:220px;color:#ff3b5c;
  font-weight:900;opacity:0;text-shadow:0 0 40px #f33;z-index:10}}
.alert{{position:absolute;left:60px;right:60px;padding:26px 30px;border-radius:20px;background:linear-gradient(135deg,#2a1020,#120818);
  border:3px solid #ff5a7a;font-size:40px;font-weight:800;opacity:0;box-shadow:0 0 30px #f558}}
.vs-grid{{position:absolute;left:40px;right:40px;top:340px;display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.panel{{padding:28px 20px;border-radius:22px;background:linear-gradient(160deg,#101828,#0a101c);border:3px solid #55ccff;
  min-height:340px;opacity:0}}
.panel.r{{border-color:#ff99aa}}
.panel h3{{font-size:34px;margin-bottom:14px}}
.panel p{{font-size:26px;line-height:1.5;color:#cde}}
.vs{{position:absolute;left:50%;top:46%;transform:translate(-50%,-50%);font-size:96px;font-weight:900;
  color:#fff;text-shadow:0 0 40px #f40;opacity:0;z-index:5}}
.chariot{{position:absolute;left:10px;right:10px;top:300px;height:920px}}
.chip{{display:inline-block;margin:8px;padding:12px 18px;background:#1a1230;border:2px solid #c9a0ff;
  border-radius:999px;font-size:26px;opacity:0;box-shadow:0 0 16px #a0f8}}
.chips{{position:absolute;left:30px;right:30px;bottom:300px;text-align:center}}
.kinetic{{position:absolute;left:60px;right:60px;top:220px;text-align:center;font-weight:900;opacity:0;z-index:25;
  font-size:52px;text-shadow:0 0 24px currentColor;pointer-events:none}}
.cta{{position:absolute;left:40px;right:40px;bottom:300px;text-align:center;font-size:34px;font-weight:800;
  color:#ffd27a;opacity:0;text-shadow:0 0 20px #f0a05088}}
.stamp{{position:absolute;right:70px;top:260px;width:210px;height:210px;border:10px solid #ff3b5c;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:900;color:#ff3b5c;
  transform:rotate(-18deg);opacity:0;box-shadow:0 0 40px #ff3b5c88}}
.pulse-ring{{position:absolute;left:50%;top:40%;width:170px;height:170px;margin:-85px 0 0 -85px;border-radius:50%;
  border:4px solid #6cf;opacity:0}}
</style></head><body>
<div id="root" class="clip" data-composition-id="dense-short-v2" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
  <div class="flash" id="flash"></div>
  <div class="wm" id="wm" data-layout-ignore="true">
    <div class="wm-b">小电讲电路</div>
    <div class="wm-s">驭者 · Agent Harness</div>
  </div>
  <div class="series" id="series">驭者 · Agent Harness</div>
  <div class="kinetic" id="kx"></div>

  <div class="scene" id="sc-hook" style="opacity:1">
    <div class="bubble" id="b1" style="left:70px;bottom:500px">复制这段</div>
    <div class="bubble" id="b2" style="left:400px;bottom:600px">再粘贴</div>
    <div class="bubble" id="b3" style="left:140px;bottom:720px">终端报错?</div>
    <div class="bubble" id="b4" style="left:480px;bottom:800px">又改一遍…</div>
    <div class="bubble" id="b5" style="left:220px;bottom:900px">人当胶水</div>
    <div class="hand" id="hand" style="right:100px;bottom:540px">🖐</div>
    <div class="hub" id="hub"></div>
    <div class="pulse-ring" id="pring"></div>
    <div class="ray" id="r1" style="transform:rotate(-50deg)"></div>
    <div class="ray" id="r2" style="transform:rotate(-15deg)"></div>
    <div class="ray" id="r3" style="transform:rotate(20deg)"></div>
    <div class="ray" id="r4" style="transform:rotate(55deg)"></div>
    <div class="mod" id="m1" style="left:70px;top:500px">Tool</div>
    <div class="mod" id="m2" style="left:280px;top:660px">FS</div>
    <div class="mod" id="m3" style="right:260px;top:660px">Git</div>
    <div class="mod" id="m4" style="right:70px;top:500px">Shell</div>
    <div class="title" id="ht">Agent Harness · 驭者</div>
    <div class="sub" id="hs">不是简单 API 套壳</div>
    <div class="stamp" id="stamp">驭者</div>
  </div>

  <div class="scene" id="sc-anti">
    <div class="code" id="code">while (true) {{
  callAPI();
  parse();
  execute();
}}</div>
    <div class="xmark" id="xmark">✕</div>
  </div>

  <div class="scene" id="sc-alert">
    <div class="alert" id="a1" style="top:340px">⏱ 超时</div>
    <div class="alert" id="a2" style="top:500px">🧩 格式错</div>
    <div class="alert" id="a3" style="top:660px">🔐 权限乱</div>
    <div class="alert" id="a4" style="top:820px">📚 上下文满</div>
  </div>

  <div class="scene" id="sc-vs">
    <div class="vs-grid">
      <div class="panel" id="p1"><h3>遥控器</h3><p>简单封装<br/>人一步步遥控<br/>迟缓 · 易断</p></div>
      <div class="panel r" id="p2"><h3>整车 Harness</h3><p>能跑 · 能停<br/>能诊断<br/>目标驱动</p></div>
    </div>
    <div class="vs" id="vs">VS</div>
  </div>

  <div class="scene" id="sc-cart">
    <div class="chariot">
      <svg viewBox="0 0 1000 900" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
        <defs>
          <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ffe29a"/><stop offset="100%" stop-color="#c9832a"/>
          </linearGradient>
          <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <line x1="40" y1="720" x2="960" y2="720" stroke="#334" stroke-width="4" opacity=".5"/>
        <g id="horse" filter="url(#glow)">
          <ellipse cx="260" cy="560" rx="120" ry="52" fill="#8b5a2b"/>
          <ellipse cx="370" cy="510" rx="58" ry="40" fill="#a0672f"/>
          <rect x="180" y="590" width="16" height="90" fill="#5a3a1a" rx="4"/>
          <rect x="240" y="590" width="16" height="90" fill="#5a3a1a" rx="4"/>
          <rect x="310" y="590" width="16" height="90" fill="#5a3a1a" rx="4"/>
          <rect x="360" y="590" width="16" height="90" fill="#5a3a1a" rx="4"/>
          <text x="160" y="430" fill="#ffd27a" font-size="42" font-weight="700">骏马 · 模型</text>
        </g>
        <path id="rein" d="M380 500 C480 440, 620 420, 720 480" stroke="#e8c36a" stroke-width="12" fill="none" stroke-linecap="round"/>
        <g id="carriage" filter="url(#glow)">
          <rect x="680" y="440" width="260" height="150" rx="16" fill="url(#gold)" stroke="#fff6" stroke-width="3"/>
          <text x="720" y="530" fill="#2a1500" font-size="36" font-weight="900">舆 · 系统</text>
          <circle id="w1" cx="720" cy="620" r="42" fill="#222" stroke="#aaa" stroke-width="7"/>
          <circle id="w2" cx="900" cy="620" r="42" fill="#222" stroke="#aaa" stroke-width="7"/>
          <line x1="680" y1="520" x2="420" y2="560" stroke="#c9a05a" stroke-width="12" stroke-linecap="round"/>
        </g>
        <g id="driver" filter="url(#glow)">
          <circle cx="760" cy="380" r="32" fill="#f0c090"/>
          <rect x="735" y="410" width="50" height="70" rx="10" fill="#2a5080"/>
          <text x="600" y="330" fill="#7cf" font-size="38" font-weight="900">御者 · 你</text>
        </g>
      </svg>
    </div>
    <div class="chips" id="chips">
      <div class="chip" id="ch1">缰绳 = Harness</div>
      <div class="chip" id="ch2">骏马 = LLM</div>
      <div class="chip" id="ch3">舆 = 整车系统</div>
      <div class="chip" id="ch4">能跑 · 能停 · 能诊断</div>
    </div>
    <div class="cta" id="cta">完整版在 B 站合集「驭者·Agent Harness」</div>
  </div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
const T = {total:.3f};
const flash = (t) => {{ tl.to("#flash", {{opacity:0.55, duration:0.04}}, t); tl.to("#flash", {{opacity:0, duration:0.14}}, t+0.04); }};

tl.set("#wm", {{opacity:0.72}}, 0);
tl.fromTo("#series", {{opacity:0, y:-16}}, {{opacity:1, y:0, duration:0.3}}, 0.08);

// ===== HOOK 0 → first VO =====
tl.fromTo("#b1", {{opacity:0, y:70, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.28}}, 0.12);
tl.fromTo("#b2", {{opacity:0, y:70, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.28}}, 0.32);
tl.fromTo("#b3", {{opacity:0, y:70, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.28}}, 0.52);
tl.fromTo("#b4", {{opacity:0, y:70, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.28}}, 0.72);
tl.fromTo("#b5", {{opacity:0, y:70, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.28}}, 0.92);
flash(0.50);
tl.fromTo("#hand", {{opacity:0, x:50}}, {{opacity:1, x:0, duration:0.2}}, 0.45);
tl.to("#hand", {{x:-200, y:-140, duration:0.28}}, 0.75);
tl.to("#hand", {{x:10, y:10, duration:0.28}}, 1.10);
tl.to("#hand", {{x:-170, y:-90, duration:0.25}}, 1.45);
tl.to("#hand", {{x:-40, y:-200, duration:0.25}}, 1.75);
flash(1.10); flash(1.75);
tl.to(["#b1","#b2","#b3","#b4","#b5"], {{opacity:0, scale:0.15, x:160, y:-220, duration:0.45, stagger:0.05}}, 2.00);
tl.fromTo("#hub", {{opacity:0, scale:0.15}}, {{opacity:1, scale:1, duration:0.35}}, 2.25);
tl.fromTo("#pring", {{opacity:0.8, scale:1}}, {{opacity:0, scale:2.2, duration:0.55}}, 2.35);
flash(2.30);
tl.fromTo(["#r1","#r2","#r3","#r4"], {{opacity:0, scaleY:0}}, {{opacity:1, scaleY:1, duration:0.32, stagger:0.06}}, 2.55);
tl.fromTo(["#m1","#m2","#m3","#m4"], {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.28, stagger:0.06}}, 2.85);
tl.to("#hub", {{scale:1.3, duration:0.14}}, 3.55);
tl.to("#hub", {{scale:1.0, duration:0.18}}, 3.70);
flash(3.60);
tl.fromTo("#ht", {{opacity:0, scale:1.2, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:0.4}}, 3.75);
tl.fromTo("#hs", {{opacity:0, y:18}}, {{opacity:1, y:0, duration:0.28}}, 4.15);
tl.fromTo("#stamp", {{opacity:0, scale:1.5, rotation:-42}}, {{opacity:1, scale:1, rotation:-18, duration:0.3}}, 4.35);
flash(4.40);
tl.to("#sc-hook", {{opacity:0, duration:0.18}}, {t_anti - 0.18:.3f});
tl.set("#sc-anti", {{opacity:1}}, {t_anti:.3f});

// ===== ANTI locked to sent0 =====
tl.fromTo("#code", {{opacity:0, y:50, scale:0.92}}, {{opacity:1, y:0, scale:1, duration:0.35}}, {t_anti:.3f});
flash({t_anti:.3f});
// highlight lines sequentially inside anti window
tl.to("#code", {{borderColor:"#f55", boxShadow:"0 0 50px #f55a", duration:0.25}}, {(t_anti+t_alert)/2:.3f});
tl.fromTo("#xmark", {{opacity:0, scale:0}}, {{opacity:1, scale:1.2, duration:0.22}}, {(t_anti+t_alert)/2:.3f});
tl.to("#xmark", {{scale:1, duration:0.15}}, {(t_anti+t_alert)/2 + 0.22:.3f});
flash({(t_anti+t_alert)/2:.3f});
tl.to("#sc-anti", {{opacity:0, duration:0.15}}, {t_alert - 0.15:.3f});
tl.set("#sc-alert", {{opacity:1}}, {t_alert:.3f});

// ===== ALERTS locked to phrases =====
{chr(10).join(alert_tl)}
tl.to(["#a1","#a2","#a3","#a4"], {{opacity:0, y:-24, duration:0.18, stagger:0.03}}, {t_vs - 0.22:.3f});
tl.to("#sc-alert", {{opacity:0, duration:0.12}}, {t_vs - 0.12:.3f});
tl.set("#sc-vs", {{opacity:1}}, {t_vs:.3f});

// ===== VS locked to sent2 =====
tl.fromTo("#p1", {{opacity:0, x:-100, rotate:-3}}, {{opacity:1, x:0, rotate:0, duration:0.32}}, {t_vs:.3f});
tl.fromTo("#p2", {{opacity:0, x:100, rotate:3}}, {{opacity:1, x:0, rotate:0, duration:0.32}}, {t_vs + 0.25:.3f});
tl.fromTo("#vs", {{opacity:0, scale:0}}, {{opacity:1, scale:1.25, duration:0.22}}, {t_vs + 0.55:.3f});
tl.to("#vs", {{scale:1, duration:0.15}}, {t_vs + 0.8:.3f});
flash({t_vs + 0.55:.3f});
tl.to("#p2", {{boxShadow:"0 0 48px #f8a8", scale:1.05, duration:0.28}}, {t_vs + (t_cart-t_vs)*0.55:.3f});
tl.to("#sc-vs", {{opacity:0, duration:0.15}}, {t_cart - 0.15:.3f});
tl.set("#sc-cart", {{opacity:1}}, {t_cart:.3f});

// ===== CHARIOT locked to sent3 =====
tl.fromTo("#horse", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:0.35}}, {t_cart:.3f});
flash({t_cart:.3f});
tl.fromTo("#rein", {{opacity:0}}, {{opacity:1, duration:0.25}}, {t_cart + 0.25:.3f});
tl.to("#horse", {{y:14, duration:0.14, yoyo:true, repeat:9}}, {t_cart + 0.3:.3f});
tl.to("#w1", {{rotation:360, transformOrigin:"50% 50%", duration:1.2, repeat:3, ease:"none"}}, {t_cart + 0.3:.3f});
tl.to("#w2", {{rotation:360, transformOrigin:"50% 50%", duration:1.2, repeat:3, ease:"none"}}, {t_cart + 0.3:.3f});
tl.fromTo("#carriage", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.35}}, {t_cart + 0.45:.3f});
tl.fromTo("#driver", {{opacity:0, y:-40}}, {{opacity:1, y:0, duration:0.3}}, {t_cart + 0.7:.3f});
flash({t_cart + 0.7:.3f});
tl.fromTo("#ch1", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.2}}, {t_cart + 1.0:.3f});
tl.fromTo("#ch2", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.2}}, {t_cart + 1.25:.3f});
tl.fromTo("#ch3", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.2}}, {t_cart + 1.5:.3f});
tl.fromTo("#ch4", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.2}}, {t_cart + 1.75:.3f});
tl.to("#rein", {{attr:{{stroke:"#fff"}}, duration:0.12, yoyo:true, repeat:5}}, {t_cart + 1.1:.3f});

// ===== CTA locked to sent4 =====
tl.fromTo("#cta", {{opacity:0, y:28, scale:0.95}}, {{opacity:1, y:0, scale:1, duration:0.35}}, {t_cta:.3f});
flash({t_cta:.3f});
tl.to("#cta", {{scale:1.04, duration:0.35, yoyo:true, repeat:3}}, {t_cta + 0.4:.3f});

// phrase kinetic layer + light shakes
{chr(10).join(kinetic_lines)}
{chr(10).join(shake_lines)}

tl.set("#sc-cart", {{opacity:1}}, T-0.05);
window.__timelines["dense-short-v2"] = tl;
</script></body></html>
'''
    (COMP / "dense-short-v2.html").write_text(doc, encoding="utf-8")


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
<div class="clip" data-composition-id="dense-short-v2" data-composition-src="compositions/dense-short-v2.html" data-start="0" data-duration="{total:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>
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
        "name": "ch01-short-v2", "private": True, "type": "module",
        "scripts": {"render": "npx --yes hyperframes@0.8.210 render", "check": "npx --yes hyperframes@0.8.210 check"},
    }, indent=2), encoding="utf-8")
    (SHORT / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}, "authoringSkill": "hyperframes", "registryItems": [],
    }, indent=2), encoding="utf-8")
    (SHORT / "meta.json").write_text(json.dumps({"id": "ch01-short-v2", "name": "ch01-short-v2"}, indent=2), encoding="utf-8")


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
    lines = ["# short-v2 A/V sync map", "", "| t | scene | phrase |", "|---|---|---|"]
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
    print(f"OK short-v2 assembled total={total:.3f}s caps={len(phrases)} sents={len(sents)} sfx={len(sfx)}")
    print("phrases:", [p["text"] for p in phrases])


if __name__ == "__main__":
    main()