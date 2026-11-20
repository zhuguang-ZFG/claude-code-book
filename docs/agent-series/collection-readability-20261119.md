# 合集阅读修订记录

日期：2026-11-19。范围为书稿与本地构建器，产品版本沿用各卷原基线。

## 阅读入口

- 新增[合集导读](../../合集导读.md)，按任务提供四条起步路线、十卷入口、七项故障速查和证据范围说明。
- 修订十个卷首说明，删除过时卷数和没有比较实验支撑的强弱排序。
- 同步 Pi、Hermes、Codex、DeepSeek、Kimi 前言，让上一批恢复实验可以从各卷入口找到。
- README 区分历史成品数据和当前书稿；合集保留分卷章节号与索引，PDF 使用连续页码。

## 合集导航

- 合集导读进入总目录、侧栏和 PDF 书签；窄屏提供返回导读与目录的常驻入口。
- 跨卷 Markdown 章节链接使用整本的目标表，已收录章节在单文件内跳转。仓库脚本与独立验证记录仍是外部链接。
- PDF 页码清单补入卷标题，避免目录中卷名有位置却没有页码。
- 保留各卷来源与索引入口，侧栏补上章节号和卷首链接。
- 构建前拒绝卷标题、导读、章节或保留页面之间的锚点冲突。
- 修复窄屏长标题挤出章徽的问题；导读表头允许换行，390 像素宽度下三张表均无需横向滚动。

## 验证

本轮在 Windows 本地完成以下检查，结果与产物摘要见[验证数据](collection-readability-20261119.json)。

| 检查 | 实际结果 |
| --- | --- |
| `python scripts/bookctl.py check --fast`（Windows 上与 `make check` 相同） | 9 项检查通过：通用测试 332 项、构建器测试 616 项，共 948 项；内容、Mermaid 和衍生产物检查均通过 |
| 十卷合集源码装配与完整 HTML 渲染 | 10 卷、246 个正文单元、333 幅图版、813 条旁注、182 处导读条、113 条编者札记；HTML 约 74.6 MB |
| 浏览器实测 | 最终完整 HTML 在 1440 像素宽屏浅色、390 像素窄屏浅色与深色均无整页横向溢出；窄屏导读三张表的表头换行，表格宽 324 像素且无内部横向滚动 |
| 窄屏导航 | 从导读进入 Pi 恢复小节，再通过常驻入口返回导读，均成功 |
| PDF 扩展抽检 | 30 页，覆盖封面、导读、目录首末页、十卷卷首与首章、65 幅横向图版中的首/中/末幅、附录及末页；未发现裁切；目录末页现为第 22 页，附录 D 与“来源与许可”同页 |
| 全量构建 EPUB 阅读器 | SumatraPDF 成功打开本地 EPUB，分页控件显示 2,382 个重排页；未逐页通读 |
| 完整 PDF | 1,924 页、322 个书签、87 个索引页码，97,182,780 字节；全书空白页为 0，322 行目录页码及书签目标全部核对通过 |
| 全量构建 EPUB（目录层级调整前） | 52,918,403 字节、604 张图片、2,426 条导航；6,670 处内部引用无断链、无重复 ID；EPUBCheck 5.4.0：0 fatal、0 error、0 warning、0 info |
| 导航更新后的 EPUB | 52,921,213 字节、605 张图片、2,426 条导航（325 个顶层、2,101 个嵌套）；ZIP/XML 检查通过，3,526 处正文片段引用与 2,426 个目录链接均无断链；未重跑 EPUBCheck 或阅读器检查 |

完整 HTML、PDF 和 EPUB 的复建命令：

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$env:PLAYWRIGHT_NODEJS_PATH = 'C:\Program Files\nodejs\node.exe'
python scripts/bookctl.py build --product collected --lang zh --pdf --epub --out-dir .scratch/collection-improved-20261119
```

完整产物位于 `.scratch/collection-improved-20261119/`，文件名为 `yuyu-collected-zh.html`、`yuyu-collected-zh.pdf` 和 `yuyu-collected-zh.epub`；同目录保存构建报告与最终验证记录。本地构建产物与 30 页 PDF 联系表不随源码提交。

本次完整构建退出码为 0，耗时约 37.7 分钟。环境为 Windows 11、Edge 157.0.4341.60、微软雅黑；目录末尾“来源与许可”调整后与附录 D 合页，合订本从 1,925 页降至 1,924 页。PDF 保持 322 个有效书签，87 个索引页码回填后页码稳定；全量构建 EPUB 使用同一份 HTML，内部链接检查无断链。随后使用同一份 HTML 单独重建 EPUB，生成按标题层级嵌套的目录；ZIP、XML、正文片段链接和目录链接检查通过，未再次运行 EPUBCheck 或阅读器。

抽检 30 页 PDF 联系表，覆盖十卷卷首与首章、三幅横向图版和书末附录；页面清晰，未发现裁切，末尾目录内容完整。EPUBCheck 5.4.0 与 SumatraPDF 的结果对应导航调整前的全量构建版本；后续重建版仅完成上表记录的结构与链接检查。

历史成品的页数与摘要仍只对应此前构建。本轮排版验证不扩展五组恢复实验的覆盖范围，不代表真实模型任务、登录授权或平台投递已经验证。

## 2026-11-20 补充：离线 EPUB 按篇拆文档

上表「导航更新后的 EPUB」一行只做过结构检查，没重跑 EPUBCheck。本轮补齐，并把离线版的结构对齐到参考书的做法（每章一个 XHTML 文档）：

- 正文不再是单个 `content.xhtml`。按文章（章、卷首、篇分隔、来源页、页脚）拆成独立文档，合订本 326 个文档，最大的正文一篇 190 KB（`ch15`，导航文件 `nav.xhtml` 321 KB）；拆分前的单文档为 6.0 MB。
- 每篇文档的 `<title>` 取自篇内首个 h1/h2，阅读器目录和状态栏显示章节名，不再一律显示书名。
- 封面图在 OPF 里以 `properties="cover-image"` 声明，供阅读器缩略图使用；EPUB 3 推荐此写法，未加已弃用的 `<meta name="cover">`（加它会触发 EPUBCheck 警告）。
- 屏幕专用的 `no-print` 合集跳转栏不再进入离线版；清理后只剩空壳的块不生成文档。书名去掉「— 作者」后缀。

验证（2026-11-20，Windows 11）：

| 检查 | 实际结果 |
| --- | --- |
| `python scripts/bookctl.py build --product collected --lang zh --epub --out-dir .scratch/epub-split2` | 退出 0；HTML 74.6 MB、246 个正文单元、333 幅图版；EPUB 53,396,104 字节、604 图、502 张栅格化 SVG、2,426 条导航、326 个文档、封面项 `image-0` |
| EPUBCheck 5.4.0（`scripts/check_epub.py`，expanded 模式） | 0 fatal / 0 error / 0 warning / 0 info |
| 内部引用审计（同文档片段 + 跨文档 + nav + 目录） | 5,950 处链接（同文档 953、跨文档 4,997），0 断链；1,043 处图片与样式引用全部存在；327 个 XHTML（含 nav）无空文档 |
| `python -m unittest discover -s tests` | 345 项通过 |
| `python -m unittest discover -s yuyu-book/tests` | 616 项通过 |

拆分、跨文档链接与封面声明由 `tests/test_epub_splitting.py` 钉住；把该文件放到拆分前的单文档构建器上，fixture 初始化即报 `dangling internal link #toc`、`Ran 0 tests`——旧构建器不通过这套测试，但各条断言并未逐条在旧构建器上执行过，这是套件级失败，不是逐用例失败。同一文件里的「未知锚点中止构建」用例守的是原有的死链检查，不构成拆分回归的证据。EPUBCheck 用本机 5.4.0 版（`.scratch/collection-readability/epubcheck-5.4.0/`），与 CI 下载的发布包同版本。阅读器逐页翻检未做，`EPUBCheck` 与链接审计只说明包结构与引用合法。

上述产物为 `.scratch/epub-split2/yuyu-collected-zh.epub`，53,396,104 字节、SHA-256 `92a53120492797452a338377f3ad82191b35f65652fd7fc5392570d6f65c03a9`，同目录的 `artifact-manifest.json` 由同一次构建写出并记录同一组数值。这个 SHA 不是构建指纹：`dcterms:modified` 取自输入 HTML 的修改时间，内容相同的两次构建会给出不同摘要。
