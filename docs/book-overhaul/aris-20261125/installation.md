# ARIS 安装与书稿适配

用户指定仓库：<https://github.com/wanshuiyin/auto-claude-code-research-in-sleep>。
固定提交：`3fefd34146d3317e407aec65a5a29335de87b9ee`。

本次安装 Codex 原生包中的 `auto-paper-improvement-loop`，位置为工作区的 `.agents/skills/auto-paper-improvement-loop/`；同时安装 7 份共享参考和只解析配置的 `reviewer_route.py`。这是书稿修订所需的子集，不是完整的 87 项技能包。安装使用 Codex `skill-installer` 的下载脚本，依赖来自同一固定提交。原始文件校验值、本地文件校验值和适配说明分别保存在技能目录的 `INSTALLATION.json`、`BOOK-ADAPTATION.md`。

## 安装前审查

**PASS：限定在本地原生审读流程。** 在未加入技能发现路径的暂存目录中读取目标 `SKILL.md`、7 份参考（reviewer-backends、reviewer-routing、reviewer-independence、review-tracing、integration-contract、writing-principles、output-composition）、路由 Python 全文和许可文件。路由脚本只读取项目配置并输出选择结果，不启动模型、不修改设置。

上游技能还有外部模型、飞书通知及论文专用审计的条件分支。本次本地适配禁用通知、外部写作服务和自动更新，不启动定时任务。未安装、未执行上游 PowerShell 全量安装器；未审查整库其他技能，不能把本次 PASS 扩大成整库安全结论。参考文档提到但本次不调用的外部后端和其他技能也不在审查覆盖内。

本地 `SKILL.md` 只新增指向 `BOOK-ADAPTATION.md` 的入口，上游流程正文保留。适配说明把论文的 LaTeX/PDF 对应为源 Markdown、配套示例、离线 HTML 与实际页面截图。书稿没有定理重述或会议投稿页数要求，相应步骤不适用；使用标题、块 ID、插图引用、示例一致性及项目构建检查。不会把这些检查写成通过了上游论文投稿审计。

## 本次执行约定

- 范围：LLM 卷第 7、8、14 章，关联的第 16 章术语和四个示例；保留本轮开始时已有改动。
- 两轮审读各启动一个新上下文，指定 `gpt-6-astra / xhigh`，不给上一轮意见或执行者解释。
- 先保存原始 Markdown/HTML，再按严重程度修订、构建并复审。原始请求与回答写入本地 `.aris/traces/`，快照写入忽略目录 `.scratch/aris-book-20261125/`。
- 模型名和推理强度记录为请求值；宿主未独立返回的身份字段留空。审读标记为 `same-family / provisional`，不声称跨模型家族验收。
- 只改有事实或阅读依据的问题。中文润色遵循 `humanizer-zh`：不虚构经历，不改数值与确定程度，不机械删除限定词。
- 沿用项目当前仅维护中文的规则；不重建已退役的英文整书。

这次安装可在工作区的后续对话中使用。本轮直接读取已安装文件并执行，不以等待技能列表刷新代替书稿修订。
