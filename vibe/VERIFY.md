# 验证记录

## 2026-11-15 · 首次装配

命令：

```bash
python scripts/bookctl.py build --product vibe --lang zh --check
```

最终产物（同一命令加 `--pdf --epub`）：

```text
yuyu-vibe-zh.html  314 KB
yuyu-vibe-zh.pdf   3.3 MB / 49 页 / 16 书签 / 90 个链接
yuyu-vibe-zh.epub  273 KB / 4 张图 / 93 条导航
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
图内最小文字 12.14 px
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
