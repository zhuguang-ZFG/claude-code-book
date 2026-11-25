# 十二卷书稿与插图深度精修实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 精修十二卷中文书稿及其所属插图，改善准确性、清晰度、阅读节奏和图文关系，并通过分卷与合订本验证。

**Architecture:** 以 `manifest-collected.json` 引用的十二份分册 manifest 为工作清单，按分卷真源审阅和编辑正文及专属插图；先用《御舆》校准尺度，再逐卷完成其余十一册。每卷先经源稿检查和独立格式构建，最终再构建合订本并运行全仓检查。

**Tech Stack:** UTF-8 Markdown、JSON manifest/source registries、SVG/PNG、Mermaid、Python `scripts/bookctl.py`、现有 `unittest`/内容检查、HTML/PDF/EPUB 构建。

**Spec:** [2026-11-24-twelve-volume-editorial-illustration-overhaul-design.md](../specs/2026-11-24-twelve-volume-editorial-illustration-overhaul-design.md)

## Global Constraints

- 内容真源是各分册 manifest 的中文 `units` 路径；不得直接编辑 `dist/` 或合订本派生产物。
- 主册遵循 `CONTRIBUTING.md` 单语维护规则，不修改已停止维护的 `en/` 整书。
- 不自动刷新来源、不改写来源钉点、不把推断或教学简化写成上游事实；事实修改需可追溯到已登记来源。
- 保留 `<!-- block: ... -->` 稳定标识、代码示例语义、跨章引用和构建器派生锚点；不手写生成的图号、脚注、索引锚点。
- 不套用统一章节模板；按清晰、准确、连贯和适当阅读节奏逐处修改，不为增加篇幅而扩写。
- 图稿按产品归属目录维护，保留各卷视觉身份、语义和既有 SVG/PNG 管线约束；审计发现缺少产品专属图稿时可手绘补齐 SVG；不调用生图服务、不新增生成式图像资产。
- 每卷改过的图稿必须在该卷构建产物中目视检查，至少包含封面和所有有改动的图稿页；可用仓库已固定的 PyMuPDF 将目标 PDF 页栅格化到 `.scratch` 临时目录，确认无裁切、重叠或难辨线条，临时图不入库。
- 修改术语、H2 结构或通俗层证据时，只更新对应产品已有的 glosses、notes、guides、reading-paths、revisions 等登记项；不为没有该层的书另建同类系统。
- 先记录当前基线；若基线检查已有失败，区分原有失败与本轮引入的问题。
- 每卷输出到 `yuyu-book/.scratch/overhaul/<product>/`，避免覆盖现有发行产物。
- 每卷作为独立可审查任务在本地创建一次 conventional commit；不推送、不合并。

## 文件地图与资产归属

| 产品 | manifest / source registry | 正文源稿 | 主要插图资产 |
|---|---|---|---|
| `book` | `yuyu-book/manifest.json`、`sources.json` | 根目录前言、四部分 15 章、`附录/` 中 A–D；20 单元 | `yuyu-book/illustrations/`，含 SVG 与已验收的 `part-p1.png`、`part-p2.png` |
| `llm` | `manifest-llm.json`、`sources-llm.json` | `llm/00-前言.md`、`llm/ch01.md`–`ch16.md`；17 单元 | `illustrations-agents/llm-*`、`part-llm-*`、`cover-llm.svg` |
| `omp` | `manifest-omp.json`、`sources-omp.json` | `omp/00-前言.md`、`omp/ch01.md`–`ch33.md`、`omp/appendix-A.md`–`E.md`；39 单元 | `omp/images/`、`illustrations-omp/omp-*`、本计划拟补 `illustrations-omp/cover-omp.svg` |
| `pi` | `manifest-pi.json`、`sources-pi.json` | `pi/00-前言.md`、`pi/ch01.md`–`ch25.md`、`pi/appendix-A.md`–`E.md`；31 单元 | `illustrations-pi/`、本计划拟补 `illustrations-pi/cover-pi.svg` |
| `opencode` | `manifest-opencode.json`、`sources-opencode.json` | `opencode/` manifest 所列前言、18 章、附录 A–D；23 单元 | 已有 `illustrations-agents/cover-opencode.svg`；正文图为 Markdown 内 Mermaid |
| `deepseek` | `manifest-deepseek.json`、`sources-deepseek.json` | `deepseek/` manifest 所列前言、18 章、附录 A–D；23 单元 | 已有 `illustrations-agents/cover-deepseek.svg`；正文图为 Markdown 内 Mermaid |
| `hermes` | `manifest-hermes.json`、`sources-hermes.json` | `hermes/` manifest 所列前言、18 章、附录 A–D；23 单元 | 已有 `illustrations-agents/cover-hermes.svg`；正文图为 Markdown 内 Mermaid |
| `codex` | `manifest-codex.json`、`sources-codex.json` | `codex/` manifest 所列前言、18 章、附录 A–D；23 单元 | 已有 `illustrations-agents/cover-codex.svg`；正文图为 Markdown 内 Mermaid |
| `prompt` | `manifest-prompt.json`、`sources-prompt.json` | `prompt/` manifest 所列前言、18 章、附录 A–D；23 单元 | 本计划拟补 `illustrations-agents/cover-prompt.svg` |
| `kimi` | `manifest-kimi.json`、`sources-kimi.json` | `kimi/` manifest 所列前言、18 章、附录 A–D；23 单元 | 本计划拟补 `illustrations-agents/cover-kimi.svg` |
| `vibe` | `manifest-vibe.json`、`sources-vibe.json` | `vibe/` manifest 所列前言、12 章、附录 A–D；17 单元 | 已有章内图与篇题图；本计划拟补 `illustrations-agents/cover-vibe.svg` |
| `t3code` | `manifest-t3code.json`、`sources-t3code.json` | `t3code/` manifest 所列前言、18 章、附录 A–D；23 单元 | 已有 `illustrations-agents/t3code-*`、`part-t3code-*`、`cover-t3code.svg` |

所有表中 manifest 的 `units` / `parts` 同时是最终路径清单；遇到上表的文件名概括与 manifest 不一致时，以 manifest 为准。通俗层登记表按 `yuyu-book/PRODUCTS.md` 的产品后缀规则读取。每个分卷 task 还会更新 `docs/book-overhaul/audit-and-change-log.md` 对应章节。

## Tasks

### Task 1：建立全书审计与修改记录

**Files:**
- Create: `docs/book-overhaul/audit-and-change-log.md`
- Read only: `yuyu-book/manifest-collected.json`、十二份分册 `manifest*.json` 与 `sources*.json`、`CONTRIBUTING.md`、`STRUCTURE.md`、各分卷 `VERIFY.md`/`PIN.md`、插图目录和相关测试

- [ ] **Step 1: 记录当前质量门基线**

Run: `python scripts/bookctl.py check --fast`

在记录文件的“基线”表中写入日期、命令、退出码和失败摘要；若命令失败，把失败归为既存问题或待复核项，不通过放松门禁让后续数字看起来通过。

- [ ] **Step 2: 按合订本清单逐卷登记全部单元**

依 `manifest-collected.json` 的 `volumes` 顺序读取每个 manifest 的 `front`、`parts[].units` 和 `appendices`。在记录文件中为每卷列出全部单元 ID、正文路径、钉版文件和图稿目录，并核对合计十二卷；保留各卷不同的单元数量。

- [ ] **Step 3: 将正文插图锚点和封面映射到实际图稿**

逐个单元检查 Markdown 中的 `ill` 围栏与 Mermaid 图，将图名映射到本计划文件地图所列资产目录。另登记封面、篇题、章徽和插图说明；缺图、孤儿图、重复或图名错配逐项注明，不直接改资产。构建每个产品的封面并确认其使用本书专属图稿；封面回落到《御舆》共用图而与本卷主题不符时，列为待补图问题。

- [ ] **Step 4: 写入逐卷审计记录**

对每个单元记录文字问题、事实/来源风险、图文问题、拟采取的动作或“不需修改”的依据。问题引用稳定 block marker 或章节标题与路径，不使用会因增删行而失效的行号作为唯一定位。

### Task 2：《御舆》作为校准卷

**Files:**
- Read: `yuyu-book/manifest.json`、`yuyu-book/sources.json`、`docs/YUYU-OVERHAUL-SPEC.md`、`CONTRIBUTING.md`
- Modify: manifest 中列出的根目录中文 20 个单元、`yuyu-book/illustrations/` 中确有审计问题的资产、`docs/book-overhaul/audit-and-change-log.md`
- Conditional: `yuyu-book/glosses.json`、`guides.json`、`notes.json`、`reading-paths.json`、`revisions.json`，仅在正文变化使对应证据或版本说明需要同步时修改

- [ ] **Step 1: 精修前言与第一篇**

覆盖 `00-前言.md`、`第一部分-基础篇/01-智能体编程的新范式.md` 至 `04-权限管线-Agent的护栏.md`。先按审计记录核对论证和例子，再修改段落；同步检查 `front.svg`、`part-p1.svg`、`ch01.svg`–`ch04.svg` 及这些单元的正文图。审阅过但无需改的图也在记录中标记。

- [ ] **Step 2: 精修第二篇**

覆盖 `第二部分-核心系统篇/05-设置与配置-Agent的基因.md` 至 `08-钩子系统-Agent的生命周期扩展点.md`，以及 `part-p2`、对应章徽和正文图。检查设置、记忆、上下文、钩子四章之间的边界，避免术语或机制重复造成误解。

- [ ] **Step 3: 精修第三篇**

覆盖 `第三部分-高级模式篇/09-子智能体与Fork模式.md` 至 `12-MCP集成与外部协议.md`，以及 `part-p3`、对应章徽和正文图。核对多智能体、技能与协议之间的关系图是否准确表达正文定义。

- [ ] **Step 4: 精修第四篇与附录**

覆盖 `第四部分-工程实践篇/13-流式架构与性能优化.md` 至 `15-构建你自己的Agent-Harness.md` 和 `附录/A-源码导航地图.md` 至 `D-术语表.md`，以及 `part-p4`、对应章徽、`keeper.svg` 和有正文锚点的插图。

- [ ] **Step 5: 校准后验证整卷**

运行 `python docs/yuyu-overhaul/check_block_markers.py`、`python scripts/bookctl.py build --product book --lang zh --check`，再运行：

```powershell
python scripts/bookctl.py build --product book --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/book
```

按改动范围运行 `python -m unittest discover -s yuyu-book/tests -p "test_art.py" -v`、`test_illustrations.py`、`test_plain.py` 或 `test_docclaims.py`；记录修改前后标准是否适用、修正了哪些审计问题，以及命令退出码。

### Task 3：《大模型》精修

**Files:**
- Read: `yuyu-book/manifest-llm.json`、`sources-llm.json`、`llm/VERIFY.md`、`llm/facts/source-lock.json`
- Modify: manifest 所列 `llm/` 17 个正文单元、`llm/examples/` 中因正文修改而需同步的示例、`yuyu-book/illustrations-agents/llm-*` 与 `part-llm-*` / `cover-llm.svg` 中有审计问题的资产、`yuyu-book/tests/test_art.py`、审计记录

- [ ] **Step 1: 精修前言及第 1–7 章**

按 manifest 顺序检查前言与 `llm/ch01.md`–`ch07.md`，核对模型基础概念、训练数据与训练过程的递进；逐一检查对应例子、篇题与正文图。把已有 `cover-llm.svg` 纳入 `test_art.py` 的产品封面列表，将测试名改为 `test_all_nonbook_products_have_distinct_offline_covers`，并运行该套件确认独立封面正确渲染。
- [ ] **Step 2: 精修第 8–16 章**

检查 `llm/ch08.md`–`ch16.md`，特别复核推理、对齐、服务、RAG 与评测之间的因果关系，保留来源钉点和可复跑示例；逐一检查关联图稿。
- [ ] **Step 3: 运行示例与分卷验证**

运行 `llm/VERIFY.md` 指定的示例测试；再运行 `python scripts/bookctl.py build --product llm --lang zh --check` 和：

```powershell
python scripts/bookctl.py build --product llm --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/llm
```

### Task 4：《Omp》精修

**Files:**
- Read: `yuyu-book/manifest-omp.json`、`sources-omp.json`、`omp/VERIFY.md`、`omp/BUILD.md`、`omp/overhaul/`
- Modify: manifest 所列 `omp/` 前言、33 章和附录 A–E、关联的 `omp/images/` 示例图及 `illustrations-omp/` 资产（含拟新增 `cover-omp.svg`）、`yuyu-book/tests/test_art.py`、审计记录
- Conditional: `glosses-omp.json`、`guides-omp.json`、`notes-omp.json`、`reading-paths-omp.json`、`revisions-omp.json`，仅在对应契约要求时修改

- [ ] **Step 1: 精修前言与第 1–7 章**，检查 agent 基础、模型与配置铺垫及相关手绘图。
- [ ] **Step 2: 精修第 8–18 章**，检查工具、上下文、会话及架构图的定义和边界。
- [ ] **Step 3: 精修第 19–29 章**，检查高级功能、实验与实践路径，核实示例所依赖的写作钉版本。
- [ ] **Step 4: 精修第 30–33 章与附录 A–E**，核对速查资料、命令、功能旗标及篇题和图例；并依 Omp 前言和篇题图确定专属封面隐喻，手绘 `yuyu-book/illustrations-omp/cover-omp.svg`。图稿表达 Omp 的开源终端 Agent 与本书实际讲述的机制，不使用泛化“AI 大脑”符号。修改 `test_art.py` 的产品封面列表加入 `omp`；先运行 `python -m unittest discover -s yuyu-book/tests -p "test_art.py" -v`，确认因缺少此封面而失败，再完成图稿后复跑通过。
- [ ] **Step 5: 运行 Omp 专属审计与完整输出**

运行 `python omp/overhaul/audit_structure.py --check`、`python omp/overhaul/audit_delivery.py`、`python scripts/bookctl.py build --product omp --lang zh --check`，并运行：

```powershell
python scripts/bookctl.py build --product omp --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/omp
```

若有示例或通俗层变化，再运行 `omp/VERIFY.md` 中对应命令并更新本卷审计记录。

### Task 5：《Pi Agent》精修

**Files:**
- Read: `yuyu-book/manifest-pi.json`、`sources-pi.json`、`pi/VERIFY.md`、`pi/PIN.md`
- Modify: manifest 所列 `pi/` 前言、25 章、附录 A–E，`illustrations-pi/` 中有审计问题的资产及拟新增 `cover-pi.svg`、`yuyu-book/tests/test_art.py`、审计记录
- Conditional: Pi 自有 glosses、guides、notes、reading paths 与 revisions JSON

- [ ] **Step 1: 精修前言、第 1–8 章与前两篇相关图稿**，保持从核心循环进入插件和配置的学习顺序。
- [ ] **Step 2: 精修第 9–19 章与中段图稿**，核对会话、扩展和运行时行为是否由写作钉支持。
- [ ] **Step 3: 精修第 20–25 章及附录 A–E**，检查诊断、实战步骤和参考资料之间的衔接；并依 Pi 前言、篇题图和写作钉确定专属封面隐喻，手绘 `yuyu-book/illustrations-pi/cover-pi.svg`。语义从本书实际机制中来，不与其他产品共用封面主图。将 `pi` 加入 `test_art.py` 的封面列表，先运行该套件确认因缺少此封面而失败，再完成图稿后复跑通过，并确认 SVG 契约。
- [ ] **Step 4: 运行 Pi 检查与完整输出**

运行 `python scripts/bookctl.py build --product pi --lang zh --check`、`pi/VERIFY.md` 中对本轮改动适用的测试，以及：

```powershell
python scripts/bookctl.py build --product pi --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/pi
```

### Task 6：《OpenCode》精修

**Files:** `opencode/` manifest 所列 23 个正文单元；现有 `illustrations-agents/cover-opencode.svg`；正文 Mermaid 图仍在对应 Markdown 源稿中；`sources-opencode.json` 与相关 lock files 只读；审计记录按需更新。

- [ ] **Step 1:** 精修前言、第一至第二篇（第 1–10 章），跟踪一次任务穿过客户端、服务与工具的主线，并检查对应图稿。
- [ ] **Step 2:** 精修第三至第四篇（第 11–18 章），复核权限、插件和服务边界及其图文说明。
- [ ] **Step 3:** 精修附录 A–D，保证术语和命令与正文一致；只更新本卷已有通俗层登记。
- [ ] **Step 4:** 运行 `python scripts/bookctl.py build --product opencode --lang zh --check`、`opencode/VERIFY.md` 中适用的示例测试，以及 `python scripts/bookctl.py build --product opencode --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/opencode`；记录结果。

### Task 7：《DeepSeek Harness》精修

**Files:** `deepseek/` manifest 所列 23 个正文单元；现有 `illustrations-agents/cover-deepseek.svg`；正文 Mermaid 图仍在对应 Markdown 源稿中；source lock 只读；审计记录按需更新。

- [ ] **Step 1:** 精修前言及第 1–4 章，检查插件系统引入和基础叙事。
- [ ] **Step 2:** 精修第 5–14 章，核对中段插件生命周期、并发与持久化说明及对应流程图。
- [ ] **Step 3:** 精修第 15–18 章和附录 A–D，确保故障路径与章节总结不超出钉版证据。
- [ ] **Step 4:** 运行 `python scripts/bookctl.py build --product deepseek --lang zh --check`、`deepseek/VERIFY.md` 中适用的示例测试，以及 `python scripts/bookctl.py build --product deepseek --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/deepseek`；记录结果。

### Task 8：《Hermes Agent》精修

**Files:** `hermes/` manifest 所列 23 个正文单元；现有 `illustrations-agents/cover-hermes.svg`；正文 Mermaid 图仍在对应 Markdown 源稿中；source lock 只读；审计记录按需更新。

- [ ] **Step 1:** 精修前言及第 1–4 章，验证记忆组件的概念入口和术语定义。
- [ ] **Step 2:** 精修第 5–14 章，梳理资料库、技能、任务调度的层次，并检查图中状态转换。
- [ ] **Step 3:** 精修第 15–18 章和附录 A–D，检查长期任务、暂停恢复和参考资料的语义。
- [ ] **Step 4:** 运行 `python scripts/bookctl.py build --product hermes --lang zh --check`、`hermes/VERIFY.md` 中适用的示例测试，以及 `python scripts/bookctl.py build --product hermes --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/hermes`；记录结果。

### Task 9：《Codex CLI》精修

**Files:** `codex/` manifest 所列 23 个正文单元；现有 `illustrations-agents/cover-codex.svg`；正文 Mermaid 图仍在对应 Markdown 源稿中；source lock 只读；审计记录按需更新。

- [ ] **Step 1:** 精修前言及第 1–4 章，校准执行边界、规则和审批的概念关系。
- [ ] **Step 2:** 精修第 5–10 章，核对沙箱、权限、工具和执行记录之间的说明与图示。
- [ ] **Step 3:** 精修第 11–18 章和附录 A–D，检查跨章节流程、工程实践步骤和受钉版行为。
- [ ] **Step 4:** 运行 `python scripts/bookctl.py build --product codex --lang zh --check`、`codex/VERIFY.md` 中适用的示例测试，以及 `python scripts/bookctl.py build --product codex --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/codex`；记录结果。

### Task 10：《提示词工程》精修

**Files:** `prompt/` manifest 所列 23 个正文单元、正文所引用且本轮确需同步的 `prompt/examples/` 内容、拟新增 `yuyu-book/illustrations-agents/cover-prompt.svg`、`yuyu-book/tests/test_art.py`、审计记录。

- [ ] **Step 1:** 精修前言及第 1–4 章，明确提示词、任务说明和交付约束的递进。
- [ ] **Step 2:** 精修第 5–14 章，核对模板、例子和 agent 协作工作流是否彼此印证。
- [ ] **Step 3:** 精修第 15–18 章和附录 A–D，验证练习、检查表与随书示例包保持一致；若修改示例，重建 `yuyu-prompt-zh-examples.zip` 并检查包内 manifest 摘要。
- [ ] **Step 4:** 根据前言与实际练习设计 `yuyu-book/illustrations-agents/cover-prompt.svg`。将 `prompt` 加入 `test_art.py` 的封面列表，先运行 art 测试确认因缺少该图而失败，再完成 SVG 并复跑通过；构建后确认产品封面不再回落到《御舆》的 `cover.svg`。
- [ ] **Step 5:** 运行本卷 `VERIFY.md` 和练习包测试，运行 `python scripts/bookctl.py build --product prompt --lang zh --check`，再运行 `python scripts/bookctl.py build --product prompt --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/prompt`；记录结果。

### Task 11：《Kimi Code》精修

**Files:** `kimi/` manifest 所列 23 个正文单元、因正文修改而需同步的 `kimi/examples/`、拟新增 `yuyu-book/illustrations-agents/cover-kimi.svg`、`yuyu-book/tests/test_art.py`、审计记录；`facts/source-lock.json` 只读。

- [ ] **Step 1:** 精修前言及第 1–4 章，检查插件能力的入门解释和边界。
- [ ] **Step 2:** 精修第 5–13 章，核对插件到审查助手的工作流、示例与图示。
- [ ] **Step 3:** 精修第 14–18 章和附录 A–D，检查实战结论与参考资料是否匹配。
- [ ] **Step 4:** 根据前言与核心插件/审查流程设计 `yuyu-book/illustrations-agents/cover-kimi.svg`。将 `kimi` 加入 `test_art.py` 的封面列表，先运行 art 测试确认因缺少该图而失败，再完成 SVG 并复跑通过；确认产品封面不再回落到《御舆》的 `cover.svg`。
- [ ] **Step 5:** 运行本卷示例测试，运行 `python scripts/bookctl.py build --product kimi --lang zh --check` 和 `python scripts/bookctl.py build --product kimi --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/kimi`；记录结果。

### Task 12：《Vibe Coding》精修

**Files:** `vibe/` manifest 所列 17 个正文单元、正文所引用且本轮确需同步的练习模板/示例、`illustrations-agents/vibe-*`/`part-vibe-*` 中有审计问题的资产、拟新增 `cover-vibe.svg`、`yuyu-book/tests/test_art.py`、审计记录。

- [ ] **Step 1:** 精修前言及第 1–4 章，检查从想法到需求的起始路径。
- [ ] **Step 2:** 精修第 5–8 章，检查设计、生成与验证之间的闭环。
- [ ] **Step 3:** 精修第 9–12 章和附录 A–D，复核交付、维护与练习模板的一致性。
- [ ] **Step 4:** 依据前三幅篇题图和“把想法做成能跑的软件”主线设计 `yuyu-book/illustrations-agents/cover-vibe.svg`。将 `vibe` 加入 `test_art.py` 封面列表，先运行 art 测试确认因缺少封面而失败，再完成 SVG 并复跑通过；确认屏幕与打印中均清楚表达交付闭环。
- [ ] **Step 5:** 运行 `vibe/VERIFY.md` 中适用的练习检查，运行 `python scripts/bookctl.py build --product vibe --lang zh --check` 和 `python scripts/bookctl.py build --product vibe --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/vibe`；记录结果。

### Task 13：《T3 Code》精修

**Files:** `t3code/` manifest 所列 23 个正文单元、`illustrations-agents/t3code-*`/`part-t3code-*`/`cover-t3code.svg` 中有审计问题的资产、审计记录；上游 `3b3b662f` 写作钉只读。

- [ ] **Step 1:** 精修前言及第 1–5 章，核对 coding agent 控制平面的入门模型。
- [ ] **Step 2:** 精修第 6–14 章，检查工作区、任务执行、审查及可视界面之间的流程。
- [ ] **Step 3:** 精修第 15–18 章和附录 A–D，验证工具能力、限制说明和图文关系。
- [ ] **Step 4:** 运行 `t3code/VERIFY.md` 中适用的检查，运行 `python scripts/bookctl.py build --product t3code --lang zh --check` 和 `python scripts/bookctl.py build --product t3code --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/t3code`；记录结果。

### Task 14：更新依赖正文的通俗层与站点图页

**Files:** 仅在 Task 2–13 的正文或插图实际影响它们时修改 `yuyu-book/glosses*.json`、`guides*.json`、`notes*.json`、`reading-paths*.json`、`revisions*.json`、`subject-index*.json`、`docs/illustration-prompts.md` 与再生页面。

- [ ] **Step 1:** 对每个改变过的 H2 数量、术语首现、证据块或章节图稿，逐个核对本卷通俗层登记表是否需同步；按该产品现行 schema 更新，并运行该产品 `build --check`。
- [ ] **Step 2:** 若主册插图变动，运行 `python scripts/bookctl.py build --product gallery` 和 `python scripts/bookctl.py build --product reader`，检查生成页面只反映当前主册源稿；若 Omp 专属 gallery 有对应生成器，按 `omp/BUILD.md` 再生，保持 Omp 与主册托盘隔离。
- [ ] **Step 3:** 对 README/STRUCTURE 中由构建尺寸、页数或图数自动核对的宣称，只在最终实测值要求更新时修改；仅在能使用对应的 CI/Noto 产物目录时运行 `python scripts/check_artifact_claims.py`，记录文件注明字体与平台条件，避免把 Windows 本机字体差异误报为回归。

### Task 15：全仓与十二卷合订本验收

**Files:** 修改过的源稿、图稿、登记表、必要的再生页面、审计记录、`yuyu-book/tests/test_art.py`；不手改任何 `dist/` 文件。

- [ ] **Step 1: 核对记录覆盖率**

从 `manifest-collected.json` 重数十二卷与全部单元 ID，和 `docs/book-overhaul/audit-and-change-log.md` 对照；每个正文单元和所属图稿都应有“已检查/修改/无须修改”状态及依据。

- [ ] **Step 2: 运行全仓快速门禁**

Run: `python scripts/bookctl.py check --fast`

检查命令通过且未新增 Markdown、Mermaid、来源、产品隔离、示例或登记表错误。

- [ ] **Step 3: 运行图稿与排版相关门禁**

Run: `python scripts/bookctl.py check --full`

对 SVG/PNG 变化另运行 `python -m unittest discover -s yuyu-book/tests -p "test_art.py" -v` 和 `python -m unittest discover -s yuyu-book/tests -p "test_illustrations.py" -v`。若有某卷特有图稿契约，运行其 `VERIFY.md` 指定的测试。

产品封面断言随各产品任务逐步覆盖全部 11 个非主册产品（`llm`、`omp`、`pi`、`opencode`、`deepseek`、`hermes`、`codex`、`prompt`、`kimi`、`vibe`、`t3code`），最终确认每个 `cover-<product>` 均可加载、渲染结果含该图稿且没有产品间重复；测试命令为 `python -m unittest discover -s yuyu-book/tests -p "test_art.py" -v`。

- [ ] **Step 4: 构建合订本**

```powershell
python scripts/bookctl.py build --product collected --lang zh --pdf --epub --mermaid render --out-dir yuyu-book/.scratch/overhaul/collected
```

核对产物 manifest、页内链接、图片引用、导航和 EPUBCheck 结果；用 `collected` 对应的测试确认十二卷及顺序正确。

- [ ] **Step 5: 完成修改记录**

在 `docs/book-overhaul/audit-and-change-log.md` 写入逐卷修改摘要、未改内容的理由、全部验证命令及结果，并列出仍受来源不确定性约束的说明。运行 `git diff --check`，确认没有临时构建产物进入变更。

## Self-review Checklist

- [x] 十二卷在文件地图与各自 task 中均有覆盖，且合订本只在最终任务验证。
- [x] 每卷按 manifest 中真实单元数和当前来源路径工作；额外产品结构（Omp/Pi/LLM/Vibe/T3Code）有各自专项步骤。
- [x] 每个会改正文/图稿的 task 都包含自身的内容检查与构建命令。
- [x] 主册英文维护边界、来源钉版、图稿管线、记录文件以及最终 HTML/PDF/EPUB 验收均覆盖设计文档要求。
- [x] 不新增测试来机械断言文案；只对发生语义变化的代码示例运行已有测试。
- [x] 无未完成占位符；路径、产品 ID、命令选项均与当前仓库一致。
