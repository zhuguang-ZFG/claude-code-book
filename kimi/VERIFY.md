# Kimi Code 分册验证记录

日期：2026-11-10。钉版 2.5.2，提交 `1c142a007c10e881602690def96057c23a2baa12`。

## 实际完成

- 本机发布 CLI 2.5.2；参数与 ACP 握手记录见 [cli-2.5.2.json](facts/cli-2.5.2.json)。独立临时数据根，0 次模型请求。
- 原创库存样例：8 个输入中，故意错误的实现 3 项通过，参考实现 8 项通过。
- `python -m unittest discover -s kimi/examples -p "test_*.py" -v`：5 个测试方法通过，包含多个 Hook 子进程、MCP 请求与库存守恒输入。
- 真实固定源码组件：12 个场景通过，见 [source-probes.json](facts/source-probes.json)。读取上游原文件并编译，未重写解析器替代它。

## 范围

组件探针环境为 Node 24.14.0 / esbuild 0.28.2，低于上游完整工程声明的 Node 24.15.0 下限；只记录所测组件，不声称完整工程在此版本受支持。

尚未验证：完整模型审查、TUI 插件安装与热重载、模型通过 MCP 查询、真实 IDE 的 ACP 会话与反向调用、其他操作系统的完整宿主。书中将这些步骤标为读者练习。

固定源码、许可证和关键输入摘要见 [source-lock.json](facts/source-lock.json)。构建与成品验证另记实际结果，不由上述组件实验替代。

### 2026-11-12 重建

构建器改版后重出三格式：HTML 0.5 MB、PDF 80 页 28 书签、EPUB 332 925 字节，23 个单元齐全。
首轮重建在 PDF 补页码阶段失败：目录跨到第二页后，扫描只从最后一个命中「目录」的页面开始，
前半目录 11/28 行没有拿到页码。修法是 `contents_span()` 从第一个命中页开始扫，
并补 `yuyu-book/tests/test_pdf.py` 的 ContentsPages 用例；修后重建通过。
页数比 11-10 的 84 页少，来自版式调整，不是删章；上文保留当日结果。

## 成品验收

- `python scripts/bookctl.py check --fast`（`make check` 的同一入口）：8 步通过，仓级 228 项与构建器 573 项测试通过。
- 三格式构建通过：23 个单元、18 章、6 张 Mermaid 图；PDF 84 页、29 个书签。
- EPUBCheck 5.4.0：0 fatal、0 error、0 warning。
- HTML 在禁用 JavaScript 的 390 px 浅色、1280 px 深色与打印模式中检查：无横向溢出、失效内部锚点或索引重叠。实际代码文字的最低对比度分别为 5.94、6.80、5.99。
- PDF 全页文字范围检查无越界、无替换字符、无空白页；封面、插件、Hook、ACP、JSONL 和索引样页已目视审阅。
- 修复包含“目录”的附录条目导致 PDF 漏补页码的问题，并补回归用例；全书线路图由清单计算实际章节数。
- 第 16 章 UTF-8 保存方式已在 PowerShell 5.1 实测，保留中文与退出码，见 [记录](facts/powershell-utf8.json)。

产物摘要、书稿摘要与版面检查见 [publication-2026-11-10.json](facts/publication-2026-11-10.json)。本次为本地验收，未将远程 GitHub Actions 标为通过。
