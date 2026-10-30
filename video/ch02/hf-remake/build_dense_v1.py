# -*- coding: utf-8 -*-
"""ch02 long densify v1 — clone of ch01 v4 quality bar. No publish."""
from __future__ import annotations
import html
import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMP = ROOT / "compositions"
SFX = ROOT / "assets" / "sfx"
TRANS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
TOTAL = 627.624


BLOCKS = [
    {
        "id": 'b01_hook',
        "title": '开场钩子 · 心跳',
        "start": 0.0,
        "end": 56.112,
        "huashu": [],
        "beats": [
        (0.0, 'section', '心跳', '开场钩子 · 心跳'),
        (5.0, 'persona_ah', 'Agent Harness', '考工记御者 · 收辔控速'),
        (10.2, 'card', 'PI 套壳，是能跑、能停、', 'PI 套壳，是能跑、能停、能诊断的整车。'),
        (15.75, 'stamp', '这一集拆开发动机的点火节', '记下这一点'),
        (21.65, 'card', '先停三秒想一下：如果你在源码里找', '先停三秒想一下：如果你在源码里找「心跳」，它最可能是什么？'),
        (26.85, 'pause', '停一下 · 它最可能是什么？回调', '跟 VO 对齐想一拍'),
        (32.4, 'section', 'unction 星号？答案写', 'unction 星号？答案写在本章标题里——异步'),
        (38.3, 'card', 'nerator。每一次 yiel', 'nerator。每一次 yield，就像一次脉搏：把「正在发生的'),
        (43.5, 'card', '而不是等整场手术做完才开门。书稿', '而不是等整场手术做完才开门。书稿第二节开篇就说：'),
        (49.05, 'persona_cl', 'Claude', '会诊医生 · 边想边说边开检查'),
        ],
    },
    {
        "id": 'b02_async',
        "title": '§2.1 异步生成器骨骼',
        "start": 56.112,
        "end": 221.28,
        "huashu": [],
        "beats": [
        (0.0, 'section', '§2.1 异步生成器骨骼', '§2.1 异步生成器骨骼'),
        (5.0, 'card', '可恢复、可取消的「心」。三层能力', '可恢复、可取消的「心」。三层能力叠在一起。第一层，流式产出：'),
        (10.55, 'stamp', '每次 yield 推送一', '记下这一点'),
        (16.45, 'card', 'AbortSignal 或迭代器', 'AbortSignal 或迭代器的 return，能走到 fin'),
        (21.65, 'pause', '停一下 · 把资源收干净——对应', '跟 VO 对齐想一拍'),
        (27.2, 'section', '第三层，背压：消费者跟不上时', '第三层，背压：消费者跟不上时，生成器自动暂停，事'),
        (33.1, 'card', '这三层，正好对应 Agent 真', '这三层，正好对应 Agent 真需求：'),
        (38.3, 'card', '边想边画、随时能停、工具狂奔时别', '边想边画、随时能停、工具狂奔时别把内存撑爆。'),
        (43.85, 'card', '为什么不选回调？回调会把逻辑撕碎', '为什么不选回调？回调会把逻辑撕碎在各个注册点。为什么不选 Pro'),
        (49.75, 'chariot', '辔绳收得住', '上下文窗口就是舆的载重'),
        (54.95, 'card', '装不下一路涌出的增量事件。Obs', '装不下一路涌出的增量事件。Observable 很强，但学习与类'),
        (60.5, 'persona_ah', 'Agent Harness', '考工记御者 · 收辔控速'),
        (66.05, 'card', '取消路径清晰。函数签名本身就是契', '取消路径清晰。函数签名本身就是契约。Yield 出来的是联合'),
        (71.95, 'card', '类型事件；真正的终局用 Term', '类型事件；真正的终局用 Terminal 表达；参数则收成一个结'),
        (77.15, 'stamp', '参数则收成一个结构体——', '记下这一点'),
        (82.7, 'card', '压缩策略入口，都从这里进，不在散', '压缩策略入口，都从这里进，不在散落的全局里偷拿。'),
        (88.6, 'vs_auto', '生成器 vs 回调 vs Promise', '刚刚好的那一档'),
        (93.8, 'card', '每次 API 将发未发，UI 可', '每次 API 将发未发，UI 可以亮「正在思考」。StreamE'),
        (99.35, 'persona_cl', 'Claude', '会诊医生 · 边想边说边开检查'),
        (104.9, 'p', 'tool_use，像视频', 'tool_use，像视频的每一帧。Message'),
        (110.8, 'card', '助手、用户、系统，', '助手、用户、系统，相当于剪辑好的镜头。TombstoneMes'),
        (116.0, 'code', 'async function*', 'yield 事件 · return Terminal'),
        (121.55, 'card', 'ryMessage：一批工具跑完', 'ryMessage：一批工具跑完后的折叠摘要，长会话才不至于被输'),
        (127.45, 'layers', '三层能力', '流式 · AbortSignal · 背压'),
        (132.65, 'card', '既是用户输入，也承载 tool_', '既是用户输入，也承载 tool_result——在 API 协议'),
        (138.2, 'flow', '想 → 调 → 收 → 再想', '一次脉搏'),
        (144.1, 'card', 'sage 可以同时带文本和 to', 'sage 可以同时带文本和 tool_use，边说边动手。'),
        (149.3, 'sum', 'SystemMessage ', 'SystemMessage 不进 API，只做第四面墙。'),
        (154.85, 'card', 'Attachment 与 Pro', 'Attachment 与 Progress 分别承载附件通知和工'),
        (160.75, 'card', '记住：事件是脉搏，消息是可归档的', '记住：事件是脉搏，消息是可归档的病历。什么叫一轮 Turn？'),
        ],
    },
    {
        "id": 'b03_turn',
        "title": '§2.2 Turn 生命周期',
        "start": 221.28,
        "end": 381.888,
        "huashu": [],
        "beats": [
        (0.0, 'section', '§2.2 Turn 生命周期', '§2.2 Turn 生命周期'),
        (5.0, 'card', '再决定继续或收束——这就是一次心', '再决定继续或收束——这就是一次心跳周期。书稿用医学比喻：'),
        (10.55, 'stamp', '模型是医生，先问诊再开检', '记下这一点'),
        (16.45, 'card', '个 while true。每一圈', '个 while true。每一圈大致五阶段。阶段一，'),
        (21.65, 'pause', '停一下 · 阶段一，状态初始化：', '跟 VO 对齐想一拍'),
        (27.2, 'section', '再准备本圈可写容器——读和写', '再准备本圈可写容器——读和写之间有清晰边界。阶段'),
        (33.1, 'card', '七步管线。阶段三，注入的 cal', '七步管线。阶段三，注入的 callModel 发起流式请求，'),
        (38.3, 'card', '边收边 yield，同时收集助手', '边收边 yield，同时收集助手消息与工具块；'),
        (43.85, 'card', '若开启流式工具执行，甚至可以在响', '若开启流式工具执行，甚至可以在响应未完成时先跑工具。'),
        (49.75, 'chariot', '辔绳收得住', '上下文窗口就是舆的载重'),
        (54.95, 'card', '附件注入、打包新 State、c', '附件注入、打包新 State、continue 回阶段一。'),
        (60.5, 'number', '7', '步预处理 · 从轻到重'),
        (66.4, 'card', '顺序刻意从轻到重。一，工具结果预', '顺序刻意从轻到重。一，工具结果预算，超长输出先截断或外置。'),
        (71.6, 'stamp', '二，Snip，按消息级裁', '记下这一点'),
        (77.15, 'card', '缓存友好的轻量压缩，尽量别把 A', '缓存友好的轻量压缩，尽量别把 API 侧已缓'),
        (83.05, 'vs_auto', '生成器 vs 回调 vs Promise', '刚刚好的那一档'),
        (88.25, 'card', '把一段对话收成更高密度的摘要图。', '把一段对话收成更高密度的摘要图。五，系统提示组装，'),
        (93.8, 'p', '稳定前缀才能保住缓存命中', '稳定前缀才能保住缓存命中。六，Autocompa'),
        (99.7, 'card', '是重量级最后手段之一。七，Tok', '是重量级最后手段之一。七，Token 阻断检查，'),
        (104.9, 'code', 'async function*', 'yield 事件 · return Terminal'),
        (110.45, 'card', '原则就一句：先付最小代价。马车意', '原则就一句：先付最小代价。马车意象也在这里：辔绳收得住，'),
        (116.35, 'layers', '三层能力', '流式 · AbortSignal · 背压'),
        (121.55, 'card', '车轴会断。终止不是含糊的 err', '车轴会断。终止不是含糊的 error。书稿列了十种原因：'),
        (127.1, 'flow', '想 → 调 → 收 → 再想', '一次脉搏'),
        (133.0, 'card', 'aming 与 aborted_', 'aming 与 aborted_tools 对应用户在流式或工具'),
        (138.2, 'sum', 'max_turns、bloc', 'max_turns、blocking_limit、'),
        (143.75, 'card', 'prompt_too_long、', 'prompt_too_long、model_error、stop'),
        (149.65, 'card', 'evented、hook_sto', 'evented、hook_stopped、image_error'),
        (154.85, 'stamp', '覆盖循环上限、硬顶、恢复', '记下这一点'),
        ],
    },
    {
        "id": 'b04_deps',
        "title": '§2.3–2.4 依赖注入 + 状态机',
        "start": 381.888,
        "end": 533.808,
        "huashu": [],
        "beats": [
        (0.0, 'section', '§2.3–2.4 依赖注入 + ', '§2.3–2.4 依赖注入 + 状态机'),
        (5.0, 'persona_ah', 'Agent Harness', '考工记御者 · 收辔控速'),
        (10.2, 'card', 'callModel、microc', 'callModel、microcompact、autocompa'),
        (15.75, 'stamp', 'uuid。测试时塞假实现', '记下这一点'),
        (21.65, 'card', 'On 模块。书稿原话大意：今天光', 'On 模块。书稿原话大意：今天光 callModel 和 aut'),
        (25.0, 'quiz', '猜一猜：为什么不用 class 扛状态？', '闭包隔离 · 多会话不串味'),
        (32.4, 'section', '依赖注入把「和外部世界打交道', '依赖注入把「和外部世界打交道」的边界钉死，循环内'),
        (38.3, 'card', '为什么坚持函数式生成器，而不是 ', '为什么坚持函数式生成器，而不是 class？每次对话一个新闭包，'),
        (43.5, 'card', '没有实例字段串味；yield 自', '没有实例字段串味；yield 自带背压；return 走 fin'),
        (49.05, 'card', 'ally；yield 星号把子循', 'ally；yield 星号把子循环的事件与终值一起委托上来'),
        (54.95, 'chariot', '辔绳收得住', '上下文窗口就是舆的载重'),
        (60.15, 'card', '或长寿命实例字段。全局杀并发测试', '或长寿命实例字段。全局杀并发测试，实例字段让多会话互相踩。'),
        (65.7, 'card', '闭包是最安全的舆厢。状态机三元模', '闭包是最安全的舆厢。状态机三元模型：State、'),
        (71.6, 'card', 'Continue、Termina', 'Continue、Terminal。State 可变但可控，'),
        (76.8, 'stamp', '每次 continue ', '记下这一点'),
        (82.35, 'card', 'Continue 是继续信号，带', 'Continue 是继续信号，带原因与附件。Terminal 是'),
        (88.25, 'vs_auto', '生成器 vs 回调 vs Promise', '刚刚好的那一档'),
        (93.45, 'card', '七条 Continue 路径要能', '七条 Continue 路径要能叫出名字。next_turn：'),
        (99.0, 'p', '工具跑完，历史扩展，最常', '工具跑完，历史扩展，最常见。max_output'),
        (104.9, 'card', 'okens_escalate：首', 'okens_escalate：首次截断先抬输出上限。'),
        (110.1, 'code', 'async function*', 'yield 事件 · return Terminal'),
        (115.65, 'card', '仍截断就注入恢复消息，最多再试三', '仍截断就注入恢复消息，最多再试三次。reactive_com'),
        (121.55, 'layers', '三层能力', '流式 · AbortSignal · 背压'),
        (126.75, 'card', 'collapse_drain_r', 'collapse_drain_retry：更细粒度的折叠排水恢复'),
        (132.3, 'flow', '想 → 调 → 收 → 再想', '一次脉搏'),
        (138.2, 'card', '后把信息注回，让模型有机会换策略', '后把信息注回，让模型有机会换策略。token_budget_co'),
        (143.4, 'sum', '_continuation：', '_continuation：预算提醒，不是粗暴掐断。每条'),
        ],
    },
    {
        "id": 'b05_practice',
        "title": '实战练习要点',
        "start": 533.808,
        "end": 588.72,
        "huashu": [],
        "beats": [
        (0.0, 'section', '实战练习要点', '实战练习要点'),
        (5.0, 'card', 'uest_start、首个 to', 'uest_start、首个 tool_use 到达、'),
        (8.0, 'quiz', '猜一猜：练习先打哪四个点？', 'stream_start · tool_use · runTools ·'),
        (16.45, 'card', '进执行再回到下一轮。第二，在测试', '进执行再回到下一轮。第二，在测试里注入「半截就截断'),
        (21.65, 'pause', '停一下 · 」的假模型，观察 e', '跟 VO 对齐想一拍'),
        (27.2, 'section', '么切换。第三，估算没有 DI', '么切换。第三，估算没有 DI 时，七条 Cont'),
        (33.1, 'card', 'mock。第四，故意喂一串吃上下', 'mock。第四，故意喂一串吃上下文的任务，看 Snip 与 Au'),
        (38.3, 'card', 'ocompact 谁先亮灯。细节', 'ocompact 谁先亮灯。细节实现后面核心篇还会拆压缩；'),
        (43.85, 'card', '本章先把心跳的节律听熟。收五句。', '本章先把心跳的节律听熟。收五句。一，AsyncGenerat'),
        (49.75, 'chariot', '辔绳收得住', '上下文窗口就是舆的载重'),
        ],
    },
    {
        "id": 'b06_outro',
        "title": '总结 + 片尾',
        "start": 588.72,
        "end": 627.624,
        "huashu": [],
        "beats": [
        (0.0, 'section', '总结 + 片尾', '总结 + 片尾'),
        (5.0, 'card', '三，状态可变，转换可追。', '三，状态可变，转换可追。四，QueryDeps 让测'),
        (10.55, 'stamp', '试成为工程而不是苦行。五', '记下这一点'),
        (16.45, 'card', '下一集第 03 章，我们转去工具', '下一集第 03 章，我们转去工具系统——Ag'),
        (21.65, 'pause', '停一下 · ent 的双手：编排', '跟 VO 对齐想一拍'),
        (27.2, 'section', '本系列基于开源书稿。系列名：', '本系列基于开源书稿。系列名：驭者·Agent H'),
        (33.1, 'card', 'ness。关注小电讲电路，合集里', 'ness。关注小电讲电路，合集里看目录更新。'),
        ],
    },
]

SFX_CUE = [
    (0.02, 'whoosh.wav', 0.28, 0.3),
    (12.653, 'punch.wav', 0.28, 0.2),
    (24.681, 'impact.wav', 0.28, 0.24),
    (38.46, 'ui_blip.wav', 0.22, 0.08),
    (50.213, 'glitch.wav', 0.28, 0.15),
    (63.589, 'rein_snap.wav', 0.28, 0.08),
    (76.369, 'gallop.wav', 0.28, 0.4),
    (88.072, 'tick.wav', 0.22, 0.04),
    (101.348, 'whoosh.wav', 0.28, 0.3),
    (112.979, 'punch.wav', 0.28, 0.2),
    (125.997, 'impact.wav', 0.28, 0.24),
    (137.741, 'ui_blip.wav', 0.22, 0.08),
    (149.559, 'glitch.wav', 0.28, 0.15),
    (162.545, 'rein_snap.wav', 0.28, 0.08),
    (176.938, 'gallop.wav', 0.28, 0.4),
    (188.872, 'tick.wav', 0.22, 0.04),
    (201.153, 'whoosh.wav', 0.28, 0.3),
    (214.849, 'punch.wav', 0.28, 0.2),
    (229.666, 'impact.wav', 0.28, 0.24),
    (243.186, 'ui_blip.wav', 0.22, 0.08),
    (256.074, 'glitch.wav', 0.28, 0.15),
    (270.991, 'rein_snap.wav', 0.28, 0.08),
    (282.654, 'gallop.wav', 0.28, 0.4),
    (297.159, 'tick.wav', 0.22, 0.04),
    (309.673, 'whoosh.wav', 0.28, 0.3),
    (321.677, 'punch.wav', 0.28, 0.2),
    (333.59, 'impact.wav', 0.28, 0.24),
    (346.169, 'ui_blip.wav', 0.22, 0.08),
    (360.526, 'glitch.wav', 0.28, 0.15),
    (372.658, 'rein_snap.wav', 0.28, 0.08),
    (386.194, 'gallop.wav', 0.28, 0.4),
    (399.93, 'tick.wav', 0.22, 0.04),
    (412.734, 'whoosh.wav', 0.28, 0.3),
    (426.151, 'punch.wav', 0.28, 0.2),
    (437.87, 'impact.wav', 0.28, 0.24),
    (449.579, 'ui_blip.wav', 0.22, 0.08),
    (461.8, 'glitch.wav', 0.28, 0.15),
    (475.681, 'rein_snap.wav', 0.28, 0.08),
    (488.678, 'gallop.wav', 0.28, 0.4),
    (501.277, 'tick.wav', 0.22, 0.04),
    (514.827, 'whoosh.wav', 0.28, 0.3),
    (527.913, 'punch.wav', 0.28, 0.2),
    (540.462, 'impact.wav', 0.28, 0.24),
    (554.743, 'ui_blip.wav', 0.22, 0.08),
    (568.689, 'glitch.wav', 0.28, 0.15),
    (581.043, 'rein_snap.wav', 0.28, 0.08),
    (594.554, 'gallop.wav', 0.28, 0.4),
    (607.892, 'tick.wav', 0.22, 0.04),
    (622.455, 'whoosh.wav', 0.28, 0.3),
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

.persona-card{display:flex;gap:22px;align-items:center;padding:28px 36px;border:2px solid #5b8def;
  border-radius:18px;background:rgba(12,18,28,.82);box-shadow:0 12px 40px rgba(0,0,0,.45);max-width:1100px}
.persona-badge{width:72px;height:72px;border-radius:18px;display:flex;align-items:center;justify-content:center;
  font-size:28px;font-weight:800;color:#0b1020;flex-shrink:0}
.persona-name{font-size:20px;font-weight:700;letter-spacing:.08em;margin-bottom:6px}
.persona-title{font-size:36px;font-weight:800;color:#eef3f8;line-height:1.25}
.persona-sub{font-size:22px;color:#a8b4c4;margin-top:10px;line-height:1.4}

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
<div class="book-plate" style="position:relative;width:1600px;height:620px;margin:0 auto;border:2px solid #8a735588;border-radius:6px;overflow:hidden;background:#0e0b09;box-shadow:0 12px 40px #000a">
  <img src="../assets/book-chariot-paper.png" alt="kaogongji plate" style="width:100%;height:100%;object-fit:contain;display:block"/>
  <div style="position:absolute;left:36px;top:48px;padding:10px 14px;background:#f3ead7ee;border:1.5px solid #8a7355;color:#2a2118;font-family:serif;font-size:28px;font-weight:700;box-shadow:2px 3px 0 #0006">骏马<span style="display:block;font-size:16px;color:#5a4a32;font-weight:600">模型 · LLM</span></div>
  <div style="position:absolute;left:520px;top:28px;padding:10px 14px;background:#f3ead7ee;border:1.5px solid #8a7355;color:#2a2118;font-family:serif;font-size:28px;font-weight:700;box-shadow:2px 3px 0 #0006">辔 / 缰绳<span style="display:block;font-size:16px;color:#5a4a32;font-weight:600">Harness</span></div>
  <div style="position:absolute;right:48px;top:80px;padding:10px 14px;background:#f3ead7ee;border:1.5px solid #8a7355;color:#2a2118;font-family:serif;font-size:28px;font-weight:700;box-shadow:2px 3px 0 #0006">舆<span style="display:block;font-size:16px;color:#5a4a32;font-weight:600">整车系统</span></div>
  <div style="position:absolute;right:80px;top:220px;padding:10px 14px;background:#f3ead7ee;border:1.5px solid #8a7355;color:#2a2118;font-family:serif;font-size:28px;font-weight:700;box-shadow:2px 3px 0 #0006">御者 · 你<span style="display:block;font-size:16px;color:#5a4a32;font-weight:600">架构认知</span></div>
  <div style="position:absolute;left:0;right:0;bottom:14px;text-align:center;font-family:serif;letter-spacing:.28em;color:#c9b48a;font-size:22px">考工记 · 四马古车图版</div>
</div>
'''



def beat_html(kind: str, title: str, sub: str, bid: str) -> str:

    if kind.startswith("persona_"):
        who = {"persona_cl": ("Cl", "Claude", "#5b8def"), "persona_cx": ("Cx", "Codex", "#e8a838"), "persona_ah": ("AH", "Agent", "#6bcf7f")}.get(kind, ("?", title, "#aaa"))
        badge, name, color = who
        return (
            f'<div class="beat-inner persona" id="{bid}">'
            f'<div class="persona-card" style="border-color:{color}">'
            f'<div class="persona-badge" style="background:{color}">{esc(badge)}</div>'
            f'<div class="persona-body"><div class="persona-name" style="color:{color}">{esc(name)}</div>'
            f'<div class="persona-title">{esc(title)}</div><div class="persona-sub">{esc(sub)}</div></div>'
            f'</div></div>'
        )

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

    if kind.startswith("persona_"):
        return [
            f'tl.fromTo("#{bid}", {{opacity:0,scale:0.92,y:24}}, {{opacity:1,scale:1,y:0,duration:0.45,ease:"power2.out"}}, {t0:.3f});',
            f'tl.to("#{bid}", {{opacity:0,y:-12,duration:0.28}}, {t0+hold-0.32:.3f});',
        ]

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
        ken = max(hold - 1.2, 2.5)
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0,scale:0.97}}, {{opacity:1,scale:1,duration:0.4,ease:"power2.out"}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .kicker", {{opacity:0,y:12}}, {{opacity:1,y:0,duration:0.32}}, {t0+0.08:.3f});',
            f'tl.fromTo("#{bid} .h1", {{opacity:0,y:18}}, {{opacity:1,y:0,duration:0.36}}, {t0+0.16:.3f});',
            f'tl.fromTo("#{bid} .book-plate", {{opacity:0,scale:1.04}}, {{opacity:1,scale:1,duration:0.45}}, {t0+0.28:.3f});',
            f'tl.fromTo("#{bid} .book-plate > div", {{opacity:0,y:10,scale:0.94}}, {{opacity:1,y:0,scale:1,duration:0.28,stagger:0.1}}, {t0+0.55:.3f});',
            f'tl.to("#{bid} .book-plate img", {{scale:1.04,x:-10,duration:{ken:.3f},ease:"none"}}, {t0+0.7:.3f});',
            f'tl.fromTo("#{bid} .chip", {{opacity:0,y:14,scale:0.92}}, {{opacity:1,y:0,scale:1,duration:0.28,stagger:0.07}}, {t0+1.0:.3f});',
            f'tl.to("#{bid}", {{opacity:0,scale:0.99,duration:0.32}}, {out_at:.3f});',
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
        if kind in ("chariot", "vs_auto", "stamp", "number", "section", "quiz", "pause") or kind.startswith("persona_"):
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

# SFX_CUE injected below
# see SFX_CUE above


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
    SFX.mkdir(parents=True, exist_ok=True)
    ensure_sfx()
    # ensure chariot asset reachable from compositions
    chariot = ROOT / "assets" / "book-chariot-paper.png"
    if chariot.exists():
        dest = COMP / "book-chariot-paper.png"
        if not dest.exists() or dest.stat().st_size != chariot.stat().st_size:
            dest.write_bytes(chariot.read_bytes())
    for blk in BLOCKS:
        write_block(blk)
    write_captions()
    write_watermark()
    write_index()
    # package meta
    (ROOT / "package.json").write_text(
        json.dumps({
            "name": "ch02-long-v1",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "npx --yes hyperframes@0.8.210 preview",
                "check": "npx --yes hyperframes@0.8.210 check",
                "render": "npx --yes hyperframes@0.8.210 render",
            },
        }, indent=2),
        encoding="utf-8",
    )
    (ROOT / "hyperframes.json").write_text(
        json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True},
            "authoringSkill": "hyperframes",
            "registryItems": [],
        }, indent=2),
        encoding="utf-8",
    )
    (ROOT / "meta.json").write_text(
        json.dumps({"id": "ch02-long-v1", "name": "ch02-long-v1", "duration": TOTAL}, indent=2),
        encoding="utf-8",
    )
    print("ch02 dense v1 assembled TOTAL", TOTAL, "blocks", len(BLOCKS), "sfx", len(SFX_CUE), "caps", len(TRANS))


if __name__ == "__main__":
    main()
