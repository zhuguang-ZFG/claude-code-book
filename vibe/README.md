# Vibe Coding：把想法做成能跑的软件

从一句需求出发，用旧书交换市集的 CSV 走完任务卡、样例、十分钟循环、报错定位、风险边界、验收与交接。中文技术试读版，8 章 + 附录 A–C。

## 读什么

| 部分 | 章节 | 留下什么 |
| --- | --- | --- |
| 起步 | 第 1–3 章 | 任务卡、输入输出样例、否定验收 |
| 迭代 | 第 4–6 章 | 可运行的 `shelf.py`、最小复现、风险分级 |
| 交付 | 第 7–8 章 | 测试、回滚、交接包 |

## 构建

在仓库根目录：

```bash
python scripts/bookctl.py build --product vibe --lang zh --pdf --epub
```

或：

```bash
make book-vibe-all
```

产物写入 `yuyu-book/dist/`：`yuyu-vibe-zh.html`、`.pdf`、`.epub`。

## 验证

- `python scripts/bookctl.py build --product vibe --lang zh --check`：结构、锚点、来源与图版检查通过。
- 书中的 `shelf.py` 与 `test_shelf.py` 已在 Python 3.12 下用 8 行 fixtures 实际运行：4 张卡片、2 个重复组、跳过第 5/9 行，缺输入时退出码 2 且不生成输出。
- 390 px 浏览器实测：文档宽度等于视口；Mermaid 图内文字最小有效字号 11.97 px（按 SVG 缩放折算，不取行盒高度）。

完整运行记录与未测范围见 [VERIFY.md](VERIFY.md)。
