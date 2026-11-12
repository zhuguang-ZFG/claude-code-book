# 提示词工程分册验证记录

2026-11-10，中文技术试读版 0.1.0。已完成前言、十八章和附录 A–D，提供 HTML、PDF、EPUB 与独立练习 ZIP。下列结果来自本地运行；未调用模型服务。

## 已完成的检查

| 对象 | 实际结果 | 记录 |
| --- | --- | --- |
| 仓库完整检查 | 8 步通过；通用测试 259 项，构建器测试 573 项；当时检查 426 个 Markdown 文件和 436 个 Mermaid 图，无错误 | [机器报告](evidence/repository-check-full.json) |
| 独立练习工具 | 两组共 31 项测试通过；故障版 8/12，人工修复后 12/12；缺项目、语法错误与超时各有真实回执 | [修复练习记录](evidence/exercise-verification.json) |
| 最终 PDF | 107 页、29 个书签；未发现空白页、替换字符或文字超出页面 | [排版报告](evidence/layout-final.json) |
| HTML | 390 像素浅色、1280 像素深色、665 像素打印模式均无横向溢出、失效内部锚点或索引重叠；代码最低对比度分别为 6.07、6.80、6.12 | [排版报告](evidence/layout-final.json) |
| EPUB | EPUBCheck 5.4.0：0 个致命错误、0 个错误、0 个警告 | [校验报告](evidence/epubcheck-final.json) |

最终调整索引打印分页及来源条目后，另跑产品、封面和示例页面相关测试 30 项，全部通过，并重新构建三种书籍文件。人工抽看 PDF 第 1、56、60、68、77、107 页，确认索引标题与条目同页；这不等于逐页人工校对。

全稿按 humanizer-zh 的编辑约束审读，修改空泛铺垫、重复总结和无用对比；核对跨章说明、业务规则、授权范围与未测状态。保留代码、判据、引文和实测数字，不用检测器分数评价文风。

### 2026-11-12 重建

构建器改版后重出三格式：HTML 480 713 字节、PDF 99 页 27 书签、EPUB 154 384 字节，23 个单元齐全。
页数比 11-10 的 107 页少，来自版式调整，不是删章；上一节保留当日结果。

练习包的打包脚本是本轮补回的 `scripts/package_prompt.py`。以 11-10 的文本重打包，71 个成员与交付件
逐字节一致（SHA-256 `f5cab8a44c537465867f…`，与 `docs/series/prompt-package-verification-20261110.json`
的 `archive_sha256` 相同）；本轮改过本节后重打包，只有 `prompt/VERIFY.md` 与其在
`package-manifest.json` 里的摘要两处变化，其余 69 个成员不变。仓内保留的交付件就是 11-10 那一个包，
它的字节由该记录负责，不再被覆盖。

## 复做命令

使用 Python 3.11 或更新版本。练习只依赖标准库，解压后的随书包可运行：

```bash
python -m unittest discover -s tests -p "test_prompt_*.py" -v
python prompt/examples/check_workshop.py --mode reference
python prompt/examples/exercise.py prepare --out .scratch/prompt-repair
python prompt/examples/exercise.py check --project .scratch/prompt-repair --receipt .scratch/prompt-before.json
```

参考版预期 12/12；故障副本预期 8/12，最后一条命令退出码 1 表示教学用业务失败。每次使用新目录和新回执名，避免覆盖已有练习。

安装完整仓库的构建依赖后，在仓库根目录运行：

```bash
python scripts/bookctl.py check --fast
python scripts/bookctl.py build --product prompt --lang zh --pdf --epub
python scripts/package_prompt.py --output yuyu-book/dist/yuyu-prompt-zh-examples.zip
java -jar /path/to/epubcheck.jar yuyu-book/dist/yuyu-prompt-zh.epub
```

`bookctl check --fast` 是 `make check` 使用的入口。PDF 构建需要本地浏览器与中文字体。本次环境为 Windows、Python 3.13.14；EPUBCheck 使用 Java 17。校验时使用与最终 EPUB 字节一致的临时副本。

## 尚未验证的范围

新册的模型 A/B、跨模型迁移、实际宿主权限组合、独立读者试读和学习效果验收尚未完成。28 份模型请求只是已准备的输入。第 16 章引用 DMX 的固定版本实验，未在本轮复跑；单元测试中的人工响应也不计作模型成绩。

工具处理可信教学代码，不提供恶意代码隔离。业务检查只覆盖公开定义的 12 个用例，不覆盖真实身份、并发、持久化或通知发送。英文版尚未编写。

源文件指纹见 [provenance-release.json](evidence/provenance-release.json)。练习 ZIP 内的 `package-manifest.json` 对包内源文件另列哈希；书籍和 ZIP 的最终哈希保存在仓库的 [本地交付记录](../docs/series/prompt-publication-20261110.json)。
