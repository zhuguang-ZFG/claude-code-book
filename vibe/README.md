# Vibe Coding：把想法做成能跑的软件

从一句需求出发，用旧书交换市集的 CSV 走完任务卡、样例、十分钟循环、报错定位、回归测试、风险边界、数据权限、部署与交接。中文技术试读版，12 章 + 附录 A–D。

## 读什么

| 部分 | 章节 | 留下什么 |
| --- | --- | --- |
| 入门 | 第 1–4 章 | 任务卡、输入输出样例、可运行的最小版本和回退点 |
| 进阶 | 第 5–8 章 | 十分钟循环、最小复现、回归测试、风险分级 |
| 精通 | 第 9–12 章 | 四层验收、数据与权限、部署记录、交接包 |

附录 A 是三张模板，附录 B 是固定提交的 GitHub 书目（含五本社区开源书），附录 C 是术语表，附录 D 是从入门到精通的三阶段练习路线。正文另有五幅手绘说明图和两幅流程图。

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
- 第 7 章的同名不同作者测试在旧去重键下失败（`AssertionError: 1 != 2`），改为 `title + author` 后通过。
- 第 10 章的 SQLite 结构已实测：重复插入被唯一约束拒绝，公开视图不包含联系方式。
- 390 px 浏览器实测：文档宽度等于视口；Mermaid 图内文字最小有效字号 11.97 px（按 SVG 缩放折算，不取行盒高度）。

完整运行记录与未测范围见 [VERIFY.md](VERIFY.md)。
