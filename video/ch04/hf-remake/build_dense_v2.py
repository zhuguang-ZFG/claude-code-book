# -*- coding: utf-8 -*-
"""ch04 long densify v2 (hold-fixed + denser) — clone of ch01 v4 / ch02 v1 quality bar. No publish."""
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
TOTAL = 453.048


BLOCKS = [
    {
        "id": "b01_hook",
        "title": "开场钩子 · 护栏",
        "start": 0.0,
        "end": 39.696,
        "huashu": [("01_key_vs_gates.mp4", 6.0, 7.0), ("08_building_gates.mp4", 22.0, 6.5)],
        "beats": [
        (0.0, "section", "护栏", "开场钩子 · 护栏"),
        (2.673, "persona_cl", "Claude", "会诊医生 · 边想边过闸"),
        (5.0, "card", "ness 第 04 讲。上一集双", "ness 第 04 讲。上一集双手装上了："),
        (7.46, "flow", "上一集双手装上了：", "优先级铁律"),
        (9.26, "code", "专工具", "allow · deny · ask"),
        (10.55, "persona_ah", "Agent Harness", "考工记御者 · 护栏握缰"),
        (12.35, "card", "双手能伸多远", "护栏说了算"),
        (14.0, "quiz", "猜一猜：真护栏是什么？", "一扇大门？还是四道闸？"),
        (16.636, "pause", "停一下 · ent 的护栏", "跟 VO 对齐想一想"),
        (18.436, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (22.0, "card", "rm -rf、npm publi", "rm -rf、npm publish——没有护栏就是裸奔。"),
        (24.737, "code", "—没有护栏就是裸奔", "allow · deny · ask"),
        (27.2, "pause", "停一下 · 真护栏是啥？猜一猜：", "跟 VO 对齐想一拍"),
        (29.0, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (30.55, "card", "是四道闸", "万能钥匙乱开"),
        (32.75, "section", "万能钥匙乱开，四道闸逐关落下", "万能钥匙乱开，四道闸逐关落下。纵深防御，才叫大楼"),
        (34.55, "stamp", "纵深防御", "记下这一句"),
        (36.223, "stamp", "才叫大楼门禁", "不叫门口一个保安"),
        ],
    },
    {
        "id": "b02_phases",
        "title": "§4.1 四阶段权限管线",
        "start": 39.696,
        "end": 155.064,
        "huashu": [("02_four_phases.mp4", 10.0, 7.0), ("03_deny_ask_allow.mp4", 40.0, 7.0), ("02_four_phases.mp4", 70.0, 7.0), ("03_deny_ask_allow.mp4", 95.0, 6.5)],
        "beats": [
        (0.0, "section", "§4.1 四阶段权限管线", "§4.1 四阶段权限管线"),
        (2.2, "code", "的权限检查不是一个布尔函", "allow · deny · ask"),
        (5.0, "card", "数，而是四阶段管线。前一阶段做出", "数，而是四阶段管线。前一阶段做出终局决定，后面就短路不再跑。"),
        (6.8, "card", "前一阶段做出终局决定", "后面就短路不再跑"),
        (7.927, "card", "后面就短路不再跑", "阶段一"),
        (10.55, "stamp", "阶段一，validate", "记下这一点"),
        (12.35, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (14.25, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (16.45, "card", "先问数据合不合法，再问该不该用。", "先问数据合不合法，再问该不该用。缺 command 字段？"),
        (18.65, "vs_auto", "万能钥匙 vs 四道闸", "纵深防御打败单门卫"),
        (20.45, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (21.65, "pause", "停一下 · 解析失败。注意：失败", "跟 VO 对齐想一拍"),
        (23.85, "stamp", "而是优雅降级成 ask", "记下这一句"),
        (25.65, "stamp", "让用户决定要不要继续", "记下这一句"),
        (27.2, "section", "安全系统里，错误处理要「安全", "安全系统里，错误处理要「安全」，不是只求「正确」"),
        (29.0, "warn", "错误处理要「安全」", "反模式 · 别踩"),
        (30.543, "warn", "不是只求「正确」", "反模式 · 别踩"),
        (33.1, "card", "阶段二，规则匹配——deny 大", "阶段二，规则匹配——deny 大于 ask 大于 all"),
        (35.3, "card", "于 ask 大于 all", "ow"),
        (37.1, "card", "ow", "铁律："),
        (38.3, "card", "ow。铁律：显式拒绝压过显式允许", "ow。铁律：显式拒绝压过显式允许。工具被整体 deny，"),
        (41.082, "persona_cl", "Claude", "会诊医生 · 边想边过闸"),
        (43.85, "card", "立刻拒；ask 就强制确认；都没", "立刻拒；ask 就强制确认；都没命中再看 allow。"),
        (46.458, "flow", "都没命中再看 allow", "优先级铁律"),
        (48.258, "persona_cl", "Claude", "会诊医生 · 边想边过滤"),
        (49.75, "chariot", "大楼门禁", "纵深防御才叫护栏"),
        (51.95, "pause", "停一下 · 会话级压过命令行", "跟 VO 对齐想一想"),
        (53.75, "flow", "命令行压过项目", "deny > ask > allow"),
        (54.95, "card", "命令行压过项目，项目压过全局用户", "命令行压过项目，项目压过全局用户。MCP 还能用服务器级通配，"),
        (57.584, "code", "MCP 还能用服务器级通配", "allow · deny · ask"),
        (59.384, "pause", "停一下 · 一把管住一整组工具", "跟 VO 对齐想一拍"),
        (60.5, "card", "一把管住一整组工具。阶段三，ch", "一把管住一整组工具。阶段三，checkPermissions——"),
        (62.398, "code", "checkPermiss", "allow · deny · ask"),
        (64.2, "card", "ions——工具自己的上", "下文评估"),
        (66.4, "card", "下文评估。Bash 会拆子命令、", "下文评估。Bash 会拆子命令、看路径、配前缀规则。"),
        (68.2, "card", "Bash 会拆子命令", "看路径"),
        (69.275, "stamp", "看路径", "记下这一句"),
        (71.6, "stamp", "返回四种行为：allow", "记下这一点"),
        (74.089, "flow", "ask", "优先级铁律"),
        (75.889, "stamp", "passthrough", "记下这一句"),
        (77.15, "card", "passthrough 是「我没", "passthrough 是「我没意见，交给后面」；ask 是「我"),
        (78.95, "flow", "是「我没意见", "deny > ask > allow"),
        (80.039, "flow", "交给后面」", "优先级铁律"),
        (81.839, "flow", "ask 是「我认为要确认」", "deny > ask > allow"),
        (83.05, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (85.25, "layers", "盖过 passthrou", "校验 · 规则 · 上下文 · 确认"),
        (87.05, "layers", "gh", "校验 · 规则 · 上下文 · 确认"),
        (88.25, "card", "gh，盖不过明确的 ask。意图", "gh，盖不过明确的 ask。意图不同，结果不同。阶段四，"),
        (90.913, "code", "阶段四", "allow · deny · ask"),
        (92.713, "code", "交互式提示——人类授权", "allow · deny · ask"),
        (93.8, "p", "进入 ask 后，Hoo", "进入 ask 后，Hook、分类器、用户三路可能"),
        (95.6, "card", "Hook", "分类器"),
        (96.935, "card", "用户三路可能同时出手", "ResolveOnce："),
        (99.7, "card", "ResolveOnce：先到先得", "ResolveOnce：先到先得，一张单程机票只能兑一次。"),
        (102.074, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (103.874, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (104.9, "code", "PermissionResult", "allow · deny · ask · pass"),
        (106.7, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (108.131, "vs_auto", "万能钥匙 vs 四道闸", "纵深防御打败单门卫"),
        (110.45, "card", "预置 allow、开 auto、", "预置 allow、开 auto、或写 Hook——三招可叠加。"),
        ],
    },
    {
        "id": "b03_context",
        "title": "§4.2 PermissionContext",
        "start": 155.064,
        "end": 211.56,
        "huashu": [("04_immutable_ctx.mp4", 10.0, 7.0), ("04_immutable_ctx.mp4", 35.0, 6.5)],
        "beats": [
        (0.0, "section", "§4.2 PermissionC", "§4.2 PermissionContext"),
        (2.323, "code", "ntext 是权限系统的", "allow · deny · ask"),
        (5.0, "card", "核心快照：模式、规则、", "核心快照：模式、规则、额外工作目录、是否避免弹窗……字段全"),
        (6.8, "persona_cl", "Claude", "会诊医生 · 边想边过滤"),
        (7.93, "card", "是否避免弹窗……字段全 ", "readonly"),
        (10.55, "stamp", "readonly。每次更", "记下这一点"),
        (12.35, "flow", "每次更新产生新对象", "deny > ask > allow"),
        (13.725, "stamp", "不改旧的", "记下这一句"),
        (16.45, "card", "谁也不会踩到半截新半截旧的中间态", "谁也不会踩到半截新半截旧的中间态。决策有三个来源："),
        (19.145, "flow", "的中间态", "优先级铁律"),
        (21.65, "pause", "停一下 · 决策有三个来源：ho", "跟 VO 对齐想一拍"),
        (23.45, "pause", "停一下 · classifier", "跟 VO 对齐想一拍"),
        (25.0, "flow", "hook 像管理员剧本", "优先级铁律"),
        (27.2, "section", "CI 里先判；user 是当", "CI 里先判；user 是当面点允许或拒绝，还可"),
        (29.0, "code", "user 是当面点允许或拒绝", "allow · deny · ask"),
        (30.815, "layers", "还可选永久写入", "校验 · 规则 · 上下文 · 确认"),
        (33.1, "card", "classifier 是 AI ", "classifier 是 AI 监督 AI，信任最低，有些检查对"),
        (35.85, "code", "信任最低", "allow · deny · ask"),
        (38.3, "card", "ResolveOnce 提供 r", "ResolveOnce 提供 resolve、isResolve"),
        (40.5, "card", "提供 resolve", "isResolved"),
        (42.3, "card", "isResolved", "claim"),
        (43.85, "card", "claim。单线程里 claim", "claim。单线程里 claim 就是轻量互斥：两个回调几乎同时"),
        (45.65, "stamp", "单线程里 claim 就", "记下这一句"),
        (46.669, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (48.469, "flow", "两个回调几乎同时到", "deny > ask > allow"),
        (49.75, "chariot", "大楼门禁", "纵深防御才叫护栏"),
        (51.55, "number", "跟第 02 章不可变状态", "流转一脉相承——状态要么"),
        (53.123, "vs_auto", "流转一脉相承——状态要么", "旧要么新"),
        ],
    },
    {
        "id": "b04_modes",
        "title": "§4.3 五种权限模式",
        "start": 211.56,
        "end": 316.872,
        "huashu": [("05_mode_spectrum.mp4", 12.0, 7.0), ("05_mode_spectrum.mp4", 45.0, 7.0), ("05_mode_spectrum.mp4", 80.0, 6.5)],
        "beats": [
        (0.0, "section", "§4.3 五种权限模式", "§4.3 五种权限模式"),
        (2.8, "card", "plan", "auto"),
        (5.0, "card", "auto、bypassPermi", "auto、bypassPermissions，外加内部的 bub"),
        (7.2, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (9.0, "code", "default：", "allow · deny · ask"),
        (10.55, "stamp", "default：逐次确认", "记下这一点"),
        (12.876, "vs_auto", "万能钥匙 vs 四道闸", "纵深防御打败单门卫"),
        (14.676, "card", "也最繁琐", "大重构几十次编辑"),
        (16.45, "card", "也最繁琐；大重构几十次编辑，会打", "也最繁琐；大重构几十次编辑，会打断思路。plan：只读为主。"),
        (18.844, "stamp", "plan：", "记下这一句"),
        (20.644, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (21.65, "pause", "停一下 · Edit、Write", "跟 VO 对齐想一拍"),
        (24.215, "warn", "Read", "反模式 · 别踩"),
        (26.015, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (27.2, "section", "Glob 放行。先看懂再动手", "Glob 放行。先看懂再动手——代码审查、架构分"),
        (29.0, "stamp", "先看懂再动手——代码审查", "记下这一句"),
        (30.161, "card", "架构分析最合适", "auto："),
        (31.961, "warn", "auto：", "反模式 · 别踩"),
        (33.1, "card", "auto：分类器自动审批。到达 ", "auto：分类器自动审批。到达 ask 时，YOLO 分类器替你"),
        (34.9, "card", "到达 ask 时", "YOLO 分类器替你判"),
        (36.072, "persona_cl", "Claude", "会诊医生 · 边想边过闸"),
        (38.3, "card", "短路优化：acceptEdits", "短路优化：acceptEdits 先过就免调分类器；"),
        (40.1, "persona_cl", "Claude", "会诊医生 · 边想边过滤"),
        (41.631, "flow", "先过就免调分类器", "优先级铁律"),
        (43.85, "card", "只读白名单跳过；连续拒绝就熔断回", "只读白名单跳过；连续拒绝就熔断回交互。涉及点 git、"),
        (45.65, "flow", "连续拒绝就熔断回交互", "deny > ask > allow"),
        (46.997, "pause", "停一下 · 涉及点 git", "跟 VO 对齐想一想"),
        (49.75, "persona_cl", "Claude", "会诊医生 · 边想边过闸"),
        (51.95, "code", "分类器免疫——它批准也绕不过", "allow · deny · ask"),
        (53.85, "pause", "停一下 · 生产部署", "跟 VO 对齐想一拍"),
        (55.65, "chariot", "大楼门禁", "纵深防御才叫护栏"),
        (58.003, "card", "bypassPermis", "sions："),
        (59.803, "code", "sions：", "allow · deny · ask"),
        (60.85, "card", "sions：除 deny 和不可", "sions：除 deny 和不可绕过的安全检查外全放行。CI、"),
        (63.05, "stamp", "的安全检查外全放行", "记下这一句"),
        (64.85, "card", "CI", "容器隔离场景常用"),
        (66.4, "card", "容器隔离场景常用。即便全信任，d", "容器隔离场景常用。即便全信任，deny、requiresUser"),
        (68.207, "stamp", "requiresUser", "记下这一句"),
        (70.1, "flow", "Interaction", "优先级铁律"),
        (72.3, "card", "内容级 ask、safetyCh", "内容级 ask、safetyCheck 仍守底线。"),
        (74.1, "flow", "safetyCheck ", "deny > ask > allow"),
        (75.3, "flow", "仍守底线", "优先级铁律"),
        (77.5, "stamp", "bubble：子智能体权", "记下这一点"),
        (79.3, "number", "权限边界不扩张", "跟第 03 章 Agen"),
        (80.8, "layers", "跟第 03 章 Agen", "校验 · 规则 · 上下文 · 确认"),
        (83.05, "card", "tTool 的 createSu", "tTool 的 createSubagentContext 绑在"),
        (84.85, "layers", "teSubagentCo", "校验 · 规则 · 上下文 · 确认"),
        (86.382, "code", "ntext 绑在一起——", "allow · deny · ask"),
        (88.95, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (91.345, "card", "先分析后改代码", "该开哪一档"),
        (93.145, "code", "该开哪一档", "allow · deny · ask"),
        (94.15, "card", "答案是 plan；要省确认又不想", "答案是 plan；要省确认又不想裸奔，再考虑 auto 加白名单"),
        (96.437, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (98.237, "card", "Bash 最难管：", "git status 安全"),
        (99.7, "p", "Bash 最难管：git", "Bash 最难管：git status 安全，g"),
        (101.5, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (102.506, "vs_auto", "git push --f", "orce 危险"),
        ],
    },
    {
        "id": "b05_bash",
        "title": "§4.4 BashTool 细粒度",
        "start": 316.872,
        "end": 357.552,
        "huashu": [("06_bash_match.mp4", 8.0, 7.0), ("06_bash_match.mp4", 25.0, 6.5)],
        "beats": [
        (0.0, "section", "§4.4 BashTool 细粒", "§4.4 BashTool 细粒度"),
        (2.8, "persona_cl", "Claude", "会诊医生 · 边想边过闸"),
        (5.0, "card", "精确 Bash(npm test", "精确 Bash(npm test)；前缀 Bash(npm:*)"),
        (7.2, "flow", "前缀 Bash(npm:*)", "优先级铁律"),
        (9.0, "card", "通配 Bash(git ", "commit *)"),
        (10.55, "stamp", "通配 Bash(git ", "记下这一点"),
        (12.35, "persona_cl", "Claude", "会诊医生 · 边想边过滤"),
        (13.38, "pause", "停一下 · 表达能力递增", "跟 VO 对齐想一想"),
        (15.18, "flow", "误放行风险也递增", "deny > ask > allow"),
        (16.45, "card", "优先前缀：语义清晰，少踩坑。", "优先前缀：语义清晰，少踩坑。git:* 和 git 空格星，"),
        (18.25, "pause", "停一下 · 语义清晰", "跟 VO 对齐想一拍"),
        (19.425, "code", "git:* 和 git 空格星", "allow · deny · ask"),
        (21.65, "pause", "停一下 · 设计成等价，减轻记忆", "跟 VO 对齐想一拍"),
        (24.328, "card", "减轻记忆负担", "分类器还有投机审批："),
        (26.128, "code", "分类器还有投机审批：", "allow · deny · ask"),
        (27.2, "section", "分类器还有投机审批：ask ", "分类器还有投机审批：ask 时与两秒定时器赛跑。"),
        (29.0, "card", "ask 时与两秒定时器赛跑", "两秒内高置信度就自动放"),
        (30.9, "stamp", "两秒内高置信度就自动放", "记下这一句"),
        (33.1, "card", "超时就弹窗给你。太短易空等网络，", "超时就弹窗给你。太短易空等网络，"),
        (35.627, "flow", "太短易空等网络", "太长用户烦——两秒是甜蜜点"),
        (38.153, "number", "太长用户烦——两秒是甜蜜点", "PermissionUp"),
        ],
    },
    {
        "id": "b06_outro",
        "title": "持久化 + 实战 + 片尾",
        "start": 357.552,
        "end": 453.048,
        "huashu": [("07_persist.mp4", 10.0, 7.0), ("08_building_gates.mp4", 40.0, 7.0), ("01_key_vs_gates.mp4", 70.0, 6.5)],
        "beats": [
        (0.0, "section", "持久化 + 实战 + 片尾", "持久化 + 实战 + 片尾"),
        (2.2, "card", "date 六种操作乘五种", "配置源"),
        (5.0, "card", "配置源，三十种组合。apply ", "配置源，三十种组合。apply 改内存，立刻生效；persist"),
        (7.271, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (10.0, "quiz", "合上书之前", "四道闸五句能背吗？"),
        (11.8, "code", "只有 local", "allow · deny · ask"),
        (13.155, "vs_auto", "万能钥匙 vs 四道闸", "纵深防御打败单门卫"),
        (14.955, "card", "session 和 cl", "iArg 只活在当次"),
        (16.45, "card", "session 和 cliArg", "session 和 cliArg 只活在当次。团队基线放进项目级"),
        (18.25, "stamp", "iArg 只活在当次", "记下这一句"),
        (19.45, "stamp", "团队基线放进项目级 se", "记下这一句"),
        (21.65, "pause", "停一下 · ttings.jso", "跟 VO 对齐想一拍"),
        (23.45, "flow", "json 提交仓库", "deny > ask > allow"),
        (25.0, "warn", "个人偏好放 local 不提交", "反模式 · 别踩"),
        (27.2, "section", "临时需求用会话级，别污染持久", "临时需求用会话级，别污染持久配置。"),
        (29.933, "card", "别污染持久配置", "练习可以很具体"),
        (31.733, "flow", "练习可以很具体", "deny > ask > allow"),
        (33.1, "card", "一，写项目级 allow/den", "一，写项目级 allow/deny。二，用前缀管住 npm 工具"),
        (34.9, "layers", "写项目级 allow/den", "校验 · 规则 · 上下文 · 确认"),
        (36.1, "persona_cl", "Claude", "会诊医生 · 边想边过闸"),
        (38.3, "card", "单独 deny publish。", "单独 deny publish。三，企业模板："),
        (40.1, "code", "单独 deny publish", "allow · deny · ask"),
        (41.458, "flow", "三", "优先级铁律"),
        (43.85, "card", "容器加 deny 加 allow", "容器加 deny 加 allowedTools 加审计。四，情景"),
        (46.637, "pause", "停一下 · 加审计", "跟 VO 对齐想一想"),
        (48.437, "card", "deny 与 allow", " 冲突谁赢——铁律"),
        (49.75, "chariot", "大楼门禁", "纵深防御才叫护栏"),
        (52.15, "code", "deny 赢", "allow · deny · ask"),
        (53.95, "persona_cx", "Codex", "易裸奔 · 要护栏"),
        (54.95, "persona_ah", "Agent Harness", "考工记御者 · 护栏握缰"),
        (57.519, "card", "deny 大于 ask ", "大于 allow"),
        (60.15, "card", "大于 allow。三，Permi", "大于 allow。三，PermissionCo"),
        (62.35, "stamp", "PermissionCo", "记下这一句"),
        (64.15, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (65.7, "number", "4", "闸门 · validate→ask"),
        (67.5, "stamp", "模式光谱按场景选", "记下这一句"),
        (68.676, "flow", "bypass 仍有底线", "优先级铁律"),
        (70.476, "warn", "五", "反模式 · 别踩"),
        (71.6, "card", "五，Bash 用前缀与通配管语义", "五，Bash 用前缀与通配管语义，持久化分层别混。"),
        (73.4, "card", "持久化分层别混", "下一集继续往下拆——双手"),
        (74.554, "flow", "持久化分层别混", "优先级铁律"),
        (76.8, "stamp", "下一集继续往下拆——双手", "记下这一点"),
        (78.6, "persona_cl", "Claude", "会诊医生 · 边想边过滤"),
        (79.77, "layers", "Harness 才能放心", "校验 · 规则 · 上下文 · 确认"),
        (82.35, "card", "把缰绳递给 Agent。本系列基", "把缰绳递给 Agent。本系列基于开源书稿。"),
        (84.584, "code", "本系列基于开源书稿", "allow · deny · ask"),
        (86.45, "flow", "系列名：", "deny > ask > allow"),
        (88.25, "vs_auto", "万能钥匙 vs 四道闸", "纵深闸门打败单门卫"),
        (90.665, "card", "关注小电讲电路", "合集里看目录更新"),
        ],
    },
]

SFX_CUE = [
    (0.0, "whoosh.wav", 0.2, 0.18),
    (2.673, "rein_snap.wav", 0.22, 0.12),
    (5.0, "punch.wav", 0.2, 0.18),
    (7.46, "tick.wav", 0.18, 0.08),
    (9.26, "tick.wav", 0.2, 0.18),
    (10.55, "rein_snap.wav", 0.22, 0.12),
    (12.35, "ui_blip.wav", 0.2, 0.18),
    (14.0, "ui_blip.wav", 0.22, 0.1),
    (16.636, "ui_blip.wav", 0.22, 0.1),
    (18.436, "rein_snap.wav", 0.22, 0.12),
    (22.0, "impact.wav", 0.2, 0.18),
    (24.737, "glitch.wav", 0.2, 0.18),
    (27.2, "ui_blip.wav", 0.22, 0.1),
    (29.0, "whoosh.wav", 0.28, 0.3),
    (30.55, "rein_snap.wav", 0.2, 0.18),
    (32.75, "gallop.wav", 0.2, 0.18),
    (34.55, "impact.wav", 0.28, 0.24),
    (36.223, "impact.wav", 0.28, 0.24),
    (39.696, "whoosh.wav", 0.2, 0.18),
    (41.896, "punch.wav", 0.2, 0.18),
    (44.696, "tick.wav", 0.2, 0.18),
    (46.496, "ui_blip.wav", 0.2, 0.18),
    (47.623, "impact.wav", 0.2, 0.18),
    (50.246, "impact.wav", 0.28, 0.24),
    (52.046, "rein_snap.wav", 0.22, 0.12),
    (53.946, "rein_snap.wav", 0.22, 0.12),
    (56.146, "glitch.wav", 0.2, 0.18),
    (58.346, "whoosh.wav", 0.28, 0.3),
    (60.146, "whoosh.wav", 0.28, 0.3),
    (61.346, "ui_blip.wav", 0.22, 0.1),
    (63.546, "impact.wav", 0.28, 0.24),
    (65.346, "impact.wav", 0.28, 0.24),
    (66.896, "rein_snap.wav", 0.2, 0.18),
    (68.696, "impact.wav", 0.28, 0.24),
    (70.239, "impact.wav", 0.28, 0.24),
    (72.796, "gallop.wav", 0.2, 0.18),
    (74.996, "whoosh.wav", 0.2, 0.18),
    (76.796, "punch.wav", 0.2, 0.18),
    (77.996, "tick.wav", 0.2, 0.18),
    (80.778, "rein_snap.wav", 0.22, 0.12),
    (83.546, "ui_blip.wav", 0.2, 0.18),
    (86.154, "tick.wav", 0.18, 0.08),
    (87.954, "rein_snap.wav", 0.22, 0.12),
    (89.446, "gallop.wav", 0.28, 0.4),
    (91.646, "ui_blip.wav", 0.22, 0.1),
    (93.446, "tick.wav", 0.18, 0.08),
    (94.646, "impact.wav", 0.2, 0.18),
    (97.28, "glitch.wav", 0.2, 0.18),
    (99.08, "ui_blip.wav", 0.22, 0.1),
    (100.196, "rein_snap.wav", 0.2, 0.18),
    (102.094, "gallop.wav", 0.2, 0.18),
    (103.896, "whoosh.wav", 0.2, 0.18),
    (106.096, "punch.wav", 0.2, 0.18),
    (107.896, "tick.wav", 0.2, 0.18),
    (108.971, "impact.wav", 0.28, 0.24),
    (111.296, "impact.wav", 0.28, 0.24),
    (113.785, "tick.wav", 0.18, 0.08),
    (115.585, "impact.wav", 0.28, 0.24),
    (116.846, "ui_blip.wav", 0.2, 0.18),
    (118.646, "tick.wav", 0.18, 0.08),
    (119.735, "tick.wav", 0.18, 0.08),
    (121.535, "tick.wav", 0.18, 0.08),
    (122.746, "whoosh.wav", 0.28, 0.3),
    (124.946, "tick.wav", 0.18, 0.08),
    (126.746, "tick.wav", 0.18, 0.08),
    (127.946, "impact.wav", 0.2, 0.18),
    (130.609, "glitch.wav", 0.2, 0.18),
    (132.409, "rein_snap.wav", 0.2, 0.18),
    (133.496, "gallop.wav", 0.2, 0.18),
    (135.296, "whoosh.wav", 0.2, 0.18),
    (136.631, "punch.wav", 0.2, 0.18),
    (139.396, "tick.wav", 0.2, 0.18),
    (141.77, "rein_snap.wav", 0.22, 0.12),
    (143.57, "rein_snap.wav", 0.22, 0.12),
    (144.596, "ui_blip.wav", 0.2, 0.18),
    (146.396, "whoosh.wav", 0.28, 0.3),
    (147.827, "whoosh.wav", 0.28, 0.3),
    (150.146, "impact.wav", 0.2, 0.18),
    (155.064, "glitch.wav", 0.2, 0.18),
    (157.387, "rein_snap.wav", 0.2, 0.18),
    (160.064, "gallop.wav", 0.2, 0.18),
    (161.864, "rein_snap.wav", 0.22, 0.12),
    (162.994, "whoosh.wav", 0.2, 0.18),
    (165.614, "impact.wav", 0.28, 0.24),
    (167.414, "tick.wav", 0.18, 0.08),
    (168.789, "impact.wav", 0.28, 0.24),
    (171.514, "punch.wav", 0.2, 0.18),
    (174.209, "tick.wav", 0.18, 0.08),
    (176.714, "ui_blip.wav", 0.22, 0.1),
    (178.514, "ui_blip.wav", 0.22, 0.1),
    (180.064, "tick.wav", 0.18, 0.08),
    (182.264, "tick.wav", 0.2, 0.18),
    (184.064, "ui_blip.wav", 0.2, 0.18),
    (185.879, "tick.wav", 0.18, 0.08),
    (188.164, "impact.wav", 0.2, 0.18),
    (190.914, "glitch.wav", 0.2, 0.18),
    (193.364, "rein_snap.wav", 0.2, 0.18),
    (195.564, "gallop.wav", 0.2, 0.18),
    (197.364, "whoosh.wav", 0.2, 0.18),
    (198.914, "punch.wav", 0.2, 0.18),
    (200.714, "impact.wav", 0.28, 0.24),
    (201.733, "rein_snap.wav", 0.22, 0.12),
    (203.533, "tick.wav", 0.18, 0.08),
    (204.814, "gallop.wav", 0.28, 0.4),
    (206.614, "tick.wav", 0.2, 0.18),
    (208.187, "whoosh.wav", 0.28, 0.3),
    (211.56, "ui_blip.wav", 0.2, 0.18),
    (214.36, "impact.wav", 0.2, 0.18),
    (216.56, "glitch.wav", 0.2, 0.18),
    (218.76, "rein_snap.wav", 0.22, 0.12),
    (220.56, "rein_snap.wav", 0.2, 0.18),
    (222.11, "impact.wav", 0.28, 0.24),
    (224.436, "whoosh.wav", 0.28, 0.3),
    (226.236, "gallop.wav", 0.2, 0.18),
    (228.01, "whoosh.wav", 0.2, 0.18),
    (230.404, "impact.wav", 0.28, 0.24),
    (232.204, "rein_snap.wav", 0.22, 0.12),
    (233.21, "ui_blip.wav", 0.22, 0.1),
    (235.775, "impact.wav", 0.28, 0.24),
    (237.575, "whoosh.wav", 0.28, 0.3),
    (238.76, "punch.wav", 0.2, 0.18),
    (240.56, "impact.wav", 0.28, 0.24),
    (241.721, "tick.wav", 0.2, 0.18),
    (243.521, "impact.wav", 0.28, 0.24),
    (244.66, "ui_blip.wav", 0.2, 0.18),
    (246.46, "impact.wav", 0.2, 0.18),
    (247.632, "rein_snap.wav", 0.22, 0.12),
    (249.86, "glitch.wav", 0.2, 0.18),
    (251.66, "rein_snap.wav", 0.22, 0.12),
    (253.191, "tick.wav", 0.18, 0.08),
    (255.41, "rein_snap.wav", 0.2, 0.18),
    (257.21, "tick.wav", 0.18, 0.08),
    (258.557, "ui_blip.wav", 0.22, 0.1),
    (261.31, "rein_snap.wav", 0.22, 0.12),
    (263.51, "gallop.wav", 0.2, 0.18),
    (265.41, "ui_blip.wav", 0.22, 0.1),
    (267.21, "gallop.wav", 0.28, 0.4),
    (269.563, "whoosh.wav", 0.2, 0.18),
    (271.363, "punch.wav", 0.2, 0.18),
    (272.41, "tick.wav", 0.2, 0.18),
    (274.61, "impact.wav", 0.28, 0.24),
    (276.41, "ui_blip.wav", 0.2, 0.18),
    (277.96, "impact.wav", 0.2, 0.18),
    (279.767, "impact.wav", 0.28, 0.24),
    (281.66, "tick.wav", 0.18, 0.08),
    (283.86, "glitch.wav", 0.2, 0.18),
    (285.66, "tick.wav", 0.18, 0.08),
    (286.86, "tick.wav", 0.18, 0.08),
    (289.06, "impact.wav", 0.28, 0.24),
    (290.86, "rein_snap.wav", 0.2, 0.18),
    (292.36, "tick.wav", 0.18, 0.08),
    (294.61, "gallop.wav", 0.2, 0.18),
    (296.41, "tick.wav", 0.18, 0.08),
    (297.942, "whoosh.wav", 0.2, 0.18),
    (300.51, "whoosh.wav", 0.28, 0.3),
    (302.905, "punch.wav", 0.2, 0.18),
    (304.705, "tick.wav", 0.2, 0.18),
    (305.71, "ui_blip.wav", 0.2, 0.18),
    (307.997, "rein_snap.wav", 0.22, 0.12),
    (309.797, "impact.wav", 0.2, 0.18),
    (311.26, "glitch.wav", 0.2, 0.18),
    (313.06, "rein_snap.wav", 0.22, 0.12),
    (314.066, "whoosh.wav", 0.28, 0.3),
    (316.872, "rein_snap.wav", 0.2, 0.18),
    (319.672, "rein_snap.wav", 0.22, 0.12),
    (321.872, "gallop.wav", 0.2, 0.18),
    (324.072, "tick.wav", 0.18, 0.08),
    (325.872, "whoosh.wav", 0.2, 0.18),
    (327.422, "impact.wav", 0.28, 0.24),
    (329.222, "rein_snap.wav", 0.22, 0.12),
    (330.252, "ui_blip.wav", 0.22, 0.1),
    (332.052, "tick.wav", 0.18, 0.08),
    (333.322, "punch.wav", 0.2, 0.18),
    (335.122, "ui_blip.wav", 0.22, 0.1),
    (336.297, "tick.wav", 0.2, 0.18),
    (338.522, "ui_blip.wav", 0.22, 0.1),
    (341.2, "ui_blip.wav", 0.2, 0.18),
    (343.0, "impact.wav", 0.2, 0.18),
    (344.072, "glitch.wav", 0.2, 0.18),
    (345.872, "rein_snap.wav", 0.2, 0.18),
    (347.772, "impact.wav", 0.28, 0.24),
    (349.972, "gallop.wav", 0.2, 0.18),
    (352.499, "tick.wav", 0.18, 0.08),
    (355.025, "whoosh.wav", 0.2, 0.18),
    (357.552, "punch.wav", 0.2, 0.18),
    (359.752, "tick.wav", 0.2, 0.18),
    (362.552, "ui_blip.wav", 0.2, 0.18),
    (364.823, "rein_snap.wav", 0.22, 0.12),
    (367.552, "ui_blip.wav", 0.22, 0.1),
    (369.352, "impact.wav", 0.2, 0.18),
    (370.707, "whoosh.wav", 0.28, 0.3),
    (372.507, "glitch.wav", 0.2, 0.18),
    (374.002, "rein_snap.wav", 0.2, 0.18),
    (375.802, "impact.wav", 0.28, 0.24),
    (377.002, "impact.wav", 0.28, 0.24),
    (379.202, "ui_blip.wav", 0.22, 0.1),
    (381.002, "tick.wav", 0.18, 0.08),
    (382.552, "impact.wav", 0.28, 0.24),
    (384.752, "gallop.wav", 0.2, 0.18),
    (387.485, "whoosh.wav", 0.2, 0.18),
    (389.285, "tick.wav", 0.18, 0.08),
    (390.652, "punch.wav", 0.2, 0.18),
    (392.452, "tick.wav", 0.18, 0.08),
    (393.652, "rein_snap.wav", 0.22, 0.12),
    (395.852, "tick.wav", 0.2, 0.18),
    (397.652, "ui_blip.wav", 0.2, 0.18),
    (399.01, "tick.wav", 0.18, 0.08),
    (401.402, "impact.wav", 0.2, 0.18),
    (404.189, "ui_blip.wav", 0.22, 0.1),
    (405.989, "glitch.wav", 0.2, 0.18),
    (407.302, "gallop.wav", 0.28, 0.4),
    (409.702, "rein_snap.wav", 0.2, 0.18),
    (411.502, "rein_snap.wav", 0.22, 0.12),
    (412.502, "rein_snap.wav", 0.22, 0.12),
    (415.071, "gallop.wav", 0.2, 0.18),
    (417.702, "whoosh.wav", 0.2, 0.18),
    (419.902, "impact.wav", 0.28, 0.24),
    (421.702, "whoosh.wav", 0.28, 0.3),
    (423.252, "punch.wav", 0.2, 0.18),
    (425.052, "impact.wav", 0.28, 0.24),
    (426.228, "tick.wav", 0.18, 0.08),
    (428.028, "impact.wav", 0.28, 0.24),
    (429.152, "tick.wav", 0.2, 0.18),
    (430.952, "ui_blip.wav", 0.2, 0.18),
    (432.106, "tick.wav", 0.18, 0.08),
    (434.352, "impact.wav", 0.28, 0.24),
    (436.152, "rein_snap.wav", 0.22, 0.12),
    (437.322, "tick.wav", 0.18, 0.08),
    (439.902, "impact.wav", 0.2, 0.18),
    (442.136, "glitch.wav", 0.2, 0.18),
    (444.002, "tick.wav", 0.18, 0.08),
    (445.802, "whoosh.wav", 0.28, 0.3),
    (448.217, "rein_snap.wav", 0.2, 0.18)
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
          <div class="kicker">隐喻对照 · 第04讲</div>
          <div class="vs-grid">
            <div class="vpanel"><h3>万能钥匙</h3><p>一把开全楼<br/>裸奔 · 无边界</p></div>
            <div class="vpanel r"><h3>四道闸</h3><p>校验 · 规则 · 上下文 · 确认<br/>纵深防御 · 短路截断</p></div>
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
    if kind in ("card", "section", "p", "sum", "next", "credit", "flow", "stack", "contrast", "question"):
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0,scale:0.94,y:28}}, {{opacity:1,scale:1,y:0,duration:0.38,ease:"power3.out"}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .kicker", {{opacity:0,x:-16}}, {{opacity:1,x:0,duration:0.28}}, {t0+0.06:.3f});',
            f'tl.fromTo("#{bid} .h1", {{opacity:0,y:22}}, {{opacity:1,y:0,duration:0.4,ease:"power2.out"}}, {t0+0.12:.3f});',
            f'tl.fromTo("#{bid} .h2", {{opacity:0,y:14}}, {{opacity:1,y:0,duration:0.32}}, {t0+0.28:.3f});',
            f'tl.to("#{bid}", {{scale:1.015,duration:{max(hold-0.9,1.2):.2f},ease:"sine.inOut",yoyo:true,repeat:1}}, {t0+0.5:.3f});',
            f'tl.to("#{bid}", {{opacity:0,y:-16,scale:0.98,duration:0.28}}, {out_at:.3f});',
        ]
        return lines
    if kind == "layers":
        lines += [
            f'tl.fromTo("#{bid}", {{opacity:0}}, {{opacity:1,duration:0.3}}, {t0:.3f});',
            f'tl.fromTo("#{bid} .layer", {{opacity:0,y:30,scale:0.9}}, {{opacity:1,y:0,scale:1,duration:0.32,stagger:0.1,ease:"back.out(1.4)"}}, {t0+0.15:.3f});',
            f'tl.to("#{bid}", {{opacity:0,duration:0.28}}, {out_at:.3f});',
        ]
        return lines
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
    bad = ["", "视觉", "听觉", "证明", "能量", ""]
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
    (ROOT / "package.json").write_text(
        json.dumps({
            "name": "ch04-long-v1",
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
        json.dumps({"id": "ch04-long-v1", "name": "ch04-long-v1", "duration": TOTAL}, indent=2),
        encoding="utf-8",
    )
    print("ch04 dense v2 densify assembled TOTAL", TOTAL, "blocks", len(BLOCKS), "sfx", len(SFX_CUE), "caps", len(TRANS))


if __name__ == "__main__":
    main()
