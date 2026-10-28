# -*- coding: utf-8 -*-
"""Dark engineering slides + short anim clips for ch01 long lecture."""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (12, 16, 24)
PANEL = (22, 30, 44)
ACCENT = (64, 180, 255)
ACCENT2 = (120, 220, 170)
WARN = (255, 170, 70)
TEXT = (230, 236, 245)
MUTED = (140, 152, 170)
LINE = (40, 52, 72)
RED = (240, 100, 100)
GREEN = (90, 210, 140)

OUT = Path(__file__).resolve().parent.parent / "slides"
ANIM = Path(__file__).resolve().parent.parent / "anim"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"

def font(size, bold=False):
    path = FONT_BD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size, index=0)
    except Exception:
        return ImageFont.truetype(FONT_REG, size)

def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 64], fill=(8, 12, 18))
    d.rectangle([0, 62, W, 64], fill=ACCENT)
    d.text((40, 16), "驭者·Agent Harness  ·  第 01 讲", font=font(26, True), fill=ACCENT)
    d.text((W - 420, 18), "基于开源书稿", font=font(24), fill=MUTED)
    d.rectangle([0, H - 48, W, H], fill=(8, 12, 18))
    d.text((40, H - 38), "小电讲电路", font=font(20), fill=MUTED)
    return img, d

def card(d, xy, wh, title, body_lines, accent=ACCENT):
    x, y = xy
    w, h = wh
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=PANEL, outline=LINE, width=2)
    d.rectangle([x, y, x + 8, y + h], fill=accent)
    d.text((x + 28, y + 18), title, font=font(28, True), fill=accent)
    yy = y + 64
    for line in body_lines:
        d.text((x + 28, yy), line, font=font(24), fill=TEXT)
        yy += 36

def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.png"
    img.save(p, "PNG")
    return p

def slide_open():
    img, d = new_canvas()
    d.text((80, 160), "智能体编程的新范式", font=font(64, True), fill=TEXT)
    d.text((80, 260), "为什么需要 Agent Harness，而不是只包一层 API", font=font(34), fill=MUTED)
    d.rounded_rectangle([80, 360, 820, 520], radius=20, fill=PANEL, outline=ACCENT, width=2)
    d.text((110, 400), "系列：驭者·Agent Harness", font=font(32, True), fill=ACCENT)
    d.text((110, 450), "出处：基于开源书稿", font=font(28), fill=TEXT)
    d.text((80, 580), "Chatbot 手工胶水  →  Agent 工具编排", font=font(36), fill=ACCENT2)
    return save(img, "open")

def render_chatbot_anim():
    ANIM.mkdir(parents=True, exist_ok=True)
    frames = []
    steps = ["复制 Prompt", "粘贴到编辑器", "跑终端", "把报错贴回对话"]
    tools = ["Tool", "FS", "Git", "Shell"]
    for f in range(24):
        img, d = new_canvas()
        d.text((80, 100), "Chatbot 胶水 vs Agent 编排", font=font(44, True), fill=TEXT)
        d.rounded_rectangle([80, 180, 900, 900], radius=18, fill=PANEL, outline=RED, width=2)
        d.text((120, 210), "左边：人当胶水", font=font(32, True), fill=RED)
        for i, s in enumerate(steps):
            y = 290 + i * 110
            active = (f // 3) % 4 == i
            col = WARN if active else MUTED
            d.rounded_rectangle([120, y, 840, y + 80], radius=12, fill=(30, 20, 24) if active else (18, 22, 30), outline=col, width=2)
            d.text((160, y + 22), f"{i+1}. {s}", font=font(28), fill=col)
        d.rounded_rectangle([960, 180, 1840, 900], radius=18, fill=PANEL, outline=GREEN, width=2)
        d.text((1000, 210), "右边：Agent 自己编排", font=font(32, True), fill=GREEN)
        cx, cy = 1400, 520
        d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=ACCENT, width=4)
        d.text((cx - 48, cy - 18), "Agent", font=font(28, True), fill=ACCENT)
        progress = min(1.0, f / 16)
        for i, t in enumerate(tools):
            ang = -math.pi / 2 + i * (math.pi / 2)
            tx = cx + int(math.cos(ang) * 220 * max(progress, 0.05))
            ty = cy + int(math.sin(ang) * 180 * max(progress, 0.05))
            lit = progress > 0.4
            if progress > 0.05:
                d.line([cx, cy, tx, ty], fill=ACCENT if lit else LINE, width=3)
            d.rounded_rectangle([tx - 70, ty - 36, tx + 70, ty + 36], radius=10, fill=PANEL, outline=ACCENT2 if lit else LINE, width=2)
            d.text((tx - 30, ty - 14), t, font=font(26, True), fill=ACCENT2 if lit else MUTED)
        fp = ANIM / f"chatbot-glue_{f:03d}.png"
        img.save(fp)
        frames.append(fp)
    img = Image.open(frames[-1])
    save(img, "chatbot-glue")
    return frames

def slide_llm_roles():
    img, d = new_canvas()
    d.text((80, 110), "范式转移：参谋 → 指挥官", font=font(44, True), fill=TEXT)
    card(d, (80, 220), (820, 520), "过去：对话伙伴 / 参谋", ["LLM 写文本、答问题", "人负责落地与决策", "边界停在「说清楚」"], WARN)
    card(d, (1000, 220), (820, 520), "现在：推理引擎 / 指挥官", ["Tool Use 打开边界", "模型决定调什么工具", "系统层必须接住风险"], ACCENT2)
    return save(img, "llm-roles")

def slide_six_challenges():
    img, d = new_canvas()
    d.text((80, 110), "六大工程挑战 → Harness 中心", font=font(42, True), fill=TEXT)
    items = ["注册与发现", "参数校验", "权限管控", "错误恢复", "状态一致性", "并发与调度"]
    for i, t in enumerate(items):
        x = 120 + (i % 3) * 560
        y = 220 + (i // 3) * 280
        d.rounded_rectangle([x, y, x + 500, y + 200], radius=16, fill=PANEL, outline=LINE, width=2)
        d.text((x + 40, y + 70), f"{i+1}. {t}", font=font(36, True), fill=ACCENT)
    d.ellipse([860, 470, 1060, 670], outline=ACCENT2, width=4)
    d.text((890, 545), "Harness", font=font(28, True), fill=ACCENT2)
    return save(img, "six-challenges")

def slide_car():
    img, d = new_canvas()
    d.text((80, 120), "遥控器汽车 vs 自动驾驶系统", font=font(42, True), fill=TEXT)
    card(d, (80, 240), (820, 500), "简单封装 ≈ 遥控器", ["while 循环 + call API", "假设理想世界", "流式/权限/恢复全靠人"], RED)
    card(d, (1000, 240), (820, 500), "Agent Harness ≈ 自动驾驶", ["感知·规划·约束·冗余", "统一接住六大挑战", "可扩展、可恢复、可审计"], GREEN)
    return save(img, "car-remote-vs-autonomous")

def slide_anti():
    img, d = new_canvas()
    d.text((80, 120), "反模式：裸 while 循环", font=font(42, True), fill=TEXT)
    code = [
        "while True:",
        "    resp = call_api(messages)",
        "    tool = parse(resp)",
        "    result = execute(tool)   # no permission/stream/retry",
        "    messages.append(result)",
    ]
    d.rounded_rectangle([120, 220, 1800, 780], radius=16, fill=(16, 20, 28), outline=RED, width=2)
    for i, line in enumerate(code):
        d.text((180, 280 + i * 70), line, font=font(34), fill=WARN if "execute" in line else TEXT)
    d.text((120, 840), "停一下：流式、取消、权限、重试……这些都要 Harness 接住。", font=font(28), fill=MUTED)
    return save(img, "anti-pattern-while")

def slide_paradigm():
    img, d = new_canvas()
    d.text((80, 200), "§1.1 范式转移", font=font(56, True), fill=TEXT)
    d.text((80, 320), "从 Chatbot 到 Agent：推理引擎 + Tool Use + Harness", font=font(32), fill=MUTED)
    return save(img, "paradigm")

def slide_architecture():
    img, d = new_canvas()
    d.text((80, 200), "§1.2 全景架构", font=font(56, True), fill=TEXT)
    d.text((80, 320), "规模 · 技术栈 · 五模块骨架", font=font(32), fill=MUTED)
    return save(img, "architecture")

def slide_timeline():
    img, d = new_canvas()
    d.text((80, 110), "AI 编程工具时间线", font=font(42, True), fill=TEXT)
    nodes = ["Copilot", "Function Calling", "Devin / Cursor", "Claude Code", "MCP", "源码公开"]
    y = 520
    d.line([140, y, 1780, y], fill=LINE, width=4)
    for i, n in enumerate(nodes):
        x = 180 + i * 280
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=ACCENT if i >= 3 else MUTED)
        d.text((x - 70, y + 40), n, font=font(22, True), fill=TEXT if i >= 3 else MUTED)
    d.text((1180, 280), "你在这里 →", font=font(30, True), fill=ACCENT2)
    return save(img, "ai-tools-timeline")

def render_scale_anim():
    ANIM.mkdir(parents=True, exist_ok=True)
    frames = []
    for f in range(30):
        t = f / 29
        files = int(1884 * t)
        loc = int(512664 * t)
        img, d = new_canvas()
        d.text((80, 120), "Claude Code 规模锚点", font=font(42, True), fill=TEXT)
        d.text((80, 280), f"{files:,}", font=font(120, True), fill=ACCENT)
        d.text((80, 430), "TypeScript 文件", font=font(36), fill=MUTED)
        d.text((980, 280), f"{loc:,}", font=font(100, True), fill=ACCENT2)
        d.text((980, 430), "行代码（LOC）", font=font(36), fill=MUTED)
        d.text((80, 560), "接近一个 VS Code 体量级的终端 Agent 系统", font=font(30), fill=TEXT)
        d.rounded_rectangle([80, 660, 1840, 860], radius=16, fill=PANEL, outline=LINE, width=2)
        d.text((120, 720), "高度模块化 + 工具编排 + 系统边界 = Harness 可维护性关键", font=font(32), fill=ACCENT)
        fp = ANIM / f"scale_{f:03d}.png"
        img.save(fp)
        frames.append(fp)
    img, d = new_canvas()
    d.text((80, 120), "Claude Code 规模锚点", font=font(42, True), fill=TEXT)
    d.text((80, 280), "1,884", font=font(120, True), fill=ACCENT)
    d.text((80, 430), "TypeScript 文件", font=font(36), fill=MUTED)
    d.text((980, 280), "512,664", font=font(100, True), fill=ACCENT2)
    d.text((980, 430), "行代码（LOC）", font=font(36), fill=MUTED)
    d.text((80, 560), "接近一个 VS Code 体量级的终端 Agent 系统", font=font(30), fill=TEXT)
    save(img, "scale-1884-512664")
    return frames

def slide_arch_layers():
    img, d = new_canvas()
    d.text((80, 100), "架构分层：五模块骨架", font=font(42, True), fill=TEXT)
    layers = [
        ("Entry", "CLI 启动 · React+Ink · 会话初始化", ACCENT),
        ("QueryEngine", "会话状态 · 历史 · 文件上下文 · 交互/SDK", ACCENT2),
        ("AsyncGenerator 主循环", "压上下文 → 流式 API → 工具/权限 → 状态", WARN),
        ("Tools + Permission", "55+ 工具 · 四阶段权限 · 并行与持久化", GREEN),
        ("Ext", "MCP · 子智能体 · 插件 · Hook", MUTED),
    ]
    for i, (title, body, col) in enumerate(layers):
        y = 180 + i * 140
        d.rounded_rectangle([120, y, 1800, y + 120], radius=14, fill=PANEL, outline=col, width=2)
        d.text((160, y + 22), title, font=font(32, True), fill=col)
        d.text((160, y + 68), body, font=font(26), fill=TEXT)
    return save(img, "arch-layers")

def slide_tech():
    img, d = new_canvas()
    d.text((80, 110), "技术栈五格", font=font(42, True), fill=TEXT)
    cells = [
        ("运行时", "Bun"),
        ("终端 UI", "React + Ink"),
        ("CLI", "Commander.js"),
        ("校验", "Zod v4"),
        ("LLM SDK", "@anthropic-ai/sdk"),
    ]
    for i, (k, v) in enumerate(cells):
        x = 100 + i * 360
        d.rounded_rectangle([x, 280, x + 330, 720], radius=16, fill=PANEL, outline=ACCENT, width=2)
        d.text((x + 40, 360), k, font=font(28), fill=MUTED)
        d.text((x + 40, 460), v, font=font(32, True), fill=TEXT)
    return save(img, "tech-stack-table")

def slide_async_steps():
    img, d = new_canvas()
    d.text((80, 100), "主循环七步（AsyncGenerator）", font=font(40, True), fill=TEXT)
    steps = ["拼系统 Prompt / 历史 / 工具定义", "流式读模型响应", "解析工具调用", "权限校验", "执行允许的工具", "写回结果到历史", "继续或结束 / 可中途取消"]
    for i, s in enumerate(steps):
        y = 180 + i * 100
        d.ellipse([100, y + 10, 160, y + 70], outline=ACCENT, width=3)
        d.text((118, y + 22), str(i + 1), font=font(28, True), fill=ACCENT)
        d.text((200, y + 22), s, font=font(30), fill=TEXT)
    return save(img, "async-generator-steps")

def slide_principles():
    img, d = new_canvas()
    d.text((80, 200), "§1.3 五大原则", font=font(56, True), fill=TEXT)
    d.text((80, 320), "Async · Security · Cache · Progressive · Immutable", font=font(30), fill=MUTED)
    return save(img, "principles")

def render_principles_anim():
    ANIM.mkdir(parents=True, exist_ok=True)
    names = [
        ("异步流式优先", "Async Generator First"),
        ("安全边界内嵌", "Security at the Perimeter"),
        ("缓存感知设计", "Cache-Aware Architecture"),
        ("渐进式能力扩展", "Progressive Capability"),
        ("不可变状态流转", "Immutable State Flow"),
    ]
    details = [
        ("principle-async", "异步流式优先", "yield 事件流 · Ctrl+C 可中断", "不为「等整包」牺牲可控性", 0),
        ("principle-security", "安全边界内嵌", "可见性→校验→决策→运行时", "权限是循环旁的硬闸门", 1),
        ("principle-cache", "缓存感知设计", "系统 Prompt 稳定前缀", "子智能体共享缓存命中", 2),
        ("principle-progressive", "渐进式能力扩展", "Tool → Skill → Plugin → MCP", "先小步，再打开边界", 3),
        ("principle-immutable", "不可变状态流转", "updater(prev)=>next", "快照传递，拒绝原地篡改", 4),
    ]
    for key, title, line1, line2, idx in details:
        img, d = new_canvas()
        d.text((80, 140), title, font=font(48, True), fill=TEXT)
        d.text((80, 240), line1, font=font(34), fill=ACCENT)
        d.text((80, 320), line2, font=font(30), fill=MUTED)
        for i, (cn, en) in enumerate(names):
            x = 80 + i * 360
            on = i == idx
            d.rounded_rectangle([x, 480, x + 340, 860], radius=14, fill=PANEL, outline=ACCENT if on else LINE, width=3 if on else 1)
            d.text((x + 24, 540), f"{i+1}", font=font(36, True), fill=ACCENT if on else MUTED)
            d.text((x + 24, 620), cn, font=font(26, True), fill=TEXT if on else MUTED)
            d.text((x + 24, 700), en.split()[0], font=font(20), fill=MUTED)
        save(img, key)

    frames = []
    for f in range(25):
        lit = min(4, f // 5)
        img, d = new_canvas()
        d.text((80, 120), "五大原则依次点亮", font=font(42, True), fill=TEXT)
        for i, (cn, en) in enumerate(names):
            x = 80 + i * 360
            on = i <= lit
            d.rounded_rectangle([x, 280, x + 340, 820], radius=14, fill=PANEL, outline=ACCENT if on else LINE, width=3 if on else 1)
            d.text((x + 30, 360), f"0{i+1}", font=font(40, True), fill=ACCENT if on else MUTED)
            d.text((x + 30, 480), cn, font=font(28, True), fill=TEXT if on else MUTED)
            for j, w in enumerate(en.split()):
                d.text((x + 30, 560 + j * 40), w, font=font(22), fill=MUTED)
        fp = ANIM / f"principles_{f:03d}.png"
        img.save(fp)
        frames.append(fp)
    return frames

def slide_practice():
    img, d = new_canvas()
    d.text((80, 200), "实战练习速览", font=font(56, True), fill=TEXT)
    d.text((80, 320), "install → /doctor → 一次工具调用", font=font(32), fill=MUTED)
    return save(img, "practice")

def slide_install():
    img, d = new_canvas()
    d.text((80, 140), "安装 Claude Code", font=font(44, True), fill=TEXT)
    d.rounded_rectangle([120, 260, 1800, 700], radius=16, fill=(16, 20, 28), outline=ACCENT, width=2)
    d.text((180, 340), "npm install -g @anthropic-ai/claude-code", font=font(36), fill=ACCENT2)
    d.text((180, 460), "claude --version", font=font(36), fill=TEXT)
    d.text((120, 780), "装好后先确认版本，再进 /doctor。", font=font(28), fill=MUTED)
    return save(img, "install-claude")

def slide_doctor():
    img, d = new_canvas()
    d.text((80, 110), "/doctor：五项检查（流式出结果）", font=font(40, True), fill=TEXT)
    items = ["环境", "权限", "MCP", "API", "文件系统"]
    for i, t in enumerate(items):
        x = 120 + i * 350
        d.rounded_rectangle([x, 300, x + 320, 700], radius=16, fill=PANEL, outline=ACCENT2, width=2)
        d.text((x + 40, 420), f"{i+1}", font=font(48, True), fill=ACCENT)
        d.text((x + 40, 520), t, font=font(32, True), fill=TEXT)
    return save(img, "doctor-flow")

def render_toolcall_anim():
    ANIM.mkdir(parents=True, exist_ok=True)
    stages = ["思考", "GlobTool(*.ts)", "拿到结果", "写回复"]
    frames = []
    for f in range(24):
        lit = min(3, f // 6)
        img, d = new_canvas()
        d.text((80, 110), "一次工具调用完整路径", font=font(42, True), fill=TEXT)
        for i, s in enumerate(stages):
            x = 160 + i * 420
            on = i <= lit
            d.rounded_rectangle([x, 360, x + 360, 560], radius=16, fill=PANEL, outline=ACCENT if on else LINE, width=3 if on else 1)
            d.text((x + 40, 430), s, font=font(30, True), fill=TEXT if on else MUTED)
            if i < 3:
                d.polygon([(x + 370, 450), (x + 400, 460), (x + 370, 470)], fill=ACCENT if i < lit else LINE)
        d.text((160, 700), "心中对照：QueryEngine → 主循环 → 工具注册 → 权限", font=font(28), fill=MUTED)
        fp = ANIM / f"toolcall_{f:03d}.png"
        img.save(fp)
        frames.append(fp)
    img = Image.open(frames[-1])
    save(img, "one-tool-call")
    return frames

def slide_outro():
    img, d = new_canvas()
    d.text((80, 160), "总结", font=font(48, True), fill=TEXT)
    bullets = [
        "范式已转移：从对话伙伴到推理引擎",
        "Harness 是工程系统，不是薄封装",
        "五模块是骨架，五原则是红线",
        "下一讲：对话主循环 AsyncGenerator",
    ]
    for i, b in enumerate(bullets):
        d.text((100, 280 + i * 80), f"·  {b}", font=font(32), fill=TEXT)
    d.rounded_rectangle([80, 640, 1840, 920], radius=18, fill=PANEL, outline=ACCENT, width=2)
    d.text((120, 700), "本系列基于开源书稿 · 驭者·Agent Harness", font=font(36, True), fill=ACCENT)
    d.text((120, 780), "关注小电讲电路 · 合集与置顶目录见简介", font=font(30), fill=TEXT)
    return save(img, "outro")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ANIM.mkdir(parents=True, exist_ok=True)
    print("static slides...")
    slide_open()
    slide_paradigm()
    slide_llm_roles()
    slide_six_challenges()
    slide_car()
    slide_anti()
    slide_architecture()
    slide_timeline()
    slide_arch_layers()
    slide_tech()
    slide_async_steps()
    slide_principles()
    slide_practice()
    slide_install()
    slide_doctor()
    slide_outro()
    img = Image.open(OUT / "outro.png")
    img.save(OUT / "outro-series.png")
    print("anims...")
    render_chatbot_anim()
    render_scale_anim()
    render_principles_anim()
    render_toolcall_anim()
    print("done slides=", len(list(OUT.glob('*.png'))), "anim_frames=", len(list(ANIM.glob('*.png'))))

if __name__ == "__main__":
    main()
