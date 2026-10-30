# -*- coding: utf-8 -*-
"""Dense proof: visual+audio punch, chariot metaphor, burned captions. No publish."""
from __future__ import annotations
import html, json, math, struct, subprocess, wave
from pathlib import Path

HF = Path(__file__).resolve().parent
PROOF = HF / "proof"
ASSETS = PROOF / "assets"
SFX_SRC = HF / "assets" / "sfx"
OUT_VO = ASSETS / "proof-vo.mp3"
TRANS = json.loads((HF / "transcript.json").read_text(encoding="utf-8"))
SEGS = [("hook", 0.0, 18.0), ("metaphor", 64.0, 82.0), ("autocar", 265.0, 290.0)]
TOTAL = sum(b - a for _, a, b in SEGS)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def ensure() -> None:
    for d in (PROOF, ASSETS, PROOF / "assets" / "sfx", PROOF / "compositions"):
        d.mkdir(parents=True, exist_ok=True)
    if SFX_SRC.exists():
        for f in SFX_SRC.glob("*.wav"):
            (PROOF / "assets" / "sfx" / f.name).write_bytes(f.read_bytes())


def synth_sfx() -> None:
    """Ensure punchy SFX exist even if missing."""
    out = PROOF / "assets" / "sfx"
    out.mkdir(parents=True, exist_ok=True)
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
                freq = f0 + (f1 - f0) * (t / dur)
                sample = env * 0.45 * math.sin(2 * math.pi * freq * t)
            elif name == "gallop":
                # 3 hoof hits
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


def build_vo():
    full = HF / "full.mp3"
    if not full.exists():
        raise SystemExit(f"missing {full}")
    parts, mapping, t = [], [], 0.0
    for name, a, b in SEGS:
        dur = b - a
        part = ASSETS / f"seg_{name}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(a), "-t", str(dur), "-i", str(full),
             "-c:a", "libmp3lame", "-q:a", "2", str(part)],
            check=True, capture_output=True,
        )
        parts.append(part)
        mapping.append((t, t + dur, a, b, name))
        t += dur
    concat = ASSETS / "concat.txt"
    concat.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c:a", "libmp3lame", "-q:a", "2", str(OUT_VO)],
        check=True, capture_output=True, cwd=str(ASSETS),
    )
    return mapping, t


def map_caps(mapping):
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


def sfx_events(total: float):
    # Timed to hook / metaphor / autocar beats — punchy, not bed
    ev = [
        (0.15, "whoosh", 0.55),
        (1.0, "impact", 0.65),
        (2.4, "ui_blip", 0.45),
        (4.0, "punch", 0.55),
        (6.5, "whoosh", 0.5),
        (9.0, "impact", 0.6),
        (12.0, "ui_blip", 0.4),
        (15.5, "punch", 0.5),
        # metaphor block starts ~18s
        (18.2, "whoosh", 0.6),
        (19.0, "rein_snap", 0.7),
        (20.5, "gallop", 0.55),
        (22.0, "impact", 0.65),
        (24.0, "rein_snap", 0.55),
        (26.0, "ui_blip", 0.45),
        (28.0, "gallop", 0.5),
        (30.5, "whoosh", 0.55),
        (33.0, "impact", 0.6),
        (35.5, "rein_snap", 0.5),
        # autocar ~36s
        (36.3, "whoosh", 0.55),
        (38.0, "punch", 0.6),
        (41.0, "ui_blip", 0.45),
        (44.0, "impact", 0.55),
        (48.0, "whoosh", 0.5),
        (52.0, "punch", 0.55),
        (56.0, "ui_blip", 0.4),
        (59.0, "impact", 0.6),
    ]
    return [(t, n, v) for t, n, v in ev if t < total - 0.2]


def write_html(caps, total: float) -> None:
    cap_js = json.dumps(caps, ensure_ascii=False)
    sfx = sfx_events(total)
    sfx_tags = "\n".join(
        f'<audio class="sfx" data-at="{t}" data-vol="{v}" preload="auto" src="assets/sfx/{n}.wav"></audio>'
        for t, n, v in sfx
    )
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ch01 dense proof</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:#05070d;color:#f4f7ff;
  font-family:"Microsoft YaHei","PingFang SC",sans-serif}}
.stage{{position:relative;width:1920px;height:1080px}}
.scene{{position:absolute;inset:0;opacity:0;pointer-events:none}}
.scene.on{{opacity:1}}
.bg{{position:absolute;inset:0;background:
  radial-gradient(ellipse at 30% 20%,#1a2744 0%,transparent 55%),
  radial-gradient(ellipse at 80% 70%,#2a1030 0%,transparent 50%),
  linear-gradient(160deg,#070b14,#0d1528 40%,#120a18)}}
.flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;z-index:50}}
.hook-title{{position:absolute;left:120px;top:280px;font-size:92px;font-weight:900;letter-spacing:4px;
  text-shadow:0 0 40px #4af,0 8px 0 #000;transform:scale(0.6);opacity:0}}
.hook-sub{{position:absolute;left:130px;top:420px;font-size:42px;color:#9ecbff;opacity:0;transform:translateY(40px)}}
.stamp{{position:absolute;right:140px;top:200px;width:280px;height:280px;border:10px solid #ff3b5c;
  border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:64px;font-weight:900;
  color:#ff3b5c;transform:rotate(-18deg) scale(0);opacity:0;box-shadow:0 0 40px #ff3b5c88}}
.card-row{{position:absolute;left:100px;top:560px;display:flex;gap:28px}}
.card{{width:360px;height:180px;background:linear-gradient(145deg,#162038,#0c1220);border:2px solid #3af6;
  border-radius:18px;padding:28px;font-size:36px;font-weight:700;opacity:0;transform:translateY(80px) rotateX(30deg);
  box-shadow:0 20px 60px #000a,0 0 30px #3af4}}
.meta-label{{position:absolute;left:80px;top:60px;font-size:28px;letter-spacing:8px;color:#ffd27a;opacity:0}}
.chariot{{position:absolute;left:160px;top:220px;width:1600px;height:620px}}
.svg-wrap{{width:100%;height:100%}}
.part{{opacity:0;transform-origin:center}}
.map-row{{position:absolute;left:100px;bottom:160px;display:flex;gap:18px;flex-wrap:wrap;width:1700px}}
.chip{{padding:14px 22px;background:#1a1230;border:2px solid #c9a0ff;border-radius:999px;font-size:26px;
  opacity:0;transform:scale(0.5);box-shadow:0 0 20px #a0f}}
.auto-grid{{position:absolute;left:120px;top:180px;display:grid;grid-template-columns:1fr 1fr;gap:36px;width:1680px}}
.panel{{background:linear-gradient(160deg,#101828,#0a101c);border:2px solid #5cf;border-radius:22px;padding:36px;
  min-height:320px;opacity:0;transform:translateX(-60px)}}
.panel.r{{transform:translateX(60px);border-color:#f6a}}
.panel h3{{font-size:40px;margin-bottom:18px}}
.panel p{{font-size:30px;line-height:1.55;color:#cde}}
.vs{{position:absolute;left:50%;top:48%;transform:translate(-50%,-50%) scale(0);font-size:120px;font-weight:900;
  color:#fff;text-shadow:0 0 40px #f40;opacity:0;z-index:5}}
.caption{{position:absolute;left:0;right:0;bottom:48px;text-align:center;font-size:40px;font-weight:700;
  text-shadow:0 2px 8px #000,0 0 12px #000;padding:0 80px;z-index:40;min-height:56px}}
.kinetic{{position:absolute;font-weight:900;opacity:0;pointer-events:none;z-index:20;
  text-shadow:0 0 24px currentColor}}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
</head>
<body>
<div class="stage" id="stage">
  <div class="bg"></div>
  <div class="flash" id="flash"></div>

  <div class="scene on" id="sc-hook">
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
      <svg class="svg-wrap" viewBox="0 0 1600 620" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ffe29a"/><stop offset="100%" stop-color="#c9832a"/>
          </linearGradient>
          <filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <!-- ground -->
        <line x1="40" y1="520" x2="1560" y2="520" stroke="#334" stroke-width="4" opacity="0.5"/>
        <!-- horses -->
        <g id="horse1" class="part" filter="url(#glow)">
          <ellipse cx="320" cy="400" rx="110" ry="48" fill="#8b5a2b"/>
          <ellipse cx="420" cy="360" rx="55" ry="38" fill="#a0672f"/>
          <rect x="250" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <rect x="300" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <rect x="360" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <rect x="400" y="430" width="14" height="70" fill="#5a3a1a" rx="4"/>
          <text x="300" y="300" fill="#ffd27a" font-size="36" font-weight="700">骏马·模型</text>
        </g>
        <g id="horse2" class="part" filter="url(#glow)">
          <ellipse cx="560" cy="410" rx="100" ry="44" fill="#6e4520"/>
          <ellipse cx="650" cy="370" rx="50" ry="34" fill="#855528"/>
          <rect x="500" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
          <rect x="545" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
          <rect x="600" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
          <rect x="635" y="440" width="14" height="65" fill="#4a3015" rx="4"/>
        </g>
        <!-- reins -->
        <path id="rein" class="part" d="M430 350 C520 300, 700 280, 880 320" stroke="#e8c36a" stroke-width="8" fill="none" stroke-linecap="round"/>
        <path id="rein2" class="part" d="M660 360 C740 320, 820 310, 900 330" stroke="#e8c36a" stroke-width="6" fill="none"/>
        <!-- carriage body 舆 -->
        <g id="carriage" class="part" filter="url(#glow)">
          <rect x="920" y="300" width="320" height="160" rx="18" fill="url(#gold)" stroke="#fff6" stroke-width="3"/>
          <text x="1000" y="390" fill="#2a1500" font-size="42" font-weight="900">舆 · 车厢</text>
          <line id="yuan" x1="920" y1="380" x2="700" y2="400" stroke="#c9a05a" stroke-width="14" stroke-linecap="round"/>
          <circle id="fu1" cx="980" cy="470" r="48" fill="#222" stroke="#aaa" stroke-width="8"/>
          <circle id="fu2" cx="1180" cy="470" r="48" fill="#222" stroke="#aaa" stroke-width="8"/>
          <circle cx="980" cy="470" r="10" fill="#ddd"/>
          <circle cx="1180" cy="470" r="10" fill="#ddd"/>
          <text x="940" y="560" fill="#9cf" font-size="26">辐 · 轮</text>
          <rect id="shi" x="1040" y="280" width="80" height="24" rx="6" fill="#6cf"/>
          <text x="1045" y="270" fill="#6cf" font-size="22">轼</text>
          <rect id="xia" x="1210" y="450" width="28" height="40" rx="4" fill="#f66"/>
          <text x="1245" y="475" fill="#f88" font-size="22">辖</text>
        </g>
        <!-- driver 御者 -->
        <g id="driver" class="part" filter="url(#glow)">
          <circle cx="1000" cy="240" r="36" fill="#f0c090"/>
          <rect x="970" y="275" width="60" height="90" rx="12" fill="#2a5080"/>
          <text x="920" y="200" fill="#7cf" font-size="40" font-weight="900">御者 · 你</text>
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

  <div class="kinetic" id="k1" style="left:700px;top:120px;font-size:72px;color:#ff5">Harness</div>
  <div class="kinetic" id="k2" style="left:200px;top:700px;font-size:56px;color:#5ff">缰绳在手</div>
  <div class="caption" id="cap"></div>
  <audio id="vo" src="assets/proof-vo.mp3" preload="auto"></audio>
  {sfx_tags}
</div>
<script>
const CAPS = {cap_js};
const TOTAL = {total:.3f};
window.__timelines = [];

function setCap(t) {{
  const el = document.getElementById('cap');
  let text = '';
  for (const c of CAPS) {{
    if (t >= c.start && t < c.end) {{ text = c.text; break; }}
  }}
  el.textContent = text;
}}

function build() {{
  const tl = gsap.timeline({{paused:true}});
  window.__timelines.push(tl);
  const flash = () => {{ gsap.fromTo('#flash', {{opacity:0.55}}, {{opacity:0, duration:0.18}}); }};

  // HOOK 0-18
  tl.set('#sc-hook', {{opacity:1}});
  tl.fromTo('#ht', {{scale:0.5, opacity:0, x:-80}}, {{scale:1.05, opacity:1, x:0, duration:0.55, ease:'back.out(2)'}}, 0.1);
  tl.to('#ht', {{scale:1, duration:0.2}}, 0.65);
  tl.fromTo('#hs', {{y:50, opacity:0}}, {{y:0, opacity:1, duration:0.45}}, 0.7);
  tl.fromTo('#stamp', {{scale:0, rotation:-40}}, {{scale:1.15, rotation:-18, duration:0.4, ease:'back.out(3)'}}, 1.1);
  tl.to('#stamp', {{scale:1, duration:0.15}}, 1.5);
  tl.call(flash, null, 1.1);
  tl.fromTo('#c1', {{y:90, opacity:0, rotateX:40}}, {{y:0, opacity:1, rotateX:0, duration:0.4}}, 2.2);
  tl.fromTo('#c2', {{y:90, opacity:0, rotateX:40}}, {{y:0, opacity:1, rotateX:0, duration:0.4}}, 2.7);
  tl.fromTo('#c3', {{y:90, opacity:0, rotateX:40}}, {{y:0, opacity:1, rotateX:0, duration:0.4}}, 3.2);
  tl.fromTo('#k1', {{scale:2, opacity:0}}, {{scale:1, opacity:1, duration:0.35}}, 4.0);
  tl.to('#k1', {{opacity:0, y:-40, duration:0.4}}, 5.2);
  tl.fromTo('#k2', {{x:-100, opacity:0}}, {{x:0, opacity:1, duration:0.4}}, 6.0);
  tl.to('#k2', {{opacity:0, duration:0.3}}, 8.0);
  // punchy card shake
  tl.to('#c1,#c2,#c3', {{x:'+=8', duration:0.06, yoyo:true, repeat:5}}, 9.0);
  tl.to('#ht', {{color:'#ff6b8a', duration:0.2}}, 12.0);
  tl.to('#ht', {{color:'#f4f7ff', duration:0.2}}, 12.4);

  // METAPHOR 18-36
  tl.to('#sc-hook', {{opacity:0, duration:0.25}}, 17.7);
  tl.set('#sc-meta', {{opacity:1}}, 17.95);
  tl.fromTo('#ml', {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.35}}, 18.1);
  tl.fromTo('#horse1', {{opacity:0, x:-120}}, {{opacity:1, x:0, duration:0.5, ease:'power3.out'}}, 18.4);
  tl.fromTo('#horse2', {{opacity:0, x:-100}}, {{opacity:1, x:0, duration:0.45}}, 18.7);
  tl.fromTo('#rein,#rein2', {{opacity:0, strokeDashoffset:400}}, {{opacity:1, duration:0.4}}, 19.2);
  tl.fromTo('#carriage', {{opacity:0, x:150, scale:0.8}}, {{opacity:1, x:0, scale:1, duration:0.55, ease:'back.out(1.6)'}}, 19.8);
  tl.fromTo('#driver', {{opacity:0, y:-80, scale:0.5}}, {{opacity:1, y:0, scale:1, duration:0.45, ease:'back.out(2)'}}, 20.6);
  tl.call(flash, null, 20.6);
  // gallop motion loop (not ambient audio — visual kinetic)
  tl.to('#horse1,#horse2', {{y:'+=12', duration:0.18, yoyo:true, repeat:17, ease:'sine.inOut'}}, 21.0);
  tl.to('#carriage,#driver', {{y:'+=6', duration:0.18, yoyo:true, repeat:17, ease:'sine.inOut'}}, 21.0);
  // chips rapid fire
  const chips = gsap.utils.toArray('#map .chip');
  chips.forEach((el, i) => {{
    tl.fromTo(el, {{scale:0.3, opacity:0}}, {{scale:1.1, opacity:1, duration:0.28, ease:'back.out(3)'}}, 24.0 + i * 0.28);
    tl.to(el, {{scale:1, duration:0.1}}, 24.25 + i * 0.28);
  }});
  tl.to('#rein,#rein2', {{attr:{{stroke:'#ff6'}}, duration:0.15, yoyo:true, repeat:3}}, 28.5);
  tl.call(flash, null, 30.0);
  tl.fromTo('#k1', {{left:600, top:80, scale:0.5, opacity:0, color:'#ffd27a'}}, {{scale:1.2, opacity:1, duration:0.35}}, 31.0);
  tl.to('#k1', {{opacity:0, duration:0.3}}, 33.0);

  // AUTOCAR 36-61
  tl.to('#sc-meta', {{opacity:0, duration:0.3}}, 35.7);
  tl.set('#sc-auto', {{opacity:1}}, 35.95);
  tl.fromTo('#p1', {{x:-80, opacity:0}}, {{x:0, opacity:1, duration:0.45}}, 36.2);
  tl.fromTo('#p2', {{x:80, opacity:0}}, {{x:0, opacity:1, duration:0.45}}, 36.7);
  tl.fromTo('#vs', {{scale:0, opacity:0, rotation:-20}}, {{scale:1.2, opacity:1, rotation:0, duration:0.4, ease:'back.out(3)'}}, 37.5);
  tl.to('#vs', {{scale:1, duration:0.15}}, 37.9);
  tl.call(flash, null, 37.5);
  tl.to('#p1', {{borderColor:'#f66', duration:0.3}}, 42.0);
  tl.to('#p2', {{borderColor:'#5f6', boxShadow:'0 0 40px #5f68', duration:0.4}}, 46.0);
  tl.to('#p2', {{scale:1.04, duration:0.3, yoyo:true, repeat:3}}, 50.0);
  tl.fromTo('#k2', {{left:760, top:900, opacity:0, scale:0.8}}, {{opacity:1, scale:1, duration:0.4}}, 54.0);
  tl.to('#k2', {{opacity:0, duration:0.3}}, 57.0);
  tl.to('#sc-auto', {{opacity:0.9, duration:0.5}}, TOTAL - 1.2);

  // captions + SFX sync via ticker
  tl.eventCallback('onUpdate', () => {{
    const t = tl.time();
    setCap(t);
  }});

  // SFX schedule
  document.querySelectorAll('audio.sfx').forEach(a => {{
    const at = parseFloat(a.dataset.at);
    const vol = parseFloat(a.dataset.vol || '0.5');
    tl.call(() => {{
      try {{ a.volume = vol; a.currentTime = 0; a.play(); }} catch(e) {{}}
    }}, null, at);
  }});

  // VO
  const vo = document.getElementById('vo');
  tl.call(() => {{ try {{ vo.currentTime = 0; vo.play(); }} catch(e) {{}} }}, null, 0);

  return tl;
}}

document.addEventListener('DOMContentLoaded', () => {{
  const tl = build();
  // HyperFrames looks for window.__timelines
  window.__proofReady = true;
  // For local preview
  if (location.search.includes('play=1')) tl.play(0);
}});
</script>
</body>
</html>
"""
    (PROOF / "index.html").write_text(html_doc, encoding="utf-8")


def write_project(total: float) -> None:
    # Minimal HyperFrames project.json if used by remake tooling
    proj = {
        "name": "ch01-long-dense-proof",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration": total,
        "entry": "index.html",
    }
    (PROOF / "project.json").write_text(json.dumps(proj, ensure_ascii=False, indent=2), encoding="utf-8")
    (PROOF / "compositions" / "main.json").write_text(
        json.dumps({"id": "main", "duration": total, "html": "../index.html"}, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    ensure()
    synth_sfx()
    mapping, total = build_vo()
    caps = map_caps(mapping)
    write_html(caps, total)
    write_project(total)
    meta = {"segments": SEGS, "total": total, "caps": len(caps), "mapping": mapping}
    (PROOF / "proof-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK proof ready total={total:.2f}s caps={len(caps)} html={PROOF/'index.html'}")


if __name__ == "__main__":
    main()
