# 十二卷合集精修审计与修改记录

## 基线

- 执行方案：`D:/Users/claude/collected-polish-plan.md`（2026-11-27）。
- 远程 `main` 与本地 `HEAD`：`02f9e1333e71c1dce3d7af400a3425f6a3f9fd55`，无差值。
- 合集真源：`yuyu-book/manifest-collected.json`，十二卷、286 个单元。
- 当前工作树含此前未提交改动；本记录区分“已在工作树、待提交”与“本轮新增”，不回滚用户或前序工作。
- `python scripts/bookctl.py check --fast`：9 步通过；通用测试 487 项、构建器测试 638 项、498 份 Markdown、280 个 Mermaid、7 个产品输出字节一致。
- `task_verify run`：未验证，原因 `project-or-git-baseline-unavailable`。
- 既有警告：`Duplicate name: 'EPUB/package.opf'`；不改变门禁结论。

## 缺口总表

| 卷 | 产品 | 单元 | 正文手绘 `ill` | Mermaid | Markdown 图 | 无任何正文图单元 | 专属封面 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 卷一 | `book` | 20 | 31 | 160 | 0 | 0 | `illustrations/cover.svg` |
| 卷二 | `llm` | 17 | 31 | 0 | 0 | 1 | `illustrations-agents/cover-llm.svg` |
| 卷三 | `omp` | 39 | 1 | 13 | 212 | 0 | `illustrations-agents/cover-omp.svg`（工作树已有） |
| 卷四 | `pi` | 31 | 11 | 23 | 0 | 9 | `illustrations-agents/cover-pi.svg`（工作树已有） |
| 卷五 | `opencode` | 23 | 0 | 26 | 0 | 6 | `illustrations-agents/cover-opencode.svg` |
| 卷六 | `deepseek` | 23 | 0 | 14 | 0 | 13 | `illustrations-agents/cover-deepseek.svg` |
| 卷七 | `hermes` | 23 | 0 | 17 | 0 | 11 | `illustrations-agents/cover-hermes.svg` |
| 卷八 | `codex` | 23 | 0 | 15 | 0 | 12 | `illustrations-agents/cover-codex.svg` |
| 卷九 | `kimi` | 23 | 0 | 6 | 0 | 17 | `illustrations-agents/cover-kimi.svg`（工作树已有） |
| 卷十 | `prompt` | 23 | 0 | 2 | 0 | 21 | `illustrations-agents/cover-prompt.svg`（工作树已有） |
| 卷十一 | `vibe` | 17 | 12 | 2 | 0 | 5 | `illustrations-agents/cover-vibe.svg`（工作树已有） |
| 卷十二 | `t3code` | 23 | 0 | 2 | 0 | 21 | `illustrations-agents/cover-t3code.svg` |

### 优先级结论

1. 《御舆》先定尺度：十五章仍保留“三句话带走”模板标签；先去掉标签，保留具体检查项与派生页提取能力。
2. 《大模型》高优先级：17 单元逐段通俗化；优先前言及第 2、3、4、7、9、10 章。保留 11 月下旬正确性修订、来源钉点、数值与边界。
3. 五张封面已在此前工作树补齐，`test_art.py` 的产品列表也已扩展；本轮验收其加载、独特性和印刷效果，不重复新增资产。
4. 提示词、Kimi 缺图最严重；OpenCode、DeepSeek、Hermes、Codex 几乎只有 Mermaid；T3 有章徽但缺解释性正文图；Pi 有 9 个无图单元。按“每卷 3–6 个关键机制”补手绘，不凑装饰章徽。
5. 合订本窄屏深层锚点遮挡已在前序工作中修复并回归；本轮纳入最终合订本验收，不重复修改。

## 单元清单

### 卷一 · 御舆：解码 Agent Harness（`vol1`）

manifest：`manifest.json`；sources：`sources.json`；20 单元。

| unit | path |
| --- | --- |
| `front` | `00-前言.md` |
| `ch01` | `第一部分-基础篇/01-智能体编程的新范式.md` |
| `ch02` | `第一部分-基础篇/02-对话循环-Agent的心跳.md` |
| `ch03` | `第一部分-基础篇/03-工具系统-Agent的双手.md` |
| `ch04` | `第一部分-基础篇/04-权限管线-Agent的护栏.md` |
| `ch05` | `第二部分-核心系统篇/05-设置与配置-Agent的基因.md` |
| `ch06` | `第二部分-核心系统篇/06-记忆系统-Agent的长期记忆.md` |
| `ch07` | `第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md` |
| `ch08` | `第二部分-核心系统篇/08-钩子系统-Agent的生命周期扩展点.md` |
| `ch09` | `第三部分-高级模式篇/09-子智能体与Fork模式.md` |
| `ch10` | `第三部分-高级模式篇/10-协调器模式-多智能体编排.md` |
| `ch11` | `第三部分-高级模式篇/11-技能系统与插件架构.md` |
| `ch12` | `第三部分-高级模式篇/12-MCP集成与外部协议.md` |
| `ch13` | `第四部分-工程实践篇/13-流式架构与性能优化.md` |
| `ch14` | `第四部分-工程实践篇/14-Plan模式与结构化工作流.md` |
| `ch15` | `第四部分-工程实践篇/15-构建你自己的Agent-Harness.md` |
| `apxa` | `附录/A-源码导航地图.md` |
| `apxb` | `附录/B-工具完整清单.md` |
| `apxc` | `附录/C-功能标志速查表.md` |
| `apxd` | `附录/D-术语表.md` |

### 卷二 · 大模型：写给 Agent 工程师的原理与实战（`vol2`）

manifest：`manifest-llm.json`；sources：`sources-llm.json`；17 单元。

| unit | path |
| --- | --- |
| `llm-front` | `llm/00-前言.md` |
| `llm-ch01` | `llm/ch01.md` |
| `llm-ch02` | `llm/ch02.md` |
| `llm-ch03` | `llm/ch03.md` |
| `llm-ch04` | `llm/ch04.md` |
| `llm-ch05` | `llm/ch05.md` |
| `llm-ch06` | `llm/ch06.md` |
| `llm-ch07` | `llm/ch07.md` |
| `llm-ch08` | `llm/ch08.md` |
| `llm-ch09` | `llm/ch09.md` |
| `llm-ch10` | `llm/ch10.md` |
| `llm-ch11` | `llm/ch11.md` |
| `llm-ch12` | `llm/ch12.md` |
| `llm-ch13` | `llm/ch13.md` |
| `llm-ch14` | `llm/ch14.md` |
| `llm-ch15` | `llm/ch15.md` |
| `llm-ch16` | `llm/ch16.md` |

### 卷三 · Omp 从入门到精通：原理与实战（`vol3`）

manifest：`manifest-omp.json`；sources：`sources-omp.json`；39 单元。

| unit | path |
| --- | --- |
| `omp-front` | `omp/00-前言.md` |
| `omp-ch01`–`omp-ch33` | `omp/ch01.md`–`omp/ch33.md` |
| `omp-apxa`–`omp-apxe` | `omp/appendix-A.md`–`omp/appendix-E.md` |

### 卷四 · Pi Agent：从原理到实战（`vol4`）

manifest：`manifest-pi.json`；sources：`sources-pi.json`；31 单元。

| unit | path |
| --- | --- |
| `pi-front` | `pi/00-前言.md` |
| `pi-ch01`–`pi-ch25` | `pi/ch01.md`–`pi/ch25.md` |
| `pi-apxa`–`pi-apxe` | `pi/appendix-A.md`–`pi/appendix-E.md` |

### 卷五 · OpenCode：从原理到实战（`vol5`）

manifest：`manifest-opencode.json`；sources：`sources-opencode.json`；23 单元。

| unit | path |
| --- | --- |
| `opencode-front` | `opencode/00-前言.md` |
| `opencode-ch01`–`opencode-ch18` | `opencode/ch01.md`–`opencode/ch18.md` |
| `opencode-apxa`–`opencode-apxd` | `opencode/appendix-a.md`–`opencode/appendix-d.md` |

### 卷六 · DeepSeek Harness：插件化运行时（`vol6`）

manifest：`manifest-deepseek.json`；sources：`sources-deepseek.json`；23 单元。

| unit | path |
| --- | --- |
| `deepseek-front` | `deepseek/00-前言.md` |
| `deepseek-ch01`–`deepseek-ch18` | `deepseek/ch01.md`–`deepseek/ch18.md` |
| `deepseek-apxa`–`deepseek-apxd` | `deepseek/appendix-a.md`–`deepseek/appendix-d.md` |

### 卷七 · Hermes Agent：记忆、技能与持续任务（`vol7`）

manifest：`manifest-hermes.json`；sources：`sources-hermes.json`；23 单元。

| unit | path |
| --- | --- |
| `hermes-front` | `hermes/00-前言.md` |
| `hermes-ch01`–`hermes-ch18` | `hermes/ch01.md`–`hermes/ch18.md` |
| `hermes-apxa`–`hermes-apxd` | `hermes/appendix-a.md`–`hermes/appendix-d.md` |

### 卷八 · Codex CLI：执行边界与工程实践（`vol8`）

manifest：`manifest-codex.json`；sources：`sources-codex.json`；23 单元。

| unit | path |
| --- | --- |
| `codex-front` | `codex/00-前言.md` |
| `codex-ch01`–`codex-ch18` | `codex/ch01.md`–`codex/ch18.md` |
| `codex-apxa`–`codex-apxd` | `codex/appendix-a.md`–`codex/appendix-d.md` |

### 卷九 · Kimi Code：从插件到审查助手（`vol9`）

manifest：`manifest-kimi.json`；sources：`sources-kimi.json`；23 单元。

| unit | path |
| --- | --- |
| `kimi-front` | `kimi/00-前言.md` |
| `kimi-ch01`–`kimi-ch18` | `kimi/ch01.md`–`kimi/ch18.md` |
| `kimi-apxa`–`kimi-apxd` | `kimi/appendix-a.md`–`kimi/appendix-d.md` |

### 卷十 · 提示词工程：从提问到 Agent 协作（`vol10`）

manifest：`manifest-prompt.json`；sources：`sources-prompt.json`；23 单元。

| unit | path |
| --- | --- |
| `prompt-front` | `prompt/00-前言.md` |
| `prompt-ch01`–`prompt-ch18` | `prompt/ch01.md`–`prompt/ch18.md` |
| `prompt-apxa`–`prompt-apxd` | `prompt/appendix-a.md`–`prompt/appendix-d.md` |

### 卷十一 · Vibe Coding：把想法做成能跑的软件（`vol11`）

manifest：`manifest-vibe.json`；sources：`sources-vibe.json`；17 单元。

| unit | path |
| --- | --- |
| `vibe-front` | `vibe/00-前言.md` |
| `vibe-ch01`–`vibe-ch12` | `vibe/ch01.md`–`vibe/ch12.md` |
| `vibe-apxa`–`vibe-apxd` | `vibe/appendix-a.md`–`vibe/appendix-d.md` |

### 卷十二 · T3 Code：coding agent 的控制平面（`vol12`）

manifest：`manifest-t3code.json`；sources：`sources-t3code.json`；23 单元。

| unit | path |
| --- | --- |
| `t3code-front` | `t3code/00-前言.md` |
| `t3code-ch01`–`t3code-ch18` | `t3code/ch01.md`–`t3code/ch18.md` |
| `t3code-apxa`–`t3code-apxd` | `t3code/appendix-a.md`–`t3code/appendix-d.md` |

## 修改记录

### 2026-11-27 · 阶段 A：基线审计

- 核对远程与本地 SHA 一致。
- 建立十二卷单元、封面、`ill` / Mermaid / Markdown 图计数。
- 确认五张缺失封面已在前序工作树存在，避免重复绘制。
- 确认合订本深层锚点遮挡已修复并回归。
- 下一步：以《御舆》去掉 15 处模板标签并校准派生页提取。

### 2026-11-27 · 阶段 B：《御舆》校准

- 十五章章末的“三句话带走”统一标签已移除；三条具体检查项逐字保留。
- `chapter_copy.recap` 改为结构提取：从后向前找最后一个含三条带圈检查项的引用块，兼容旧标签；知识卡与样章标题改为“本章核对”。
- 重建 `docs/knowledge-cards.html`、`docs/sample-chapter.html`、`docs/search-index.json`、`docs/concept-map.json`。
- 回归证据：改标签后旧提取器在 `ch01`/`ch02` 报 `expected 3 ... found 0`；改为结构提取后，知识卡、样章和产品 token 共 16 项通过。
- `check_block_markers.py`：20 个主册文件通过，锚点、锁定词形和 Mermaid 围栏数未变。
- 图稿契约：`test_art.py` 21 项、`test_illustrations.py` 19 项、`test_diagram_style.py` 3 项通过。
- 校准尺度：保留章节结构；章首先给具体问题；总结保留可执行检查项，不用统一营销标签；图注必须说明图在做什么，不只重复节标题。

### 2026-11-27 · 阶段 D 前置：十一册封面契约

- 前序工作树已有 `cover-llm/opencode/deepseek/hermes/codex/t3code/omp/pi/kimi/prompt/vibe.svg`。
- `test_art.py` 的封面测试更名为 `test_all_nonbook_products_have_distinct_offline_covers`，产品列表补齐 `llm`，覆盖全部 11 本非主册。
- 脚本核对：11 个封面加载成功、互不重复、均不等于御舆 `cover.svg`；21 项 art 测试通过。

### 2026-11-27 · 阶段 C：《大模型》通俗化收尾

- 完成前言、第 1–16 章审阅；保留公式、数值、正确性修订、来源钉点与实验边界。
- 第 2 章合并 ANN 的重复说明；第 3–8 章压缩过度比喻与重复解释，补足 GQA/MQA、Norm、SwiGLU、采样、KV cache、LoRA 与分类微调的条件。
- 回归证据：`test_llm_examples.py` 136 项、`test_llm_product` 9 项全部通过。
- HTML/PDF/EPUB 已构建一轮；最终文本改动后随全产品构建重新生成。

### 2026-11-27 · 阶段 D：八卷关键手绘图

- 为提示词、Kimi、OpenCode、DeepSeek、Hermes、Codex、T3、Pi 各新增 3 张原创机制图，共 24 张；不调用生图服务。
- 图直接解释证据链、输出契约、请求往返、重载边界、模块缓存、Hook 关联、依赖门禁、资源所有权、工具输出、目录边界、记忆快照、调度状态、执行入口、权限闸门、修复证据、控制平面、事务 outbox、逐 RPC 授权、上下文预算、turn 生命周期与信任边界。
- 所有新图使用 `currentColor`、无 ID、无外部引用；720 单位宽的画面标签不低于 28 单位，适配 390px 窄屏。
- `test_art.py` 与 `test_illustrations.py` 共 40 项通过，其中窄屏标签宽度与图稿加载契约均通过。
- 同步压缩 Omp、Pi、Vibe、OpenCode、T3 与 LLM 的重复 framing；保留命令、版本、权限条件和技术限定。
- Pi 的 `pi-plate-p1` / `pi-plate-p3` 只重复空框与抽象圆环，已删除对应 `ill` 引用和资产；第 1、9 章改由新的上下文预算图与 run/turn 生命周期图承担解释。

### 2026-11-27 · 阶段 E：合订本 PDF 打印边界

- 76.3 MB 合订本 HTML 在 Playwright 默认 30 秒导航超时；独立计时显示 Chromium 加载需 32.72 秒，已将 PDF 导航超时调整为 120 秒。
- Edge 全册 `Page.printToPDF` 在约 10 分钟后返回 `Printing failed`；10 页与 500 页探针成功，Chrome 全册探针最终输出 101.8 MB PDF，说明失败与浏览器/规模相关。
- `_launch` 改为优先 Chrome，并保留 Edge 与 Chromium 回退；正式合订本 PDF/EPUB 正在用该路径重建。
- Chrome 全册打印成功后的 PDF 审计发现第 26 页只有“主题索引”孤行；真实 24–28 页探针证明它是目录最后一组链接，不是索引正文。打印样式改为压缩倒数第二组，同时保留最后一组 4px / 2.4px 的既有契约；探针中卷一扉页回到第 26 页，孤行消失。

### 2026-11-27 · 阶段 F：最终门禁与产物

- `python scripts/bookctl.py check --fast`：通用测试 487 项、构建器测试 638 项通过；内容、Omp 白话、Mermaid、视频配置与产品幂等门禁通过。
- 分册 PDF 页数：御舆 555、LLM 182、提示词 99、Kimi 88、OpenCode 156、DeepSeek 146、Hermes 137、Codex 151、T3 129、Pi 186、Omp 439、Vibe 81；对应 EPUB 均由正式构建器生成。
- 390px 下已目检御舆、LLM、八卷新增图、Omp 与 Vibe 的代表章；PDF 封面与代表章页已生成接触表目检。
- `task_verify run`：未验证，原因 `project-or-git-baseline-unavailable`；不把窄测试或完整门禁写成 task_verify 通过。
- 合订本最终 PDF/EPUB 正在重建；完成后补入页数、字节数与 EPUB 导航证据。
