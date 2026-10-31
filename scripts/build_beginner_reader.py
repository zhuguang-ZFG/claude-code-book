#!/usr/bin/env python3
"""Regenerate docs/beginner-reader.html (+ .en.html) — the plain-language
on-ramp.

一本真正浅显易懂的入门分册：每站 = 一幅手绘插图 + 大书里现成的
「一句话讲明白」与「打个比方」，按四篇由浅入深排站（底色随篇目加深，
"由浅入深"因此被画出来），每站一枚链接跳回大书对应章。正文零改动——
所有句子都取自作者自己的通俗层（zh 从中文 dist 提取，en 从英文 dist）。

Run after `python yuyu-book/build.py [--lang en]` (reads the built HTML for
the plain-language layer; anchors link back into it).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "yuyu-book" / "illustrations"

YT_CHANNEL = "https://www.youtube.com/@anthropic-ai"
YT_SEARCH = "https://www.youtube.com/results?search_query="
B_SEARCH = "https://search.bilibili.com/all?keyword="

STRIP = re.compile(r"<[^>]+>")

# 由浅入深：四篇的底色一层比一层深，深浅即顺序
PARTS = [
    ("第一部分 · 基础篇", "起步", "#FBF6EC", ["ch01", "ch02", "ch03", "ch04"]),
    ("第二部分 · 核心系统篇", "进阶", "#F3EAD8", ["ch05", "ch06", "ch07", "ch08"]),
    ("第三部分 · 高级模式篇", "深入", "#EADFC7", ["ch09", "ch10", "ch11", "ch12"]),
    ("第四部分 · 工程实践篇", "实战", "#E0D4B8", ["ch13", "ch14", "ch15"]),
]
ORDER = ["front"] + [u for _, _, _, us in PARTS for u in us] + ["apxd"]
WIDTH = {u: 148 for u in ORDER}

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
    "keeper": "老驿卒：每章结尾替你守夜总结的人",
    "cover": "四马古车：书名「御舆」——驾驭一辆车，也驾驭一个 Agent",
}

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

# 带走这一句：只复述当页已有的比方与白话，不新增任何技术断言
TAKEAWAYS = {
    "ch01": "记住：范式换了——瞄准的方式也要跟着换。",
    "ch02": "记住：心跳不停，对话循环就不会断。",
    "ch03": "记住：工具是它的双手——手越多，能干的越多。",
    "ch04": "记住：护栏不是限制，是让它敢放手动力的前提。",
    "ch05": "记住：配置是基因——性格一层一层定下来。",
    "ch06": "记住：长期记忆是一本只记要点的折角册页。",
    "ch07": "记住：工作记忆是量器——装太满会洒。",
    "ch08": "记住：钩子是装在生命周期节点上的小动作。",
    "ch09": "记住：分叉就是把活交给小助手，各办各的。",
    "ch10": "记住：编排者是中枢——四方小队听它调。",
    "ch11": "记住：技能是兜里的卡片——插上就会。",
    "ch12": "记住：外接线接进来的是整个世界的工具。",
    "ch13": "记住：流式 = 一边生成，一边已经看到。",
    "ch14": "记住：先画路线、插好旗，再出发。",
    "ch15": "记住：Harness 你也可以亲手造——辘轳摇起来。",
    "apxd": "记住：生词不查词典，路会越走越糊涂。",
}

VIDEOS = {
    "front": [("YouTube · Anthropic 官方频道", YT_CHANNEL),
              ("YouTube · Mastering Claude Code in 30 minutes（官方，已核验）",
               "https://www.youtube.com/watch?v=6eBSHbLKuN0"),
              ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch01": [("B 站 · Claude Code 教程（社区，已核验）",
              "https://www.bilibili.com/video/BV1uS9UBQEuH"),
             ("YouTube · Mastering Claude Code in 30 minutes（官方，已核验）",
              "https://www.youtube.com/watch?v=6eBSHbLKuN0")],
    "ch02": [("B 站 · 搜「Claude Code 对话」", B_SEARCH + "Claude%20Code%20%E5%AF%B9%E8%AF%9D")],
    "ch03": [("B 站 · 搜「Claude Code 工具」", B_SEARCH + "Claude%20Code%20%E5%B7%A5%E5%85%B7")],
    "ch04": [("B 站 · 搜「Claude Code 权限」", B_SEARCH + "Claude%20Code%20%E6%9D%83%E9%99%90")],
    "ch05": [("B 站 · 搜「Claude Code 配置」", B_SEARCH + "Claude%20Code%20%E9%85%8D%E7%BD%AE"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch06": [("B 站 · 搜「Claude Code 记忆」", B_SEARCH + "Claude%20Code%20%E8%AE%B0%E5%BF%86")],
    "ch07": [("B 站 · 搜「Claude Code 上下文」", B_SEARCH + "Claude%20Code%20%E4%B8%8A%E4%B8%8B%E6%96%87"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch08": [("B 站 · 搜「Claude Code Hooks」", B_SEARCH + "Claude%20Code%20Hooks"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch09": [("B 站 · 搜「Claude Code 子智能体」", B_SEARCH + "Claude%20Code%20%E5%AD%90%E6%99%BA%E8%83%BD%E4%BD%93"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch10": [("YouTube · Anthropic 官方频道（多智能体）", YT_CHANNEL)],
    "ch11": [("B 站 · 搜「Claude Skills」", B_SEARCH + "Claude%20Skills")],
    "ch12": [("B 站 · MCP 教程（社区，已核验）", "https://www.bilibili.com/video/BV1qkHrzHEh4"),
             ("B 站 · 搜「MCP 教程」", B_SEARCH + "MCP%20%E6%95%99%E7%A8%8B"),
             ("YouTube · Anthropic 官方频道（MCP）", YT_CHANNEL),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch13": [("B 站 · 搜「Claude Code 流式」", B_SEARCH + "Claude%20Code%20%E6%B5%81%E5%BC%8F")],
    "ch14": [("B 站 · 搜「Claude Code Plan」", B_SEARCH + "Claude%20Code%20Plan")],
    "ch15": [("YouTube · Anthropic 官方频道（agent 深讲）", YT_CHANNEL)],
}

# ---------------- English edition ----------------
PARTS_EN = [
    ("Part I · Foundations", "Start", "#FBF6EC", ["ch01", "ch02", "ch03", "ch04"]),
    ("Part II · Core Systems", "Core", "#F3EAD8", ["ch05", "ch06", "ch07", "ch08"]),
    ("Part III · Advanced Patterns", "Deep", "#EADFC7", ["ch09", "ch10", "ch11", "ch12"]),
    ("Part IV · Engineering Practice", "Practice", "#E0D4B8", ["ch13", "ch14", "ch15"]),
]
ORDER_EN = ["front"] + [u for _, _, _, us in PARTS_EN for u in us] + ["apxd"]

CAPTIONS_EN = {
    "front": "An old map: the whole book is one road",
    "ch01": "Compass: from chatbot to co-worker — a new way to aim",
    "ch02": "Heartbeat: the loop of one message in, one out",
    "ch03": "Nut: the agent's hands — more tools, more skill",
    "ch04": "Gate: risky actions pass a checked guardrail first",
    "ch05": "Layer cake: settings are genes, layer by layer",
    "ch06": "Folded notebook: where long-term memory lives",
    "ch07": "Gauge: how much workbench is left in mind",
    "ch08": "Hooks: small actions wired into life's milestones",
    "ch09": "Fork: send small helpers to work in parallel",
    "ch10": "Conductor: one orchestrator, four squads on call",
    "ch11": "Skill cards: the manual in your pocket",
    "ch12": "Jacks: one line to the world's tools",
    "ch13": "Funnel: answers flow like water, watchable as they pour",
    "ch14": "Flag: draw the route first, plant the flag as proof",
    "ch15": "Windlass: crank one yourself — build an agent of your own",
    "apxa": "Treasure map: where the source lives, located",
    "apxb": "Tool inventory: every belonging, ticked off",
    "apxc": "Switch bank: which flags are on, at a glance",
    "apxd": "Pocket dictionary: too many new words? Look here",
    "keeper": "The old courier: summarizing at every chapter's end",
    "part-p1": "The great compass: foundations, aim first",
    "part-p2": "The chest: core systems locked inside",
    "part-p3": "Mountain path: advanced patterns, the hill shortcut",
    "part-p4": "Gateway: engineering practice, the road out of town",
    "cover": "The four-horse chariot: Yù Yú — drive a chariot, drive an agent",
}

TRANSITIONS_EN = {
    "ch01": "Stand at the start: see where this paradigm shift has taken programmers.",
    "ch02": "Aim set, first listen for the agent's heartbeat — how it talks with you, back and forth.",
    "ch03": "The heart beats; now for hands: what lets it actually act.",
    "ch04": "Hands need guardrails — keep it from touching what it shouldn't.",
    "ch05": "Rails up, give it character: settings are its genes.",
    "ch06": "Character set, it must remember everything you share.",
    "ch07": "A perfect memory is a burden — how it manages working memory.",
    "ch08": "Want a say during its lifecycle? Hooks are those interfaces.",
    "ch09": "One helper isn't enough? Let it spawn sub-agents.",
    "ch10": "Many helpers need a conductor — the orchestrator takes the stage.",
    "ch11": "Order established, hand it skill cards: plug-and-play ability.",
    "ch12": "The world beyond the wall: MCP wires outside tools in.",
    "ch13": "All wired up — let answers flow like water.",
    "ch14": "Before it runs free, learn to draw the route and plant the flag.",
    "ch15": "You've seen it all — now crank a windlass of your own.",
    "apxd": "New words on the road all live in this little dictionary.",
}

# Take one sentence home: restates only the analogy already on the page
TAKEAWAYS_EN = {
    "ch01": "Remember: the paradigm changed — so does the way you aim.",
    "ch02": "Remember: keep the heartbeat steady and the loop never breaks.",
    "ch03": "Remember: tools are its hands — more hands, more it can do.",
    "ch04": "Remember: guardrails aren't limits; they let it act boldly.",
    "ch05": "Remember: settings are genes — character settles layer by layer.",
    "ch06": "Remember: long-term memory is a folded notebook of key points.",
    "ch07": "Remember: working memory is a gauge — overfill it and it spills.",
    "ch08": "Remember: hooks are small actions on lifecycle milestones.",
    "ch09": "Remember: forking means handing work to small helpers.",
    "ch10": "Remember: the orchestrator is the hub — four squads on call.",
    "ch11": "Remember: skills are cards in your pocket — plug in and they work.",
    "ch12": "Remember: that one line connects it to the world's tools.",
    "ch13": "Remember: streaming = generated and watched at the same time.",
    "ch14": "Remember: draw the route, plant the flag, then set out.",
    "ch15": "Remember: you can build a Harness yourself — crank the windlass.",
    "apxd": "Remember: skip the dictionary and the road gets confusing.",
}

VIDEOS_EN = {
    "front": [("YouTube · Anthropic official channel", YT_CHANNEL),
              ("YouTube · Mastering Claude Code in 30 minutes (official, verified)",
               "https://www.youtube.com/watch?v=6eBSHbLKuN0"),
              ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch01": [("Bilibili · Claude Code tutorial (community, verified)",
              "https://www.bilibili.com/video/BV1uS9UBQEuH"),
             ("YouTube · Mastering Claude Code in 30 minutes (official, verified)",
              "https://www.youtube.com/watch?v=6eBSHbLKuN0")],
    "ch02": [("Bilibili · search “Claude Code conversation”", B_SEARCH + "Claude%20Code%20%E5%AF%B9%E8%AF%9D")],
    "ch03": [("Bilibili · search “Claude Code tools”", B_SEARCH + "Claude%20Code%20%E5%B7%A5%E5%85%B7")],
    "ch04": [("Bilibili · search “Claude Code permissions”", B_SEARCH + "Claude%20Code%20%E6%9D%83%E9%99%90")],
    "ch05": [("Bilibili · search “Claude Code settings”", B_SEARCH + "Claude%20Code%20%E9%85%8D%E7%BD%AE")],
    "ch06": [("Bilibili · search “Claude Code memory”", B_SEARCH + "Claude%20Code%20%E8%AE%B0%E5%BF%86")],
    "ch07": [("Bilibili · search “Claude Code context”", B_SEARCH + "Claude%20Code%20%E4%B8%8A%E4%B8%8B%E6%96%87"),
             ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch08": [("Bilibili · search “Claude Code Hooks”", B_SEARCH + "Claude%20Code%20Hooks")],
    "ch09": [("Bilibili · search “Claude Code sub-agents”", B_SEARCH + "Claude%20Code%20%E5%AD%90%E6%99%BA%E8%83%BD%E4%BD%93"),
             ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch10": [("YouTube · Anthropic official channel (multi-agent)", YT_CHANNEL)],
    "ch11": [("Bilibili · search “Claude Skills”", B_SEARCH + "Claude%20Skills")],
    "ch12": [("Bilibili · MCP tutorial (community, verified)", "https://www.bilibili.com/video/BV1qkHrzHEh4"),
             ("Bilibili · search “MCP tutorial”", B_SEARCH + "MCP%20%E6%95%99%E7%A8%8B"),
             ("YouTube · Anthropic official channel (MCP)", YT_CHANNEL),
             ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch13": [("Bilibili · search “Claude Code streaming”", B_SEARCH + "Claude%20Code%20%E6%B5%81%E5%BC%8F")],
    "ch14": [("Bilibili · search “Claude Code plan mode”", B_SEARCH + "Claude%20Code%20Plan")],
    "ch15": [("YouTube · Anthropic official channel (agent deep dive)", YT_CHANNEL)],
}

STRIP = re.compile(r"<[^>]+>")


GLOSS = json.load(open(ROOT / "yuyu-book" / "glosses.json", encoding="utf-8"))


def glossify(text: str, lang: str, limit: int = 3) -> str:
    """Wrap the first few glossary terms with a hover definition.

    作者在 glosses.json 里为每个术语写好了白话释义——分册直接借用，
    不新增任何解释。最长形态优先、互不重叠、每站限量，避免满屏虚线。
    """
    if not text:
        return text
    forms = []
    for gid, g in GLOSS.items():
        d = g["plain"].get(lang, "")
        if not d:
            continue
        for f in g["forms"].get(lang, []):
            f = f.strip()
            if len(f) >= (2 if lang == "zh" else 4):
                forms.append((f, d))
    forms.sort(key=lambda x: -len(x[0]))
    taken = []
    for f, d in forms:
        start = 0
        while True:
            i = text.find(f, start)
            if i < 0:
                break
            end = i + len(f)
            if all(end <= a or i >= b for a, b, _, _ in taken):
                taken.append((i, end, f, d))
                if len(taken) >= limit:
                    break
            start = i + len(f)
        if len(taken) >= limit:
            break
    for i, end, f, d in sorted(taken, reverse=True):
        safe = d.replace('"', "'")
        text = (text[:i] + f'<span class="gl" title="{safe}">{f}</span>'
                + text[end:])
    return text


def extract_units(html: str, uids: list) -> dict:
    marks = {u: html.find(f'id="{u}"') for u in uids}
    order = sorted(marks.items(), key=lambda kv: kv[1])
    units = {}
    for i, (uid, pos) in enumerate(order):
        stop = order[i + 1][1] if i + 1 < len(order) else len(html)
        seg = html[pos:stop]
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", seg, re.S)
        title = STRIP.sub("", title_m.group(1)).strip() if title_m else uid
        plain_m = re.search(r'class="lb-plain">(.*?)</p>', seg, re.S)
        analogy_m = re.search(r'class="lb-a-tag">[^<]*</span>(.*?)</p>', seg, re.S)
        question_m = re.search(r'class="cc-tag">[^<]*</h4><p>(.*?)</p>', seg, re.S)
        deliver_m = re.search(r'compass-card deliverable"><h4 class="cc-tag">[^<]*</h4><p>(.*?)</p>', seg, re.S)
        units[uid] = {
            "title": title,
            "plain": STRIP.sub("", plain_m.group(1)).strip() if plain_m else "",
            "analogy": STRIP.sub("", analogy_m.group(1)).strip() if analogy_m else "",
            "question": STRIP.sub("", question_m.group(1)).strip() if question_m else "",
            "deliver": STRIP.sub("", deliver_m.group(1)).strip() if deliver_m else "",
        }
    return units


def station(uid: str, num: str, unit: dict, svg: str, tier: str, part: str,
            bg: str, width: int, t) -> str:
    ana_txt = glossify(unit["analogy"], t["lang"]) if unit["analogy"] else ""
    analogy = (f'<p class="st-ana">{t["analogy_label"]}{ana_txt}</p>'
               if unit["analogy"] else "")
    plain_txt = glossify(unit["plain"], t["lang"]) if unit["plain"] else ""
    plain = (f'<p class="st-plain">{plain_txt}</p>' if unit["plain"] else "")
    trans = t["transitions"].get(uid, "")
    trans_html = f'<p class="st-trans">{trans}</p>' if trans else ""
    vids = "".join(f'<a class="st-vid" href="{url}" target="_blank"'
                   f' rel="noopener" title="{t["verified_note"]}">📺 {label}</a>'
                   for label, url in t["videos"].get(uid, []))
    vids_html = f'<p class="st-vids">{vids}</p>' if vids else ""
    take = t["takeaways"].get(uid, "")
    take_html = f'<p class="st-take">🔖 {take}</p>' if take else ""
    gain = unit.get("deliver", "")
    gain_html = (f'<p class="st-gain">{t["gain_label"]}{gain}</p>'
                 if gain else "")
    question = unit.get("question", "")
    quiz_html = (f'<details class="st-quiz"><summary>{t["quiz_label"]}'
                 f'</summary><p>{question}</p></details>') if question else ""
    return f"""<article class="st" style="background:{bg}">
  <div class="st-art" style="width:{width}px" tabindex="0" role="button"
       aria-label="{t["replay_label"].format(name=unit["title"])}">{svg}</div>
  <div class="st-body">
    <p class="st-part">{t["station_word"].format(num=num, total=t["total"])} · {part} · <b class="st-tier">{tier}</b></p>
    <h2>{unit["title"]}</h2>
    <p class="st-cap">{t["captions"].get(uid, "")}</p>
    {trans_html}{plain}{analogy}{take_html}{gain_html}{quiz_html}{vids_html}
    <a class="st-go" href="{t["book"]}#{uid}">{t["go_deeper"]}</a>
  </div>
</article>"""


def build(lang: str) -> tuple[str, int]:
    t = LANGS[lang]
    dist = ROOT / "yuyu-book" / "dist" / t["dist"]
    html = dist.read_text(encoding="utf-8")
    svgs = {u: (ART / f"{u}.svg").read_text(encoding="utf-8").strip()
            for u in t["order"] + ["cover", "keeper"]
            if (ART / f"{u}.svg").exists()}
    units = extract_units(html, t["order"])

    stations = [f"""<article class="st st-hero" style="background:#FBF6EC">
  <div class="st-art" style="width:200px">{svgs.get("cover", "")}</div>
  <div class="st-body">
    <p class="st-part">{t["hero_tag"]}</p>
    <h2>{t["hero_h2"]}</h2>
    <p class="st-cap">{t["captions"]["cover"]}</p>
    <p class="st-plain">{t["hero_plain"]}</p>
    <a class="st-go" href="{t["book"]}#front">{t["hero_link"]}</a>
  </div>
</article>"""]

    num = 0
    for part, tier, bg, us in t["parts"]:
        for uid in us:
            num += 1
            stations.append(station(uid, num,
                                    units.get(uid, {"title": uid}),
                                    svgs.get(uid, ""), tier, part, bg,
                                    t["widths"].get(uid, 148), t))

    num += 1
    stations.append(f"""<article class="st" style="background:#FBF6EC">
  <div class="st-art" style="width:148px">{svgs.get("apxd", "")}</div>
  <div class="st-body">
    <p class="st-part">{t["station_word"].format(num=num, total=t["total"])} · {t["appendix_tag"]} · <b class="st-tier">{t["appendix_tier"]}</b></p>
    <h2>{t["appendix_h2"]}</h2>
    <p class="st-cap">{t["captions"]["apxd"]}</p>
    <p class="st-plain">{t["appendix_plain"]}</p>
    <a class="st-go" href="{t["book"]}#apxd">{t["appendix_link"]}</a>
  </div>
</article>
<article class="st st-hero" style="background:#FBF6EC">
  <div class="st-art" style="width:148px">{svgs.get("keeper", "")}</div>
  <div class="st-body">
    <p class="st-part">{t["keeper_tag"]}</p>
    <h2>{t["keeper_h2"]}</h2>
    <p class="st-cap">{t["captions"]["keeper"]}</p>
    <p class="st-plain">{t["keeper_plain"]}</p>
    <a class="st-go" href="{t["book"]}">{t["keeper_link"]}</a>
  </div>
</article>""")

    page = t["page_head"] + "\n".join(stations) + t["page_tail"]
    out = ROOT / "docs" / t["out"]
    out.write_text(page, encoding="utf-8")
    return out, len(stations)


PAGE_HEAD_ZH = """<!doctype html>
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
.st-take{margin:0 0 10px;font-size:13.5px;color:#8A4A34}
.st-gain{margin:0 0 10px;font-size:13.5px;color:#4E6E5D}
.gl{border-bottom:1px dashed #8A7D68;cursor:help}
.st-vids{margin:0 0 10px;font-size:12.5px}
.st-vids .st-vid{display:inline-block;margin-right:14px;color:#4C7093;
  text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
.st-vids .st-vid:hover{color:#B4472F;border-bottom-color:#B4472F}
.st-go{font-size:13.5px;color:#26221B;text-decoration:none;border-bottom:1.5px solid #B4472F;
       padding-bottom:1px;transition:color .16s ease}
.st-go:hover{color:#B4472F}
.st-art{cursor:pointer;transition:transform .25s cubic-bezier(.34,1.56,.64,1)}
.st-art:hover{transform:scale(1.03)}
.resume{position:fixed;left:18px;bottom:16px;z-index:98;display:flex;gap:10px;align-items:center;background:#FFFDF8;border:1.5px solid #B4472F;color:#26221B;font-size:12.5px;padding:9px 13px;border-radius:6px 3px 7px 4px/4px 7px 3px 6px;box-shadow:2px 3px 0 rgba(38,34,27,.18)}
.resume b{color:#B4472F}
.resume button{padding:5px 11px;font-size:12px}
.resume .ghost{border-color:#8A7D68;color:#675F4F;box-shadow:none}
.st-art:hover{transform:scale(1.03)}
.st-art:focus-visible{outline:2px solid #B4472F;outline-offset:4px}
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
  <p class="hint">每一站的句子都取自大书作者自己的通俗层；底色一层比一层深，就是"由浅入深"的顺序；句中带虚线的词，悬停即出白话释义。某站看懂了，就推开「想深入」的门，去大书里读完整的原理。</p>
</header>
<main>
"""

PAGE_TAIL_ZH = """</main>
<footer>
本分册由大书的通俗层与 <a href="illustration-gallery.html">26 幅手绘插图</a> 组成；
画风体系来自 <a href="https://github.com/yang0/handraw-style">yang0/handraw-style</a>
（MIT with Attribution）。大书：<a href="yuyu-agent-harness-zh.html">御舆：解码 Agent Harness</a>。
<br>📺 页内视频为官方频道与社区资源，属<b>非规范来源</b>（仅核验存在性，
核验日期 2026-10-31）；一切技术事实以大书正文及其规范来源为准。本分册对应大书 v0.3.3 构建基线。
</footer>
<div class="resume" id="resume" style="display:none">
  <span>上次读到第 <b id="resume-station"></b> 站</span>
  <button id="resume-go">继续读 →</button>
  <button id="resume-no" class="ghost">从头开始</button>
</div>
<script>
/* click or Enter re-inks the drawing — the reader takes part in it */
document.querySelectorAll(".st-art").forEach(art => {
  const fig = art.closest(".st");
  const replay = (cx, cy) => {
    const svg = art.querySelector("svg");
    if (!svg) return;
    svg.querySelectorAll("path, circle").forEach(el => {
      el.style.strokeDasharray = "100 100";
      const a = el.animate([{strokeDashoffset:"100"},{strokeDashoffset:"0"}],
        {duration:700, delay:Math.random()*250, fill:"both", easing:"ease-out"});
      a.onfinish = () => { el.style.strokeDasharray = ""; };
    });
    if (cx !== undefined) {
      for (let i = 0; i < 8; i++) {
        const sp = document.createElement("i");
        sp.style.cssText = "position:fixed;width:6px;height:6px;border-radius:60% 40% 55% 45%;pointer-events:none;z-index:99;background:" + (i % 3 ? "#26221B" : "#B4472F");
        sp.style.left = cx + "px"; sp.style.top = cy + "px";
        document.body.appendChild(sp);
        const ang = (i / 8) * Math.PI * 2, d = 16 + Math.random() * 22;
        const an = sp.animate([{transform:"translate(0,0) scale(1)",opacity:1},
          {transform:`translate(${Math.cos(ang)*d}px,${Math.sin(ang)*d+8}px) scale(.25)`,opacity:0}],
          {duration:460, easing:"cubic-bezier(.34,1.56,.64,1)", fill:"both"});
        an.onfinish = () => sp.remove();
      }
    }
  };
  art.addEventListener("click", e => replay(e.clientX, e.clientY));
  art.addEventListener("keydown", e => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    const r = art.getBoundingClientRect();
    replay(r.left + r.width / 2, r.top + r.height / 2);
  });
});
</script>
<script>
(function () {
  const KEY = "yy-reader-zh";
  let saved = 0;
  try { saved = +localStorage.getItem(KEY) || 0; } catch (e) {}
  let lastSave = 0;
  window.addEventListener("scroll", () => {
    const now = Date.now();
    if (now - lastSave < 800) return;
    lastSave = now;
    try { localStorage.setItem(KEY, String(window.scrollY)); } catch (e) {}
  }, {passive: true});
  if (saved > 600) {
    const banner = document.getElementById("resume");
    banner.style.display = "flex";
    const st = document.querySelectorAll(".st");
    let idx = 0;
    st.forEach((el, i) => {
      if (el.getBoundingClientRect().top + window.scrollY <= saved) idx = i;
    });
    document.getElementById("resume-station").textContent = idx + 1;
    document.getElementById("resume-go").onclick = () => {
      window.scrollTo({top: saved, behavior: "smooth"});
      banner.style.display = "none";
    };
    document.getElementById("resume-no").onclick = () => {
      try { localStorage.removeItem(KEY); } catch (e) {}
      banner.style.display = "none";
    };
  }
})();
</script>
<script>
(function () {
  const KEY = "yy-reader-en";
  let saved = 0;
  try { saved = +localStorage.getItem(KEY) || 0; } catch (e) {}
  let lastSave = 0;
  window.addEventListener("scroll", () => {
    const now = Date.now();
    if (now - lastSave < 800) return;
    lastSave = now;
    try { localStorage.setItem(KEY, String(window.scrollY)); } catch (e) {}
  }, {passive: true});
  if (saved > 600) {
    const banner = document.getElementById("resume");
    banner.style.display = "flex";
    const st = document.querySelectorAll(".st");
    let idx = 0;
    st.forEach((el, i) => {
      if (el.getBoundingClientRect().top + window.scrollY <= saved) idx = i;
    });
    document.getElementById("resume-station").textContent = idx + 1;
    document.getElementById("resume-go").onclick = () => {
      window.scrollTo({top: saved, behavior: "smooth"});
      banner.style.display = "none";
    };
    document.getElementById("resume-no").onclick = () => {
      try { localStorage.removeItem(KEY); } catch (e) {}
      banner.style.display = "none";
    };
  }
})();
</script>
</body>
</html>
"""

PAGE_HEAD_EN = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Yù Yú · Beginner Reader — Agent Harness in Pictures</title>
<style>
body{margin:0;font:16px/1.8 "Iowan Old Style",Palatino,Georgia,"Noto Serif SC",serif;background:#F5F0E6;color:#26221B}
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
.st-take{margin:0 0 10px;font-size:13.5px;color:#8A4A34}
.st-gain{margin:0 0 10px;font-size:13.5px;color:#4E6E5D}
.gl{border-bottom:1px dashed #8A7D68;cursor:help}
.st-vids{margin:0 0 10px;font-size:12.5px}
.st-vids .st-vid{display:inline-block;margin-right:14px;color:#4C7093;
  text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
.st-vids .st-vid:hover{color:#B4472F;border-bottom-color:#B4472F}
.st-go{font-size:13.5px;color:#26221B;text-decoration:none;border-bottom:1.5px solid #B4472F;
       padding-bottom:1px;transition:color .16s ease}
.st-go:hover{color:#B4472F}
.st-art{cursor:pointer;transition:transform .25s cubic-bezier(.34,1.56,.64,1)}
.st-art:hover{transform:scale(1.03)}
.resume{position:fixed;left:18px;bottom:16px;z-index:98;display:flex;gap:10px;align-items:center;background:#FFFDF8;border:1.5px solid #B4472F;color:#26221B;font-size:12.5px;padding:9px 13px;border-radius:6px 3px 7px 4px/4px 7px 3px 6px;box-shadow:2px 3px 0 rgba(38,34,27,.18)}
.resume b{color:#B4472F}
.resume button{padding:5px 11px;font-size:12px}
.resume .ghost{border-color:#8A7D68;color:#675F4F;box-shadow:none}
.st-art:hover{transform:scale(1.03)}
.st-art:focus-visible{outline:2px solid #B4472F;outline-offset:4px}
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
  <h1>Yù Yú · Beginner Reader</h1>
  <svg class="brush" viewBox="0 0 190 10" aria-hidden="true"><path d="M4 6q30-4.5 62-2.5t72-1q24 .2 46 1.8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".85"/><path d="M152 5.6q10-.6 20-.2" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".45"/><circle cx="178" cy="5.8" r="1.5" fill="currentColor" stroke="none"/></svg>
  <p class="sub">Understanding Agent Harness in pictures — one concept per station, one sentence at a time</p>
  <p class="hint">Every sentence comes from the book's own plain-language layer; the paper darkens station by station — that is the shallow-to-deep order. Dotted terms show a plain-language definition on hover. When a station clicks, push open the “go deeper” door and read the full principle in the book.</p>
</header>
<main>
"""

PAGE_TAIL_EN = """</main>
<footer>
This reader is assembled from the full book's plain-language layer and the
<a href="illustration-gallery.html">26 hand-inked figures</a>; the style system comes
from <a href="https://github.com/yang0/handraw-style">yang0/handraw-style</a>
(MIT with Attribution). Full book: <a href="yuyu-agent-harness-en.html">Yù Yú: Decoding Agent Harness</a>.
<br>📺 Videos are official-channel and community resources — <b>non-normative</b>
(existence verified 2026-10-31); every technical fact defers to the book and its
normative sources. This reader tracks book baseline v0.3.3.
</footer>
<div class="resume" id="resume" style="display:none">
  <span>You stopped at station <b id="resume-station"></b></span>
  <button id="resume-go">Continue →</button>
  <button id="resume-no" class="ghost">Start over</button>
</div>
<script>
/* click or Enter re-inks the drawing — the reader takes part in it */
document.querySelectorAll(".st-art").forEach(art => {
  const fig = art.closest(".st");
  const replay = (cx, cy) => {
    const svg = art.querySelector("svg");
    if (!svg) return;
    svg.querySelectorAll("path, circle").forEach(el => {
      el.style.strokeDasharray = "100 100";
      const a = el.animate([{strokeDashoffset:"100"},{strokeDashoffset:"0"}],
        {duration:700, delay:Math.random()*250, fill:"both", easing:"ease-out"});
      a.onfinish = () => { el.style.strokeDasharray = ""; };
    });
    if (cx !== undefined) {
      for (let i = 0; i < 8; i++) {
        const sp = document.createElement("i");
        sp.style.cssText = "position:fixed;width:6px;height:6px;border-radius:60% 40% 55% 45%;pointer-events:none;z-index:99;background:" + (i % 3 ? "#26221B" : "#B4472F");
        sp.style.left = cx + "px"; sp.style.top = cy + "px";
        document.body.appendChild(sp);
        const ang = (i / 8) * Math.PI * 2, d = 16 + Math.random() * 22;
        const an = sp.animate([{transform:"translate(0,0) scale(1)",opacity:1},
          {transform:`translate(${Math.cos(ang)*d}px,${Math.sin(ang)*d+8}px) scale(.25)`,opacity:0}],
          {duration:460, easing:"cubic-bezier(.34,1.56,.64,1)", fill:"both"});
        an.onfinish = () => sp.remove();
      }
    }
  };
  art.addEventListener("click", e => replay(e.clientX, e.clientY));
  art.addEventListener("keydown", e => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    const r = art.getBoundingClientRect();
    replay(r.left + r.width / 2, r.top + r.height / 2);
  });
});
</script>
</body>
</html>
"""

LANGS = {
    "zh": {
        "dist": "yuyu-agent-harness-zh.html",
        "book": "yuyu-agent-harness-zh.html",
        "out": "beginner-reader.html",
        "order": ORDER, "parts": PARTS, "total": 16,
        "widths": WIDTH,
        "lang": "zh",
        "captions": CAPTIONS, "transitions": TRANSITIONS, "videos": VIDEOS,
        "takeaways": TAKEAWAYS,
        "quiz_label": "自测一下 · 答案在大书这一章",
        "gain_label": "读完你能：",
        "replay_label": "重播「{name}」的手绘过程",
        "verified_note": "链接存在性核验 2026-10-31（非规范来源）",
        "station_word": "第 {num} / {total} 站",
        "go_deeper": "想深入？翻开大书这一章 →",
        "hero_tag": "开卷 · 人人可读",
        "hero_h2": "这本书在讲一件什么事？",
        "hero_plain": ("大模型很聪明，但让它真正替你干活，还需要一整套“驾车”的装备"
                       "——这本书把这套装备拆开给你看。不用先懂编程，跟着图往下走就行。"),
        "hero_link": "想深入？翻开前言 →",
        "appendix_tag": "附录", "appendix_tier": "随身",
        "appendix_h2": "路上遇到生词？",
        "appendix_plain": "术语表、源码地图、工具清单、功能开关——都在附录里，随时折回去查。",
        "appendix_link": "想深入？翻开附录 D →",
        "keeper_tag": "到站 · 老驿卒的话",
        "keeper_h2": "路走完了，接下来呢？",
        "keeper_plain": ("这本分册只是地图，真正的风景在大书里——每站都有「想深入」的门，"
                         "推门进去，那里有完整的原理、代码与练习。"),
        "keeper_link": "回到大书 →",
        "analogy_label": "打个比方：",
        "page_head": PAGE_HEAD_ZH,
        "page_tail": PAGE_TAIL_ZH,
    },
    "en": {
        "dist": "yuyu-agent-harness-en.html",
        "book": "yuyu-agent-harness-en.html",
        "out": "beginner-reader.en.html",
        "order": ORDER_EN, "parts": PARTS_EN, "total": 16,
        "widths": {u: 148 for u in ORDER_EN},
        "lang": "en",
        "captions": CAPTIONS_EN, "transitions": TRANSITIONS_EN,
        "videos": VIDEOS_EN,
        "takeaways": TAKEAWAYS_EN,
        "quiz_label": "Test yourself · the answer is in the chapter",
        "gain_label": "After this chapter you can: ",
        "replay_label": "Replay the ink drawing of “{name}”",
        "verified_note": "link existence verified 2026-10-31 (non-normative)",
        "station_word": "Station {num} / {total}",
        "go_deeper": "Go deeper — open this chapter in the full book →",
        "hero_tag": "Opening · for everyone",
        "hero_h2": "What is this book about?",
        "hero_plain": ("LLMs are brilliant, but to make one truly work for you takes a "
                       "whole set of driving gear — this book takes that gear apart, "
                       "piece by piece. No programming required; just follow the pictures."),
        "hero_link": "Want depth? Open the preface →",
        "appendix_tag": "Appendix", "appendix_tier": "At hand",
        "appendix_h2": "New words on the road?",
        "appendix_plain": ("Glossary, source map, tool inventory, feature flags — all in "
                           "the appendices, ready to be looked up."),
        "appendix_link": "Depth? Open Appendix D →",
        "keeper_tag": "Arrived · a word from the old courier",
        "keeper_h2": "The road ends — what next?",
        "keeper_plain": ("This reader is just the map; the real scenery is in the full "
                         "book — every station has a door marked “go deeper”."),
        "keeper_link": "Back to the full book →",
        "analogy_label": "Think of it as: ",
        "page_head": PAGE_HEAD_EN,
        "page_tail": PAGE_TAIL_EN,
    },
}


def main():
    for lang in ("zh", "en"):
        out, n = build(lang)
        print(f"{out} ({n} stations)")


if __name__ == "__main__":
    main()
