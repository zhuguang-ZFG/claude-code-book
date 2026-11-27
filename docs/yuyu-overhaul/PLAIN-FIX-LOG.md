# PLAIN-FIX-LOG — 御舆通俗层审计（Y-M2）

对象：`yuyu-book/glosses.json`（术语）、`notes.json`（按语）、`reading-paths.json`（档位）、`manifest.json` 的 20 条 guides。
判定器：`yuyu-book/yuyu_book/plain.py` 的 `validate_plain` / `validate_notes`，由 `build.py --check` 调用。

## Step 3：`--check both` 首跑结果

```
python yuyu-book/build.py --lang both --check
[zh] yuyu-agent-harness-zh.html: 5.8 MB, 20 units, 176 plates, 3 cited links,
     296 glosses, 20 lead bands, 105 tier chips, 20 emblems, 4 headpieces, 20 keeper notes
[en] yuyu-agent-harness-en.html: 5.9 MB, 20 units, 176 plates, 3 cited links,
     303 glosses, 20 lead bands, 105 tier chips, 20 emblems, 4 headpieces, 20 keeper notes
CHECK OK
```

首跑即绿，**没有** 悬空的 `file:line`、没有词形对不上、没有缺失按语。所以本里程碑没有「修证据」这一项工作，只有一处主动收尾（见下）。

两个语言版本的 gloss 数不同（296 / 303）不是错：同一批术语在中英两版里的词形不同（中文版按中文词形与英文原词匹配，英文版按英文词形匹配），命中个数自然不等。

## 唯一的改动：证据去重

`ch01`、`ch05`、`apxc`、`apxd` 四条 guide 的 `plain_evidence` 里有重复条目（同一个 block id 连续写了两遍）：

| guide | 去重前 | 去重后 | 指向的语言集合 |
|-------|--------|--------|----------------|
| `ch01` | 8 条（`ch01.agent-harness` ×2） | 7 条 | 不变（zh + en） |
| `ch05` | 8 条（`ch05.b-336ab860` ×2） | 7 条 | 不变 |
| `apxc` | 8 条（两条各重复一次） | 6 条 | 不变 |
| `apxd` | 6 条（两条各重复一次） | 4 条 | 不变 |

证据去重不影响校验（校验器本来就按集合比对），改它是为了清单本身可读。`manifest.json` 的 diff 因此只有 6 行删除。

## Step 4：双开关构建对照

```
python yuyu-book/build.py --lang zh --no-plain --out-dir yuyu-book/.scratch/yuyu-no-plain
python yuyu-book/build.py --lang zh              --out-dir yuyu-book/.scratch/yuyu-plain
```

两次都退出 0；抽查产物里的真实标签（不是 CSS 里的同名类）：

| 产物 | `class="lead-band"` | `class="keeper"` | `id="keeper-notes"` | `class="gloss"` | `sec-tier` |
|------|--------------------|------------------|---------------------|-----------------|------------|
| `yuyu-no-plain` | 0 | 0 | 0 | 0 | 2（只留图例） |
| `yuyu-plain` | 20 | 20 | 1 | 296 | 107（105 枚 + 2 图例） |

也就是说 `--no-plain` 真的能把导读带、按语、术语卡与档位芯片整体关掉，不是「关了但还在」。

## 没有做的事（以及为什么）

- 没有改任何一条 guide 的文字：20 条本来就不是模板填的，`question` / `deliverable` / `boundary` 三组各 20 条互不相同，反例一条没踩（详见 `GUIDES-QA.md`）。
- 没有动 `glosses.json` 的 `LIMITS` 边界内文案，也没有为了凑数加词：现有 296 / 303 个标记点是正文真实出现的词形。
- 没有改 `reading-paths.json` 的档位：105 节的分档与正文小节一一对应，`stamp_tiers` 按渲染出的 `<h2>` 顺序盖章，长度校验通过。

## 2026-11-27：章节层级标签可读性

真实 390px 书页测量发现，`.sec-tier` 与 `.tier-chip` 的实际字号为 9.92px，低于正文版式审计采用的 10px 下限。共享样式将字号从 `.62rem` 调到 `.64rem`，实际渲染为 10.24px；颜色、边框、布局和语义不变。

新增计算样式回归 `test_section_tier_labels_keep_ten_pixel_minimum_on_phone`：旧样式下以 `9.92 < 10.0` 失败，修正后通过。主册与十二卷合订本重新构建成功；390px 与 1280px 实测所有层级标签均为 10.24px，页面宽度等于视口宽度，正文文本无越界。

## 2026-11-27：参考 zlib 手册与 GitHub 文档精修门户

参考一手资料只提炼信息架构原则，不复制文案：zlib README 先交代用途、用法示例、构建测试与变更记录；zlib 手册用编号目录和页内锚点组织长文；GitHub Docs 要求按用户任务排序、提供页内跳转、使用有意义的标题并保持可扫描。对应来源：

- https://github.com/madler/zlib
- https://www.zlib.net/manual.html
- https://docs.github.com/en/contributing/writing-for-github-docs/best-practices-for-github-docs

门户从装饰卡片页改为安静的技术文档索引：新增“跳到主要内容”和命名 `nav`，入口按入门、整书、样章、分册、图版、复习排序；移除背景渐变、卡片投影、emoji 标题、错峰入场与旋转/弹跳 hover。真实本地验收发现 `docs/portal.html` 引用的 `cover.png` 只存在于仓库根目录，干净环境会显示破图；Pages 虽会复制该资源，本地文档入口仍不需要这张非必要封面，因此移除图片，由标题与印章承担识别。保留御舆印章、共享字体/圆角、全部离线文件与 Omp 条件链接，并补 GitHub 仓库和十二卷导读入口。

新增回归 `test_front_door_is_a_quiet_document_index`：旧页面因缺少跳转链接失败，修正后通过。原 reduced-motion 测试改为“无非必要动效”契约，避免继续钉住已删除的动画。窄契约 46 项通过；真实 390px/1280px 页面 `docWidth` 等于视口、无元素越界，渐变/投影/动画/位移均为 `none`；键盘 Tab 可见聚焦跳转链接，Enter 后 `hash=#content` 且焦点落在 `main`。
