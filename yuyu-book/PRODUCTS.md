# yuyu-book products

| product | 书 | manifest | 产物前缀 | bookctl |
|---------|----|----------|----------|---------|
| `book` | 《御舆：解码 Agent Harness》 | `manifest.json` | `yuyu-agent-harness-*` | `build --product book`（现网；`make book`） |
| `omp` | 《Omp 从入门到精通：原理与实战》 | `manifest-omp.json` | `yuyu-omp-*` | `build --product omp --lang zh`（`make book-omp` / `make book-omp-pdf`） |
| `pi` | 《Pi Agent：从原理到实战》 | `manifest-pi.json` | `yuyu-pi-*` | `build --product pi --lang zh`（`make book-pi` / `book-pi-all`） |
| `opencode` | 《OpenCode：从原理到实战》 | `manifest-opencode.json` | `yuyu-opencode-*` | `build --product opencode --lang zh --pdf --epub`（`make book-opencode-all`） |
| `deepseek` | 《DeepSeek Harness：插件化运行时》 | `manifest-deepseek.json` | `yuyu-deepseek-*` | 同上（`make book-deepseek-all`） |
| `hermes` | 《Hermes Agent：记忆、技能与持续任务》 | `manifest-hermes.json` | `yuyu-hermes-*` | 同上（`make book-hermes-all`） |
| `codex` | 《Codex CLI：执行边界与工程实践》 | `manifest-codex.json` | `yuyu-codex-*` | 同上（`make book-codex-all`） |
| `prompt` | 《提示词工程：从提问到 Agent 协作》 | `manifest-prompt.json` | `yuyu-prompt-*` | 同上（`make book-prompt-all`），随书练习包另见下 |
| `kimi` | 《Kimi Code：从插件到审查助手》 | `manifest-kimi.json` | `yuyu-kimi-*` | 同上（`make book-kimi-all`） |
| `collected` | 《Agent Harness 九卷合订本》 | `manifest-collected.json` | `yuyu-collected-*` | `build --product collected --lang zh`（`make book-collected`） |

御舆、omp、pi 各有一套通俗层登记表：`plain.registry_names()` 按 manifest 的 `product` 字段
取同名兄弟文件——御舆用裸名（`glosses.json` / `notes.json` / `reading-paths.json`），
omp 用 `-omp` 后缀，pi 用 `-pi` 后缀（`glosses-pi.json` / `notes-pi.json` / `reading-paths-pi.json`），
写第二分册的通俗层不会顺手改到第一分册。`omp` 过去走 `--no-plain` 整层跳过，M2 之后已不传该
开关；`--no-plain` 仍是 `python -m yuyu_book` / `bookctl build` 的正式开关，留着出「无通俗层」对照排版。插画双轨：正文
`omp/images/` 手绘嵌入 + Mermaid 管道。不要用 `make book` 编 omp。

## Agent 分册

六本 Agent 分册共用 `manifest-<product>.json` / `sources-<product>.json`，各有前言、十八章和
附录 A–D（23 个单元），中文单语，产物前缀 `yuyu-<product>`，由 `make book-agents` 一次编完，
CI 的 `agent-volumes` 任务按同一矩阵逐个构建 HTML、PDF、EPUB。

- `opencode`、`deepseek`、`hermes`、`codex` 带完整通俗层：guides、reading-paths、
  `subject-index-*`、`revisions-*` 都是自己的文件，`docs/agent-series/sources.lock.json`
  固定四个上游提交。
- `prompt`、`kimi` 声明 `plain_optional`，不带通俗层，因此没有 guides、索引和修订页；
  书架形状与另四册相同，`yuyu-book/tests/test_agent_products.py` 分开校验这两类契约。
  两册的上游钉版各记在自己的 `facts/source-lock.json`。
- `prompt` 另发随书练习包 `yuyu-prompt-zh-examples.zip`，由
  `python scripts/package_prompt.py --output yuyu-book/dist/yuyu-prompt-zh-examples.zip`
  重建；包内 `package-manifest.json` 记录全部源文件摘要，同一份源重打包得到同一字节。

## 合订本

`collected` 把九卷合成一本：`manifest-collected.json` 的 `volumes` 逐卷引用各自的
manifest 与 sources，卷宗、卷目录和页码层级由 `build_collected()` 生成。`load_collection()`
只做一件事——拒绝两卷共用同一个页面锚点或重复的卷 ID，否则合订本会出现两个同名页。
合订本只出中文，并且只出单文件 HTML：九册把全部图版内联进同一份文档（2026-11-12 实测 72.5 MB、9 卷 228 个单元 308 张图版、本机 86 秒），再复制成 PDF/EPUB 既拖长构建也没有阅读收益。`make book-collected` 与 CI 的 `collected` 任务都只构建这一个 HTML；拉取请求阶段由构建器套件覆盖装载与锚点契约。

这条路径长期卡在 `iter_doc()` 的注释扫描上：它每个分块都把文档余下部分重扫一遍，6 MB 的书要 381 秒、60 MB 的分册要 564 秒，合订本因此永远跑不完。改为记住下一个 `<!--` 的位置后，同样的 60 MB 只要 4.1 秒，全文分块逐字节不变。

## Omp 英文开启条件

`en/omp/` 当前只有预留说明，`manifest-omp.json` 保持 `langs=["zh"]`。
开启英文需按以下顺序完成：

1. 翻译前言、33 章和五篇附录，为 39 个 unit 增加真实的 `en` 源路径。
2. 补齐 guides、glosses、notes、reading-paths 的英文内容及插画标签；核对双语结构与引用，检查未翻译汉字。
3. 将 manifest 的 `langs` 扩为 `['zh', 'en']`，同时更新产品隔离测试中「仅中文」的明确断言。
4. 对 omp 跑双语 `--check` 与 HTML/PDF 构建，再扩 CI 的语言覆盖；御舆仍保留自己的 20 单元契约。

`shared_with` 是 omp 词条到御舆词条的对照 ID，不参与正文替换，也不让构建器合并两册登记表。
对照面来源独立登记，不能用它支撑 omp 的 CLI 行为。

## Pi 分册

`pi` 是第三分册，31 个 unit（1 前言 + 25 章 + 5 附录），中文单语，写作钉 **pi/1.5.0**。
它与另两册共用构建器，但登记表、插画托盘（`yuyu-book/illustrations-pi/`，48 份）和产物前缀都是自己的：
`make book-pi` 只编 pi，`make book` / `make book-omp` 不会碰它。

通俗层已经接入：12 个词条、31 条 lead band、31 条眉批、156 枚档位芯片、218 处虚线术语标记。
主题索引 37 个词条，含 pi-purge，单独写 `subject-index-pi.json`，不碰御舆的索引。英文版尚未开始；`langs` 只有 `zh`。
构建口径、页数与体积见 `pi/README.md` 与 `pi/VERIFY.md`，接入改动清单见 `pi/BUILD-PLAN.md`。
