# -*- coding: utf-8 -*-
"""Assemble proof/ as a HyperFrames 0.8.210 project with VO + SFX + chariot dense motion."""
from __future__ import annotations
import html, json, math, struct, wave
from pathlib import Path

HF = Path(__file__).resolve().parent
PROOF = HF / "proof"
ASSETS = PROOF / "assets"
TOTAL = 61.0
SEGS = [("hook", 0.0, 18.0), ("metaphor", 64.0, 82.0), ("autocar", 265.0, 290.0)]
TRANS = json.loads((HF / "transcript.json").read_text(encoding="utf-8"))


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def ensure_sfx() -> None:
    out = ASSETS / "sfx"
    out.mkdir(parents=True, exist_ok=True)
    src = HF / "assets" / "sfx"
    if src.exists():
        for f in src.glob("*.wav"):
            (out / f.name).write_bytes(f.read_bytes())
    specs = {
        "whoosh": (0.28, 900, 180),
        "impact": (0.22, 80, 40),
        "rein_snap": (0.12, 2200, 600),
        "gallop": (0.55, 120, 90),
        "ui_blip": (0.08, 1400, 1100),
        "punch": (0.18, 60, 30),
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
            else:
                sample = env * 0.6 * math.sin(2 * math.pi * f0 * t)
            sample = max(-1.0, min(1.0, sample))
            frames += struct.pack("<h", int(sample * 30000))
        with wave.open(str(path), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(frames)


def map_caps():
    mapping = []
    t = 0.0
    for name, a, b in SEGS:
        mapping.append((t, t + (b - a), a, b, name))
        t += b - a
    caps = []
    for w in TRANS:
        text = (w.get("text") or "").strip()
        if not text:
            continue
        s, e = float(w["start"]), float(w["end"])
        for ps, pe, sa, sb, name in mapping:
            if e <= sa or s >= sb:
                continue
            cs, ce = max(s, sa), min(e, sb)
            if ce - cs < 0.12:
                continue
            caps.append({"start": ps + (cs - sa), "end": ps + (ce - sa), "text": text})
    return caps


def sfx_events():
    ev = [
        (0.15, "whoosh", 0.50),
        (1.05, "impact", 0.58),
        (2.40, "ui_blip", 0.40),
        (4.00, "punch", 0.50),
        (6.50, "whoosh", 0.45),
        (9.00, "impact", 0.55),
        (12.00, "ui_blip", 0.38),
        (15.50, "punch", 0.48),
        (18.20, "whoosh", 0.55),
        (19.05, "rein_snap", 0.62),
        (20.50, "gallop", 0.48),
        (22.00, "impact", 0.58),
        (24.00, "rein_snap", 0.50),
        (26.00, "ui_blip", 0.40),
        (28.00, "gallop", 0.45),
        (30.50, "whoosh", 0.50),
        (33.00, "impact", 0.55),
        (35.50, "rein_snap", 0.48),
        (36.30, "whoosh", 0.50),
        (38.00, "punch", 0.55),
        (41.00, "ui_blip", 0.40),
        (44.00, "impact", 0.50),
        (48.00, "whoosh", 0.45),
        (52.00, "punch", 0.50),
        (56.00, "ui_blip", 0.38),
        (59.00, "impact", 0.55),
    ]
    return [(t, n, v) for t, n, v in ev if t < TOTAL - 0.15]


def write_dense_comp() -> None:
    comp = PROOF / "compositions"
    comp.mkdir(parents=True, exist_ok=True)
    body = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#05070d}
body{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;color:#f4f7ff}
#root{position:absolute;inset:0;background:
  radial-gradient(ellipse at 30% 20%,#1a2744 0%,transparent 55%),
  radial-gradient(ellipse at 80% 70%,#2a1030 0%,transparent 50%),
  linear-gradient(160deg,#070b14,#0d1528 40%,#120a18)}
.flash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;z-index:40}
.scene{position:absolute;inset:0;opacity:0}
.hook-title{position:absolute;left:120px;top:260px;font-size:92px;font-weight:900;letter-spacing:4px;
  text-shadow:0 0 40px #4af,0 8px 0 #000;opacity:0}
.hook-sub{position:absolute;left:130px;top:400px;font-size:42px;color:#9ecbff;opacity:0}
.stamp{position:absolute;right:140px;top:180px;width:280px;height:280px;border:10px solid #ff3b5c;
  border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:64px;font-weight:900;
  color:#ff3b5c;transform:rotate(-18deg);opacity:0;box-shadow:0 0 40px #ff3b5c88}
.card-row{position:absolute;left:100px;top:560px;display:flex;gap:28px}
.card{width:360px;height:180px;background:linear-gradient(145deg,#162038,#0c1220);border:2px solid #33aaff;
  border-radius:18px;padding:28px;font-size:36px;font-weight:700;opacity:0;
  box-shadow:0 20px 60px #000a,0 0 30px #33aaff55}
.meta-label{position:absolute;left:80px;top:56px;font-size:28px;letter-spacing:8px;color:#ffd27a;opacity:0}
.chariot{position:absolute;left:80px;top:140px;width:1760px;height:680px}
.map-row{position:absolute;left:80px;bottom:48px;display:flex;gap:14px;flex-wrap:wrap;width:1760px}
.chip{padding:12px 20px;background:#1a1230;border:2px solid #c9a0ff;border-radius:999px;font-size:24px;opacity:0;
  box-shadow:0 0 18px #a0f8}
.auto-grid{position:absolute;left:120px;top:180px;display:grid;grid-template-columns:1fr 1fr;gap:36px;width:1680px}
.panel{background:linear-gradient(160deg,#101828,#0a101c);border:2px solid #55ccff;border-radius:22px;padding:36px;
  min-height:340px;opacity:0}
.panel.r{border-color:#ff99aa}
.panel h3{font-size:40px;margin-bottom:18px}
.panel p{font-size:30px;line-height:1.55;color:#cde}
.vs{position:absolute;left:50%;top:48%;transform:translate(-50%,-50%);font-size:120px;font-weight:900;
  color:#fff;text-shadow:0 0 40px #ff4400;opacity:0;z-index:5}
.kinetic{position:absolute;font-weight:900;opacity:0;z-index:20;text-shadow:0 0 24px currentColor}
</style></head><body>
<div id="root" class="clip" data-composition-id="dense" data-start="0" data-duration="61" data-width="1920" data-height="1080" data-fps="30">
  <div class="flash" id="flash"></div>

  <div class="scene" id="sc-hook" style="opacity:1">
    <div class="hook-title" id="ht">别再当码农了</div>
    <div class="hook-sub" id="hs">智能体编程 · 第 01 讲 · 驭者</div>
    <div class="stamp" id="stamp">驭者</div>
    <div class="card-row">
      <div class="card" id="c1">马车 = 系统</div>
      <div class="card" id="c2">缰绳 = Harness</div>
      <div class="card" id="c3">骏马 = 模型</div>
    </div>
  </div>

  <div class="scene" id="sc-meta">
    <div class="meta-label" id="ml">前言隐喻 · 动起来</div>
    <div class="chariot">
      <svg viewBox="0 0 1600 620" width="1600" height="620" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ffe29a"/><stop offset="100%" stop-color="#c9832a"/>
          </linearGradient>
          <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <line x1="40" y1="520" x2="1560" y2="520" stroke="#334455" stroke-width="4" opacity="0.5"/>
        <g id="horse1" filter="url(#glow)" opacity="0">
          <ellipse cx="320" cy="400" rx="110" ry="48" fill="#8b5a2b"/>
          <ellipse cx="420" cy="360" rx="55" ry="38" fill="#a0672f"/>
          <rect x="250" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <rect x="300" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <rect x="360" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <rect x="400" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <text x="260" y="300" fill="#ffd27a" font-size="34" font-weight="700">骏马·模型</text>
        </g>
        <g id="horse2" filter="url(#glow)" opacity="0">
          <ellipse cx="560" cy="410" rx="100" ry="44" fill="#6e4520"/>
          <ellipse cx="650" cy="370" rx="50" ry="34" fill="#855528"/>
          <rect x="500" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
          <rect x="545" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
          <rect x="600" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
          <rect x="635" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
        </g>
        <path id="rein" d="M430 350 C520 300, 700 280, 880 320" stroke="#e8c36a" stroke-width="8" fill="none" stroke-linecap="round" opacity="0"/>
        <path id="rein2" d="M660 360 C740 320, 820 310, 900 330" stroke="#e8c36a" stroke-width="6" fill="none" opacity="0"/>
        <g id="carriage" filter="url(#glow)" opacity="0">
          <rect x="920" y="300" width="320" height="160" rx="18" fill="url(#gold)" stroke="#ffffff66" stroke-width="3"/>
          <text x="990" y="390" fill="#2a1500" font-size="40" font-weight="900">舆 · 车厢</text>
          <line id="yuan" x1="920" y1="380" x2="700" y2="400" stroke="#c9a05a" stroke-width="14" stroke-linecap="round"/>
          <circle cx="980" cy="470" r="48" fill="#222" stroke="#aaa" stroke-width="8"/>
          <circle cx="1180" cy="470" r="48" fill="#222" stroke="#aaa" stroke-width="8"/>
          <circle cx="980" cy="470" r="10" fill="#ddd"/>
          <circle cx="1180" cy="470" r="10" fill="#ddd"/>
          <text x="940" y="560" fill="#99ccff" font-size="26">辐 · 轮</text>
          <rect x="1040" y="280" width="80" height="24" rx="6" fill="#66ccff"/>
          <text x="1045" y="270" fill="#66ccff" font-size="22">轼</text>
          <rect x="1210" y="450" width="28" height="40" rx="4" fill="#ff6666"/>
          <text x="1245" y="475" fill="#ff8888" font-size="22">辖</text>
          <text x="700" y="360" fill="#e8c36a" font-size="22">辕</text>
        </g>
        <g id="driver" filter="url(#glow)" opacity="0">
          <circle cx="1000" cy="240" r="36" fill="#f0c090"/>
          <rect x="970" y="275" width="60" height="90" rx="12" fill="#2a5080"/>
          <text x="900" y="200" fill="#77ccff" font-size="38" font-weight="900">御者 · 你</text>
        </g>
      </svg>
    </div>
    <div class="map-row" id="map">
      <div class="chip">御 = 驾驭</div>
      <div class="chip">舆 = 车厢/系统</div>
      <div class="chip">辕 = 连接</div>
      <div class="chip">辐 = 轮辐</div>
      <div class="chip">軎/辖 = 锁定</div>
      <div class="chip">轼 = 扶手/界面</div>
      <div class="chip">缰绳 = Harness</div>
      <div class="chip">骏马 = LLM</div>
    </div>
  </div>

  <div class="scene" id="sc-auto">
    <div class="auto-grid">
      <div class="panel" id="p1"><h3>遥控器模式</h3><p>人一步步遥控<br/>迟缓 · 易断 · 难规模化</p></div>
      <div class="panel r" id="p2"><h3>自动驾驶模式</h3><p>Harness 握缰<br/>目标驱动 · 自主冲刺</p></div>
    </div>
    <div class="vs" id="vs">VS</div>
  </div>

  <div class="kinetic" id="k1" style="left:700px;top:100px;font-size:72px;color:#ff5555">Harness</div>
  <div class="kinetic" id="k2" style="left:200px;top:720px;font-size:56px;color:#55ffff">缰绳在手</div>
</div>
<script>
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const flash = () => { gsap.fromTo("#flash", {opacity:0.5}, {opacity:0, duration:0.18, overwrite:true}); };

tl.set("#sc-hook", {opacity:1}, 0);
tl.fromTo("#ht", {scale:0.55, opacity:0, x:-90}, {scale:1.06, opacity:1, x:0, duration:0.55, ease:"back.out(2)"}, 0.12);
tl.to("#ht", {scale:1, duration:0.18}, 0.67);
tl.fromTo("#hs", {y:48, opacity:0}, {y:0, opacity:1, duration:0.42}, 0.72);
tl.fromTo("#stamp", {scale:0, rotation:-42}, {scale:1.12, rotation:-18, duration:0.4, ease:"back.out(3)"}, 1.12);
tl.to("#stamp", {scale:1, duration:0.14}, 1.52);
tl.call(flash, null, 1.12);
tl.fromTo("#c1", {y:90, opacity:0}, {y:0, opacity:1, duration:0.38}, 2.2);
tl.fromTo("#c2", {y:90, opacity:0}, {y:0, opacity:1, duration:0.38}, 2.7);
tl.fromTo("#c3", {y:90, opacity:0}, {y:0, opacity:1, duration:0.38}, 3.2);
tl.fromTo("#k1", {scale:2.2, opacity:0}, {scale:1, opacity:1, duration:0.32}, 4.0);
tl.to("#k1", {opacity:0, y:-36, duration:0.35}, 5.2);
tl.fromTo("#k2", {x:-110, opacity:0}, {x:0, opacity:1, duration:0.38}, 6.0);
tl.to("#k2", {opacity:0, duration:0.28}, 8.0);
tl.to("#c1,#c2,#c3", {x:"+=10", duration:0.05, yoyo:true, repeat:7}, 9.0);
tl.to("#ht", {color:"#ff6b8a", duration:0.18}, 12.0);
tl.to("#ht", {color:"#f4f7ff", duration:0.18}, 12.35);

tl.to("#sc-hook", {opacity:0, duration:0.22}, 17.7);
tl.set("#sc-meta", {opacity:1}, 17.92);
tl.fromTo("#ml", {opacity:0, x:-40}, {opacity:1, x:0, duration:0.32}, 18.05);
tl.fromTo("#horse1", {opacity:0, x:-130}, {opacity:1, x:0, duration:0.48, ease:"power3.out"}, 18.35);
tl.fromTo("#horse2", {opacity:0, x:-110}, {opacity:1, x:0, duration:0.42}, 18.65);
tl.fromTo("#rein", {opacity:0}, {opacity:1, duration:0.35}, 19.15);
tl.fromTo("#rein2", {opacity:0}, {opacity:1, duration:0.35}, 19.25);
tl.fromTo("#carriage", {opacity:0, x:160, scale:0.82}, {opacity:1, x:0, scale:1, duration:0.52, ease:"back.out(1.5)"}, 19.75);
tl.fromTo("#driver", {opacity:0, y:-90, scale:0.45}, {opacity:1, y:0, scale:1, duration:0.42, ease:"back.out(2)"}, 20.55);
tl.call(flash, null, 20.55);
tl.to("#horse1,#horse2", {y:"+=14", duration:0.16, yoyo:true, repeat:20, ease:"sine.inOut"}, 21.0);
tl.to("#carriage,#driver", {y:"+=7", duration:0.16, yoyo:true, repeat:20, ease:"sine.inOut"}, 21.0);
const chips = gsap.utils.toArray("#map .chip");
chips.forEach((el, i) => {
  tl.fromTo(el, {scale:0.25, opacity:0}, {scale:1.12, opacity:1, duration:0.26, ease:"back.out(3)"}, 24.0 + i * 0.26);
  tl.to(el, {scale:1, duration:0.08}, 24.22 + i * 0.26);
});
tl.to("#rein,#rein2", {attr:{stroke:"#ffcc55"}, duration:0.12, yoyo:true, repeat:5}, 28.4);
tl.call(flash, null, 30.0);
tl.fromTo("#k1", {left:620, top:70, scale:0.4, opacity:0, color:"#ffd27a"}, {scale:1.15, opacity:1, duration:0.32}, 31.0);
tl.to("#k1", {opacity:0, duration:0.28}, 33.0);

tl.to("#sc-meta", {opacity:0, duration:0.28}, 35.7);
tl.set("#sc-auto", {opacity:1}, 35.95);
tl.fromTo("#p1", {x:-90, opacity:0}, {x:0, opacity:1, duration:0.42}, 36.15);
tl.fromTo("#p2", {x:90, opacity:0}, {x:0, opacity:1, duration:0.42}, 36.65);
tl.fromTo("#vs", {scale:0, opacity:0, rotation:-25}, {scale:1.18, opacity:1, rotation:0, duration:0.38, ease:"back.out(3)"}, 37.45);
tl.to("#vs", {scale:1, duration:0.12}, 37.85);
tl.call(flash, null, 37.45);
tl.to("#p1", {borderColor:"#ff6666", duration:0.28}, 42.0);
tl.to("#p2", {borderColor:"#55ff77", boxShadow:"0 0 42px #55ff7788", duration:0.38}, 46.0);
tl.to("#p2", {scale:1.05, duration:0.28, yoyo:true, repeat:3}, 50.0);
tl.fromTo("#k2", {left:760, top:920, opacity:0, scale:0.75}, {opacity:1, scale:1, duration:0.36}, 54.0);
tl.to("#k2", {opacity:0, duration:0.28}, 57.0);

window.__timelines["dense"] = tl;
</script></body></html>
'''
    (comp / "dense.html").write_text(body, encoding="utf-8")


def write_captions(caps) -> None:
    parts = []
    tl_lines = ['window.__timelines = window.__timelines || {};', 'const tl = gsap.timeline({ paused: true });']
    for i, c in enumerate(caps):
        s = float(c["start"])
        e = float(c["end"])
        dur = max(0.2, e - s)
        text = esc(c["text"])
        parts.append(
            f'<div id="c{i}" class="cap-clip clip" data-start="{s:.3f}" data-duration="{dur:.3f}" data-track-index="10">'
            f'<div class="cap-inner" id="c{i}-in">{text}</div></div>'
        )
        tl_lines.append(f'tl.set("#c{i}-in", {{opacity:0}}, 0);')
        tl_lines.append(f'tl.to("#c{i}-in", {{opacity:1, duration:0.12}}, {s:.3f});')
        tl_lines.append(f'tl.to("#c{i}-in", {{opacity:0, duration:0.12}}, {max(s + 0.15, e - 0.12):.3f});')
    tl_lines.append('window.__timelines["captions-zh"] = tl;')
    html_doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:transparent}}
.cap-clip{{position:absolute;left:0;right:0;bottom:72px;display:flex;justify-content:center;pointer-events:none}}
.cap-inner{{max-width:1600px;padding:14px 28px;border-radius:10px;background:rgba(8,10,14,.72);color:#fff;
  font-size:34px;line-height:1.45;text-align:center;opacity:0;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;
  text-shadow:0 2px 8px rgba(0,0,0,.55);white-space:pre-wrap}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-track-kind="captions" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080" data-fps="30" style="position:relative;width:1920px;height:1080px;background:transparent">
{''.join(parts)}
</div>
<script>
{chr(10).join(tl_lines)}
</script></body></html>
'''
    (PROOF / "compositions" / "captions-zh.html").write_text(html_doc, encoding="utf-8")


def write_index(sfx) -> None:
    sfx_tags = []
    for i, (t, name, vol) in enumerate(sfx):
        # short clip duration for one-shot SFX
        dur = {"whoosh": 0.30, "impact": 0.24, "rein_snap": 0.14, "gallop": 0.58, "ui_blip": 0.10, "punch": 0.20}.get(name, 0.25)
        sfx_tags.append(
            f'<audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.wav" data-start="{t:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="{20 + (i % 8)}" data-volume="{vol:.2f}"></audio>'
        )
    index = f'''<!doctype html>
<html lang="zh-CN" data-resolution="landscape"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#000}}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080" data-fps="30">
<div class="clip" id="clip-dense" data-composition-id="dense" data-composition-src="compositions/dense.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>
<div class="clip" id="clip-captions" data-composition-id="captions-zh" data-composition-src="compositions/captions-zh.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="10" data-track-kind="captions" style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>
<audio id="a-roll-audio" src="assets/proof-vo.mp3" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="2" data-volume="1"></audio>
{chr(10).join(sfx_tags)}
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>
'''
    (PROOF / "index.html").write_text(index, encoding="utf-8")


def write_meta() -> None:
    (PROOF / "package.json").write_text(
        json.dumps(
            {
                "name": "ch01-long-dense-proof",
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
    (PROOF / "hyperframes.json").write_text(
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
    (PROOF / "meta.json").write_text(
        json.dumps({"id": "ch01-long-dense-proof", "name": "ch01-long-dense-proof"}, indent=2),
        encoding="utf-8",
    )
    tmp = PROOF / ".hf-tmpdir"
    tmp.mkdir(parents=True, exist_ok=True)


def main() -> None:
    if not (ASSETS / "proof-vo.mp3").exists():
        raise SystemExit("missing proof-vo.mp3 — run build_dense_proof.py first")
    ensure_sfx()
    caps = map_caps()
    sfx = sfx_events()
    write_dense_comp()
    write_captions(caps)
    write_index(sfx)
    write_meta()
    meta = {"total": TOTAL, "caps": len(caps), "sfx": len(sfx), "segments": SEGS}
    (PROOF / "proof-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK HF proof assembled total={TOTAL}s caps={len(caps)} sfx={len(sfx)}")


if __name__ == "__main__":
    main()
