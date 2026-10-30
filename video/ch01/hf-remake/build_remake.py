# -*- coding: utf-8 -*-
from __future__ import annotations
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRANS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
COMP = ROOT / "compositions"
COMP.mkdir(parents=True, exist_ok=True)
(ROOT / "assets" / "huashu").mkdir(parents=True, exist_ok=True)

BLOCKS = [
    {"id":"b01_hook","title":"开场钩子","start":0.0,"end":43.896,
     "huashu":[("01_hook_glue.mp4",8.0,7.0)],
     "beats":[(0.0,"series","驭者·Agent Harness","第 01 讲 · 打地基"),(8.0,"contrast","Chatbot 时代","人当系统胶水"),(22.0,"contrast2","Agent 时代","自己编排工具调用"),(32.0,"question","为什么不能只包一层 API？","需要 Agent Harness")]},
    {"id":"b02_paradigm","title":"§1.1 范式转移","start":43.896,"end":265.32,
     "huashu":[("02_llm_roles.mp4",50.0,7.0),("03_six_challenges.mp4",120.0,7.5),("04_harness_def.mp4",200.0,7.0)],
     "beats":[(0.0,"section","§1.1 范式转移","LLM：对话伙伴 → 推理引擎"),(40.0,"card","Tool Use","打开边界 · 六大工程挑战"),(100.0,"card","简单封装","while 循环假设理想世界"),(160.0,"card","Agent Harness","流式 · 权限 · 上下文 · 恢复 · 持久化"),(190.0,"warn","反模式","裸 while(true){ callAPI }")]},
    {"id":"b03_arch","title":"§1.2 全景架构","start":265.32,"end":568.632,
     "huashu":[("05_arch_layers.mp4",80.0,7.5),("06_tech_stack.mp4",180.0,7.0)],
     "beats":[(0.0,"section","§1.2 全景架构","从 Copilot 到 Claude Code / MCP"),(40.0,"number","1,884","个 TypeScript 文件"),(70.0,"number","512,664","行代码"),(120.0,"layers","五模块骨架","Entry → QueryEngine → Loop → Tools → Ext"),(200.0,"stack","技术栈","Bun · React+Ink · Zod v4 · SDK"),(250.0,"tools","55 个工具","权限四阶段")]},
    {"id":"b04_principles","title":"§1.3 五大原则","start":568.632,"end":910.464,
     "huashu":[("07_p_async.mp4",20.0,7.0),("08_p_security.mp4",90.0,7.5),("09_p_cache.mp4",160.0,7.0),("10_p_progressive.mp4",230.0,7.5),("11_p_immutable.mp4",300.0,7.0)],
     "beats":[(0.0,"section","§1.3 五大原则","红线，不是口号"),(15.0,"p","1 · 异步流式优先","Async Generator First"),(85.0,"p","2 · 安全边界内嵌","Security at the Perimeter"),(155.0,"p","3 · 缓存感知设计","Cache-Aware Architecture"),(225.0,"p","4 · 渐进式能力扩展","Tool → Skill → Plugin → MCP"),(295.0,"p","5 · 不可变状态流转","Immutable State Flow")]},
    {"id":"b05_practice","title":"实战练习速览","start":910.464,"end":1056.912,
     "huashu":[("12_doctor_flow.mp4",40.0,7.0)],
     "beats":[(0.0,"section","实战练习速览","动手验证 Harness"),(20.0,"code","npm i -g @anthropic-ai/claude-code","claude --version"),(50.0,"code","/doctor","环境 · 权限 · MCP · API · 文件系统"),(90.0,"flow","一次工具调用","思考 → GlobTool → 回复")]},
    {"id":"b06_outro","title":"总结 + 片尾","start":1056.912,"end":1148.352,
     "huashu":[("13_outro.mp4",5.0,7.0)],
     "beats":[(0.0,"section","本讲收束","四句记住"),(10.0,"sum","范式已转移","Harness 是工程系统"),(35.0,"sum","五模块是骨架","五原则是红线"),(55.0,"next","第 02 讲预告","对话主循环 AsyncGenerator"),(70.0,"credit","基于开源书稿","驭者·Agent Harness · 关注小电讲电路")]},
]
TOTAL = 1148.352
FONT = """
@font-face { font-family: 'Noto Sans SC'; src: local('Noto Sans SC'), local('NotoSansSC-Regular'), local('Microsoft YaHei'); font-weight: 100 900; }
@font-face { font-family: 'Microsoft YaHei'; src: local('Microsoft YaHei'), local('Microsoft YaHei UI'); }
"""
CSS = FONT + r"""
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#0b0d10}
body{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;color:#e8ecf1}
.scene{position:absolute;inset:0;background:radial-gradient(1200px 700px at 50% 30%,#151a22 0%,#0b0d10 70%)}
.grain{position:absolute;inset:0;opacity:.06;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.vignette{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.55) 100%)}
.series-bar{position:absolute;top:48px;left:64px}
.series-in{display:flex;align-items:center;gap:16px;opacity:0}
.badge{width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,#f0a050,#c45c1a);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:22px;color:#111}
.series-name{font-size:22px;letter-spacing:.08em;color:#c9d2de}
.series-sub{font-size:16px;color:#7a8799;margin-top:4px}
.panel{position:absolute;left:64px;right:64px;top:160px;bottom:160px}
.panel-body{display:flex;flex-direction:column;justify-content:center;gap:28px;height:100%;opacity:0}
.kicker{font-size:20px;letter-spacing:.2em;color:#f0a050;opacity:0}
.h1{font-size:64px;font-weight:700;line-height:1.15;opacity:0;max-width:1400px}
.h2{font-size:36px;font-weight:400;color:#aeb8c6;opacity:0;max-width:1200px;line-height:1.4}
.big-num{font-size:120px;font-weight:800;color:#f0a050;letter-spacing:-.02em;opacity:0;line-height:1}
.layers-row{display:flex;gap:12px;opacity:0}
.layer{flex:1;padding:22px 12px;text-align:center;border-radius:12px;background:#161c24;border:1px solid #2a3340;font-size:20px;font-weight:600;opacity:0}
.huashu-wrap{position:absolute;inset:0;pointer-events:none}
.huashu-in{width:100%;height:100%;opacity:0}
.huashu-in video{width:100%;height:100%;object-fit:cover}
"""

def esc(s): return html.escape(s, quote=True)

def write_block(b):
    dur = b["end"] - b["start"]; bid = b["id"]
    panels=[]; anim=[f'tl.from("#series-in", {{ opacity: 0, y: -16, duration: 0.6 }}, 0);', f'tl.set("#series-in", {{ opacity: 1 }}, 0.05);']
    for i,(t,kind,h1,h2) in enumerate(b["beats"]):
        pid=f"p{i}"; nxt=b["beats"][i+1][0] if i+1<len(b["beats"]) else dur
        pdur=max(4.0, min(nxt-t+2.0, dur-t)); end=min(nxt-0.15, t+pdur-0.15)
        inner=f'<div class="kicker" id="{pid}-k">{esc(b["title"])}</div>'
        if kind=="number":
            inner += f'<div class="big-num" id="{pid}-h1">{esc(h1)}</div><div class="h2" id="{pid}-h2">{esc(h2)}</div>'
        elif kind=="layers":
            layers=["Entry","QueryEngine","Loop","Tools","Ext"]
            cards="".join(f'<div class="layer" id="{pid}-l{j}">{esc(x)}</div>' for j,x in enumerate(layers))
            inner += f'<div class="h1" id="{pid}-h1">{esc(h1)}</div><div class="h2" id="{pid}-h2">{esc(h2)}</div><div class="layers-row" id="{pid}-row">{cards}</div>'
        else:
            inner += f'<div class="h1" id="{pid}-h1">{esc(h1)}</div><div class="h2" id="{pid}-h2">{esc(h2)}</div>'
        panels.append(f'<div id="{pid}" class="clip panel" data-start="{t:.3f}" data-duration="{pdur:.3f}" data-track-index="1"><div class="panel-body" id="{pid}-body">{inner}</div></div>')
        anim += [
            f'tl.set("#{pid}-body", {{opacity:1}}, {t:.3f});',
            f'tl.from("#{pid}-k", {{opacity:0, y:12, duration:0.5}}, {t:.3f});',
            f'tl.from("#{pid}-h1", {{opacity:0, y:28, duration:0.7}}, {t+0.15:.3f});',
            f'tl.from("#{pid}-h2", {{opacity:0, y:18, duration:0.6}}, {t+0.35:.3f});',
        ]
        if kind=="layers":
            for j in range(5):
                anim.append(f'tl.from("#{pid}-l{j}", {{opacity:0, y:16, duration:0.4}}, {t+0.55+j*0.15:.3f});')
            anim.append(f'tl.from("#{pid}-row", {{opacity:0, duration:0.3}}, {t+0.5:.3f});')
        anim.append(f'tl.to("#{pid}-body", {{opacity:0, duration:0.35}}, {end:.3f});')
    huashu=[]
    for fname,at,hd in b.get("huashu",[]):
        hid=Path(fname).stem.replace("-","_")
        huashu.append(f'<div id="hv-{hid}" class="clip huashu-wrap" data-start="{at:.3f}" data-duration="{hd:.3f}" data-track-index="3"><div class="huashu-in" id="hv-{hid}-in"><video src="../assets/huashu/{fname}" muted playsinline data-start="{at:.3f}" data-duration="{hd:.3f}" data-has-audio="false"></video></div></div>')
        anim.append(f'tl.to("#hv-{hid}-in", {{opacity:1, duration:0.4}}, {at:.3f});')
        anim.append(f'tl.to("#hv-{hid}-in", {{opacity:0, duration:0.4}}, {at+hd-0.4:.3f});')
    body=f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head><body>
<div id="root" class="scene clip" data-composition-id="{bid}" data-start="0" data-duration="{dur:.3f}" data-width="1920" data-height="1080" data-fps="30">
  <div class="series-bar clip" id="series" data-start="0" data-duration="{dur:.3f}" data-track-index="0"><div class="series-in" id="series-in"><div class="badge">01</div><div><div class="series-name">驭者·Agent Harness</div><div class="series-sub">{esc(b["title"])}</div></div></div></div>
  {"".join(panels)}
  {"".join(huashu)}
  <div class="grain"></div><div class="vignette"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(anim)}
window.__timelines["{bid}"] = tl;
</script></body></html>"""
    (COMP/f"{bid}.html").write_text(body, encoding="utf-8"); print("wrote", bid)

def write_captions():
    parts=[]; anim=[]
    for i,w in enumerate(TRANS):
        text=(w.get("text") or "").strip()
        if not text: continue
        start=max(0.1,float(w["start"])); end=float(w["end"])
        if end<=start: end=start+1.2
        cid=f"c{i}"; dur=end-start
        parts.append(f'<div id="{cid}" class="cap-clip clip" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="10"><div class="cap-inner" id="{cid}-in">{esc(text)}</div></div>')
        anim += [f'tl.set("#{cid}-in", {{opacity:0}}, 0);', f'tl.to("#{cid}-in", {{opacity:1, duration:0.12}}, {start:.3f});', f'tl.to("#{cid}-in", {{opacity:0, duration:0.12}}, {max(start,end-0.12):.3f});']
    body=f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{FONT}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:transparent}}
.cap-clip{{position:absolute;left:0;right:0;bottom:72px;display:flex;justify-content:center;pointer-events:none}}
.cap-inner{{max-width:1600px;padding:14px 28px;border-radius:10px;background:rgba(8,10,14,.72);color:#fff;font-size:34px;line-height:1.45;text-align:center;opacity:0;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;text-shadow:0 2px 8px rgba(0,0,0,.55);white-space:pre-wrap}}
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
    (COMP/"captions-zh.html").write_text(body, encoding="utf-8"); print("captions", len(TRANS))

def write_index():
    hosts=[]
    for b in BLOCKS:
        dur=b["end"]-b["start"]
        hosts.append(f'<div class="clip" data-composition-src="compositions/{b["id"]}.html" data-start="{b["start"]:.3f}" data-duration="{dur:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>')
    hosts.append(f'<div class="clip" data-composition-src="compositions/captions-zh.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="10" data-track-kind="captions" style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>')
    (ROOT/"index.html").write_text(f"""<!doctype html>
<html lang="zh-CN" data-resolution="landscape"><head><meta charset="UTF-8"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#000}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080" data-fps="30">
{"".join(hosts)}
<audio id="a-roll-audio" src="full.mp3" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="2" data-volume="1"></audio>
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>""", encoding="utf-8"); print("index")

if __name__=="__main__":
    (ROOT/"DESIGN.md").write_text("# DESIGN\n- charcoal/amber engineering look\n- GSAP seekable; no loop beds\n- Chinese caption rail burn-in\n- huashu y3_whiteboard inserts\n", encoding="utf-8")
    for b in BLOCKS: write_block(b)
    write_captions(); write_index(); print("DONE")
