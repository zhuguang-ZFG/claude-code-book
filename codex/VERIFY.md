# Codex CLI 验证记录

日期：2026-11-10。基线：rust-v0.167.0，提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。

## 已完成

读取固定提交的 CLI、exec 参数与运行入口、项目指令、配置、execpolicy、app-server、插件清单、Hook 发现/信任与技能入口。官方当前文档通过 Context7 读取，和钉版事实分开引用；直接网页抓取失败，未声称保存了官网快照。

本机 npm 与 Windows x64 原生程序版本均为 0.167.0。真实 CLI 运行八项检查全部通过：

| 检查 | 结果 |
| --- | --- |
| git status 前缀 | allow |
| git diff 前缀 | allow |
| git push 前缀 | prompt |
| git push --force 前缀 | forbidden，保留两条命中 |
| 未列出的 git commit | matchedRules 为空、无 decision |
| 绝对路径 git.exe | 默认检查无匹配 |
| 错误的 match 正例 | CLI 非零退出 |
| app-server 静态 schema | 生成 322 份 JSON，包含四个关键方法 |

运行命令和驱动见 [examples](examples/README.md)，脱敏结果见 [facts](facts/local-cli-20261110.json)。程序与输入文件摘要记录在结果中。没有执行示例中的 Git 推送，没有创建代理任务会话，没有调用外部模型。

深化版新增两组实际运行：

- `python -B codex/examples/check_workshop.py`：十三项原创离线检查。临时副本中的运费错误版 exit 1、修复版 exit 0；直接启动 Python Hook 处理器验证正常、拒绝与坏输入；检查 JSONL 的成功、失败命令、不完整终态、进程非零、坏数据与失败补丁；核对插件声明资源和处理器副本。[结果与输入摘要](facts/workshop-20261110.json)。
- `python -B codex/examples/check_protocol.py --schema DIR --hooks-schema DIR`：十一项静态校验。七份 app-server 参数/结果、错误字段名、两份 Hook 输入输出和缺少 turn_id 的反例。使用 jsonschema 4.26.0 与固定 CLI/源码的 schema；未打开服务连接。[结果与 schema 摘要](facts/protocol-20261110.json)。

补读固定源码的技能发现/解析、插件清单解析、Hook matcher、输出语义、事件汇总、命令运行、并发分发与包内容指纹。新增解释固定到同一提交，尤其区分 schema 可表达值与运行时支持的字段组合。

## 未验证

截至 2026-11-10，未验证首次在线安装、真实认证与模型请求、由 Codex 完成完整修复任务、审批 UI/自动审查、平台沙箱文件和网络边界、由宿主发现/信任/触发及取消 Hook、MCP、resume/fork、跨平台行为。2026-11-18 新增的沙箱初始化与 MCP 进程实验见文末；直接运行原创处理器与静态消息校验不替代宿主实验。

## 书稿与构建

0.2.0 中文稿包含前言、18 章及附录 A–D，共 23 个阅读单元，约 5.3 万中文汉字。专属 manifest、来源、阅读路径、术语、阅读提示、索引与修订表已更新。深化稿装配检查通过：15 幅图、88 条引用、23 条阅读提示；15 张 Mermaid 全部解析通过，37 个固定源码文件或目录链接都存在于固定 Git 树中。新增四幅图解释命令数据、审批分层、Hook 分支和双向协议。

装配命令：`python scripts/bookctl.py build --product codex --lang zh --check --mermaid source`。本地 HTML/PDF/EPUB 由统一构建主线生成并检查，最终文件位于主工作区 `yuyu-book/dist/`；实际产物状态以主线交付记录为准。


## 本地成品

0.1.0 初版于 2026-11-10 生成 HTML、PDF（96 页）和 EPUB，并复制到主工作区 `yuyu-book/dist/`。PDF 包含 29 个书签，EPUBCheck 5.4.0 零错误、零警告。[初版交付记录](../docs/agent-series/local-publication-20261110.json)保留当时校验值。

0.2.0 深化稿本轮仅做装配和示例验证，PDF/EPUB 由主线统一重建；不能用初版文件的页数与校验值表示新版已出版。


## 深化版成品交付

v0.2.0 已在本机重建：PDF 147 页、30 个书签；EPUBCheck 5.4.0 零错误、零警告。四册封面、章节排版、目录、示例页与索引已抽查。文件已校验复制到 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`，旧初稿另存 `.ebook-validation-tools/agent-drafts-20261110`。[交付摘要](../docs/agent-series/local-publication-20261110-revised.json)保留大小与 SHA-256。

## 0.2.1 阅读修订

本次修改正文表达与导读，保留既有实验范围。重新生成的 PDF 为 144 页、30 个书签；EPUBCheck 5.4.0 零错误、零警告。代码围栏、图示、行内代码、表格、标题、链接和显式 ID 均与修订前比对一致。[当前交付记录](../docs/agent-series/local-publication-20261110-reading.json)对应主 dist 文件；前述记录保留为历史版本。

## 0.2.2 跟做路线与索引

正文补清执行目录、实例状态和首次阅读入口；原有代码与实验范围保持。新版 PDF 为 146 页，EPUBCheck 5.4.0 零错误、零警告。索引完成窄屏、深色和打印布局检查；本地文件摘要见[当前记录](../docs/agent-series/local-publication-20261110-reader-path.json)，前述构建记录为历史版本。

## 2026-11-18 离线故障恢复复核

原生程序、输入文件摘要和逐项输出见[2026-11-18 记录](facts/recovery-20261118.json)。批量记录器嵌套启动实验时另观察到 `CreateRestrictedToken failed: 87`，随后两次直接运行通过。错误发生在恢复后的令牌创建阶段，原因尚未确定。

Windows，Node.js 24.14.0／Python 3.13.14。本次运行使用 Codex CLI 0.167.0 Windows 原生程序、随书 Hook 以及本地 MCP 处理器。案例见第 8.10 节。

```powershell
python -B codex/examples/check_windows_recovery.py $codexBinary
```

- [x] 同名文件占用 `.sandbox` 导致错误 183，子进程没有输出。保留文件并腾出位置后，原命令返回 0 并输出 `BOOK_READY`。
- [x] 真实 `execpolicy check` 对练习中的发布命令返回 `prompt`。固定版 CLI 导出的 schema 接受失败与成功的 setup 通知、同一审批请求的 `decline` 与 `accept` 应答样例。
- [x] Hook 错误走 stderr 与退出码 1。MCP 错误入口能保存配置但无法启动，更正入口后通过 stdio 列出 `get_rule`。

`$codexBinary` 的准备方法和跨目录示例依赖见 [examples/README.md](examples/README.md)。沙箱是实际启动，审批是协议样例，Hook 和 MCP 进程由驱动直接调用。
