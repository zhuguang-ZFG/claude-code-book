# 附录 C：常见问题

<!-- block: t3code-apxc.b-opening -->
问题按「连接」「权限」「代码状态」三类归档，每类先给最快核对项，再指向正文对应章节。这里不复制完整排障文档，只给判断方向。

## 连接类

**手机连不上桌面上的环境。** 先确认服务器仍在运行，再确认路由来自环境自身而不是客户端的 loopback 猜测。分享端点不可用时，系统不能回退到 loopback，因为那个名字指向客户端自己的机器；也不允许把 HTTPS 配对降级成明文 HTTP。详见第 11 章。

**从 Tailscale 地址能打开页面，但 agent 登录失败。** Tailscale 只提供端点，不替环境发会话。如果地址是纯 `http`，agent 只可能发现环境，不能完成 OAuth 登录；需要 HTTPS 或 localhost。详见第 11、13 章。

**桌面预览打开的是自己电脑的 localhost。** 远程环境的 loopback 必须经环境自己的 `/api/preview/tunnel` 转发；隧道失败应当报错，而不是静默直连。Chromium 对 loopback 忽略 PAC，所以要用固定 SOCKS5 代理。详见第 11 章。

## 权限类

**外部 agent 看到了工具却调用失败。** subagent、secret 请求、HTML 渲染、浏览器预览、设备、worktree handoff 只能在 T3 线程内部的 agent 调用；外部 agent 的列表里也会出现，但调用会返回「需要在 T3 Code 内运行」的错误。交接任务应改用 `t3_thread_launch` 配合 `t3_thread_wait` 或 `t3_thread_read`。详见第 13 章。

**批准一次登录后，访问级别和预期不同。** 不带 code 的批准从 Read only 开始；带 code 的批准按 code 已携带的级别，其他 code 则重新选择，默认 Auto 或组织策略允许的最近更低档。登录有效期 30 天。详见第 13 章。

**以为开了更细的权限就能少授权。** 配对只能收窄作用域；`terminal:operate` 与 `orchestration:operate` 本身等价于以操作系统用户身份执行，所以默认授权里包含管理与 relay 管理并不是绕过边界。详见第 12 章。

## 代码状态类

**回滚被拒绝，文件没动。** 如果 provider 无法回滚它自己的会话，T3 Code 会在触碰文件系统之前拒绝这次 revert。这是保护，不是故障。详见第 7 章。

**turn 已经结束，检查点还没出现。** turn 结束与后续收敛是两个里程碑；turn-end 检查点作为 outbox effect 捕获，在提交前读者把它视为 pending，命令决策仍把这个 run 当作 waiting。详见第 7、16 章。

**一个 turn 的 diff 里多了别人带进来的文件。** turn 自己的 diff 只含它自己改动过的文件；pull、merge、rebase 带进来的文件不算。要看全部变化，用分支比较。详见第 8 章。

来源：[remote](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/internals/05_remote.md)、[outside agents](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/user/outside-agents.md)、[architecture](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/internals/01_architecture.md)。
