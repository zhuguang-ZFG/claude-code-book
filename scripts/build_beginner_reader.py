#!/usr/bin/env python3
"""Regenerate docs/beginner-reader.html — the plain-language on-ramp.

一本真正浅显易懂的入门分册：每站 = 一幅手绘插图 + 大书里现成的
「一句话讲明白」与「打个比方」，按四篇由浅入深排站（底色随篇目加深，
"由浅入深"因此被画出来），每站一枚链接跳回大书对应章。正文零改动——
所有句子都取自作者自己的通俗层。

Run after `python yuyu-book/build.py` (reads the built zh HTML for the
plain-language layer; anchors link back into it).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "yuyu-book" / "dist" / "yuyu-agent-harness-zh.html"
ART = ROOT / "yuyu-book" / "illustrations"
OUT = ROOT / "docs" / "beginner-reader.html"
BOOK = "yuyu-agent-harness-zh.html"

# 由浅入深：四篇的底色一层比一层深，深浅即顺序
PARTS = [
    ("第一部分 · 基础篇", "起步", "#FBF6EC", ["ch01", "ch02", "ch03", "ch04"]),
    ("第二部分 · 核心系统篇", "进阶", "#F3EAD8", ["ch05", "ch06", "ch07", "ch08"]),
    ("第三部分 · 高级模式篇", "深入", "#EADFC7", ["ch09", "ch10", "ch11", "ch12"]),
    ("第四部分 · 工程实践篇", "实战", "#E0D4B8", ["ch13", "ch14", "ch15"]),
]
ORDER = ["front"] + [u for _, _, _, us in PARTS for u in us] + ["apxd"]
BIG = {"front": 200, "cover": 260}
WIDTH = {u: (BIG.get(u, 148)) for u in ORDER}

# 视频指路：只收录存在性经核验的链接（官方频道 + 核验过的 B 站稿件 +
# 站内搜索页）。视频属社区/官方宣传资源，非本书规范来源；技术事实
# 以大书正文与官方文档为准。核验日期 2026-10-31。
YT_CHANNEL = "https://www.youtube.com/@anthropic-ai"
YT_SEARCH = "https://www.youtube.com/results?search_query="
B_SEARCH = "https://search.bilibili.com/all?keyword="
VIDEOS = {
    "front": [("YouTube · Anthropic 官方频道", YT_CHANNEL),
              ("YouTube · 搜「Mastering Claude Code in 30 minutes」（官方）",
               YT_SEARCH + "Mastering+Claude+Code+in+30+minutes")],
    "ch01": [("B 站 · Claude Code 教程（社区，已核验）",
              "https://www.bilibili.com/video/BV1uS9UBQEuH")],
    "ch02": [("B 站 · 搜「Claude Code 对话」", B_SEARCH + "Claude%20Code%20%E5%AF%B9%E8%AF%9D")],
    "ch03": [("B 站 · 搜「Claude Code 工具」", B_SEARCH + "Claude%20Code%20%E5%B7%A5%E5%85%B7")],
    "ch04": [("B 站 · 搜「Claude Code 权限」", B_SEARCH + "Claude%20Code%20%E6%9D%83%E9%99%90")],
    "ch05": [("B 站 · 搜「Claude Code 配置」", B_SEARCH + "Claude%20Code%20%E9%85%8D%E7%BD%AE")],
    "ch06": [("B 站 · 搜「Claude Code 记忆」", B_SEARCH + "Claude%20Code%20%E8%AE%B0%E5%BF%86")],
    "ch07": [("B 站 · 搜「Claude Code 上下文」", B_SEARCH + "Claude%20Code%20%E4%B8%8A%E4%B8%8B%E6%96%87")],
    "ch08": [("B 站 · 搜「Claude Code Hooks」", B_SEARCH + "Claude%20Code%20Hooks")],
    "ch09": [("B 站 · 搜「Claude Code 子智能体」", B_SEARCH + "Claude%20Code%20%E5%AD%90%E6%99%BA%E8%83%BD%E4%BD%93")],
    "ch10": [("YouTube · Anthropic 官方频道（多智能体）", YT_CHANNEL)],
    "ch11": [("B 站 · 搜「Claude Skills」", B_SEARCH + "Claude%20Skills")],
    "ch12": [("B 站 · 搜「MCP 教程」", B_SEARCH + "MCP%20%E6%95%99%E7%A8%8B"),
             ("YouTube · Anthropic 官方频道（MCP）", YT_CHANNEL)],
    "ch13": [("B 站 · 搜「Claude Code 流式」", B_SEARCH + "Claude%20Code%20%E6%B5%81%E5%BC%8F")],
    "ch14": [("B 站 · 搜「Claude Code Plan」", B_SEARCH + "Claude%20Code%20Plan")],
    "ch15": [("YouTube · Anthropic 官方频道（agent 深讲）", YT_CHANNEL)],
}

# 站间衔接：只做承上启下，不新增任何技术断言
TRANSITIONS = {
    "ch01": "先站上起点：看清这场范式转移把程序员带到了哪里。",
    "ch02": "方向既明，先听 Agent 的心跳——它怎么跟你一来一回。",
    "ch03": "心跳会转了，还得有手：这一站看它凭什么能动手。",
    "ch04": "手有了力气，就要有护栏——别让它碰不该碰的。",
    "ch05": "护栏立好，回头给它定性格：配置是它的基因。",
    "ch06": "基因定了，它还得记住你们相处的每一件事。",
    "ch07": "记性太好也是负担——这一站看它如何打理工作记忆。",
    "ch08": "想在它的生命周期里插手？钩子就是那些接口。",
    "ch09": "一个助手不够用？让它分身出小助手。",
    "ch10": "分身多了就要有指挥——编排者模式登场。",
    "ch11": "指挥有序，还要给它发技能卡：能力即插即用。",
    "ch12": "墙外的世界靠外接线：MCP 把外部工具接进来。",
    "ch13": "都接好了，让回答像水一样流出来。",
    "ch14": "让它放开了跑之前，先学会画路线、插红旗。",
    "ch15": "看完全程，现在亲手摇一架自己的辘轳。",
    "apxd": "路上的生词，都在这本小词典里。",
}

STRIP = re.compile(r"<[^>]+>")


def extract_units(html: str) -> dict:
    """For every unit: title, the author's own plain sentence and analogy."""
    marks = {u: html.find(f'id="{u}"') for u in ORDER if u != "apxd"}
    marks["apxd"] = html.find('id="apxd"')
    order = sorted(marks.items(), key=lambda kv: kv[1])
    units = {}
    for i, (uid, pos) in enumerate(order):
        stop = order[i + 1][1] if i + 1 < len(order) else len(html)
        seg = html[pos:stop]
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", seg, re.S)
        title = STRIP.sub("", title_m.group(1)).strip() if title_m else uid
        plain_m = re.search(r'class="lb-plain">(.*?)</p>', seg, re.S)
        analogy_m = re.search(r'class="lb-a-tag">[^<]*</span>(.*?)</p>', seg, re.S)
        units[uid] = {
            "title": title,
            "plain": STRIP.sub("", plain_m.group(1)).strip() if plain_m else "",
            "analogy": STRIP.sub("", analogy_m.group(1)).strip() if analogy_m else "",
        }
    return units


CAPTIONS = {
    "front": "一张古地图：整本书就是一条路",
    "ch01": "罗盘：从「陪聊」到「干活」，换一种瞄准方式",
    "ch02": "心跳：一句话进、一句话出的对话循环",
    "ch03": "螺母：Agent 的双手——工具越多，本事越大",
    "ch04": "闸门：危险操作先过一道勾选的护栏",
    "ch05": "千层饼：配置像基因，一层层定性格",
    "ch06": "折角笔记本：Agent 的长期记忆记在这里",
    "ch07": "仪表盘：脑子里工作台还剩多少位置",
    "ch08": "挂钩：在人生节点上，给它装上小动作",
    "ch09": "分叉路：派几个小助手分头去办",
    "ch10": "指挥家：一个主编排，四方小队听调",
    "ch11": "技能卡：把说明书装进兜里，随取随用",
    "ch12": "外接线：一根线，用上全世界的工具",
    "ch13": "漏斗：回答像水一样，一边流一边看",
    "ch14": "小红旗：先画路线再出发，插旗为证",
    "ch15": "辘轳：亲手摇一架，你也造一个 Agent",
    "apxd": "小词典：生词太多？翻这一册",
}


def station(uid: str, num: str, unit: dict, svg: str, tier: str, part: str,
            bg: str, width: int) -> str:
    analogy = (f'<p class="st-ana">打个比方：{unit["analogy"]}</p>'
               if unit["analogy"] else "")
    plain = (f'<p class="st-plain">{unit["plain"]}</p>' if unit["plain"] else "")
    trans = TRANSITIONS.get(uid, "")
    trans_html = f'<p class="st-trans">{trans}</p>' if trans else ""
    vids = "".join(f'<a class="st-vid" href="{url}" target="_blank"'
                   f' rel="noopener">📺 {label}</a>'
                   for label, url in VIDEOS.get(uid, []))
    vids_html = f'<p class="st-vids">{vids}</p>' if vids else ""
    return f"""<article class="st" style="background:{bg}">
  <div class="st-art" style="width:{width}px">{svg}</div>
  <div class="st-body">
    <p class="st-part">第 {num} 站 · {part} · <b class="st-tier">{tier}</b></p>
    <h2>{unit["title"]}</h2>
    <p class="st-cap">{CAPTIONS.get(uid, "")}</p>
    {trans_html}{plain}{analogy}{vids_html}
    <a class="st-go" href="{BOOK}#{uid}">想深入？翻开大书这一章 →</a>
  </div>
</article>"""


def main():
    html = DIST.read_text(encoding="utf-8")
    units = extract_units(html)
    svgs = {u: (ART / f"{u}.svg").read_text(encoding="utf-8").strip()
            for u in ORDER + ["cover", "keeper"] if (ART / f"{u}.svg").exists()}

    stations = [f"""<article class="st st-hero" style="background:#FBF6EC">
  <div class="st-art" style="width:200px">{svgs.get("cover", "")}</div>
  <div class="st-body">
    <p class="st-part">开卷 · <b class="st-tier">人人可读</b></p>
    <h2>这本书在讲一件什么事？</h2>
    <p class="st-cap">四马古车：书名「御舆」——驾驭一辆车，也驾驭一个 Agent</p>
    <p class="st-plain">大模型很聪明，但让它真正替你干活，还需要一整套"驾车"的
    装备——这本书把这套装备拆开给你看。不用先懂编程，跟着图往下走就行。</p>
    <a class="st-go" href="{BOOK}#front">想深入？翻开前言 →</a>
  </div>
</article>"""]

    num = 0
    total = sum(len(us) for _, _, _, us in PARTS) + 1  # + 附录 D 站
    for part, tier, bg, us in PARTS:
        for uid in us:
            num += 1
            svg = svgs.get(uid, "")
            stations.append(station(uid, f"{num} / {total}",
                                    units.get(uid, {"title": uid}), svg,
                                    tier, part, bg, WIDTH[uid]))

    num += 1
    stations.append(f"""<article class="st" style="background:#FBF6EC">
  <div class="st-art" style="width:148px">{svgs.get("apxd", "")}</div>
  <div class="st-body">
    <p class="st-part">第 {num} / {total} 站 · 附录 · <b class="st-tier">随身</b></p>
    <h2>路上遇到生词？</h2>
    <p class="st-cap">小词典：生词太多？翻这一册</p>
    <p class="st-plain">术语表、源码地图、工具清单、功能开关——都在附录里，
    随时折回去查。</p>
    <a class="st-go" href="{BOOK}#apxd">想深入？翻开附录 D →</a>
  </div>
</article>
<article class="st st-hero" style="background:#FBF6EC">
  <div class="st-art" style="width:148px">{svgs.get("keeper", "")}</div>
  <div class="st-body">
    <p class="st-part">到站 · <b class="st-tier">老驿卒的话</b></p>
    <h2>路走完了，接下来呢？</h2>
    <p class="st-cap">老驿卒：每章结尾替你守夜总结的人</p>
    <p class="st-plain">这本分册只是地图，真正的风景在大书里——每站都有
    「想深入」的门，推门进去，那里有完整的原理、代码与练习。</p>
    <a class="st-go" href="{BOOK}">回到大书 →</a>
  </div>
</article>""")

    page = PAGE_HEAD + "\n".join(stations) + PAGE_TAIL
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT} ({len(page)} bytes, {len(stations)} stations)")


PAGE_HEAD = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>御舆 · 入门分册 — 看图读懂 Agent Harness</title>
<style>
body{margin:0;font:16px/1.9 "Noto Serif SC","Source Han Serif SC","思源宋体","Songti SC","SimSun",Georgia,serif;background:#F5F0E6;color:#26221B}
header{padding:34px 30px 10px;max-width:820px;margin:0 auto}
h1{font-size:24px;margin:0 0 6px;font-weight:650}
.brush{width:190px;height:9px;color:#B4472F;display:block;margin:2px 0 8px}
.sub{color:#5C5448;font-size:13.5px}
.hint{color:#6E6353;font-size:12.5px;margin:10px 0 0}
main{max-width:820px;margin:0 auto;padding:6px 30px 50px}
.st{border:1.5px solid rgba(38,34,27,.3);border-radius:12px 7px 11px 8px/8px 11px 7px 12px;
    padding:26px 30px 24px;margin:0 0 26px;display:flex;gap:26px;align-items:center;
    box-shadow:2px 3px 0 rgba(38,34,27,.08)}
.st-hero{flex-direction:column;text-align:center;gap:10px;padding-top:34px}
.st-hero .st-body{text-align:center}
.st-art{flex:0 0 auto;line-height:0}
.st-art svg{width:100%;height:auto}
.st-body{flex:1}
.st-part{margin:0 0 6px;font-size:12px;letter-spacing:.14em;color:#8A7D68}
.st-tier{color:#B4472F}
h2{font-size:21px;margin:0 0 8px}
.st-cap{margin:0 0 10px;font-size:13px;color:#B4472F;letter-spacing:.02em}
.st-trans{margin:0 0 8px;font-size:13.5px;color:#8A7D68}
.st-plain{margin:0 0 8px;font-size:15.5px}
.st-ana{margin:0 0 10px;font-size:14px;color:#5C5448}
.st-vids{margin:0 0 10px;font-size:12.5px}
.st-vids .st-vid{display:inline-block;margin-right:14px;color:#4C7093;
  text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
.st-vids .st-vid:hover{color:#B4472F;border-bottom-color:#B4472F}
.st-go{font-size:13.5px;color:#26221B;text-decoration:none;border-bottom:1.5px solid #B4472F;
       padding-bottom:1px;transition:color .16s ease}
.st-go:hover{color:#B4472F}
.st,.st-body,.st-cap,.st-plain,.st-ana{animation:ink-rise .8s cubic-bezier(.22,.9,.3,1) both;
  animation-timeline:view();animation-range:cover 0% cover 46%}
.st-art svg path,.st-art svg circle{animation:ink-draw 1.1s ease-out both;
  animation-timeline:view();animation-range:cover 0% cover 55%}
@media screen and (prefers-reduced-motion: reduce){
  .st,.st-body,.st-cap,.st-plain,.st-ana,.st-art svg path,.st-art svg circle{animation:none}}
footer{max-width:820px;margin:0 auto;padding:0 30px 46px;color:#675F4F;font-size:12.5px}
footer a{color:inherit}
@keyframes ink-rise{from{opacity:0;transform:translateY(12px)}}
@keyframes ink-draw{from{stroke-dashoffset:100}}
</style>
</head>
<body>
<header>
  <h1>御舆 · 入门分册</h1>
  <svg class="brush" viewBox="0 0 190 10" aria-hidden="true"><path d="M4 6q30-4.5 62-2.5t72-1q24 .2 46 1.8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".85"/><path d="M152 5.6q10-.6 20-.2" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".45"/><circle cx="178" cy="5.8" r="1.5" fill="currentColor" stroke="none"/></svg>
  <p class="sub">看图读懂 Agent Harness —— 一站一个概念，一句一句说清楚</p>
  <p class="hint">每一站的句子都取自大书作者自己的通俗层；底色一层比一层深，就是"由浅入深"的顺序。某站看懂了，就推开「想深入」的门，去大书里读完整的原理。</p>
</header>
<main>
"""

PAGE_TAIL = """</main>
<footer>
本分册由大书的通俗层与 <a href="illustration-gallery.html">26 幅手绘插图</a> 组成；
画风体系来自 <a href="https://github.com/yang0/handraw-style">yang0/handraw-style</a>
（MIT with Attribution）。大书：<a href="yuyu-agent-harness-zh.html">御舆：解码 Agent Harness</a>。
<br>📺 页内视频为官方频道与社区资源，属<b>非规范来源</b>（仅核验存在性，
核验日期 2026-10-31）；一切技术事实以大书正文及其规范来源为准。
</footer>
</body>
</html>
"""

if __name__ == "__main__":
    main()
