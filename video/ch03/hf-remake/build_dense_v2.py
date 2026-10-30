# -*- coding: utf-8 -*-
"""ch03 long densify v2 — clone of ch01 v4 / ch02 v1 quality bar. No publish."""
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
TOTAL = 597.024


BLOCKS = [
    {
        "id": "b01_hook",
        "title": "开场钩子 · 双手",
        "start": 0.0,
        "end": 60.768,
        "huashu": [("01_hammer_hands.mp4", 8.0, 7.0), ("01_hammer_hands.mp4", 38.0, 6.5)],
        "beats": [
        (0.0, "section", "双手", "开场钩子 · 双手"),
        (2.375, "code", "驭者·Agent Har", "类型契约"),
        (5.0, "card", "ness 第 03 讲。上一集心", "ness 第 03 讲。上一集心跳装上了：AsyncGenera"),
        (8.202, "card", "AsyncGenerat", "or 一下一下往外吐事件"),
        (10.55, "persona_ah", "Agent Harness", "考工记御者 · 双手握缰"),
        (13.499, "stamp", "还得有双手——否则马再壮", "记下这一句"),
        (16.1, "stamp", "也够不着缰绳外的活。这一", "记下这一点"),
        (19.396, "flow", "书稿标题写得很直白：", "分区 → 并行 → yield"),
        (22.0, "card", "Agent 的双手。先借一句马斯", "Agent 的双手。先借一句马斯洛：如果你手里只有锤子，"),
        (24.61, "flow", "如果你手里只有锤子", "分区 → 并行 → yield"),
        (27.2, "pause", "停一下 · 看什么都像钉子。换成", "跟 VO 对齐想一拍"),
        (29.638, "layers", "如果只有 Bash", "协议 · 权限 · 编排"),
        (32.75, "section", "读文件变成 cat，搜代码变", "读文件变成 cat，搜代码变成 grep，改文件"),
        (35.411, "code", "改文件变成 sed——能跑", "类型契约"),
        (38.65, "card", "但不叫工程。猜一猜：源码里「双手", "但不叫工程。猜一猜：源码里「双手」最先钉住的，是五十多个函数名，"),
        (41.65, "card", "是五十多个函数名", "还是一套叫五要素的协议"),
        (43.85, "card", "还是一套叫五要素的协议？答案在本", "还是一套叫五要素的协议？答案在本章骨架里——先协议，"),
        (46.05, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (49.4, "persona_cl", "Claude", "会诊医生 · 边想边说边开检查"),
        (52.75, "vs_auto", "锤子 vs 双手", "专门化打败万能锤"),
        (54.95, "card", "Tool，三个泛型——Input", "Tool，三个泛型——Input、Output、"),
        (57.859, "stamp", "Output", "Progress"),
        ],
    },
    {
        "id": "b02_proto",
        "title": "§3.1 工具定义协议",
        "start": 60.768,
        "end": 197.88,
        "huashu": [("02_five_elements.mp4", 12.0, 7.0), ("03_zod_schema.mp4", 45.0, 7.0), ("04_permissions.mp4", 85.0, 7.0), ("02_five_elements.mp4", 115.0, 6.5)],
        "beats": [
        (0.0, "section", "§3.1 工具定义协议", "§3.1 工具定义协议"),
        (2.8, "card", "输出自由", "进度单独开类型空间"),
        (5.0, "card", "输出自由；进度单独开类型空间，好", "输出自由；进度单独开类型空间，好让执行中还能流式汇报。"),
        (7.2, "stamp", "好让执行中还能流式汇报", "记下这一句"),
        (10.55, "stamp", "三者拆开，不是炫技，是让", "记下这一点"),
        (13.5, "flow", "是让编译器分别检查三个关注点", "分区 → 并行 → yield"),
        (16.45, "persona_ah", "Agent Harness", "考工记御者 · 双手握缰"),
        (18.791, "flow", "名称与别名", "分区 → 并行 → yield"),
        (22.35, "card", "旧名靠别名继续命中。公开 API", "旧名靠别名继续命中。公开 API 里重命名是「只增不减」："),
        (25.12, "layers", "「只增不减」：", "协议 · 权限 · 编排"),
        (27.55, "pause", "停一下 · SearchTool", "跟 VO 对齐想一拍"),
        (30.489, "code", "旧名仍得认得", "类型契约"),
        (33.1, "section", "否则配置、脚本、用户肌肉记忆", "否则配置、脚本、用户肌肉记忆一起断。要素二，Zo"),
        (35.679, "card", "Zod Schema", "双重职责："),
        (39.0, "card", "双重职责：运行时验证——别信 L", "双重职责：运行时验证——别信 LLM 吐的参数；以及转成 JSO"),
        (41.2, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (44.2, "card", "hema 发给 API，当作工具", "hema 发给 API，当作工具说明书。"),
        (47.178, "vs_auto", "锤子 vs 双手", "专门化打败万能锤"),
        (49.75, "card", "describe 写清楚，模型才", "describe 写清楚，模型才知道旋钮在哪。要素三，"),
        (53.23, "stamp", "要素三", "记下这一句"),
        (55.65, "chariot", "辔绳外的活", "双手够得着才叫工程"),
        (58.061, "warn", "管数据合不合法", "反模式 · 别踩"),
        (60.85, "card", "ions 加 checkPerm", "ions 加 checkPermissions，管该不该用；最后"),
        (63.928, "card", "管该不该用", "最后运行时属性"),
        (66.4, "card", "比如 isConcurrency", "比如 isConcurrencySafe，影响后面能不能并行。数"),
        (70.088, "persona_cl", "Claude", "会诊医生 · 边想边开检查"),
        (72.3, "card", "权限策略、调度策略，各管各的，", "权限策略、调度策略，各管各的，串起来才是护栏。要素四，"),
        (74.5, "flow", "串起来才是护栏", "分区 → 并行 → yield"),
        (77.5, "stamp", "要素四，执行逻辑。真正干", "记下这一点"),
        (80.148, "pause", "停一下 · 外加 context", "跟 VO 对齐想一想"),
        (83.05, "card", "difier：写完文件要更新缓存", "difier：写完文件要更新缓存，让下一只手读到新世界。"),
        (86.102, "code", "让下一只手读到新世界", "类型契约"),
        (88.95, "vs_auto", "锤子 Bash vs 双手专工具", "专门化打败万能锤"),
        (91.95, "card", "覆盖生老病死：", "开始"),
        (94.15, "card", "开始、进度、成功、", "开始、进度、成功、被拒、出错、"),
        (96.573, "stamp", "并行分组", "记下这一句"),
        (99.7, "p", "工具外观跟组件一样可组合", "工具外观跟组件一样可组合。组装工具用 build"),
        (102.88, "flow", "组装工具用 buildTool", "分区 → 并行 → yield"),
        (105.6, "card", "工厂帮你填安全默认值，哲学是 f", "工厂帮你填安全默认值，哲学是 fail-closed："),
        (108.0, "flow", "哲学是 fail-closed：", "分区 → 并行 → yield"),
        (110.8, "code", "Tool<In,Out,Prog>", "Zod · call · UI 六态"),
        (113.689, "layers", "没声明只读", "协议 · 权限 · 编排"),
        (116.35, "card", "类比机场安检：默认人人过检，特赦", "类比机场安检：默认人人过检，特赦必须显式。"),
        (119.241, "code", "特赦必须显式", "类型契约"),
        (122.25, "layers", "三层权限", "validate · hasPerm · 并发属性"),
        (124.911, "card", "简单工具写几行", "复杂工具把方法盖满——可选覆盖"),
        (127.45, "card", "复杂工具把方法盖满——可选覆盖，", "复杂工具把方法盖满——可选覆盖，安全默认。getAllBaseT"),
        (130.58, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (133.0, "flow", "分区 → 并行 → 顺序 yield", "编排三角"),
        ],
    },
    {
        "id": "b03_reg",
        "title": "§3.2 注册与动态发现",
        "start": 197.88,
        "end": 314.664,
        "huashu": [("05_lazy_registry.mp4", 18.0, 7.0), ("06_mcp_waist.mp4", 55.0, 7.0), ("05_lazy_registry.mp4", 90.0, 6.5)],
        "beats": [
        (0.0, "section", "§3.2 注册与动态发现", "§3.2 注册与动态发现"),
        (2.505, "vs_auto", "锤子 vs 双手", "专门化打败万能锤"),
        (5.0, "card", "Edit、Write；搜索 Gl", "Edit、Write；搜索 Glob、Grep；网络 Fetch"),
        (7.677, "stamp", "网络 Fetch", "记下这一句"),
        (10.55, "stamp", "Search；智能 Ag", "记下这一点"),
        (13.334, "warn", "交互提问", "反模式 · 别踩"),
        (16.45, "card", "MCP；工作树……完整清单大约五", "MCP；工作树……完整清单大约五十五个，附录里还能对表。"),
        (19.338, "card", "附录里还能对表", "注意「并发安全」那一列："),
        (21.65, "pause", "停一下 · 注意「并发安全」那一", "跟 VO 对齐想一拍"),
        (25.0, "persona_cl", "Claude", "会诊医生 · 边想边开检查"),
        (27.2, "section", "纯读纯搜的少。后面分区算法，", "纯读纯搜的少。后面分区算法，就是在这约束里挤并行"),
        (30.52, "flow", "就是在这约束里挤并行度", "分区 → 并行 → yield"),
        (33.1, "card", "条件导入做死代码消除：功能开关关", "条件导入做死代码消除：功能开关关掉，整模块被 tree-sh"),
        (35.3, "pause", "停一下 · 功能开关关掉", "跟 VO 对齐想一想"),
        (38.3, "card", "aking 拿掉。外部构建不夹带", "aking 拿掉。外部构建不夹带内部调试工具，"),
        (41.048, "code", "外部构建不夹带内部调试工具", "类型契约"),
        (43.85, "card", "既瘦身，也少泄架构。工具一多，", "既瘦身，也少泄架构。工具一多，就上延迟发现 ToolS"),
        (46.734, "card", "就上延迟发现 ToolS", "earchTool"),
        (49.75, "chariot", "辔绳外的活", "双手够得着才叫工程"),
        (52.75, "stamp", "先给目录索引——名字列表", "记下这一句"),
        (54.95, "card", "先给目录索引——名字列表。真要用", "先给目录索引——名字列表。真要用时，再翻开那一页 schema。"),
        (57.15, "flow", "再翻开那一页 schema", "分区 → 并行 → yield"),
        (60.5, "card", "MCP 一挂几十个工具，全量 s", "MCP 一挂几十个工具，全量 schema 能吃掉几千 toke"),
        (64.072, "flow", "掉几千 token", "分区 → 并行 → yield"),
        (66.4, "card", "延迟发现省的是初始 prompt", "延迟发现省的是初始 prompt 的腰围。显式 alwaysLo"),
        (69.291, "layers", "显式 alwaysLoa", "协议 · 权限 · 编排"),
        (71.6, "stamp", "d 的不延迟；MCP 默", "记下这一点"),
        (74.005, "code", "搜索工具自己不延迟", "类型契约"),
        (77.15, "card", "从全量到 API，还要过过滤漏斗", "从全量到 API，还要过过滤漏斗：模式过滤——简单模式只留"),
        (80.85, "card", " Bash", "Read"),
        (83.05, "vs_auto", "锤子 Bash vs 双手专工具", "专门化打败万能锤"),
        (86.05, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (88.25, "card", "启用状态再筛；最后内建加 MCP", "启用状态再筛；最后内建加 MCP 合并、按名排序去重。"),
        (91.421, "vs_auto", "锤子 vs 双手", "专门化打败万能锤"),
        (93.8, "p", "排序不是洁癖，是为了 p", "排序不是洁癖，是为了 prompt 缓存稳定——"),
        (96.322, "stamp", "存稳定——顺序一抖", "记下这一句"),
        (99.7, "card", "过滤是权限的第一道：模型看不见的", "过滤是权限的第一道：模型看不见的工具，连「想用」都难。"),
        (102.509, "warn", "连「想用」都难", "反模式 · 别踩"),
        (104.9, "code", "Tool<In,Out,Prog>", "Zod · call · UI 六态"),
        (107.241, "card", "也是最需要戴手套的", "失败会取消并行的兄弟 B"),
        (110.45, "card", "失败会取消并行的兄弟 Bash—", "失败会取消并行的兄弟 Bash——命令链常有隐式依赖，mkdir"),
        (113.617, "persona_cl", "依赖", "mkdir 挂了后面别装勇敢"),
        ],
    },
    {
        "id": "b04_core",
        "title": "§3.3 核心工具深度",
        "start": 314.664,
        "end": 411.264,
        "huashu": [("07_crud_suite.mp4", 15.0, 7.0), ("08_specialized.mp4", 50.0, 7.0), ("07_crud_suite.mp4", 78.0, 6.5)],
        "beats": [
        (0.0, "section", "§3.3 核心工具深度", "§3.3 核心工具深度"),
        (2.2, "vs_auto", "锤子 vs 双手", "专门化打败万能锤"),
        (5.0, "card", "而不是立刻掐死。它还会做 AST", "而不是立刻掐死。它还会做 AST 与语义分析，"),
        (7.775, "stamp", "它还会做 AST 与语义", "记下这一句"),
        (10.55, "stamp", "判断是不是搜索只读，好折", "记下这一点"),
        (13.133, "warn", "沙盒仍是安全网：", "反模式 · 别踩"),
        (16.45, "card", "文件系统边界还能兜。文件三件套像", "文件系统边界还能兜。文件三件套像 CRUD，"),
        (19.45, "card", "文件三件套像 CRUD", "却故意缺 Delete"),
        (21.65, "pause", "停一下 · 却故意缺 Delet", "跟 VO 对齐想一拍"),
        (24.003, "persona_cl", "Claude", "会诊医生 · 边想边开检查"),
        (27.2, "section", "触发更严权限。Read 带文", "触发更严权限。Read 带文件状态缓存，"),
        (29.4, "flow", "Read 带文件状态缓存", "分区 → 并行 → yield"),
        (33.1, "card", "Edit 用 old_strin", "Edit 用 old_string 换 new_"),
        (35.3, "pause", "停一下 · tring 换 ne", "跟 VO 对齐想一想"),
        (38.3, "card", "string，不用行号——行号一", "string，不用行号——行号一偏移就改错地；精确串匹配更幂等。"),
        (41.504, "code", "精确串匹配更幂等", "类型契约"),
        (43.85, "card", "Write 最重，整文件覆盖，权", "Write 最重，整文件覆盖，权限最严。最佳实践：能 Edit "),
        (46.783, "card", "能 Edit 别 Write", "能 Read 别 Bash"),
        (49.75, "chariot", "辔绳外的活", "双手够得着才叫工程"),
        (52.75, "stamp", "Grep 对内容", "记下这一句"),
        (54.95, "card", "底层 fast-glob 与 r", "底层 fast-glob 与 ripgrep。为什么不一律 Ba"),
        (57.968, "flow", "为什么不一律 Bash ", "分区 → 并行 → yield"),
        (60.5, "card", "find/grep？结构化输出更", "find/grep？结构化输出更好解析；默认只读，"),
        (64.2, "flow", "默认只读", "分区 → 并行 → yield"),
        (66.4, "card", "权限更松；结果上限与并行可针对性", "权限更松；结果上限与并行可针对性优化。专门化打败「万能锤子」。"),
        (69.121, "layers", "专门化打败「万能锤子」", "协议 · 权限 · 编排"),
        (71.6, "stamp", "AgentTool 是派", "记下这一点"),
        (74.498, "code", "子智能体独立上下文与工具集", "类型契约"),
        (77.15, "card", "干完把结果交回。常 always", "干完把结果交回。常 alwaysLoad，"),
        (79.35, "card", "常 alwaysLoad", "别被延迟发现藏起来"),
        (83.05, "vs_auto", "锤子 Bash vs 双手专工具", "专门化打败万能锤"),
        (85.25, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (88.25, "card", "权限等边界，但不共享消息列表——", "权限等边界，但不共享消息列表——继承却不串味。细节放到扩展篇；"),
        (91.033, "vs_auto", "细节放到扩展篇", "本章先认门："),
        (93.817, "stamp", "双手里有一只专门「再生一双手」", "编排引擎是指挥中心"),
        ],
    },
    {
        "id": "b05_orch",
        "title": "§3.4 工具编排引擎",
        "start": 411.264,
        "end": 524.112,
        "huashu": [("09_partition.mp4", 12.0, 7.0), ("10_streaming_exec.mp4", 55.0, 7.0), ("09_partition.mp4", 88.0, 6.5)],
        "beats": [
        (0.0, "section", "§3.4 工具编排引擎", "§3.4 工具编排引擎"),
        (2.284, "code", "三角拉扯：", "类型契约"),
        (5.0, "persona_ah", "Agent Harness", "考工记御者 · 双手握缰"),
        (8.0, "card", "runTools 是异步生成器", "策略叫并发分区："),
        (10.2, "card", "策略叫并发分区：按序切批次；", "策略叫并发分区：按序切批次；"),
        (13.523, "stamp", "按序切批次", "记下这一句"),
        (15.75, "stamp", "连续的并发安全工具捆一批", "记下这一点"),
        (18.151, "flow", "碰到非安全", "分区 → 并行 → yield"),
        (21.65, "card", "例子：Read a、Read b", "例子：Read a、Read b、Bash ls、Read c。"),
        (24.029, "flow", "Bash ls", "分区 → 并行 → yield"),
        (26.85, "pause", "停一下 · Read c。前两个", "跟 VO 对齐想一拍"),
        (29.05, "layers", "Read c 必须等 B", "协议 · 权限 · 编排"),
        (32.4, "section", "ash 完——Bash 可能", "ash 完——Bash 可能改目录改文件，并行读"),
        (34.6, "code", "并行读会读到不确定世界", "类型契约"),
        (38.3, "card", "Glob、Grep、Bash n", "Glob、Grep、Bash npm test、Read a、"),
        (41.3, "card", "Read a", "Edit a"),
        (43.5, "card", "Edit a、Glob json", "Edit a、Glob json——你会划几批？书稿答案是五批："),
        (46.693, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (49.05, "card", "前两个并行；Bash 串；Rea", "前两个并行；Bash 串；Read 因前面非安全不能并回；"),
        (52.75, "vs_auto", "锤子 vs 双手", "专门化打败万能锤"),
        (54.95, "chariot", "辔绳外的活", "双手够得着才叫工程"),
        (57.95, "stamp", "ob 不能同批", "记下这一句"),
        (60.15, "card", "副作用边界要干净。Streami", "副作用边界要干净。StreamingToolExecutor 更"),
        (63.233, "warn", "lExecutor 更狠", "反模式 · 别踩"),
        (65.7, "card", "：不等模型整段说完，流式接到 t", "：不等模型整段说完，流式接到 tool_use 块就开工。"),
        (68.805, "card", "e 块就开工", "五工具各一秒的老算法可能七秒"),
        (71.6, "card", "五工具各一秒的老算法可能七秒；流", "五工具各一秒的老算法可能七秒；流式交叠能压到大约三秒量级。每个工"),
        (74.6, "persona_cl", "Claude", "会诊医生 · 边想边开检查"),
        (76.8, "stamp", "queued、execu", "记下这一点"),
        (79.742, "flow", "completed", "分区 → 并行 → yield"),
        (82.35, "card", "yielded。并行可以跑完，y", "yielded。并行可以跑完，yield 仍按请求序——未完成的"),
        (86.05, "pause", "停一下 · —未完成的非安全会挡", "跟 VO 对齐想一想"),
        (88.25, "vs_auto", "锤子 Bash vs 双手专工具", "专门化打败万能锤"),
        (90.45, "code", "Bash 失败取消并行兄弟", "类型契约"),
        (93.45, "card", "普通读搜失败通常不传染。进度消息", "普通读搜失败通常不传染。进度消息绕过顺序，立刻 yield，"),
        (96.346, "card", "立刻 yield", "UI 先亮着"),
        (99.0, "p", "UI 先亮着。模型 fa", "UI 先亮着。模型 fallback 时，待执行"),
        (101.882, "stamp", "待执行与执行中全部标废弃", "记下这一句"),
        (104.9, "card", "防旧结果泄漏。取消用层级子控制器", "防旧结果泄漏。取消用层级子控制器，别共用一个 AbortC"),
        (107.549, "flow", "别共用一个 AbortC", "ontroller 误伤"),
        (110.199, "number", "ontroller 误伤", "无关工具"),
        ],
    },
    {
        "id": "b06_outro",
        "title": "实战 + 总结 + 片尾",
        "start": 524.112,
        "end": 597.024,
        "huashu": [("11_five_lines.mp4", 10.0, 7.0), ("11_five_lines.mp4", 42.0, 6.5)],
        "beats": [
        (0.0, "section", "实战 + 总结 + 片尾", "实战 + 总结 + 片尾"),
        (2.8, "persona_cl", "Claude", "会诊医生 · 边想边开检查"),
        (5.0, "card", "边流边入队，边跳边干活。练习可以", "边流边入队，边跳边干活。练习可以很具体。一，用 buildToo"),
        (8.0, "quiz", "合上书之前", "双手 DNA 五句能背吗？"),
        (10.239, "flow", "做只读小工具", "分区 → 并行 → yield"),
        (13.567, "pause", "停一下 · rencySafe ", "跟 VO 对齐想一想"),
        (16.45, "card", "的两种代价。二，手动画分区。", "的两种代价。二，手动画分区。三，对 StreamingT"),
        (18.664, "code", "对 StreamingT", "类型契约"),
        (21.65, "pause", "停一下 · oolExecuto", "跟 VO 对齐想一拍"),
        (24.193, "card", "再 Ctrl+C 看取消链", "四"),
        (27.2, "section", "四，有 MCP 时对比延迟发", "四，有 MCP 时对比延迟发现开关下的 inpu"),
        (29.4, "stamp", "现开关下的 input ", "记下这一句"),
        (33.1, "card", "收五句。一，五要素协议是工具 D", "收五句。一，五要素协议是工具 DNA。二，buildTool 安"),
        (35.84, "flow", "二", "分区 → 并行 → yield"),
        (38.3, "card", "fail-closed。三，并发", "fail-closed。三，并发分区用正确标记换速度。"),
        (41.148, "flow", "并发分区用正确标记换速度", "分区 → 并行 → yield"),
        (43.85, "persona_ah", "Agent Harness", "考工记御者 · 双手握缰"),
        (46.05, "layers", "lExecutor 让双", "协议 · 权限 · 编排"),
        (49.4, "card", "五，类型契约让加新工具不必改指挥", "五，类型契约让加新工具不必改指挥部。下一集第 04 章，"),
        (53.019, "code", "下一集第 04 章", "类型契约"),
        (55.3, "chariot", "辔绳外的活", "双手够得着才叫工程"),
        (58.3, "card", "双手能伸多远", "护栏说了算"),
        (60.5, "card", "护栏说了算。本系列基于开源书稿。", "护栏说了算。本系列基于开源书稿。系列名：驭者·Agent Har"),
        (63.458, "persona_cx", "Codex", "双手执行 · 专工具优先"),
        (66.05, "card", "ness。关注小电讲电路，合集里", "ness。关注小电讲电路，合集里看目录更新。"),
        (69.481, "vs_auto", "合集里看目录更新", "我们下集见"),
        ],
    },
]

SFX_CUE = [
    (0.02, "whoosh.wav", 0.28, 0.25),
    (2.395, "punch.wav", 0.28, 0.25),
    (5.02, "tick.wav", 0.22, 0.15),
    (8.05, "whoosh.wav", 0.24, 0.3),
    (10.57, "punch.wav", 0.26, 0.2),
    (13.519, "impact.wav", 0.28, 0.24),
    (16.12, "impact.wav", 0.28, 0.24),
    (19.416, "impact.wav", 0.28, 0.25),
    (22.02, "glitch.wav", 0.28, 0.25),
    (24.63, "rein_snap.wav", 0.28, 0.25),
    (27.22, "ui_blip.wav", 0.22, 0.1),
    (29.658, "gallop.wav", 0.28, 0.25),
    (32.77, "whoosh.wav", 0.28, 0.25),
    (35.431, "punch.wav", 0.28, 0.25),
    (38.05, "whoosh.wav", 0.24, 0.3),
    (41.67, "ui_blip.wav", 0.22, 0.25),
    (43.87, "impact.wav", 0.28, 0.25),
    (46.07, "punch.wav", 0.26, 0.2),
    (49.42, "punch.wav", 0.26, 0.2),
    (52.77, "whoosh.wav", 0.28, 0.3),
    (54.97, "glitch.wav", 0.28, 0.25),
    (57.879, "impact.wav", 0.28, 0.24),
    (60.788, "rein_snap.wav", 0.28, 0.25),
    (63.588, "gallop.wav", 0.28, 0.25),
    (65.788, "whoosh.wav", 0.28, 0.25),
    (67.988, "impact.wav", 0.28, 0.24),
    (71.338, "impact.wav", 0.28, 0.24),
    (72.818, "whoosh.wav", 0.24, 0.3),
    (74.288, "punch.wav", 0.28, 0.25),
    (77.238, "punch.wav", 0.26, 0.2),
    (79.579, "tick.wav", 0.22, 0.15),
    (83.138, "ui_blip.wav", 0.22, 0.25),
    (85.908, "impact.wav", 0.28, 0.25),
    (88.338, "ui_blip.wav", 0.22, 0.1),
    (91.277, "glitch.wav", 0.28, 0.25),
    (93.888, "rein_snap.wav", 0.28, 0.25),
    (96.467, "gallop.wav", 0.28, 0.25),
    (99.788, "whoosh.wav", 0.28, 0.25),
    (101.988, "punch.wav", 0.26, 0.2),
    (104.988, "punch.wav", 0.28, 0.25),
    (107.966, "whoosh.wav", 0.28, 0.3),
    (110.538, "tick.wav", 0.22, 0.15),
    (114.018, "impact.wav", 0.28, 0.24),
    (116.438, "gallop.wav", 0.28, 0.4),
    (118.849, "impact.wav", 0.28, 0.24),
    (121.638, "ui_blip.wav", 0.22, 0.25),
    (124.716, "impact.wav", 0.28, 0.25),
    (127.188, "glitch.wav", 0.28, 0.25),
    (130.876, "punch.wav", 0.26, 0.2),
    (133.088, "rein_snap.wav", 0.28, 0.25),
    (135.288, "gallop.wav", 0.28, 0.25),
    (138.288, "impact.wav", 0.28, 0.24),
    (140.936, "ui_blip.wav", 0.22, 0.1),
    (143.838, "whoosh.wav", 0.28, 0.25),
    (145.818, "whoosh.wav", 0.24, 0.3),
    (146.89, "punch.wav", 0.28, 0.25),
    (149.738, "whoosh.wav", 0.28, 0.3),
    (152.738, "tick.wav", 0.22, 0.15),
    (154.938, "ui_blip.wav", 0.22, 0.25),
    (157.361, "impact.wav", 0.28, 0.24),
    (160.488, "impact.wav", 0.28, 0.25),
    (163.668, "glitch.wav", 0.28, 0.25),
    (166.388, "rein_snap.wav", 0.28, 0.25),
    (168.788, "gallop.wav", 0.28, 0.25),
    (171.588, "whoosh.wav", 0.28, 0.25),
    (174.477, "punch.wav", 0.28, 0.25),
    (175.818, "whoosh.wav", 0.24, 0.3),
    (177.138, "tick.wav", 0.22, 0.15),
    (180.029, "ui_blip.wav", 0.22, 0.25),
    (183.038, "impact.wav", 0.28, 0.25),
    (185.699, "glitch.wav", 0.28, 0.25),
    (188.238, "rein_snap.wav", 0.28, 0.25),
    (191.368, "punch.wav", 0.26, 0.2),
    (193.788, "gallop.wav", 0.28, 0.25),
    (197.9, "whoosh.wav", 0.28, 0.25),
    (200.405, "whoosh.wav", 0.28, 0.3),
    (202.9, "punch.wav", 0.28, 0.25),
    (205.577, "impact.wav", 0.28, 0.24),
    (208.45, "impact.wav", 0.28, 0.24),
    (211.234, "impact.wav", 0.28, 0.24),
    (214.35, "tick.wav", 0.22, 0.15),
    (215.93, "whoosh.wav", 0.24, 0.3),
    (217.238, "ui_blip.wav", 0.22, 0.25),
    (219.55, "ui_blip.wav", 0.22, 0.1),
    (222.9, "punch.wav", 0.26, 0.2),
    (225.1, "impact.wav", 0.28, 0.25),
    (228.42, "glitch.wav", 0.28, 0.25),
    (231.0, "rein_snap.wav", 0.28, 0.25),
    (233.2, "ui_blip.wav", 0.22, 0.1),
    (236.2, "gallop.wav", 0.28, 0.25),
    (238.948, "whoosh.wav", 0.28, 0.25),
    (241.75, "punch.wav", 0.28, 0.25),
    (244.634, "tick.wav", 0.22, 0.15),
    (247.65, "gallop.wav", 0.28, 0.4),
    (250.65, "impact.wav", 0.28, 0.24),
    (252.85, "ui_blip.wav", 0.22, 0.25),
    (255.05, "impact.wav", 0.28, 0.25),
    (258.4, "glitch.wav", 0.28, 0.25),
    (261.972, "rein_snap.wav", 0.28, 0.25),
    (264.3, "gallop.wav", 0.28, 0.25),
    (267.191, "whoosh.wav", 0.28, 0.25),
    (269.5, "impact.wav", 0.28, 0.24),
    (271.905, "punch.wav", 0.28, 0.25),
    (275.05, "tick.wav", 0.22, 0.15),
    (278.75, "ui_blip.wav", 0.22, 0.25),
    (280.95, "whoosh.wav", 0.28, 0.3),
    (283.95, "punch.wav", 0.26, 0.2),
    (286.15, "impact.wav", 0.28, 0.25),
    (287.93, "whoosh.wav", 0.24, 0.3),
    (289.321, "whoosh.wav", 0.28, 0.3),
    (291.7, "glitch.wav", 0.28, 0.25),
    (294.222, "impact.wav", 0.28, 0.24),
    (297.6, "rein_snap.wav", 0.28, 0.25),
    (300.409, "impact.wav", 0.28, 0.24),
    (302.8, "gallop.wav", 0.28, 0.25),
    (305.141, "whoosh.wav", 0.28, 0.25),
    (308.35, "punch.wav", 0.28, 0.25),
    (311.517, "punch.wav", 0.26, 0.2),
    (314.684, "tick.wav", 0.22, 0.15),
    (316.884, "whoosh.wav", 0.28, 0.3),
    (319.684, "ui_blip.wav", 0.22, 0.25),
    (322.459, "impact.wav", 0.28, 0.24),
    (325.234, "impact.wav", 0.28, 0.24),
    (327.817, "impact.wav", 0.28, 0.24),
    (329.714, "whoosh.wav", 0.24, 0.3),
    (331.134, "impact.wav", 0.28, 0.25),
    (334.134, "glitch.wav", 0.28, 0.25),
    (336.334, "ui_blip.wav", 0.22, 0.1),
    (338.687, "punch.wav", 0.26, 0.2),
    (341.884, "rein_snap.wav", 0.28, 0.25),
    (344.084, "gallop.wav", 0.28, 0.25),
    (347.784, "whoosh.wav", 0.28, 0.25),
    (349.984, "ui_blip.wav", 0.22, 0.1),
    (352.984, "punch.wav", 0.28, 0.25),
    (356.188, "tick.wav", 0.22, 0.15),
    (358.534, "ui_blip.wav", 0.22, 0.25),
    (361.467, "impact.wav", 0.28, 0.25),
    (364.434, "gallop.wav", 0.28, 0.4),
    (367.434, "impact.wav", 0.28, 0.24),
    (369.634, "glitch.wav", 0.28, 0.25),
    (372.652, "rein_snap.wav", 0.28, 0.25),
    (375.184, "gallop.wav", 0.28, 0.25),
    (378.884, "whoosh.wav", 0.28, 0.25),
    (381.084, "punch.wav", 0.28, 0.25),
    (383.805, "tick.wav", 0.22, 0.15),
    (386.284, "impact.wav", 0.28, 0.24),
    (389.182, "ui_blip.wav", 0.22, 0.25),
    (391.834, "impact.wav", 0.28, 0.25),
    (394.034, "glitch.wav", 0.28, 0.25),
    (397.734, "whoosh.wav", 0.28, 0.3),
    (399.934, "punch.wav", 0.26, 0.2),
    (402.934, "rein_snap.wav", 0.28, 0.25),
    (405.717, "whoosh.wav", 0.28, 0.3),
    (408.501, "impact.wav", 0.28, 0.24),
    (411.284, "gallop.wav", 0.28, 0.25),
    (413.568, "whoosh.wav", 0.28, 0.25),
    (416.284, "punch.wav", 0.26, 0.2),
    (419.284, "punch.wav", 0.28, 0.25),
    (421.484, "tick.wav", 0.22, 0.15),
    (423.314, "whoosh.wav", 0.24, 0.3),
    (424.807, "impact.wav", 0.28, 0.24),
    (427.034, "impact.wav", 0.28, 0.24),
    (429.435, "ui_blip.wav", 0.22, 0.25),
    (432.934, "impact.wav", 0.28, 0.25),
    (435.313, "glitch.wav", 0.28, 0.25),
    (438.134, "ui_blip.wav", 0.22, 0.1),
    (440.334, "rein_snap.wav", 0.28, 0.25),
    (443.684, "gallop.wav", 0.28, 0.25),
    (445.884, "whoosh.wav", 0.28, 0.25),
    (449.584, "punch.wav", 0.28, 0.25),
    (452.584, "tick.wav", 0.22, 0.15),
    (454.784, "ui_blip.wav", 0.22, 0.25),
    (457.977, "punch.wav", 0.26, 0.2),
    (460.334, "impact.wav", 0.28, 0.25),
    (464.034, "whoosh.wav", 0.28, 0.3),
    (466.234, "gallop.wav", 0.28, 0.4),
    (469.234, "impact.wav", 0.28, 0.24),
    (471.434, "glitch.wav", 0.28, 0.25),
    (474.517, "impact.wav", 0.28, 0.24),
    (476.984, "rein_snap.wav", 0.28, 0.25),
    (480.089, "gallop.wav", 0.28, 0.25),
    (482.884, "whoosh.wav", 0.28, 0.25),
    (485.884, "punch.wav", 0.26, 0.2),
    (488.084, "impact.wav", 0.28, 0.24),
    (491.026, "punch.wav", 0.28, 0.25),
    (493.634, "tick.wav", 0.22, 0.15),
    (497.334, "ui_blip.wav", 0.22, 0.1),
    (499.314, "whoosh.wav", 0.24, 0.3),
    (501.734, "ui_blip.wav", 0.22, 0.25),
    (504.734, "impact.wav", 0.28, 0.25),
    (507.63, "glitch.wav", 0.28, 0.25),
    (510.284, "rein_snap.wav", 0.28, 0.25),
    (513.166, "impact.wav", 0.28, 0.24),
    (516.184, "gallop.wav", 0.28, 0.25),
    (518.833, "whoosh.wav", 0.28, 0.25),
    (521.483, "punch.wav", 0.28, 0.25),
    (524.132, "tick.wav", 0.22, 0.15),
    (526.932, "punch.wav", 0.26, 0.2),
    (529.132, "ui_blip.wav", 0.22, 0.25),
    (532.132, "ui_blip.wav", 0.22, 0.1),
    (534.162, "whoosh.wav", 0.24, 0.3),
    (537.699, "ui_blip.wav", 0.22, 0.1),
    (540.582, "glitch.wav", 0.28, 0.25),
    (542.796, "rein_snap.wav", 0.28, 0.25),
    (545.782, "ui_blip.wav", 0.22, 0.1),
    (548.325, "gallop.wav", 0.28, 0.25),
    (551.332, "whoosh.wav", 0.28, 0.25),
    (553.532, "impact.wav", 0.28, 0.24),
    (557.232, "punch.wav", 0.28, 0.25),
    (559.972, "tick.wav", 0.22, 0.15),
    (562.432, "ui_blip.wav", 0.22, 0.25),
    (565.28, "impact.wav", 0.28, 0.25),
    (567.982, "punch.wav", 0.26, 0.2),
    (570.182, "glitch.wav", 0.28, 0.25),
    (573.532, "rein_snap.wav", 0.28, 0.25),
    (577.151, "gallop.wav", 0.28, 0.25),
    (579.432, "gallop.wav", 0.28, 0.4),
    (582.432, "whoosh.wav", 0.28, 0.25),
    (584.632, "punch.wav", 0.28, 0.25),
    (587.59, "punch.wav", 0.26, 0.2),
    (590.182, "tick.wav", 0.22, 0.15),
    (593.613, "whoosh.wav", 0.28, 0.3),
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
          <div class="kicker">隐喻对照 · 第03章</div>
          <div class="vs-grid">
            <div class="vpanel"><h3>锤子 Bash</h3><p>万能命令<br/>啥都能砸 · 啥都不精</p></div>
            <div class="vpanel r"><h3>双手专工具</h3><p>Read · Edit · Grep<br/>专门化 · 可编排 · 有护栏</p></div>
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
            "name": "ch03-long-v2",
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
        json.dumps({"id": "ch03-long-v2", "name": "ch03-long-v2", "duration": TOTAL}, indent=2),
        encoding="utf-8",
    )
    print("ch03 dense v2 assembled TOTAL", TOTAL, "blocks", len(BLOCKS), "sfx", len(SFX_CUE), "caps", len(TRANS))


if __name__ == "__main__":
    main()
