# -*- coding: utf-8 -*-
"""Build ch01 Douyin/XHS short: vertical dense motion + Yunyang VO + watermark. No publish."""
from __future__ import annotations
import asyncio, html, json, math, struct, subprocess, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHORT = ROOT / "short"
ASSETS = SHORT / "assets"
COMP = SHORT / "compositions"
OUT = ROOT.parent / "out" / "ch01-short.mp4"
SAMPLE = ROOT.parent / "assets" / "sample-short.txt"
HOOK = 5.0
FPS = 30


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def ensure_dirs() -> None:
    for d in (SHORT, ASSETS, ASSETS / "sfx", COMP, ROOT.parent / "out"):
        d.mkdir(parents=True, exist_ok=True)
    tmp = SHORT / ".hf-tmpdir"
    tmp.mkdir(parents=True, exist_ok=True)


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
            elif name == "rein_snap":
                noise = ((i * 1103515245 + 12345) & 0x7FFF) / 32768.0 - 0.5
                sample = env * (0.35 * math.sin(2 * math.pi * f0 * t) + 0.4 * noise)
            elif name == "glitch":
                noise = ((i * 214013 + 2531011) & 0x7FFF) / 32768.0 - 0.5
                freq = f0 + (f1 - f0) * (t / max(dur, 1e-6))
                sample = env * (0.25 * math.sin(2 * math.pi * freq * t) + 0.35 * noise)
            else:
                sample = env * 0.6 * math.sin(2 * math.pi * f0 * t)
            sample = max(-1.0, min(1.0, sample))
            frames += struct.pack("<h", int(sample * 30000))
        with wave.open(str(path), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(frames)


async def make_vo() -> tuple[float, list[dict]]:
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
    # probe duration
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw)],
        capture_output=True, text=True, check=True,
    )
    vo_dur = float(probe.stdout.strip())
    # pad 5s silence at front for hook
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
    # shift captions by HOOK; also split each sentence into ~6-10 char karaoke chunks
    caps: list[dict] = []
    for sent in sentences:
        body = sent["text"].strip()
        if not body:
            continue
        s0, e0 = sent["start"] + HOOK, sent["end"] + HOOK
        # chunk by punctuation first, else by length
        parts: list[str] = []
        buf = ""
        for ch in body:
            buf += ch
            if ch in "，。；、！？,.!;:" or len(buf) >= 8:
                parts.append(buf)
                buf = ""
        if buf:
            parts.append(buf)
        if not parts:
            parts = [body]
        total_chars = sum(len(p) for p in parts) or 1
        t = s0
        span = max(e0 - s0, 0.2)
        for p in parts:
            dur = span * (len(p) / total_chars)
            caps.append({"start": round(t, 3), "end": round(t + dur, 3), "text": p})
            t += dur
    (ASSETS / "short-caps.json").write_text(json.dumps(caps, ensure_ascii=False, indent=2), encoding="utf-8")
    total = HOOK + vo_dur
    return total, caps


def sfx_events(total: float) -> list[tuple[float, str, float]]:
    ev = [
        (0.12, "whoosh", 0.55),
        (0.55, "ui_blip", 0.40),
        (1.10, "impact", 0.50),
        (1.80, "glitch", 0.42),
        (2.40, "ui_blip", 0.38),
        (3.20, "whoosh", 0.48),
        (3.90, "punch", 0.55),
        (4.60, "impact", 0.52),
        (5.10, "glitch", 0.45),
        (5.80, "ui_blip", 0.40),
        (7.20, "impact", 0.55),
        (8.50, "punch", 0.50),
        (10.0, "whoosh", 0.48),
        (11.5, "ui_blip", 0.40),
        (13.0, "impact", 0.55),
        (14.2, "ui_blip", 0.42),
        (15.5, "ui_blip", 0.42),
        (16.8, "ui_blip", 0.42),
        (18.0, "punch", 0.55),
        (19.2, "whoosh", 0.50),
        (20.2, "impact", 0.52),
        (21.1, "punch", 0.55),
        (22.8, "whoosh", 0.50),
        (24.5, "impact", 0.50),
        (26.2, "rein_snap", 0.62),
        (26.8, "gallop", 0.52),
        (27.5, "rein_snap", 0.55),
        (28.5, "impact", 0.55),
        (29.5, "whoosh", 0.48),
        (31.0, "punch", 0.55),
    ]
    return [(t, n, v) for t, n, v in ev if t < total - 0.2]


def write_dense(total: float) -> None:
    # Vertical dense composition — many short beats, chariot metaphor, no meta 吸粉/冲击
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
.hub{{position:absolute;left:50%;top:42%;width:160px;height:160px;margin:-80px 0 0 -80px;border-radius:50%;
  background:radial-gradient(circle,#6cf,#148 60%,#062);box-shadow:0 0 60px #4af;opacity:0}}
.ray{{position:absolute;left:50%;top:42%;width:4px;height:220px;background:linear-gradient(#6cf,transparent);
  transform-origin:top center;opacity:0}}
.mod{{position:absolute;padding:14px 22px;border-radius:14px;background:#122038;border:2px solid #6cf;
  font-size:30px;font-weight:800;opacity:0}}
.title{{position:absolute;left:48px;right:48px;top:46%;text-align:center;font-size:72px;font-weight:900;
  letter-spacing:2px;text-shadow:0 0 40px #4af,0 6px 0 #000;opacity:0}}
.sub{{position:absolute;left:48px;right:48px;top:56%;text-align:center;font-size:34px;color:#9ecbff;opacity:0}}
.code{{position:absolute;left:56px;right:56px;top:380px;padding:36px;border-radius:24px;background:#0a101c;
  border:3px solid #f55;font-family:Consolas,monospace;font-size:34px;line-height:1.55;opacity:0;
  box-shadow:0 0 40px #f556}}
.xmark{{position:absolute;left:50%;top:52%;transform:translate(-50%,-50%) scale(0);font-size:220px;color:#ff3b5c;
  font-weight:900;opacity:0;text-shadow:0 0 40px #f33;z-index:10}}
.alert{{position:absolute;left:70px;right:70px;padding:28px 32px;border-radius:20px;background:linear-gradient(135deg,#2a1020,#120818);
  border:3px solid #ff5a7a;font-size:40px;font-weight:800;opacity:0;box-shadow:0 0 30px #f558}}
.vs-grid{{position:absolute;left:48px;right:48px;top:360px;display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.panel{{padding:32px 24px;border-radius:22px;background:linear-gradient(160deg,#101828,#0a101c);border:3px solid #55ccff;
  min-height:360px;opacity:0}}
.panel.r{{border-color:#ff99aa}}
.panel h3{{font-size:36px;margin-bottom:16px}}
.panel p{{font-size:28px;line-height:1.5;color:#cde}}
.vs{{position:absolute;left:50%;top:48%;transform:translate(-50%,-50%);font-size:96px;font-weight:900;
  color:#fff;text-shadow:0 0 40px #f40;opacity:0;z-index:5}}
.chariot{{position:absolute;left:20px;right:20px;top:320px;height:900px}}
.chip{{display:inline-block;margin:8px;padding:12px 18px;background:#1a1230;border:2px solid #c9a0ff;
  border-radius:999px;font-size:26px;opacity:0;box-shadow:0 0 16px #a0f8}}
.chips{{position:absolute;left:40px;right:40px;bottom:280px;text-align:center}}
.kinetic{{position:absolute;font-weight:900;opacity:0;z-index:20;text-shadow:0 0 24px currentColor;pointer-events:none}}
.cta{{position:absolute;left:48px;right:48px;bottom:320px;text-align:center;font-size:36px;font-weight:800;
  color:#ffd27a;opacity:0;text-shadow:0 0 20px #f0a05088}}
.stamp{{position:absolute;right:80px;top:280px;width:220px;height:220px;border:10px solid #ff3b5c;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:900;color:#ff3b5c;
  transform:rotate(-18deg);opacity:0;box-shadow:0 0 40px #ff3b5c88}}
</style></head><body>
<div id="root" class="clip" data-composition-id="dense-short" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
  <div class="flash" id="flash"></div>
  <div class="wm" id="wm" data-layout-ignore="true">
    <div class="wm-b">小电讲电路</div>
    <div class="wm-s">驭者 · Agent Harness</div>
  </div>
  <div class="series" id="series">驭者 · Agent Harness</div>

  <!-- HOOK 0-5 -->
  <div class="scene" id="sc-hook" style="opacity:1">
    <div class="bubble" id="b1" style="left:80px;bottom:520px">复制这段</div>
    <div class="bubble" id="b2" style="left:420px;bottom:620px">再粘贴</div>
    <div class="bubble" id="b3" style="left:160px;bottom:740px">终端报错?</div>
    <div class="bubble" id="b4" style="left:500px;bottom:820px">又改一遍…</div>
    <div class="hand" id="hand" style="right:120px;bottom:560px">🖐</div>
    <div class="hub" id="hub"></div>
    <div class="ray" id="r1" style="transform:rotate(-50deg)"></div>
    <div class="ray" id="r2" style="transform:rotate(-15deg)"></div>
    <div class="ray" id="r3" style="transform:rotate(20deg)"></div>
    <div class="ray" id="r4" style="transform:rotate(55deg)"></div>
    <div class="mod" id="m1" style="left:80px;top:520px">Tool</div>
    <div class="mod" id="m2" style="left:300px;top:680px">FS</div>
    <div class="mod" id="m3" style="right:280px;top:680px">Git</div>
    <div class="mod" id="m4" style="right:80px;top:520px">Shell</div>
    <div class="title" id="ht">Agent Harness · 驭者</div>
    <div class="sub" id="hs">不是简单 API 套壳</div>
    <div class="stamp" id="stamp">驭者</div>
  </div>

  <!-- ANTI while -->
  <div class="scene" id="sc-anti">
    <div class="code" id="code">while (true) {{\\n  callAPI();\\n  parse();\\n  execute();\\n}}</div>
    <div class="xmark" id="xmark">✕</div>
    <div class="kinetic" id="k1" style="left:120px;top:280px;font-size:56px;color:#ff6">理想假设</div>
  </div>

  <!-- ALERTS -->
  <div class="scene" id="sc-alert">
    <div class="alert" id="a1" style="top:360px">⏱ 超时</div>
    <div class="alert" id="a2" style="top:520px">🧩 格式错</div>
    <div class="alert" id="a3" style="top:680px">🔐 权限乱</div>
    <div class="alert" id="a4" style="top:840px">📚 上下文满</div>
    <div class="kinetic" id="k2" style="left:200px;top:240px;font-size:48px;color:#f8a">逐个打破</div>
  </div>

  <!-- REMOTE VS CAR -->
  <div class="scene" id="sc-vs">
    <div class="vs-grid">
      <div class="panel" id="p1"><h3>遥控器</h3><p>简单封装<br/>人一步步遥控<br/>迟缓 · 易断</p></div>
      <div class="panel r" id="p2"><h3>整车 Harness</h3><p>能跑 · 能停<br/>能诊断<br/>目标驱动</p></div>
    </div>
    <div class="vs" id="vs">VS</div>
  </div>

  <!-- CHARIOT -->
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
          <text x="180" y="440" fill="#ffd27a" font-size="40" font-weight="700">骏马 · 模型</text>
        </g>
        <path id="rein" d="M380 500 C480 440, 620 420, 720 480" stroke="#e8c36a" stroke-width="10" fill="none" stroke-linecap="round"/>
        <g id="carriage" filter="url(#glow)">
          <rect x="680" y="440" width="260" height="150" rx="16" fill="url(#gold)" stroke="#fff6" stroke-width="3"/>
          <text x="730" y="530" fill="#2a1500" font-size="36" font-weight="900">舆 · 系统</text>
          <circle cx="720" cy="620" r="42" fill="#222" stroke="#aaa" stroke-width="7"/>
          <circle cx="900" cy="620" r="42" fill="#222" stroke="#aaa" stroke-width="7"/>
          <line x1="680" y1="520" x2="420" y2="560" stroke="#c9a05a" stroke-width="12" stroke-linecap="round"/>
        </g>
        <g id="driver" filter="url(#glow)">
          <circle cx="760" cy="380" r="32" fill="#f0c090"/>
          <rect x="735" y="410" width="50" height="70" rx="10" fill="#2a5080"/>
          <text x="620" y="340" fill="#7cf" font-size="36" font-weight="900">御者 · 你</text>
        </g>
      </svg>
    </div>
    <div class="chips" id="chips">
      <div class="chip">缰绳 = Harness</div>
      <div class="chip">骏马 = LLM</div>
      <div class="chip">舆 = 整车系统</div>
      <div class="chip">能跑 · 能停 · 能诊断</div>
    </div>
    <div class="cta" id="cta">完整版在 B 站合集「驭者·Agent Harness」</div>
    <div class="kinetic" id="k3" style="left:160px;top:220px;font-size:52px;color:#6cf">缰绳在手</div>
  </div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
const T = {total:.3f};
const flash = (t) => {{ tl.to("#flash", {{opacity:0.55, duration:0.05}}, t); tl.to("#flash", {{opacity:0, duration:0.18}}, t+0.05); }};

tl.set("#wm", {{opacity:0.72}}, 0);
tl.fromTo("#series", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.4}}, 0.1);

// ===== HOOK 0-5: bubbles pile, hand copy-paste, hub rays, title =====
tl.fromTo("#b1", {{opacity:0, y:80, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.35}}, 0.15);
tl.fromTo("#b2", {{opacity:0, y:80, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.35}}, 0.40);
tl.fromTo("#b3", {{opacity:0, y:80, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.35}}, 0.65);
tl.fromTo("#b4", {{opacity:0, y:80, scale:0.7}}, {{opacity:1, y:0, scale:1, duration:0.35}}, 0.90);
flash(0.55);
tl.fromTo("#hand", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.25}}, 0.50);
tl.to("#hand", {{x:-180, y:-120, duration:0.35}}, 0.80);
tl.to("#hand", {{x:0, y:0, duration:0.35}}, 1.20);
tl.to("#hand", {{x:-160, y:-80, duration:0.30}}, 1.55);
flash(1.10);

// suck bubbles into hub
tl.to(["#b1","#b2","#b3","#b4"], {{opacity:0, scale:0.2, x:200, y:-200, duration:0.55, stagger:0.06}}, 1.70);
tl.fromTo("#hub", {{opacity:0, scale:0.2}}, {{opacity:1, scale:1, duration:0.45}}, 2.10);
flash(2.20);
tl.fromTo(["#r1","#r2","#r3","#r4"], {{opacity:0, scaleY:0}}, {{opacity:1, scaleY:1, duration:0.4, stagger:0.08}}, 2.40);
tl.fromTo(["#m1","#m2","#m3","#m4"], {{opacity:0, scale:0.5}}, {{opacity:1, scale:1, duration:0.35, stagger:0.08}}, 2.70);
tl.to("#hub", {{scale:1.25, duration:0.18}}, 3.50);
tl.to("#hub", {{scale:1.0, duration:0.22}}, 3.70);
flash(3.60);
tl.fromTo("#ht", {{opacity:0, scale:1.18, filter:"blur(8px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:0.45}}, 3.70);
tl.fromTo("#hs", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.35}}, 4.10);
tl.fromTo("#stamp", {{opacity:0, scale:1.4, rotation:-40}}, {{opacity:1, scale:1, rotation:-18, duration:0.35}}, 4.30);
flash(4.35);

// leave hook
tl.to("#sc-hook", {{opacity:0, duration:0.25}}, 4.95);
tl.set("#sc-anti", {{opacity:1}}, 5.0);

// ===== ANTI 5-13 =====
tl.fromTo("#code", {{opacity:0, y:40, rotateX:20}}, {{opacity:1, y:0, rotateX:0, duration:0.45}}, 5.05);
tl.fromTo("#k1", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1.1, duration:0.3}}, 6.2);
tl.to("#k1", {{opacity:0, y:-40, duration:0.35}}, 7.4);
tl.fromTo("#xmark", {{opacity:0, scale:0}}, {{opacity:1, scale:1.15, duration:0.28}}, 7.6);
tl.to("#xmark", {{scale:1, duration:0.2}}, 7.9);
flash(7.65);
tl.to("#code", {{borderColor:"#ff3b5c", boxShadow:"0 0 50px #f55a", duration:0.3}}, 7.7);
tl.to("#sc-anti", {{opacity:0, duration:0.25}}, 12.9);
tl.set("#sc-alert", {{opacity:1}}, 13.0);

// ===== ALERTS 13-23 =====
tl.fromTo("#k2", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.3}}, 13.1);
[["#a1",13.2],["#a2",14.4],["#a3",15.6],["#a4",16.9]].forEach(([sel,t])=>{{
  tl.fromTo(sel, {{opacity:0, x:80, scale:0.85}}, {{opacity:1, x:0, scale:1, duration:0.32}}, t);
  flash(t);
}});
tl.to(["#a1","#a2","#a3","#a4","#k2"], {{opacity:0, y:-30, duration:0.3, stagger:0.04}}, 19.6);
tl.to("#sc-alert", {{opacity:0, duration:0.2}}, 19.95);
tl.set("#sc-vs", {{opacity:1}}, 20.05);

// ===== VS 23-28 =====
tl.fromTo("#p1", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:0.4}}, 20.15);
tl.fromTo("#p2", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.4}}, 20.45);
tl.fromTo("#vs", {{opacity:0, scale:0}}, {{opacity:1, scale:1.2, duration:0.28}}, 21.0);
tl.to("#vs", {{scale:1, duration:0.2}}, 21.3);
flash(21.05);
tl.to("#p2", {{boxShadow:"0 0 40px #f8a8", scale:1.04, duration:0.35}}, 22.8);
tl.to("#sc-vs", {{opacity:0, duration:0.25}}, 25.85);
tl.set("#sc-cart", {{opacity:1}}, 26.0);

// ===== CHARIOT to end =====
tl.fromTo("#horse", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.45}}, 26.1);
tl.fromTo("#rein", {{opacity:0}}, {{opacity:1, duration:0.3}}, 26.5);
// gallop bob
tl.to("#horse", {{y:12, duration:0.18, yoyo:true, repeat:7}}, 26.6);
tl.fromTo("#carriage", {{opacity:0, x:50}}, {{opacity:1, x:0, duration:0.4}}, 26.9);
tl.fromTo("#driver", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.35}}, 27.3);
flash(27.4);
tl.fromTo("#k3", {{opacity:0, scale:0.7}}, {{opacity:1, scale:1.05, duration:0.3}}, 27.6);
tl.to("#k3", {{opacity:0, duration:0.35}}, 29.2);
tl.fromTo("#chips .chip", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.28, stagger:0.08}}, 28.2);
tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4}}, Math.max(T-3.2, 30.5));
tl.to("#rein", {{attr:{{stroke:"#fff"}}, duration:0.15, yoyo:true, repeat:3}}, 29.5);
flash(Math.max(T-2.8, 30.8));

// keep last scene
tl.set("#sc-cart", {{opacity:1}}, T-0.05);

window.__timelines["dense-short"] = tl;
</script></body></html>
'''
    # fix escaped newlines in code block display
    doc = doc.replace("\\\\n", "\\n")
    (COMP / "dense-short.html").write_text(doc, encoding="utf-8")


def write_captions(caps: list[dict], total: float) -> None:
    # karaoke pill captions near bottom (above safe zone)
    lines = []
    for i, c in enumerate(caps):
        lines.append(
            f'<div class="cap" id="cap{i}" style="opacity:0">{esc(c["text"])}</div>'
        )
    tl_lines = []
    for i, c in enumerate(caps):
        s, e = c["start"], c["end"]
        tl_lines.append(f'tl.set("#cap{i}", {{opacity:0}}, 0);')
        tl_lines.append(
            f'tl.fromTo("#cap{i}", {{opacity:0, y:18, scale:0.92}}, {{opacity:1, y:0, scale:1, duration:0.12}}, {s:.3f});'
        )
        tl_lines.append(
            f'tl.to("#cap{i}", {{opacity:0, y:-10, duration:0.12}}, {max(e-0.05, s+0.05):.3f});'
        )
    html_doc = f'''<!doctype html>
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
<div id="root" class="clip" data-composition-id="captions-zh" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
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
    (COMP / "captions-zh.html").write_text(html_doc, encoding="utf-8")


def write_index(total: float, sfx: list[tuple[float, str, float]]) -> None:
    sfx_tags = []
    durs = {"whoosh": 0.30, "impact": 0.24, "rein_snap": 0.14, "gallop": 0.58, "ui_blip": 0.10, "punch": 0.20, "glitch": 0.16}
    for i, (t, name, vol) in enumerate(sfx):
        dur = durs.get(name, 0.25)
        sfx_tags.append(
            f'<audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.wav" data-start="{t:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="{20 + (i % 8)}" data-volume="{vol:.2f}"></audio>'
        )
    index = f'''<!doctype html>
<html lang="zh-CN" data-resolution="portrait"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
<div class="clip" id="clip-dense" data-composition-id="dense-short" data-composition-src="compositions/dense-short.html" data-start="0" data-duration="{total:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>
<div class="clip" id="clip-captions" data-composition-id="captions-zh" data-composition-src="compositions/captions-zh.html" data-start="0" data-duration="{total:.3f}" data-track-index="10" data-track-kind="captions" style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>
<audio id="a-roll-audio" src="assets/short-vo.mp3" data-start="0" data-duration="{total:.3f}" data-track-index="2" data-volume="1"></audio>
{chr(10).join(sfx_tags)}
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>
'''
    (SHORT / "index.html").write_text(index, encoding="utf-8")


def write_meta() -> None:
    (SHORT / "package.json").write_text(
        json.dumps(
            {
                "name": "ch01-short",
                "private": True,
                "type": "module",
                "scripts": {
                    "dev": "npx --yes hyperframes@0.8.210 preview",
                    "check": "npx --yes hyperframes@0.8.210 check",
                    "render": "npx --yes hyperframes@0.8.210 render",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (SHORT / "hyperframes.json").write_text(
        json.dumps(
            {
                "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                "media": {"autoProxy": True},
                "authoringSkill": "hyperframes",
                "registryItems": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (SHORT / "meta.json").write_text(
        json.dumps({"id": "ch01-short", "name": "ch01-short"}, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    import edge_tts  # noqa: F401 — ensure available

    ensure_dirs()
    synth_sfx()
    total, caps = asyncio.run(make_vo())
    # clamp scene end timings if VO shorter/longer
    sfx = sfx_events(total)
    write_dense(total)
    write_captions(caps, total)
    write_index(total, sfx)
    write_meta()
    meta = {"total": total, "caps": len(caps), "sfx": len(sfx), "hook": HOOK, "out": str(OUT)}
    (SHORT / "short-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK short assembled total={total:.3f}s caps={len(caps)} sfx={len(sfx)} out={OUT}")


if __name__ == "__main__":
    main()
