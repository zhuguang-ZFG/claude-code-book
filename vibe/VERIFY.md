# 验证记录

## 2026-11-16 · 第三批正文手绘与文风三轮

给尚无插图的五章补正文手绘，全部为无文字的线描（沿用 `illustrations-agents/` 现有风格，`currentColor`、单 `viewBox`、无 id/href/script）：

- `vibe-ch01-split.svg`：模型铺结构（打字机与积木块），人写条件（清单与阀门）。
- `vibe-ch03-cases.svg`：正常例、边界例、反例三张卡片汇入同一个程序。
- `vibe-ch05-checkpoint.svg`：一页只改一行，逐版存档，落在提交印章上。
- `vibe-ch08-lens.svg`：放大镜只照文件里决定风险的那几行。
- `vibe-ch12-baton.svg`：装着“运行、规则、决策”三样东西的交接包，从一只手递到另一只手。

五幅图先在 Chromium 里逐幅渲染成 PNG 目检（构图、越界、遮挡），其中第 3、12 章两幅按目检结果重画一稿后再进构建。

文风三轮（主书）：`05-设置与配置` 删“从这些功能标志可以看出”并去掉“演进路径”复用；`09-子智能体` 删“简言之”；`03-工具系统` 把“统一的抓手”改为“统一的依据”，章尾“在下一章中，我们将深入”改为直陈。全书扫描“值得注意的是/总而言之/综上所述/让我们/赋能/抓手”等模式，正文命中仅剩上述已改处。

校验：

```bash
python scripts/bookctl.py build --product vibe --lang zh --check
python scripts/bookctl.py build --product vibe --lang zh --pdf --epub
python -m unittest yuyu-book.tests.test_illustrations yuyu-book.tests.test_art yuyu-book.tests.test_mixed_art -q
python scripts/check_book.py
```

```text
yuyu-vibe-zh.html  0.4 MB / 17 units / 14 plates / 13 cited links / 3 headpieces
yuyu-vibe-zh.pdf   4.5 MB / 81 页 / 21 书签 / 0 空白页
yuyu-vibe-zh.epub  239,931 B / 6 张图 / 139 条导航
test_illustrations + test_art + test_mixed_art   45 tests OK
check_book.py   447 Markdown files, 438 Mermaid diagrams, 0 errors
```

## 2026-11-15 · 恢复演练与 CI 门槛

第 10 章在备份之后补“恢复也要演练”：把备份复制到临时副本，对照主库的 `books`/`contacts` 行数，并检查 `public_books` 的列不含 `email` 或 `contact`。第 11 章在发布检查单之后补 GitHub Actions 工作流：跑单元测试、生成样例页面，再用缺失输入断言非 0 退出且不留产物；示例注明 action 标签会移动，生产仓库应固定到完整 SHA。

恢复命令已在临时库上实跑：`live: (1, 1) restored: (1, 1)`，`public_books` 列为 `id,title,author,condition,owner`，样例查询返回书名与摊主。CI 工作流用 PyYAML 解析通过；示例命令指向读者的样例项目，不在本仓库根目录执行。

```text
yuyu-vibe-zh.html  0.4 MB / 17 units / 9 plates / 13 cited links / 3 headpieces
yuyu-vibe-zh.pdf   4.4 MB / 77 页 / 21 书签 / 152 个链接 / 0 空白页
yuyu-vibe-zh.epub  239,734 B / 6 张图 / 139 条导航
```

## 2026-11-15 · 插图与文风二轮

给新增章节补七幅正文手绘，并按风险顺序补了一节评审清单：

- `vibe-ch02-card.svg`：任务卡的五个部分与一支笔。
- `vibe-ch04-paths.svg`：输入、程序、输出三个位置与回退基线。
- `vibe-ch06-report.svg`：命令、输入、期望、实际四行现场。
- `vibe-ch07-loop.svg`：失败测试 → 只改一处 → 通过，三帧胶片。
- `vibe-ch09-gates.svg`：单元、端到端、人工、回滚四道门。
- `vibe-ch10-boundary.svg`：私密联系方式、数据库与公开窗口之间的围栏和锁。
- `vibe-ch11-atomic.svg`：旧版、临时产物、新版与失败丢弃路径。
- 第 12 章新增“评审时按影响面排序”，把行为、数据边界、失败路径、测试、依赖与许可证排在样式之前；Google 工程实践只作类别参照，链接仍指向附录 B.3。

文风二轮集中在新增章节：删掉“这一章”自称、`真正的`、`才算` 等模板句；把“四层缺一不可”改成“四层各管一段”，把“精通阶段不是功能更多”改成“看别人能否接手”。

```bash
python scripts/bookctl.py build --product vibe --lang zh --pdf --epub
```

```text
yuyu-vibe-zh.html  0.4 MB / 17 units / 9 plates / 13 cited links / 3 headpieces
yuyu-vibe-zh.pdf   4.4 MB / 75 页 / 21 书签 / 152 个链接 / 0 空白页
yuyu-vibe-zh.epub  238,256 B / 6 张图 / 138 条导航
```

校验：

```text
python scripts/check_book.py                 447 Markdown files, 438 Mermaid diagrams, 0 errors
python -m unittest discover -s yuyu-book/tests -q   604 tests OK
python -m unittest discover -s tests -q             292 tests OK
python -m ruff check yuyu-book scripts video tests  All checks passed
```

## 2026-11-15 · 0.2.0 内容重构

把试读版从 8 章扩成 12 章 + 附录 A–D，并做去 AI 味与来源补充：

- 三篇结构：入门（第 1–4 章）、进阶（第 5–8 章）、精通（第 9–12 章）。
- 新增第 4、7、10、11 章及附录 D；重排旧章并更新前言、README、术语表。
- 附录 B.3 增加五本社区开源书（固定提交、许可证、阅读问题），`sources-vibe.json` 同步 5 条 `vibe-book-*` 来源；5 个 `/tree/<sha>` 链接在 2026-11-15 返回 HTTP 200。
- 全书扫掉“本章动作”“短合同”“缝/吵架”“骨架”“安全绳”“隐藏不等于禁止”等模板句；路线图引言对 vibe 改为平实说明，主书保留原比喻。

```bash
python scripts/bookctl.py build --product vibe --lang zh --pdf --epub
```

```text
yuyu-vibe-zh.html  0.4 MB / 17 units / 2 plates / 13 cited links / 3 headpieces
yuyu-vibe-zh.pdf   4.2 MB / 71 页 / 21 书签 / 151 个链接 / 0 空白页
yuyu-vibe-zh.epub  237,418 B / 6 张图 / 137 条导航
```

校验：

```text
python scripts/check_book.py                 447 Markdown files, 438 Mermaid diagrams, 0 errors
python -m unittest discover -s yuyu-book/tests -q   604 tests OK
python -m unittest discover -s tests -q             292 tests OK
python -m ruff check yuyu-book scripts video tests  All checks passed
```

功能抽查：第 7 章同名不同作者测试在旧键下失败（`AssertionError: 1 != 2`），改为 `title + author` 后通过；第 9 章改讲缺输入、退出码、旧产物与回滚；第 10 章 SQLite 唯一约束与公开视图沿用已实测示例；第 12 章补依赖、许可证、来源与技术债交接。

## 2026-11-15 · 排版修订

修掉主书模板文案与空页，并给三个篇题补手绘墨版。

```bash
python scripts/bookctl.py build --product vibe --lang zh --pdf --epub
```

```text
yuyu-vibe-zh.html  305 KB
yuyu-vibe-zh.pdf   3.3 MB / 47 页 / 16 书签 / 90 个链接
yuyu-vibe-zh.epub  220 KB / 6 张图 / 92 条导航
```

```text
[zh]
  yuyu-vibe-zh.html: 0.3 MB, 12 units, 2 plates, 8 cited links, 0 glosses,
  0 lead bands, 0 tier chips, 0 emblems, 3 headpieces, 0 keeper notes
CHECK OK
```

改动：线路图按实际单元数改写章数；没有修订条目时不再输出空白“版本与修订”页；
无序列表只保留一枚菱形；正文首字下沉只在主书启用；第 6 章删去与风险表重复的高图，
把被挤到下一页的半页空白收回；三个篇题各加一幅 `part-vibe-p*.svg`。

## 2026-11-15 · 首次装配

命令：

```bash
python scripts/bookctl.py build --product vibe --lang zh --check
```

最终产物（同一命令加 `--pdf --epub`）：

```text
yuyu-vibe-zh.html  314 KB
yuyu-vibe-zh.pdf   3.3 MB / 49 页 / 16 书签 / 90 个链接
yuyu-vibe-zh.epub  272 KB / 4 张图 / 93 条导航
```

结果：

```text
[zh]
  yuyu-vibe-zh.html: 0.3 MB, 12 units, 3 plates, 8 cited links, 0 glosses,
  0 lead bands, 0 tier chips, 0 emblems, 0 headpieces, 0 keeper notes
CHECK OK
```

390 px（Playwright，Chromium，`document.fonts.ready`）：

```text
title  Vibe Coding：把想法做成能跑的软件 — 朱光
width  390
chapters 8
figures 3
图内最小文字 11.97 px（有效字号＝computed font-size × SVG CTM 缩放）
```

## 示例程序

书中 `shelf.py` 与 `test_shelf.py` 在 Python 3.12 下运行：

```text
python shelf.py books.csv -o shelf.html
卡片：4
重复组：2
跳过行：5、9
EXIT:0

python -m unittest test_shelf.py -v
Ran 4 tests ... OK
```

缺失输入：

```text
python shelf.py missing.csv
无法读取 missing.csv: [Errno 2] No such file or directory
EXIT:2
```

`test_missing_input_leaves_no_output` 同时确认没有留下目标文件。

## 来源核对

附录 B 的六个 GitHub 固定提交在 2026-11-15 逐个请求 `/<repo>/commit/<sha>`，均返回 HTTP 200；构建器把来源页链接写成 `/tree/<sha>`，读者看到的是同一提交。

## 未测范围

- 没有用真实模型或具体 Agent 产品重跑生成过程；书中的模型行为描述是方法说明，不是产品能力证明。
- PDF/EPUB 的字体嵌入与分页随构建机字体变化；本记录只覆盖 HTML 装配与浏览器检查。
- 附录 B 的 GitHub 链接固定在提交上，仓库后续变化未跟踪。
