# 附录 B：GitHub 资源与延伸阅读

下面的链接固定在写入时的提交或页面，方便你核对当时看到的版本。它们不是“最佳工具”排名，只是几种不同形态的实现，适合带着具体问题去读。

## B.1 术语与争论

- Andrej Karpathy 的原帖：<https://x.com/karpathy/status/1886192184808149383>。Vibe coding 一词在 2025 年 2 月从这里扩散；原帖是一种姿态描述，不是工程规范。
- Simon Willison 的摘录与评论：<https://simonwillison.net/2025/Feb/6/andrej-karpathy/>。适合看这个词最初被怎样理解。

读这两条时，注意区分“个人实验的写法”和“团队交付的标准”。本书的窄定义与它们不完全相同，差异在第 1 章写明。

## B.2 可以运行的 Agent 与工具

| 项目 | 固定版本入口 | 带着什么问题去读 |
| --- | --- | --- |
| Codex CLI | <https://github.com/openai/codex/tree/6aaac694803004a63c6f393d153c96d22521a6b9> | 命令执行、审批与沙箱怎样分层 |
| Gemini CLI | <https://github.com/google-gemini/gemini-cli/tree/970413207732f5d4d8c50540c7fc359c44fdaaf2> | 终端 Agent 的工具注册与交互 |
| OpenHands | <https://github.com/OpenHands/OpenHands/tree/b968abef4779eb47f5843c975a60c7b4ccf49886> | 一个完整的 Agent 运行时如何组织 |
| oh-my-pi | <https://github.com/can1357/oh-my-pi/tree/3fedf8d53267e32a6d7521ce725fdcc4a36fdc67> | 终端 Agent 的权限模式与子命令 |
| Playwright MCP | <https://github.com/microsoft/playwright-mcp/tree/f183dad4a52965583e3cc1d59b88cdc279e2e57d> | 浏览器操作怎样作为工具暴露给模型 |
| Claude Code Templates | <https://github.com/davila7/claude-code-templates/tree/ad49b11922ea15f936e96f49f782e59ed8594342> | 项目规则、命令与配置的模板长什么样 |

这些项目各有自己的许可证与安装方式。读代码前先看 `LICENSE` 与 README，不要默认可以复制片段进你的项目。本书只做链接引用，不转载源码。

## B.3 社区开源书籍

下面五本不是工具，而是可以按章节读完的教材。链接固定在 2026-11-15 读取到的提交；许可证各不相同，本书只引用章节结构、概念和检查项，不复制或改写正文。

| 书 | 固定版本入口 | 许可证 | 带着什么问题去读 |
| --- | --- | --- | --- |
| The State of Vibe Coding | <https://github.com/oksure/vibecoding/tree/4475839a477e92551145df98a8203b53c0e23d2e> | CC BY-SA 4.0（正文）/ MIT（工具） | Vibe coding 的能力边界、评估方法和团队工作流 |
| Agentic Software Engineering | <https://github.com/awsm-research/agentic-swe-book/tree/3650237821ee96391786c327e3855e7200b7df26> | CC BY-NC-ND 4.0（书）/ MIT（代码） | AI 原生工程的需求、设计、测试、评审与安全 |
| The Missing Semester | <https://github.com/missing-semester/missing-semester/tree/1d695c94ccafdce3f06d6b9dfe3e6f106097693a> | CC BY-NC-SA 4.0 | 终端、版本控制、调试和脚本基础 |
| Pro Git | <https://github.com/progit/progit2/tree/a013e3230a1207cfa5ae94d28ba7d2021063c337> | CC BY-NC-SA 3.0 | Git 的对象模型、分支、回退与协作 |
| Google Engineering Practices | <https://github.com/google/eng-practices/tree/3bb3ec25b3b0199f4940b1aa75f0ac5c5753301c> | CC BY 3.0 | 代码评审的检查项和变更管理 |

读这些书时，先看目录和前言，确认它解决的是哪个阶段的问题。`Agentic Software Engineering` 覆盖范围最广，适合在写完第一个原型后按需查；`The Missing Semester` 和 `Pro Git` 更适合在遇到终端或版本问题时补基础；`Google Engineering Practices` 篇幅短，适合在团队准备评审流程时对照。

许可证不同，能做的事也不同。CC BY-NC-ND 不允许发布改编版，CC BY-SA 要求衍生作品沿用相同许可证。要把某本书的段落放进自己的文档前，先读原仓库的 `LICENSE`；拿不准就只保留链接和一句自己的总结。

## B.4 怎样读一个陌生仓库

带着一个问题进仓库，比从头读到尾有效。比如想知道“权限检查发生在哪”，可以按下面顺序：

1. 从入口文件找参数解析与主循环。
2. 搜 `permission`、`approve`、`sandbox`、`allow` 等词，定位相关模块。
3. 看调用链：谁调用检查函数，失败时返回什么。
4. 找一条测试，确认这条路径真的被执行过。

一次只回答一个问题。读完后写三行笔记：入口、关键函数、仍未确认的部分。不要用“大概看懂了”结束。

## B.5 不要把示例当契约

GitHub 上的项目会变。今天读到的默认值、命令和权限模式，下个版本可能不同。引用时固定提交或标签；写进文档时注明读取日期。你自己项目里的规则，也按同样方式留版本。

如果某个仓库的 README 与代码冲突，以可运行的代码和测试为准，并把冲突记下来。这正是第 6 章的做法：看运行结果，不看叙述。
