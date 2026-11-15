# 验证记录

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
