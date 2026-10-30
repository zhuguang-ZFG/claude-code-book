# -*- coding: utf-8 -*-
"""Densify full ch01 remake → index + compositions + SFX. No meta words. Keep captions + 云扬 VO."""
from __future__ import annotations
import html, json, math, struct, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMP = ROOT / "compositions"
SFX = ROOT / "assets" / "sfx"
TRANS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
TOTAL = 1148.352

# denser beats (~5–8s); book content only — no 吸粉/冲击 meta
BLOCKS = [
  {"id":"b01_hook","title":"开场钩子","start":0.0,"end":43.896,
   "huashu":[("01_hook_glue.mp4",8.0,7.0)],
   "beats":[
     (0.0,"series","驭者·Agent Harness","第 01 讲 · 打地基"),
     (5.0,"cards","马车 = 系统","缰绳 = Harness · 骏马 = 模型"),
     (12.0,"contrast","Chatbot 时代","人当系统胶水"),
     (20.0,"contrast","Agent 时代","自己编排工具调用"),
     (26.0,"pause","为什么不能只包一层 API？","先停 3 秒：边界 · 失败 · 权限谁来管？"),
     (32.0,"quiz","人在 Chatbot 时代更像什么？","A 驭者  ·  B 系统胶水  ·  C 旁观者"),
     (38.0,"stamp","御者 · 你来握缰","模型是马，Harness 是缰绳和鞍具"),
   ]},
  {"id":"b02_paradigm","title":"§1.1 范式转移","start":43.896,"end":265.32,
   "huashu":[("02_llm_roles.mp4",50.0,7.0),("03_six_challenges.mp4",120.0,7.5),("04_harness_def.mp4",200.0,7.0)],
   "beats":[
     (0.0,"section","§1.1 范式转移","LLM：对话伙伴 → 推理引擎"),
     (12.0,"card","从 Chatbot 到 Agent","工具调用打开边界"),
     (20.8,"chariot","驭者隐喻","模型是马 · Harness 是缰绳和鞍具"),
     (36.0,"card","Tool Use","打开边界 · 工程挑战随之而来"),
     (55.0,"card","六大工程挑战","流式 · 权限 · 上下文 · 恢复 · 持久化 · 扩展"),
     (78.0,"card","简单封装的幻觉","while 循环假设理想世界"),
     (92.0,"quiz","简单 while(true) 调用 API，够不够？","猜一猜：理想世界假设会在哪一步碎掉？"),
     (100.0,"warn","反模式","裸 while(true){ callAPI }"),
     (120.0,"card","真正的 Harness","正面硬刚失败 · 权限 · 上下文"),
     (145.0,"card","统一框架","把散落问题系统收进来"),
     (170.0,"card","Agent Harness","运行时框架，不是外套壳"),
     (195.0,"card","定义落地","安全 · 可靠 · 高效与外部交互"),
     (215.0,"section","准备看架构","从示例项目读五模块骨架"),
   ]},
  {"id":"b03_arch","title":"§1.2 全景架构","start":265.32,"end":568.632,
   "huashu":[("05_arch_layers.mp4",80.0,7.5),("06_tech_stack.mp4",180.0,7.0)],
   "beats":[
     (0.0,"vs_auto","遥控器 vs 自动驾驶","简单封装 vs Agent Harness"),
     (16.0,"pause","你的封装更像哪边？","遥控器：按一下动一下 · 自动驾驶：自主规划与边界"),
     (22.0,"section","§1.2 全景架构","从 Copilot 到 Claude Code / MCP"),
     (40.0,"number","1,884","个 TypeScript 文件"),
     (55.0,"number","512,664","行代码"),
     (75.0,"card","不是炫耀体量","复杂度来自工程现实"),
     (100.0,"layers","五模块骨架","Entry → QueryEngine → Loop → Tools → Ext"),
     (130.0,"card","Entry","启动 · 配置 · 会话入口"),
     (155.0,"card","QueryEngine","请求编排与流式输出"),
     (180.0,"card","Loop","主循环 · 工具调用回合"),
     (205.0,"card","Tools","权限四阶段 · 55 个工具"),
     (235.0,"stack","技术栈","Bun · React+Ink · Zod v4 · SDK"),
     (265.0,"card","可维护性","模块化是 Harness 的关键保障"),
   ]},
  {"id":"b04_principles","title":"§1.3 五大原则","start":568.632,"end":910.464,
   "huashu":[("07_p_async.mp4",20.0,7.0),("08_p_security.mp4",90.0,7.5),("09_p_cache.mp4",160.0,7.0),("10_p_progressive.mp4",230.0,7.5),("11_p_immutable.mp4",300.0,7.0)],
   "beats":[
     (0.0,"section","§1.3 五大原则","红线，不是口号"),
     (8.0,"quiz","五大原则里，哪条最容易被当成口号？","流式 · 安全 · 缓存 · 扩展 · 不可变 —— 先选一条"),
     (18.0,"p","1 · 异步流式优先","Async Generator First"),
     (40.0,"card","流式体验","首包延迟 · 可取消 · 背压"),
     (70.0,"p","2 · 安全边界内嵌","Security at the Perimeter"),
     (100.0,"card","权限四阶段","声明 · 校验 · 执行 · 审计"),
     (130.0,"p","3 · 缓存感知设计","Cache-Aware Architecture"),
     (160.0,"card","上下文成本","前缀稳定 · 复用命中"),
     (195.0,"p","4 · 渐进式能力扩展","Tool → Skill → Plugin → MCP"),
     (230.0,"card","扩展阶梯","先工具，再技能，再协议"),
     (265.0,"p","5 · 不可变状态流转","Immutable State Flow"),
     (300.0,"card","状态可追溯","回合快照 · 恢复点"),
     (330.0,"section","原则合在一起","构成 Harness 的工程红线"),
   ]},
  {"id":"b05_practice","title":"实战练习速览","start":910.464,"end":1056.912,
   "huashu":[("12_doctor_flow.mp4",40.0,7.0)],
   "beats":[
     (0.0,"section","实战练习速览","动手验证 Harness"),
     (10.0,"pause","动手前先问自己","你会先用哪条命令确认环境就绪？"),
     (18.0,"code","npm i -g @anthropic-ai/claude-code","安装 CLI"),
     (35.0,"code","claude --version","确认环境就绪"),
     (55.0,"code","/doctor","环境 · 权限 · MCP · API · 文件系统"),
     (80.0,"flow","一次工具调用","思考 → GlobTool → 回复"),
     (110.0,"card","观察 Harness","权限提示 · 流式输出 · 工具结果回流"),
     (135.0,"section","练习目的","亲手摸到运行时边界"),
   ]},
  {"id":"b06_outro","title":"总结 + 片尾","start":1056.912,"end":1148.352,
   "huashu":[("13_outro.mp4",5.0,7.0)],
   "beats":[
     (0.0,"section","本讲收束","四句记住"),
     (8.0,"quiz","合上书之前","用一句话：Harness 到底解决什么问题？"),
     (16.0,"sum","范式已转移","助手 → 自主智能体 · 地基是 Harness"),
     (32.0,"sum","Harness 是工程系统","流式 · 权限 · 上下文 · 恢复 · 持久化"),
     (52.0,"sum","五模块是骨架","五原则是红线"),
     (68.0,"next","第 02 讲预告","对话主循环 AsyncGenerator"),
     (82.0,"credit","基于开源书稿","驭者·Agent Harness · 小电讲电路"),
   ]},
]

FONT = """
@font-face { font-family: 'Noto Sans SC'; src: local('Noto Sans SC'), local('NotoSansSC-Regular'), local('Microsoft YaHei'); font-weight: 100 900; }
@font-face { font-family: 'Microsoft YaHei'; src: local('Microsoft YaHei'), local('Microsoft YaHei UI'); }
"""

def esc(s: str) -> str:
    return html.escape(s, quote=True)

def ensure_sfx() -> None:
    SFX.mkdir(parents=True, exist_ok=True)
    specs = {
        "whoosh": (0.28, 900), "impact": (0.22, 80), "rein_snap": (0.12, 2200),
        "gallop": (0.55, 90), "ui_blip": (0.08, 1400), "punch": (0.18, 60),
    }
    for name, (dur, f0) in specs.items():
        path = SFX / f"{name}.wav"
        if path.exists() and path.stat().st_size > 500:
            continue
        sr = 44100
        n = int(sr * dur)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 8)
            if name == "gallop":
                hit = 0.0
                for k in (0.0, 0.16, 0.32, 0.45):
                    dt = t - k
                    if 0 <= dt < 0.09:
                        hit += math.exp(-dt * 35) * math.sin(2 * math.pi * f0 * dt)
                        if dt < 0.01:
                            hit += (1 - dt / 0.01) * 0.7
                sample = max(-1.0, min(1.0, hit))
            elif name == "whoosh":
                freq = f0 + (180 - f0) * (t / dur)
                sample = env * 0.45 * math.sin(2 * math.pi * freq * t)
            elif name == "rein_snap":
                noise = ((i * 1103515245 + 12345) & 0x7FFF) / 32768.0 - 0.5
                sample = env * (0.35 * math.sin(2 * math.pi * f0 * t) + 0.4 * noise)
            else:
                sample = env * 0.6 * math.sin(2 * math.pi * f0 * t)
            frames += struct.pack("<h", int(max(-1, min(1, sample)) * 30000))
        with wave.open(str(path), "w") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(frames)



CSS = FONT + r"""
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#0b0d10}
body{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;color:#e8ecf1}
#root,.scene{position:absolute;inset:0;background:
  radial-gradient(ellipse at 30% 20%,#1a2744 0%,transparent 55%),
  radial-gradient(ellipse at 80% 70%,#2a1030 0%,transparent 50%),
  linear-gradient(160deg,#070b14,#0d1528 45%,#120a18)}
.flash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;z-index:40}
.grain{position:absolute;inset:0;opacity:.05;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.vignette{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.55) 100%)}
.series-bar{position:absolute;top:48px;left:64px;z-index:6}
.series-in{display:flex;align-items:center;gap:16px;opacity:0}
.badge{width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,#f0a050,#c45c1a);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:22px;color:#111}
.series-name{font-size:22px;letter-spacing:.08em;color:#c9d2de}
.series-sub{font-size:16px;color:#7a8799;margin-top:4px}
.panel{position:absolute;left:64px;right:64px;top:140px;bottom:140px}
.panel-body{display:flex;flex-direction:column;justify-content:center;gap:22px;height:100%;opacity:0}
.kicker{font-size:20px;letter-spacing:.2em;color:#f0a050;opacity:0}
.h1{font-size:60px;font-weight:800;line-height:1.15;opacity:0;max-width:1500px;text-shadow:0 0 28px #4af5}
.h2{font-size:34px;font-weight:400;color:#aeb8c6;opacity:0;max-width:1300px;line-height:1.45}
.big-num{font-size:120px;font-weight:800;color:#f0a050;letter-spacing:-.02em;opacity:0;line-height:1;text-shadow:0 0 40px #f0a05066}
.layers-row{display:flex;gap:12px;opacity:0}
.layer{flex:1;padding:22px 12px;text-align:center;border-radius:12px;background:#161c24;border:1px solid #2a3340;font-size:20px;font-weight:600;opacity:0}
.card-row{display:flex;gap:22px;opacity:0;margin-top:12px}
.mini{flex:1;padding:28px 22px;border-radius:16px;background:linear-gradient(145deg,#162038,#0c1220);border:2px solid #33aaff;font-size:30px;font-weight:700;opacity:0;box-shadow:0 0 24px #33aaff44}
.stamp{width:240px;height:240px;border:10px solid #ff3b5c;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:900;color:#ff3b5c;transform:rotate(-18deg);opacity:0;box-shadow:0 0 40px #ff3b5c88;margin-top:18px}
.vs-grid{display:grid;grid-template-columns:1fr 1fr;gap:36px;opacity:0}
.vpanel{background:linear-gradient(160deg,#101828,#0a101c);border:2px solid #55ccff;border-radius:22px;padding:36px;min-height:280px;opacity:0}
.vpanel.r{border-color:#ff99aa}
.vpanel h3{font-size:40px;margin-bottom:16px}
.vpanel p{font-size:28px;line-height:1.5;color:#cde}
.vs{font-size:96px;font-weight:900;text-align:center;opacity:0;text-shadow:0 0 36px #f40;margin:8px 0}
.chariot-wrap{position:absolute;left:40px;right:40px;top:120px;bottom:120px;opacity:0}
.map-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
.chip{padding:10px 18px;background:#1a1230;border:2px solid #c9a0ff;border-radius:999px;font-size:22px;opacity:0;box-shadow:0 0 14px #a0f6}
.huashu-wrap{position:absolute;inset:0;pointer-events:none;z-index:8}
.huashu-in{width:100%;height:100%;opacity:0}
.huashu-in video{width:100%;height:100%;object-fit:cover}

.wm-fixed{position:absolute;top:28px;right:36px;z-index:60;text-align:right;opacity:0.72;pointer-events:none;
  font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;letter-spacing:.06em}
.wm-brand{font-size:22px;font-weight:700;color:#e8ecf1;text-shadow:0 1px 6px rgba(0,0,0,.65)}
.wm-series{font-size:15px;color:#f0a050;margin-top:4px;text-shadow:0 1px 4px rgba(0,0,0,.55)}
.wm-mark{font-size:12px;color:#7a8799;margin-top:6px;letter-spacing:.18em}
.quiz-card{background:linear-gradient(145deg,#1a1430,#0c1220);border:3px solid #f0a050;border-radius:20px;
  padding:36px 40px;max-width:1400px;box-shadow:0 0 40px #f0a05055}
.quiz-tag{display:inline-block;padding:6px 16px;border-radius:999px;background:#f0a050;color:#1a1000;
  font-weight:800;font-size:22px;letter-spacing:.12em;margin-bottom:18px}
.pause-card{background:linear-gradient(145deg,#101828,#0a101c);border:3px dashed #66ccff;border-radius:20px;
  padding:36px 40px;max-width:1400px;box-shadow:0 0 28px #66ccff44}
.pause-tag{display:inline-block;padding:6px 16px;border-radius:999px;background:#66ccff;color:#061018;
  font-weight:800;font-size:22px;letter-spacing:.12em;margin-bottom:18px}
.quiz-ans{font-size:28px;color:#7dffb3;margin-top:18px;opacity:0;font-weight:600}
"""

CHARIOT_SVG = r'''
<svg viewBox="0 0 1600 520" width="1600" height="520" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#ffe29a"/><stop offset="100%" stop-color="#c9832a"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <line x1="40" y1="440" x2="1560" y2="440" stroke="#334455" stroke-width="4" opacity="0.5"/>
  <g class="horse1" filter="url(#glow)" opacity="0">
    <ellipse cx="300" cy="340" rx="100" ry="42" fill="#8b5a2b"/>
    <ellipse cx="390" cy="305" rx="48" ry="32" fill="#a0672f"/>
    <rect x="240" y="365" width="12" height="60" fill="#5a3a1a" rx="3"/>
    <rect x="285" y="365" width="12" height="60" fill="#5a3a1a" rx="3"/>
    <rect x="340" y="365" width="12" height="60" fill="#5a3a1a" rx="3"/>
    <rect x="375" y="365" width="12" height="60" fill="#5a3a1a" rx="3"/>
    <text x="240" y="250" fill="#ffd27a" font-size="32" font-weight="700">骏马·模型</text>
  </g>
  <g class="horse2" filter="url(#glow)" opacity="0">
    <ellipse cx="520" cy="350" rx="90" ry="38" fill="#6e4520"/>
    <ellipse cx="600" cy="315" rx="44" ry="28" fill="#855528"/>
    <rect x="470" y="375" width="12" height="55" fill="#4a3015" rx="3"/>
    <rect x="510" y="375" width="12" height="55" fill="#4a3015" rx="3"/>
    <rect x="555" y="375" width="12" height="55" fill="#4a3015" rx="3"/>
    <rect x="585" y="375" width="12" height="55" fill="#4a3015" rx="3"/>
  </g>
  <path class="rein" d="M400 300 C520 260, 700 245, 880 285" stroke="#e8c36a" stroke-width="8" fill="none" opacity="0"/>
  <path class="rein2" d="M620 310 C740 275, 820 270, 900 295" stroke="#e8c36a" stroke-width="6" fill="none" opacity="0"/>
  <g class="carriage" filter="url(#glow)" opacity="0">
    <rect x="920" y="250" width="300" height="140" rx="16" fill="url(#gold)" stroke="#ffffff66" stroke-width="3"/>
    <text x="990" y="330" fill="#2a1500" font-size="36" font-weight="900">舆 · 车厢</text>
    <line x1="920" y1="320" x2="700" y2="340" stroke="#c9a05a" stroke-width="12" stroke-linecap="round"/>
    <circle cx="980" cy="400" r="42" fill="#222" stroke="#aaa" stroke-width="7"/>
    <circle cx="1160" cy="400" r="42" fill="#222" stroke="#aaa" stroke-width="7"/>
    <circle cx="980" cy="400" r="9" fill="#ddd"/><circle cx="1160" cy="400" r="9" fill="#ddd"/>
    <text x="940" y="480" fill="#99ccff" font-size="26">辐 · 轮</text>
    <rect x="1035" y="232" width="70" height="20" rx="5" fill="#66ccff"/>
    <text x="1040" y="222" fill="#66ccff" font-size="24">轼</text>
    <rect x="1190" y="385" width="24" height="34" rx="3" fill="#ff6666"/>
    <text x="1220" y="408" fill="#ff8888" font-size="24">辖</text>
    <text x="720" y="310" fill="#e8c36a" font-size="24">辕</text>
  </g>
  <g class="driver" filter="url(#glow)" opacity="0">
    <circle cx="1000" cy="200" r="32" fill="#f0c090"/>
    <rect x="972" y="230" width="56" height="80" rx="10" fill="#2a5080"/>
    <text x="900" y="165" fill="#77ccff" font-size="34" font-weight="900">御者 · 你</text>
  </g>
</svg>
'''



def beat_html(kind: str, title: str, sub: str, bid: str) -> str:
    t, s = esc(title), esc(sub)
    if kind == "series":
        return f'''<div class="series-bar" data-beat="{bid}"><div class="series-in" id="{bid}">
          <div class="badge">01</div><div><div class="series-name">{t}</div><div class="series-sub">{s}</div></div>
        </div></div>'''
    if kind == "chariot":
        return f'''<div class="chariot-wrap" id="{bid}" data-beat="{bid}">
          <div class="kicker">前言隐喻 · 落地本书</div>
          <div class="h1" style="font-size:42px;margin:8px 0 12px">{t}</div>
          <div class="h2" style="font-size:26px;margin-bottom:8px">{s}</div>
          {CHARIOT_SVG}
          <div class="map-row">
            <span class="chip">御者 = 你 / 应用</span>
            <span class="chip">骏马 = LLM</span>
            <span class="chip">缰绳+鞍具 = Harness</span>
            <span class="chip">舆辕辐軎辖轼 = 运行时构件</span>
          </div>
        </div>'''
    if kind == "vs_auto":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker">隐喻对照</div>
          <div class="vs-grid">
            <div class="vpanel"><h3>遥控器</h3><p>简单封装<br/>人按一下，才动一下</p></div>
            <div class="vpanel r"><h3>自动驾驶</h3><p>Agent Harness<br/>自主规划 · 工具 · 边界</p></div>
          </div>
          <div class="vs">VS</div>
          <div class="h2">{s}</div>
        </div></div>'''
    if kind == "layers":
        layers = ["Entry","QueryEngine","Loop","Tools","Ext"]
        cells = "".join(f'<div class="layer">{esc(x)}</div>' for x in layers)
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker">{s}</div><div class="h1">{t}</div>
          <div class="layers-row">{cells}</div>
        </div></div>'''
    if kind == "number":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker">{s}</div><div class="big-num">{t}</div>
        </div></div>'''
    if kind == "quiz":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="quiz-card"><div class="quiz-tag">猜一猜</div>
          <div class="h1" style="opacity:1;font-size:48px">{t}</div>
          <div class="h2" style="opacity:1">{s}</div>
          <div class="quiz-ans" id="{bid}-ans">答案稍候揭晓 · 先自己想 3 秒</div></div>
        </div></div>'''
    if kind == "pause":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="pause-card"><div class="pause-tag">停一下 · 想一想</div>
          <div class="h1" style="opacity:1;font-size:48px">{t}</div>
          <div class="h2" style="opacity:1">{s}</div></div>
        </div></div>'''
    if kind == "stamp":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker">{s}</div><div class="h1">{t}</div>
          <div class="stamp">御</div>
        </div></div>'''
    if kind == "cards":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker">隐喻对照</div><div class="h1">{t}</div>
          <div class="card-row"><div class="mini">{s}</div></div>
        </div></div>'''
    if kind == "code":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker">{s}</div>
          <div class="h1" style="font-family:Consolas,monospace;font-size:48px;color:#7dffb3">{t}</div>
        </div></div>'''
    if kind == "warn":
        return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
          <div class="kicker" style="color:#ff6688">反模式</div>
          <div class="h1" style="color:#ff99aa">{t}</div>
          <div class="h2" style="font-family:Consolas,monospace">{s}</div>
        </div></div>'''
    # default: section/card/contrast/question/p/sum/next/credit/flow/stack
    return f'''<div class="panel" data-beat="{bid}"><div class="panel-body" id="{bid}">
      <div class="kicker">{esc(kind.upper() if kind in ("p","sum","next","credit","flow","stack") else "KEY")}</div>
      <div class="h1">{t}</div><div class="h2">{s}</div>
    </div></div>'''


def beat_tl_lines(kind: str, bid: str, t0: float, hold: float) -> list:
    """Absolute-time GSAP lines for a single composition timeline."""
    out_at = t0 + max(hold - 0.35, hold * 0.85)
    lines = []
    if kind == "series":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0,y:-30}}, {{opacity:1,y:0,duration:0.5,ease:"power3.out"}}, {t0:.3f});',
            f'tl.to("#{bid}", {{opacity:0,y:-20,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    if kind == "chariot":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0,scale:0.96}}, {{opacity:1,scale:1,duration:0.4,ease:"power2.out"}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .kicker", {{opacity:0,y:12}}, {{opacity:1,y:0,duration:0.35}}, {t0+0.1:.3f});',
            f'tl.fromTo("#{bid} .h1", {{opacity:0,y:20}}, {{opacity:1,y:0,duration:0.4}}, {t0+0.2:.3f});',
            f'tl.fromTo("#{bid} .horse1", {{opacity:0,x:-40}}, {{opacity:1,x:0,duration:0.45,ease:"power2.out"}}, {t0+0.35:.3f});',
            f'tl.fromTo("#{bid} .horse2", {{opacity:0,x:-30}}, {{opacity:1,x:0,duration:0.4}}, {t0+0.5:.3f});',
            f'tl.fromTo("#{bid} .carriage", {{opacity:0,x:50}}, {{opacity:1,x:0,duration:0.45}}, {t0+0.55:.3f});',
            f'tl.fromTo("#{bid} .driver", {{opacity:0,y:20}}, {{opacity:1,y:0,duration:0.35}}, {t0+0.7:.3f});',
            f'tl.fromTo("#{bid} .rein, #{bid} .rein2", {{opacity:0}}, {{opacity:1,duration:0.3}}, {t0+0.85:.3f});',
            f'tl.fromTo("#{bid} .chip", {{opacity:0,y:16,scale:0.9}}, {{opacity:1,y:0,scale:1,duration:0.3,stagger:0.08}}, {t0+1.0:.3f});',
            f'tl.to("#{bid} .horse1", {{x:8,duration:0.25,yoyo:true,repeat:5,ease:"sine.inOut"}}, {t0+1.2:.3f});',
            f'tl.to("#{bid} .horse2", {{x:6,duration:0.25,yoyo:true,repeat:5,ease:"sine.inOut"}}, {t0+1.28:.3f});',
            f'tl.to("#{bid}", {{opacity:0,scale:0.98,duration:0.35}}, {out_at:.3f});',
        ]
        return lines
    if kind == "vs_auto":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.25}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .vpanel", {{opacity:0,y:30,scale:0.92}}, {{opacity:1,y:0,scale:1,duration:0.45,stagger:0.12,ease:"back.out(1.4)"}}, {t0+0.1:.3f});',
            f'tl.fromTo("#{bid} .vs", {{opacity:0,scale:2.2}}, {{opacity:1,scale:1,duration:0.4,ease:"back.out(2)"}}, {t0+0.5:.3f});',
            f'tl.fromTo("#{bid} .h2", {{opacity:0,y:16}}, {{opacity:1,y:0,duration:0.35}}, {t0+0.7:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    if kind == "layers":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.25}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .kicker", {{opacity:0,y:10}}, {{opacity:1,y:0,duration:0.3}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .h1", {{opacity:0,y:24,scale:0.96}}, {{opacity:1,y:0,scale:1,duration:0.4,ease:"power3.out"}}, {t0+0.1:.3f});',
            f'tl.fromTo("#{bid} .layers-row", {{opacity:0}}, {{opacity:1,duration:0.2}}, {t0+0.25:.3f});',
            f'tl.fromTo("#{bid} .layer", {{opacity:0,y:28}}, {{opacity:1,y:0,duration:0.35,stagger:0.08,ease:"power2.out"}}, {t0+0.3:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    if kind == "quiz":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.2}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .quiz-card", {{opacity:0,scale:0.9,y:24}}, {{opacity:1,scale:1,y:0,duration:0.45,ease:"back.out(1.5)"}}, {t0:.3f});',
            f'tl.fromTo("#{bid}-ans", {{opacity:0,y:10}}, {{opacity:1,y:0,duration:0.35}}, {t0+2.2:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    if kind == "pause":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.2}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .pause-card", {{opacity:0,scale:0.92}}, {{opacity:1,scale:1,duration:0.4,ease:"power2.out"}}, {t0:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    if kind == "stamp":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.2}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .h1", {{opacity:0,y:30}}, {{opacity:1,y:0,duration:0.4}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .stamp", {{opacity:0,scale:2.5,rotation:-40}}, {{opacity:1,scale:1,rotation:-18,duration:0.5,ease:"back.out(2)"}}, {t0+0.35:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    if kind == "number":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.2}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .big-num", {{opacity:0,scale:0.5}}, {{opacity:1,scale:1,duration:0.55,ease:"back.out(1.6)"}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .kicker", {{opacity:0,y:12}}, {{opacity:1,y:0,duration:0.3}}, {t0+0.2:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.3}}, {out_at:.3f});',
        ]
        return lines
    lines += [
        f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.2}}, {t0:.3f});',
        f'tl.fromTo("#{bid} .kicker", {{opacity:0,x:-20}}, {{opacity:1,x:0,duration:0.3}}, {t0:.3f});',
        f'tl.fromTo("#{bid} .h1", {{opacity:0,y:28,scale:0.94}}, {{opacity:1,y:0,scale:1,duration:0.45,ease:"power3.out"}}, {t0+0.08:.3f});',
        f'tl.fromTo("#{bid} .h2", {{opacity:0,y:18}}, {{opacity:1,y:0,duration:0.35}}, {t0+0.28:.3f});',
        f'tl.to("#{bid}", {{opacity:0,y:-12,duration:0.28}}, {out_at:.3f});',
    ]
    return lines


def write_block(blk: dict) -> float:
    bid = blk["id"]
    dur = blk["end"] - blk["start"]
    beats = blk["beats"]
    holds = []
    for i, (t0, kind, title, sub) in enumerate(beats):
        t1 = beats[i + 1][0] if i + 1 < len(beats) else dur
        holds.append(max(3.5, t1 - t0))

    parts = []
    anim = []

    for i, ((t0, kind, title, sub), hold) in enumerate(zip(beats, holds)):
        el_id = f"{bid}_beat{i}"
        parts.append(
            f'<div id="{el_id}_wrap" class="beat clip" data-start="{t0:.3f}" data-duration="{hold:.3f}" data-track-index="1" '
            f'style="position:absolute;inset:0">{beat_html(kind, title, sub, el_id)}</div>'
        )
        anim.extend(beat_tl_lines(kind, el_id, t0, hold))
        if kind in ("chariot", "vs_auto", "stamp", "number", "section", "quiz", "pause"):
            fid = f"{bid}_flash{i}"
            parts.append(
                f'<div class="flash clip" id="{fid}" data-start="{t0:.3f}" data-duration="0.35" data-track-index="5"></div>'
            )
            anim.append(f'tl.fromTo("#{fid}", {{opacity:0}}, {{opacity:0.35,duration:0.06}}, {t0:.3f});')
            anim.append(f'tl.to("#{fid}", {{opacity:0,duration:0.25}}, {t0+0.06:.3f});')

    for hi, (fname, t0, hdur) in enumerate(blk.get("huashu", [])):
        hid = f"hv_{bid}_{hi}"
        vid = f"{hid}_vid"
        parts.append(
            f'<div id="{hid}" class="huashu-wrap" style="position:absolute;inset:0;pointer-events:none;z-index:8">'
            f'<div class="huashu-in" id="{hid}-in" style="opacity:0;width:100%;height:100%">'
            f'<video id="{vid}" src="../assets/huashu/{fname}" muted playsinline '
            f'data-start="{t0:.3f}" data-duration="{hdur:.3f}" data-has-audio="false" '
            f'style="width:100%;height:100%;object-fit:cover"></video></div></div>'
        )
        anim.append(f'tl.to("#{hid}-in", {{opacity:1, duration:0.4}}, {t0:.3f});')
        anim.append(f'tl.to("#{hid}-in", {{opacity:0, duration:0.4}}, {t0+hdur-0.4:.3f});')

    html_doc = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" class="clip" data-composition-id="{bid}" style="position:absolute;inset:0;width:1920px;height:1080px" data-start="0" data-duration="{dur:.3f}" data-width="1920" data-height="1080" data-fps="30">
  <div class="series-bar clip" id="series" data-start="0" data-duration="{dur:.3f}" data-track-index="0"><div class="series-in" id="series-in"><div class="badge">01</div><div><div class="series-name">驭者·Agent Harness</div><div class="series-sub">{esc(blk["title"])}</div></div></div></div>
  {"".join(parts)}
  <div class="grain"></div><div class="vignette"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#series-in", {{opacity:0,y:-16}}, {{opacity:1,y:0,duration:0.45}}, 0.1);
{chr(10).join(anim)}
window.__timelines["{bid}"] = tl;
</script>
</body></html>
"""
    (COMP / f"{bid}.html").write_text(html_doc, encoding="utf-8")
    print("wrote", bid, "dur", round(dur, 2), "beats", len(beats), "huashu", len(blk.get("huashu", [])))
    return dur


def tokenize_zh(text: str):
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
    return [x for x in tokens if x != ""]


def write_captions() -> None:
    parts = []
    anim = []
    for i, w in enumerate(TRANS):
        text = (w.get("text") or "").strip()
        if not text:
            continue
        start = max(0.1, float(w["start"]))
        end = float(w["end"])
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
            elif all("\u4e00" <= c <= "\u9fff" or "\u3400" <= c <= "\u4dbf" for c in tok):
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
            f'tl.to("#{cid}-in", {{opacity:0, duration:0.12}}, {max(start, end-0.12):.3f});',
        ]
        for ki, tok in enumerate(toks):
            kid = f"{cid}-k{ki}"
            spans.append(f'<span class="kw" id="{kid}">{esc(tok)}</span>')
            t_on = start + 0.08 + usable * (cursor / tw)
            step = max(0.045, usable * (weights[ki] / tw) * 0.85)
            local_anim.append(
                f'tl.fromTo("#{kid}", {{color:"#7a8799"}}, {{color:"#ffe08a", duration:{step:.3f}, ease:"none"}}, {t_on:.3f});'
            )
            cursor += weights[ki]
        parts.append(
            f'<div id="{cid}" class="cap-clip clip" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="10">'
            f'<div class="cap-inner" id="{cid}-in">{"".join(spans)}</div></div>'
        )
        anim.extend(local_anim)
    body = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>{FONT}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:transparent}}
.cap-clip{{position:absolute;left:0;right:0;bottom:72px;display:flex;justify-content:center;pointer-events:none;z-index:55}}
.cap-inner{{max-width:1600px;padding:14px 28px;border-radius:10px;background:rgba(8,10,14,.78);color:#7a8799;font-size:34px;line-height:1.5;text-align:center;opacity:0;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;text-shadow:0 2px 8px rgba(0,0,0,.55);white-space:pre-wrap}}
.kw{{display:inline;color:#7a8799;transition:none}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-track-kind="captions" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080" data-fps="30" style="position:relative;width:1920px;height:1080px;background:transparent">
{"".join(parts)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(anim)}
window.__timelines["captions-zh"] = tl;
</script></body></html>"""
    (COMP / "captions-zh.html").write_text(body, encoding="utf-8")
    print("captions karaoke", len(TRANS))


def write_watermark() -> None:
    body = f"""<!doctype html>
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
<div id="root" class="clip" data-composition-id="watermark" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080" data-fps="30" style="position:relative;width:1920px;height:1080px;background:transparent">
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
    (COMP / "watermark.html").write_text(body, encoding="utf-8")
    print("watermark written")

SFX_CUE = [
    (0.05, "whoosh.wav", 0.35, 0.30),
    (5.0, "ui_blip.wav", 0.40, 0.10),
    (12.0, "punch.wav", 0.45, 0.20),
    (20.0, "impact.wav", 0.40, 0.24),
    (28.0, "ui_blip.wav", 0.40, 0.10),
    (36.0, "rein_snap.wav", 0.55, 0.14),
    (43.9, "whoosh.wav", 0.35, 0.30),
    (64.5, "whoosh.wav", 0.40, 0.30),
    (65.0, "gallop.wav", 0.50, 0.58),
    (66.2, "rein_snap.wav", 0.55, 0.14),
    (67.5, "gallop.wav", 0.45, 0.58),
    (70.0, "ui_blip.wav", 0.35, 0.10),
    (72.0, "punch.wav", 0.40, 0.20),
    (93.9, "ui_blip.wav", 0.35, 0.10),
    (163.9, "punch.wav", 0.35, 0.20),
    (243.9, "impact.wav", 0.35, 0.24),
    (265.4, "whoosh.wav", 0.40, 0.30),
    (266.0, "impact.wav", 0.50, 0.24),
    (268.5, "punch.wav", 0.45, 0.20),
    (272.0, "ui_blip.wav", 0.35, 0.10),
    (345.3, "whoosh.wav", 0.35, 0.30),
    (445.3, "ui_blip.wav", 0.35, 0.10),
    (568.6, "whoosh.wav", 0.40, 0.30),
    (588.6, "punch.wav", 0.35, 0.20),
    (658.6, "impact.wav", 0.35, 0.24),
    (728.6, "ui_blip.wav", 0.35, 0.10),
    (798.6, "punch.wav", 0.35, 0.20),
    (868.6, "impact.wav", 0.35, 0.24),
    (910.5, "whoosh.wav", 0.35, 0.30),
    (950.5, "ui_blip.wav", 0.35, 0.10),
    (1056.9, "whoosh.wav", 0.40, 0.30),
    (1068.9, "punch.wav", 0.35, 0.20),
    (1120.0, "impact.wav", 0.40, 0.24),
    (1140.0, "rein_snap.wav", 0.45, 0.14),
    # reader interaction punches
    (26.0, "ui_blip.wav", 0.45, 0.10),
    (32.0, "punch.wav", 0.45, 0.20),
    (135.9, "ui_blip.wav", 0.45, 0.10),
    (281.3, "ui_blip.wav", 0.40, 0.10),
    (576.6, "ui_blip.wav", 0.45, 0.10),
    (920.5, "ui_blip.wav", 0.40, 0.10),
    (1064.9, "punch.wav", 0.40, 0.20),
]


def write_index() -> None:
    hosts = []
    for b in BLOCKS:
        dur = b["end"] - b["start"]
        hosts.append(
            f'<div class="clip" id="host-{b["id"]}" data-composition-id="{b["id"]}" '
            f'data-composition-src="compositions/{b["id"]}.html" '
            f'data-start="{b["start"]:.3f}" data-duration="{dur:.3f}" data-track-index="1" '
            f'style="position:absolute;inset:0"></div>'
        )
    hosts.append(
        f'<div class="clip" id="host-watermark" data-composition-id="watermark" '
        f'data-composition-src="compositions/watermark.html" data-start="0" '
        f'data-duration="{TOTAL:.3f}" data-track-index="9" '
        f'style="position:absolute;inset:0;pointer-events:none;z-index:45"></div>'
    )
    hosts.append(
        f'<div class="clip" id="host-captions-zh" data-composition-id="captions-zh" '
        f'data-composition-src="compositions/captions-zh.html" data-start="0" '
        f'data-duration="{TOTAL:.3f}" data-track-index="10" data-track-kind="captions" '
        f'style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>'
    )
    sfx_lines = []
    for i, (t0, fname, vol, sdur) in enumerate(SFX_CUE):
        track = 20 + (i % 8)
        sfx_lines.append(
            f'<audio id="sfx-{i}" class="clip" src="assets/sfx/{fname}" data-start="{t0:.3f}" '
            f'data-duration="{sdur:.3f}" data-track-index="{track}" data-volume="{vol}"></audio>'
        )
    idx = f"""<!doctype html>
<html lang="zh-CN" data-resolution="landscape"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#000}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080" data-fps="30">
{"".join(hosts)}
<audio id="a-roll-audio" src="full.mp3" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="2" data-volume="1"></audio>
{"".join(sfx_lines)}
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>"""
    (ROOT / "index.html").write_text(idx, encoding="utf-8")
    print("wrote index.html sfx", len(SFX_CUE), "comps", len(BLOCKS))


def scrub_meta(path: Path) -> int:
    bad = ["吸粉", "视觉冲击", "听觉冲击", "冲击证明", "吸粉能量", "冲击"]
    text = path.read_text(encoding="utf-8")
    n = 0
    for w in bad:
        c = text.count(w)
        if c:
            print("META_WARN", path.name, w, c)
            n += c
    return n


def main() -> None:
    COMP.mkdir(parents=True, exist_ok=True)
    ensure_sfx()
    for blk in BLOCKS:
        write_block(blk)
    write_captions()
    write_watermark()
    write_index()
    total_warn = 0
    for pth in [ROOT / "index.html"] + list(COMP.glob("b0*.html")) + [COMP / "captions-zh.html", COMP / "watermark.html"]:
        total_warn += scrub_meta(pth)
    print("META_WARN_TOTAL", total_warn)
    print("DONE densify v3 project ready")


if __name__ == "__main__":
    main()
