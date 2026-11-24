# 附录 A：命令参考

<!-- block: t3code-apxa.b-opening -->
这一份速查只收官方文档明确写出的命令形态，按场景分组。参数细节会随版本变化，核对时以固定提交的文档为准；不要把这里的例子直接复制到生产环境。

## 线程相关

```sh
id=$(t3 thread start . "Find why the tests are slow")
t3 thread send "$id" "Now fix it" --wait
t3 thread show "$id"
t3 thread list
```

`.` 指包含当前文件夹的项目，或其仓库的 git worktree；也可以直接给项目 id。新线程使用项目的默认模型与权限模式，默认在项目目录运行；传入 `--worktree <base-branch>` 才会使用独立工作树。标题取消息首行，也可用 `--title` 指定。

`send` 不会打断正在运行的线程：忙的线程会把消息留到下一轮。`-` 作为消息可从标准输入读取。`--wait` 打印 agent 的回复，运行失败或停止时退出码为 1，等待人工回答时为 2。

## 模型与选项

```sh
t3 thread send "$id" "..." --provider <instance-id> --model <slug>
t3 thread send "$id" "..." --option reasoningEffort=high
```

`--option id=value` 可多次指定。选项 id 与取值由 provider 与模型决定，先查 `orchestrator_capabilities` 再写。`true` / `false` 用于开关型选项。Codex 常用 `reasoningEffort`，Claude 常用 `effort`，二者不能互换。

## 鉴权与接入

| 目的 | 命令或入口 |
| --- | --- |
| 生成配对码 | `t3 auth pairing create` |
| 让 Claude Code 接入 | `claude mcp add --transport http t3 https://<地址>/mcp` 后 `claude mcp login t3` |
| 让 Codex 接入 | `codex mcp add t3 --url https://<地址>/mcp` 后 `codex mcp login t3` |
| 复制 MCP URL | Settings → Environments → 环境菜单 → Copy MCP URL |

## 更新与后台

更新走 provably owning installer：安装器要从解析出的可执行文件路径证明自己拥有这次安装。Nix 这类固定或只读安装保持手动更新。后台状态与模型探测必须是被动的，不能因为一次状态刷新就启动会话、拉起 MCP server 或触发登录流程。

来源：[outside-agents](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/user/outside-agents.md)、[providers](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/internals/03_providers.md)。
