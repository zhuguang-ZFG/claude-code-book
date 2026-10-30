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
    {
        "id": "b01_hook",
        "title": "开场钩子",
        "start": 0.0,
        "end": 43.896,
        "huashu": [("01_hook_glue.mp4", 8.0, 7.0)],
        "beats": [
        (0.0, "series", "驭者·Agent Harness", "第 01 讲 · 打地基"),
        (5.0, "cards", "马车 = 系统", "缰绳 = Harness · 骏马 = 模型"),
        (7.8, "card", "第 01 讲先打地基：为什么做 Ag", "二零二三年前后，大家跟大模型打交道多半是这样"),
        (12.0, "contrast", "Chatbot 时代", "人当系统胶水"),
        (16.0, "stamp", "二零二三年前后，大家跟大", "记下这一点"),
        (20.0, "contrast", "Agent 时代", "自己编排工具调用"),
        (26.0, "pause", "为什么不能只包一层 API？", "先停 3 秒：边界 · 失败 · 权限谁来管？"),
        (32.0, "quiz", "人在 Chatbot 时代更像什么？", "A 驭者  ·  B 系统胶水  ·  C 旁观者"),
        (38.0, "stamp", "御者 · 你来握缰", "模型是马，Harness 是缰绳和鞍具"),
        ],
    },
    {
        "id": "b02_paradigm",
        "title": "§1.1 范式转移",
        "start": 43.896,
        "end": 265.32,
        "huashu": [("02_llm_roles.mp4", 50.0, 7.0), ("03_six_challenges.mp4", 120.0, 7.5), ("04_harness_def.mp4", 200.0, 7.0), ("02_llm_roles.mp4", 90.0, 6.5), ("03_six_challenges.mp4", 160.0, 6.5)],
        "beats": [
        (0.0, "section", "§1.1 范式转移", "LLM：对话伙伴 → 推理引擎"),
        (4.0, "card", "Agent 会自己决定调哪个工具、传", "LLM 的价值不再只是生成段落，而是当推理引"),
        (7.861, "stamp", "LLM 的价值不再只是生", "记下这一点"),
        (12.0, "card", "从 Chatbot 到 Agent", "工具调用打开边界"),
        (16.4, "card", "可工具一多、失败一多、权限一乱，简单", "这就是本集要讲的 Agent Harness"),
        (20.8, "chariot", "驭者隐喻", "模型是马 · Harness 是缰绳和鞍具"),
        (25.867, "card", "这就是本集要讲的 Agent Har", "先从范式转移说起"),
        (31.948, "card", "先从范式转移说起", "书稿第一节就叫：从 Chatbot 到 Ag"),
        (36.0, "card", "Tool Use", "打开边界 · 工程挑战随之而来"),
        (40.75, "pause", "停一下 · 过去，LLM 更像被", "跟 VO 对齐想一拍"),
        (46.834, "card", "知识停在训练截止日，推理困在上下文窗", "有了工具调用 Tool Use，边界被打开："),
        (50.25, "stamp", "知识停在训练截止日，推理", "记下这一点"),
        (55.0, "card", "六大工程挑战", "流式 · 权限 · 上下文 · 恢复 · 持久化 · 扩展"),
        (60.75, "card", "每一次工具调用，都是跟真实世界握一次", "那个困在房间里的朋友，现在有了电话、机械手臂"),
        (66.5, "card", "每一次工具调用，都是跟真实世界握一次", "那个困在房间里的朋友，现在有了电话、机械手臂"),
        (72.25, "card", "那个困在房间里的朋友，现在有了电话、", "参谋和指挥官的差别也在这里"),
        (78.0, "card", "简单封装的幻觉", "while 循环假设理想世界"),
        (82.667, "pause", "停一下 · 参谋的指令要传令兵逐", "跟 VO 对齐想一拍"),
        (86.542, "card", "当模型从「回答问题的人」变成「决定调", "但握手一多，工程问题就来了——而且已经不是模"),
        (92.0, "quiz", "简单 while(true) 调用 API，够不够？", "猜一猜：理想世界假设会在哪一步碎掉？"),
        (96.82, "stamp", "但握手一多，工程问题就来", "记下这一点"),
        (100.0, "warn", "反模式", "裸 while(true){ callAPI }"),
        (103.948, "card", "书稿列了六大挑战", "第一，工具注册与发现：谁管注册表，模型怎么知"),
        (110.0, "card", "第一，工具注册与发现：谁管注册表，模", "第二，参数校验：类型错了、缺字段、越界，校验"),
        (113.945, "card", "第二，参数校验：类型错了、缺字段、越", "第三，权限管控：模型可能要求执行高危命令，什"),
        (120.0, "card", "真正的 Harness", "正面硬刚失败 · 权限 · 上下文"),
        (126.584, "pause", "停一下 · 第四，错误恢复：超时", "跟 VO 对齐想一拍"),
        (130.0, "card", "第四，错误恢复：超时、格式不对、工具", "第五，状态一致性：多轮操作同一资源，怎么避免"),
        (134.236, "stamp", "第五，状态一致性：多轮操", "记下这一点"),
        (140.903, "card", "第六，并发与调度：哪些能并行读文件，", "这六个问题，一起催生了 Agent Harn"),
        (145.0, "card", "统一框架", "把散落问题系统收进来"),
        (151.444, "card", "很多人以为 Harness 就是 A", "听起来够用，其实默认了理想世界——永不超时、"),
        (155.0, "card", "很多人以为 Harness 就是 A", "听起来够用，其实默认了理想世界——永不超时、"),
        (160.0, "pause", "停一下 · 听起来够用，其实默认", "跟 VO 对齐想一拍"),
        (165.0, "card", "听起来够用，其实默认了理想世界——永", "生产里这些假设会被逐个打破"),
        (170.0, "card", "Agent Harness", "运行时框架，不是外套壳"),
        (175.564, "stamp", "真正的 Harness ", "记下这一点"),
        (179.352, "card", "流式输出怎么边想边画，还不把主线程卡", "每一项都够单独开工程专题"),
        (185.0, "card", "流式输出怎么边想边画，还不把主线程卡", "每一项都够单独开工程专题"),
        (190.0, "card", "流式输出怎么边想边画，还不把主线程卡", "每一项都够单独开工程专题"),
        (195.0, "card", "定义落地", "安全 · 可靠 · 高效与外部交互"),
        (200.0, "pause", "停一下 · 每一项都够单独开工程", "跟 VO 对齐想一拍"),
        (205.0, "card", "每一项都够单独开工程专题", "Harness 的价值，是用统一框架系统地收"),
        (210.0, "stamp", "每一项都够单独开工程专题", "记下这一点"),
        (215.0, "section", "准备看架构", "从示例项目读五模块骨架"),
        ],
    },
    {
        "id": "b03_arch",
        "title": "§1.2 全景架构",
        "start": 265.32,
        "end": 568.632,
        "huashu": [("05_arch_layers.mp4", 80.0, 7.5), ("06_tech_stack.mp4", 180.0, 7.0), ("05_arch_layers.mp4", 120.0, 6.5), ("06_tech_stack.mp4", 220.0, 6.5)],
        "beats": [
        (0.0, "vs_auto", "遥控器 vs 自动驾驶", "简单封装 vs Agent Harness"),
        (5.333, "card", "Agent Harness 是整辆能", "一句话定义：Agent Harness 是围"),
        (10.667, "stamp", "Agent Harnes", "记下这一点"),
        (16.0, "pause", "你的封装更像哪边？", "遥控器：按一下动一下 · 自动驾驶：自主规划与边界"),
        (22.0, "section", "§1.2 全景架构", "从 Copilot 到 Claude Code / MCP"),
        (26.5, "card", "反模式警告也原样提醒你：如果核心循环", "流式、上下文、错误恢复想清楚了吗？"),
        (31.876, "card", "反模式警告也原样提醒你：如果核心循环", "流式、上下文、错误恢复想清楚了吗？"),
        (35.5, "card", "反模式警告也原样提醒你：如果核心循环", "流式、上下文、错误恢复想清楚了吗？"),
        (40.0, "number", "1,884", "个 TypeScript 文件"),
        (45.845, "pause", "停一下 · 没想清楚，你需要的不", "跟 VO 对齐想一拍"),
        (50.0, "card", "概念有了，用 Claude Code", "先从宏观尺度看代码库——数字本身就有信息量"),
        (55.0, "number", "512,664", "行代码"),
        (60.82, "stamp", "时间线很清楚", "记下这一点"),
        (65.0, "card", "二零二一年六月 Copilot 技术", "二零二四年前后，Devin、Cursor A"),
        (70.0, "card", "二零二一年六月 Copilot 技术", "二零二四年前后，Devin、Cursor A"),
        (75.0, "card", "不是炫耀体量", "复杂度来自工程现实"),
        (80.0, "card", "二零二四年前后，Devin、Curs", "二零二五年 Claude Code 以终端原"),
        (85.472, "pause", "停一下 · 二零二四年前后，De", "跟 VO 对齐想一拍"),
        (90.0, "card", "二零二五年 Claude Code ", "规律只有一句：演进方向始终是给 LLM 更多"),
        (95.0, "stamp", "二零二五年 Claude", "记下这一点"),
        (100.0, "layers", "五模块骨架", "Entry → QueryEngine → Loop → Tools → Ext"),
        (104.597, "card", "规律只有一句：演进方向始终是给 LL", "Harness 是这方向在架构层面的必然产物"),
        (110.0, "card", "规律只有一句：演进方向始终是给 LL", "Harness 是这方向在架构层面的必然产物"),
        (115.0, "card", "Harness 是这方向在架构层面的", "再看体量"),
        (120.0, "pause", "停一下 · Harness 是这", "跟 VO 对齐想一拍"),
        (124.213, "card", "src 里有,一千八百八十四,个 T", "一个终端工具，体量接近 VS Code 核心"),
        (130.0, "card", "Entry", "启动 · 配置 · 会话入口"),
        (135.0, "stamp", "一个终端工具，体量接近 ", "记下这一点"),
        (140.0, "card", "这说明可靠 Agent 的工程复杂度", "它不是臃肿，而是高度模块化：工具独立、子系统"),
        (143.546, "card", "它不是臃肿，而是高度模块化：工具独立", "模块化，正是 Harness 可维护性的关键"),
        (149.852, "card", "模块化，正是 Harness 可维护", "架构从上到下几层"),
        (155.0, "card", "QueryEngine", "请求编排与流式输出"),
        (160.0, "pause", "停一下 · 查询引擎 Query", "跟 VO 对齐想一拍"),
        (165.0, "card", "查询引擎 QueryEngine：会", "心脏是对话主循环，一个 AsyncGener"),
        (170.0, "stamp", "心脏是对话主循环，一个 ", "记下这一点"),
        (173.832, "card", "心脏是对话主循环，一个 AsyncG", "旁边是工具系统——约五十五个工具、编排与并发"),
        (180.0, "card", "Loop", "主循环 · 工具调用回合"),
        (186.124, "card", "旁边是工具系统——约五十五个工具、编", "主循环是心脏，驱动数据在子系统之间流转"),
        (190.0, "card", "旁边是工具系统——约五十五个工具、编", "主循环是心脏，驱动数据在子系统之间流转"),
        (195.0, "pause", "停一下 · 主循环是心脏，驱动数", "跟 VO 对齐想一拍"),
        (200.0, "card", "主循环是心脏，驱动数据在子系统之间流", "技术栈也很克制"),
        (205.0, "card", "Tools", "权限四阶段 · 55 个工具"),
        (208.651, "stamp", "运行时 Bun，图启动快", "记下这一点"),
        (215.0, "card", "终端 UI 用 React 加 In", "CLI 用 Commander.js"),
        (220.0, "card", "CLI 用 Commander.js", "校验用 Zod 第四版：运行时类型安全，还能"),
        (224.095, "card", "CLI 用 Commander.js", "校验用 Zod 第四版：运行时类型安全，还能"),
        (230.0, "pause", "停一下 · 校验用 Zod 第四", "跟 VO 对齐想一拍"),
        (235.0, "stack", "技术栈", "Bun · React+Ink · Zod v4 · SDK"),
        (240.0, "card", "LLM 侧用 Anthropic 官", "Zod 尤其关键：模型参数不可预测，校验就是"),
        (245.0, "stamp", "Zod 尤其关键：模型参", "记下这一点"),
        (248.581, "card", "启动路径上，性能探针先挂，可并行的预", "再补一层读架构的方法"),
        (255.0, "card", "再补一层读架构的方法", "从上往下看：入口解决「怎么进来」，Query"),
        (261.412, "card", "再补一层读架构的方法", "从上往下看：入口解决「怎么进来」，Query"),
        (265.0, "card", "可维护性", "模块化是 Harness 的关键保障"),
        ],
    },
    {
        "id": "b04_principles",
        "title": "§1.3 五大原则",
        "start": 568.632,
        "end": 910.464,
        "huashu": [("07_p_async.mp4", 20.0, 7.0), ("08_p_security.mp4", 90.0, 7.5), ("09_p_cache.mp4", 160.0, 7.0), ("10_p_progressive.mp4", 230.0, 7.5), ("11_p_immutable.mp4", 300.0, 7.0), ("07_p_async.mp4", 60.0, 6.5), ("08_p_security.mp4", 130.0, 6.5), ("09_p_cache.mp4", 200.0, 6.5), ("10_p_progressive.mp4", 270.0, 6.5)],
        "beats": [
        (0.0, "section", "§1.3 五大原则", "红线，不是口号"),
        (4.0, "card", "权限四阶段也值得先记住名字：可见性过", "后文原则二会展开，这里先当骨架钉子——全景图"),
        (8.0, "quiz", "五大原则里，哪条最容易被当成口号？", "流式 · 安全 · 缓存 · 扩展 · 不可变 —— 先选一条"),
        (13.0, "stamp", "后文原则二会展开，这里先", "记下这一点"),
        (18.0, "p", "1 · 异步流式优先", "Async Generator First"),
        (23.5, "card", "你后面读源码时，先问「这一段落在哪一", "主循环每轮大致七步：组请求（系统 Promp"),
        (27.777, "card", "你后面读源码时，先问「这一段落在哪一", "主循环每轮大致七步：组请求（系统 Promp"),
        (34.732, "card", "主循环每轮大致七步：组请求（系统 P", "用生成器而不是回调，上层才能 for awa"),
        (40.0, "card", "流式体验", "首包延迟 · 可取消 · 背压"),
        (45.0, "pause", "停一下 · 用生成器而不是回调，", "跟 VO 对齐想一拍"),
        (50.909, "card", "用生成器而不是回调，上层才能 for", "跨轮状态用不可变对象整体替换"),
        (55.0, "stamp", "跨轮状态用不可变对象整体", "记下这一点"),
        (60.0, "card", "跨轮状态用不可变对象整体替换", "五个关键模块——入口、QueryEngine"),
        (65.0, "card", "五个关键模块——入口、QueryEn", "注册中心还是单一事实来源：条件注册、延迟加载"),
        (70.0, "p", "2 · 安全边界内嵌", "Security at the Perimeter"),
        (75.0, "card", "注册中心还是单一事实来源：条件注册、", "细节后面几章再拆"),
        (80.0, "pause", "停一下 · 细节后面几章再拆", "跟 VO 对齐想一拍"),
        (86.068, "card", "架构背后是五条互相支撑的原则", "每条都在回答：为什么不选更简单的做法；不这样"),
        (89.676, "stamp", "每条都在回答：为什么不选", "记下这一点"),
        (95.212, "card", "原则一：异步流式优先，Async G", "传统调用是请求—响应：发完 Prompt 干"),
        (100.0, "card", "权限四阶段", "声明 · 校验 · 执行 · 审计"),
        (105.125, "card", "Agent 不是这样——一轮用户请求", "生成器刚好匹配：用 yield 增量吐事件；"),
        (110.0, "card", "生成器刚好匹配：用 yield 增量", "回调易变地狱；Promise 链好看些，但用"),
        (114.737, "pause", "停一下 · 生成器刚好匹配：用 ", "跟 VO 对齐想一拍"),
        (120.0, "card", "生成器刚好匹配：用 yield 增量", "回调易变地狱；Promise 链好看些，但用"),
        (125.5, "stamp", "回调易变地狱；Promi", "记下这一点"),
        (130.0, "p", "3 · 缓存感知设计", "Cache-Aware Architecture"),
        (135.0, "card", "同时要流式、可取消、类型安全——As", "原则二：安全边界内嵌，Security at"),
        (140.0, "card", "同时要流式、可取消、类型安全——As", "原则二：安全边界内嵌，Security at"),
        (144.484, "card", "原则二：安全边界内嵌，Securit", "权限不是外挂，是管线正中的检查点"),
        (149.272, "pause", "停一下 · 权限不是外挂，是管线", "跟 VO 对齐想一拍"),
        (155.0, "card", "先过滤工具可见性，模型看不见禁用工具", "纵深防御，没有银弹，但每层都能独立短路"),
        (160.0, "card", "上下文成本", "前缀稳定 · 复用命中"),
        (165.833, "stamp", "纵深防御，没有银弹，但每", "记下这一点"),
        (171.667, "card", "纵深防御，没有银弹，但每层都能独立短", "白名单不够用：安全性看上下文——删 node"),
        (177.5, "card", "白名单不够用：安全性看上下文——删 ", "原则三：缓存感知，Cache-Aware"),
        (183.964, "card", "原则三：缓存感知，Cache-Awa", "Prompt Caching 能砍成本和延迟"),
        (190.614, "pause", "停一下 · 系统 Prompt ", "跟 VO 对齐想一拍"),
        (195.0, "p", "4 · 渐进式能力扩展", "Tool → Skill → Plugin → MCP"),
        (200.833, "card", "不关心缓存，每次重拼 Prompt，", "原则四：渐进式能力扩展，Progressiv"),
        (206.667, "stamp", "不关心缓存，每次重拼 P", "记下这一点"),
        (212.788, "card", "原则四：渐进式能力扩展，Progre", "四级阶梯，从内建到外部：Tool 实现类型接"),
        (217.66, "card", "四级阶梯，从内建到外部：Tool 实", "简单需求别逼人搭服务器，复杂集成也别逼人改核"),
        (224.167, "card", "四级阶梯，从内建到外部：Tool 实", "简单需求别逼人搭服务器，复杂集成也别逼人改核"),
        (230.0, "card", "扩展阶梯", "先工具，再技能，再协议"),
        (235.833, "pause", "停一下 · 简单需求别逼人搭服务", "跟 VO 对齐想一拍"),
        (241.667, "card", "简单需求别逼人搭服务器，复杂集成也别", "只有 Tool，生态长不大；只留 MCP，小"),
        (247.5, "stamp", "只有 Tool，生态长不", "记下这一点"),
        (253.333, "card", "让每类贡献者站在合适抽象层上工作，扩", "原则五：不可变状态流转，Immutable "),
        (259.167, "card", "原则五：不可变状态流转，Immuta", "更新走 updater，基于 prev 算 "),
        (265.0, "p", "5 · 不可变状态流转", "Immutable State Flow"),
        (270.833, "card", "对话里跨轮状态整体替换，每轮用只读快", "可变对象在并发和子智能体场景下，容易读到改一"),
        (276.667, "pause", "停一下 · 可变对象在并发和子智", "跟 VO 对齐想一拍"),
        (282.5, "card", "可变对象在并发和子智能体场景下，容易", "不可变，是可预测、可回滚、可安全传快照的底气"),
        (288.333, "stamp", "不可变，是可预测、可回滚", "记下这一点"),
        (294.167, "card", "把五条再钉一遍，避免只记口号", "流式原则回答的是交互形态：Agent 不是一"),
        (300.0, "card", "状态可追溯", "回合快照 · 恢复点"),
        (305.0, "card", "安全原则回答的是信任边界：模型可以提", "缓存原则回答的是经济账：同一段系统提示词反复"),
        (309.81, "card", "安全原则回答的是信任边界：模型可以提", "缓存原则回答的是经济账：同一段系统提示词反复"),
        (315.0, "pause", "停一下 · 缓存原则回答的是经济", "跟 VO 对齐想一拍"),
        (320.0, "card", "缓存原则回答的是经济账：同一段系统提", "扩展原则回答的是生态：内部贡献者和外部生态要"),
        (326.338, "stamp", "扩展原则回答的是生态：内", "记下这一点"),
        (330.0, "section", "原则合在一起", "构成 Harness 的工程红线"),
        ],
    },
    {
        "id": "b05_practice",
        "title": "实战练习速览",
        "start": 910.464,
        "end": 1056.912,
        "huashu": [("12_doctor_flow.mp4", 40.0, 7.0), ("12_doctor_flow.mp4", 80.0, 6.5)],
        "beats": [
        (0.0, "section", "实战练习速览", "动手验证 Harness"),
        (5.0, "card", "没有流式，权限询问弹窗很难嵌进实时对", "所以书稿不把原则当鸡汤，而当成贯穿后文的红线"),
        (10.0, "pause", "动手前先问自己", "你会先用哪条命令确认环境就绪？"),
        (14.0, "stamp", "所以书稿不把原则当鸡汤，", "记下这一点"),
        (18.0, "code", "npm i -g @anthropic-ai/claude-code", "安装 CLI"),
        (23.667, "card", "所以书稿不把原则当鸡汤，而当成贯穿后", "五条连起来：流式解决怎么边跑边展示，安全解决"),
        (29.333, "card", "五条连起来：流式解决怎么边跑边展示，", "后面章节里，你几乎总能把「为什么这样设计」追"),
        (35.0, "code", "claude --version", "确认环境就绪"),
        (40.0, "card", "五条连起来：流式解决怎么边跑边展示，", "后面章节里，你几乎总能把「为什么这样设计」追"),
        (45.0, "pause", "停一下 · 后面章节里，你几乎总", "跟 VO 对齐想一拍"),
        (49.817, "card", "后面章节里，你几乎总能把「为什么这样", "理论先放这儿"),
        (55.0, "code", "/doctor", "环境 · 权限 · MCP · API · 文件系统"),
        (60.0, "stamp", "机器上有 Node 十八", "记下这一点"),
        (65.0, "card", "机器上有 Node 十八加或 Bun", "项目里也可用 npx 或本地安装钉版本，避免"),
        (70.348, "card", "项目里也可用 npx 或本地安装钉版", "进任意项目启动 Claude Code，输入"),
        (75.0, "card", "进任意项目启动 Claude Cod", "它会查环境、权限配置、MCP 连接、API "),
        (80.0, "flow", "一次工具调用", "思考 → GlobTool → 回复"),
        (85.0, "pause", "停一下 · 它会查环境、权限配置", "跟 VO 对齐想一拍"),
        (88.527, "card", "观察方式比结果更重要：检查是一项项冒", "有的检查会请求确认，说明诊断也走权限管线"),
        (95.0, "stamp", "有的检查会请求确认，说明", "记下这一点"),
        (99.291, "card", "有的检查会请求确认，说明诊断也走权限", "再发一句简单请求，比如列出当前目录所有 Ty"),
        (104.38, "card", "再发一句简单请求，比如列出当前目录所", "看三阶段：思考里说明打算用哪个工具；调用阶段"),
        (110.0, "card", "观察 Harness", "权限提示 · 流式输出 · 工具结果回流"),
        (115.0, "card", "看三阶段：思考里说明打算用哪个工具；", "心里对照主循环：哪步在 QueryEngin"),
        (120.0, "pause", "停一下 · 心里对照主循环：哪步", "跟 VO 对齐想一拍"),
        (125.0, "card", "心里对照主循环：哪步在 QueryE", "顺带想三问：哪些工具并发安全；按 Ctrl+"),
        (129.377, "stamp", "顺带想三问：哪些工具并发", "记下这一点"),
        (135.0, "section", "练习目的", "亲手摸到运行时边界"),
        ],
    },
    {
        "id": "b06_outro",
        "title": "总结 + 片尾",
        "start": 1056.912,
        "end": 1148.352,
        "huashu": [("13_outro.mp4", 5.0, 7.0), ("13_outro.mp4", 45.0, 6.5)],
        "beats": [
        (0.0, "section", "本讲收束", "四句记住"),
        (4.0, "card", "第一，范式已转移：助手从对话伙伴变成", "第二，Harness 是复杂工程系统：五十多"),
        (8.0, "quiz", "合上书之前", "用一句话：Harness 到底解决什么问题？"),
        (12.0, "stamp", "第二，Harness 是", "记下这一点"),
        (16.0, "sum", "范式已转移", "助手 → 自主智能体 · 地基是 Harness"),
        (21.333, "card", "第二，Harness 是复杂工程系统", "第三，五模块搭起骨架：入口、查询引擎、对话循"),
        (26.667, "card", "第三，五模块搭起骨架：入口、查询引擎", "第四，五原则是红线：异步流式优先、安全边界内"),
        (32.0, "sum", "Harness 是工程系统", "流式 · 权限 · 上下文 · 恢复 · 持久化"),
        (37.0, "card", "第三，五模块搭起骨架：入口、查询引擎", "第四，五原则是红线：异步流式优先、安全边界内"),
        (42.0, "pause", "停一下 · 第四，五原则是红线：", "跟 VO 对齐想一拍"),
        (47.0, "card", "第四，五原则是红线：异步流式优先、安", "遇到「为什么这样设计」，答案几乎都能追回其中"),
        (52.0, "sum", "五模块是骨架", "五原则是红线"),
        (57.333, "stamp", "遇到「为什么这样设计」，", "记下这一点"),
        (62.667, "card", "遇到「为什么这样设计」，答案几乎都能", "下一讲钻进对话主循环那个 AsyncGene"),
        (68.0, "next", "第 02 讲预告", "对话主循环 AsyncGenerator"),
        (72.292, "card", "本系列基于开源书稿整理而成，系列名称", "完整目录、各章进度和原书链接放在简介置顶；请"),
        (78.914, "card", "完整目录、各章进度和原书链接放在简介", "第 01 讲到这里，我们下期继续"),
        (82.0, "credit", "基于开源书稿", "驭者·Agent Harness · 小电讲电路"),
        ],
    },
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
    (0.02, "whoosh.wav", 0.28, 0.3),
    (5.02, "punch.wav", 0.28, 0.2),
    (7.82, "tick.wav", 0.22, 0.1),
    (12.02, "whoosh.wav", 0.28, 0.3),
    (16.02, "impact.wav", 0.28, 0.24),
    (20.02, "whoosh.wav", 0.28, 0.3),
    (26.02, "ui_blip.wav", 0.22, 0.1),
    (32.02, "ui_blip.wav", 0.22, 0.1),
    (38.02, "impact.wav", 0.28, 0.24),
    (43.916, "ui_blip.wav", 0.22, 0.1),
    (47.916, "impact.wav", 0.28, 0.24),
    (51.777, "impact.wav", 0.28, 0.24),
    (55.916, "glitch.wav", 0.28, 0.22),
    (60.316, "rein_snap.wav", 0.28, 0.14),
    (64.716, "gallop.wav", 0.28, 0.4),
    (69.783, "gallop.wav", 0.28, 0.4),
    (75.864, "whoosh.wav", 0.28, 0.3),
    (79.916, "punch.wav", 0.28, 0.2),
    (84.666, "ui_blip.wav", 0.22, 0.1),
    (90.75, "tick.wav", 0.22, 0.1),
    (94.166, "impact.wav", 0.28, 0.24),
    (98.916, "ui_blip.wav", 0.22, 0.1),
    (104.666, "impact.wav", 0.28, 0.24),
    (110.416, "glitch.wav", 0.28, 0.22),
    (116.166, "rein_snap.wav", 0.28, 0.14),
    (121.916, "gallop.wav", 0.28, 0.4),
    (126.583, "ui_blip.wav", 0.22, 0.1),
    (130.458, "whoosh.wav", 0.28, 0.3),
    (135.916, "ui_blip.wav", 0.22, 0.1),
    (140.736, "impact.wav", 0.28, 0.24),
    (143.916, "impact.wav", 0.28, 0.24),
    (147.864, "punch.wav", 0.28, 0.2),
    (153.916, "tick.wav", 0.22, 0.1),
    (157.861, "ui_blip.wav", 0.22, 0.1),
    (163.916, "impact.wav", 0.28, 0.24),
    (170.5, "ui_blip.wav", 0.22, 0.1),
    (173.916, "glitch.wav", 0.28, 0.22),
    (178.152, "impact.wav", 0.28, 0.24),
    (184.819, "rein_snap.wav", 0.28, 0.14),
    (188.916, "gallop.wav", 0.28, 0.4),
    (195.36, "whoosh.wav", 0.28, 0.3),
    (198.916, "punch.wav", 0.28, 0.2),
    (203.916, "ui_blip.wav", 0.22, 0.1),
    (208.916, "tick.wav", 0.22, 0.1),
    (213.916, "ui_blip.wav", 0.22, 0.1),
    (219.48, "impact.wav", 0.28, 0.24),
    (223.268, "impact.wav", 0.28, 0.24),
    (228.916, "glitch.wav", 0.28, 0.22),
    (233.916, "rein_snap.wav", 0.28, 0.14),
    (238.916, "gallop.wav", 0.28, 0.4),
    (243.916, "ui_blip.wav", 0.22, 0.1),
    (248.916, "whoosh.wav", 0.28, 0.3),
    (253.916, "impact.wav", 0.28, 0.24),
    (258.916, "punch.wav", 0.28, 0.2),
    (265.34, "whoosh.wav", 0.28, 0.3),
    (270.673, "tick.wav", 0.22, 0.1),
    (276.007, "impact.wav", 0.28, 0.24),
    (281.34, "ui_blip.wav", 0.22, 0.1),
    (287.34, "ui_blip.wav", 0.22, 0.1),
    (291.84, "impact.wav", 0.28, 0.24),
    (297.216, "glitch.wav", 0.28, 0.22),
    (300.84, "rein_snap.wav", 0.28, 0.14),
    (305.34, "gallop.wav", 0.28, 0.4),
    (311.185, "ui_blip.wav", 0.22, 0.1),
    (315.34, "whoosh.wav", 0.28, 0.3),
    (320.34, "punch.wav", 0.28, 0.2),
    (326.16, "impact.wav", 0.28, 0.24),
    (330.34, "tick.wav", 0.22, 0.1),
    (335.34, "ui_blip.wav", 0.22, 0.1),
    (340.34, "impact.wav", 0.28, 0.24),
    (345.34, "glitch.wav", 0.28, 0.22),
    (350.812, "ui_blip.wav", 0.22, 0.1),
    (355.34, "rein_snap.wav", 0.28, 0.14),
    (360.34, "impact.wav", 0.28, 0.24),
    (365.34, "gallop.wav", 0.28, 0.4),
    (369.937, "whoosh.wav", 0.28, 0.3),
    (375.34, "punch.wav", 0.28, 0.2),
    (380.34, "tick.wav", 0.22, 0.1),
    (385.34, "ui_blip.wav", 0.22, 0.1),
    (389.553, "ui_blip.wav", 0.22, 0.1),
    (395.34, "impact.wav", 0.28, 0.24),
    (400.34, "impact.wav", 0.28, 0.24),
    (405.34, "glitch.wav", 0.28, 0.22),
    (408.886, "rein_snap.wav", 0.28, 0.14),
    (415.192, "gallop.wav", 0.28, 0.4),
    (420.34, "whoosh.wav", 0.28, 0.3),
    (425.34, "ui_blip.wav", 0.22, 0.1),
    (430.34, "punch.wav", 0.28, 0.2),
    (435.34, "impact.wav", 0.28, 0.24),
    (439.172, "tick.wav", 0.22, 0.1),
    (445.34, "ui_blip.wav", 0.22, 0.1),
    (451.464, "impact.wav", 0.28, 0.24),
    (455.34, "glitch.wav", 0.28, 0.22),
    (460.34, "ui_blip.wav", 0.22, 0.1),
    (465.34, "rein_snap.wav", 0.28, 0.14),
    (470.34, "gallop.wav", 0.28, 0.4),
    (473.991, "impact.wav", 0.28, 0.24),
    (480.34, "whoosh.wav", 0.28, 0.3),
    (485.34, "punch.wav", 0.28, 0.2),
    (489.435, "tick.wav", 0.22, 0.1),
    (495.34, "ui_blip.wav", 0.22, 0.1),
    (500.34, "ui_blip.wav", 0.22, 0.1),
    (505.34, "impact.wav", 0.28, 0.24),
    (510.34, "impact.wav", 0.28, 0.24),
    (513.921, "glitch.wav", 0.28, 0.22),
    (520.34, "rein_snap.wav", 0.28, 0.14),
    (526.752, "gallop.wav", 0.28, 0.4),
    (530.34, "whoosh.wav", 0.28, 0.3),
    (568.652, "punch.wav", 0.28, 0.2),
    (572.652, "tick.wav", 0.22, 0.1),
    (576.652, "ui_blip.wav", 0.22, 0.1),
    (581.652, "impact.wav", 0.28, 0.24),
    (586.652, "ui_blip.wav", 0.22, 0.1),
    (592.152, "impact.wav", 0.28, 0.24),
    (596.429, "glitch.wav", 0.28, 0.22),
    (603.384, "rein_snap.wav", 0.28, 0.14),
    (608.652, "gallop.wav", 0.28, 0.4),
    (613.652, "ui_blip.wav", 0.22, 0.1),
    (619.561, "whoosh.wav", 0.28, 0.3),
    (623.652, "impact.wav", 0.28, 0.24),
    (628.652, "punch.wav", 0.28, 0.2),
    (633.652, "tick.wav", 0.22, 0.1),
    (638.652, "ui_blip.wav", 0.22, 0.1),
    (643.652, "impact.wav", 0.28, 0.24),
    (648.652, "ui_blip.wav", 0.22, 0.1),
    (654.72, "glitch.wav", 0.28, 0.22),
    (658.328, "impact.wav", 0.28, 0.24),
    (663.864, "rein_snap.wav", 0.28, 0.14),
    (668.652, "gallop.wav", 0.28, 0.4),
    (673.777, "whoosh.wav", 0.28, 0.3),
    (678.652, "punch.wav", 0.28, 0.2),
    (683.389, "ui_blip.wav", 0.22, 0.1),
    (688.652, "tick.wav", 0.22, 0.1),
    (694.152, "impact.wav", 0.28, 0.24),
    (698.652, "ui_blip.wav", 0.22, 0.1),
    (703.652, "impact.wav", 0.28, 0.24),
    (708.652, "glitch.wav", 0.28, 0.22),
    (713.136, "rein_snap.wav", 0.28, 0.14),
    (717.924, "ui_blip.wav", 0.22, 0.1),
    (723.652, "gallop.wav", 0.28, 0.4),
    (728.652, "whoosh.wav", 0.28, 0.3),
    (734.485, "impact.wav", 0.28, 0.24),
    (740.319, "punch.wav", 0.28, 0.2),
    (746.152, "tick.wav", 0.22, 0.1),
    (752.616, "ui_blip.wav", 0.22, 0.1),
    (759.266, "ui_blip.wav", 0.22, 0.1),
    (763.652, "impact.wav", 0.28, 0.24),
    (769.485, "glitch.wav", 0.28, 0.22),
    (775.319, "impact.wav", 0.28, 0.24),
    (781.44, "rein_snap.wav", 0.28, 0.14),
    (786.312, "gallop.wav", 0.28, 0.4),
    (792.819, "whoosh.wav", 0.28, 0.3),
    (798.652, "punch.wav", 0.28, 0.2),
    (804.485, "ui_blip.wav", 0.22, 0.1),
    (810.319, "tick.wav", 0.22, 0.1),
    (816.152, "impact.wav", 0.28, 0.24),
    (821.985, "ui_blip.wav", 0.22, 0.1),
    (827.819, "impact.wav", 0.28, 0.24),
    (833.652, "glitch.wav", 0.28, 0.22),
    (839.485, "rein_snap.wav", 0.28, 0.14),
    (845.319, "ui_blip.wav", 0.22, 0.1),
    (851.152, "gallop.wav", 0.28, 0.4),
    (856.985, "impact.wav", 0.28, 0.24),
    (862.819, "whoosh.wav", 0.28, 0.3),
    (868.652, "punch.wav", 0.28, 0.2),
    (873.652, "tick.wav", 0.22, 0.1),
    (878.462, "ui_blip.wav", 0.22, 0.1),
    (883.652, "ui_blip.wav", 0.22, 0.1),
    (888.652, "impact.wav", 0.28, 0.24),
    (894.99, "impact.wav", 0.28, 0.24),
    (898.652, "glitch.wav", 0.28, 0.22),
    (910.484, "rein_snap.wav", 0.28, 0.14),
    (915.484, "gallop.wav", 0.28, 0.4),
    (920.484, "ui_blip.wav", 0.22, 0.1),
    (924.484, "impact.wav", 0.28, 0.24),
    (928.484, "whoosh.wav", 0.28, 0.3),
    (934.151, "punch.wav", 0.28, 0.2),
    (939.817, "tick.wav", 0.22, 0.1),
    (945.484, "ui_blip.wav", 0.22, 0.1),
    (950.484, "impact.wav", 0.28, 0.24),
    (955.484, "ui_blip.wav", 0.22, 0.1),
    (960.301, "glitch.wav", 0.28, 0.22),
    (965.484, "rein_snap.wav", 0.28, 0.14),
    (970.484, "impact.wav", 0.28, 0.24),
    (975.484, "gallop.wav", 0.28, 0.4),
    (980.832, "whoosh.wav", 0.28, 0.3),
    (985.484, "punch.wav", 0.28, 0.2),
    (990.484, "tick.wav", 0.22, 0.1),
    (995.484, "ui_blip.wav", 0.22, 0.1),
    (999.011, "ui_blip.wav", 0.22, 0.1),
    (1005.484, "impact.wav", 0.28, 0.24),
    (1009.775, "impact.wav", 0.28, 0.24),
    (1014.864, "glitch.wav", 0.28, 0.22),
    (1020.484, "rein_snap.wav", 0.28, 0.14),
    (1025.484, "gallop.wav", 0.28, 0.4),
    (1030.484, "ui_blip.wav", 0.22, 0.1),
    (1035.484, "whoosh.wav", 0.28, 0.3),
    (1039.861, "impact.wav", 0.28, 0.24),
    (1045.484, "punch.wav", 0.28, 0.2),
    (1056.932, "tick.wav", 0.22, 0.1),
    (1060.932, "ui_blip.wav", 0.22, 0.1),
    (1064.932, "ui_blip.wav", 0.22, 0.1),
    (1068.932, "impact.wav", 0.28, 0.24),
    (1072.932, "impact.wav", 0.28, 0.24),
    (1078.265, "glitch.wav", 0.28, 0.22),
    (1083.599, "rein_snap.wav", 0.28, 0.14),
    (1088.932, "gallop.wav", 0.28, 0.4),
    (1093.932, "whoosh.wav", 0.28, 0.3),
    (1098.932, "ui_blip.wav", 0.22, 0.1),
    (1103.932, "punch.wav", 0.28, 0.2),
    (1108.932, "tick.wav", 0.22, 0.1),
    (1114.265, "impact.wav", 0.28, 0.24),
    (1119.599, "ui_blip.wav", 0.22, 0.1),
    (1124.932, "impact.wav", 0.28, 0.24),
    (1129.224, "glitch.wav", 0.28, 0.22),
    (1135.846, "rein_snap.wav", 0.28, 0.14),
    (1138.932, "gallop.wav", 0.28, 0.4),
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
    print("META_WARN_TOTAL", total_warn)  # scrub only
    print("DONE densify v4 project ready")


if __name__ == "__main__":
    main()
