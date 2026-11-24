# 附录 B：术语表

<!-- block: t3code-apxb.b-opening -->
这里只收固定提交文档里出现、且正文反复用到的词。中文名是本书的译法，英文原名保留，便于对照官方文档。

| 术语 | 含义 |
| --- | --- |
| 控制平面（control plane） | 管理线程、权限、工作树与连接的层，不替代 agent 自身的推理与工具执行。 |
| 环境（environment） | 真正拥有工作区、provider 进程、终端、Git 与持久状态的那一侧。 |
| 投影（projection） | 事件应用后得到的持久化读模型；它是生效后的真相源。 |
| event lane | 与线程关联的事件通道；turn-end 检查点作为 outbox effect 落在它上面。 |
| outbox effect | 与事件在同一事务里登记的副作用，提交后才由 effect worker 执行。 |
| settlement | 线程最终状态的收敛过程，由服务器拥有，客户端只渲染结果。 |
| capability | provider 声明自己支持什么；编排层与客户端读能力，不读 provider 名字。 |
| peer link | 一个环境作为普通 OAuth 客户端登录另一个环境的 `/mcp`，从而在其中工作。 |
| linkOrigin | 非 full access 的 peer link 启动的线程携带的不可变标记，用来围栏可改动的对象。 |
| DPoP | 把令牌绑定到客户端证明密钥的机制；证明无效必须失败，不能退化成 bearer。 |
| guest link | 绑定单个分享的 HMAC 令牌，不是会话，不能用于 RPC、WebSocket 或 MCP。 |
| effect worker | 在事务提交后运行副作用、并把结果作为 command 喂回编排器的工作者。 |
| worktree | 与线程关联的独立 Git 工作目录；检查点用隐藏 ref，不给用户分支加提交。 |
| usage_limit | 配额或速率限制错误的分类，可附带重置时间，不等同于一般失败。 |

## 容易混淆的三组

**turn 结束与 settlement**。provider 的这一轮回复结束，只是第一个里程碑；检查点、diff、PR 同步这些后续工作收敛，是第二个里程碑。前者完成不代表后者已完成。

**鉴权与到达方式**。Tailscale、T3 Connect、SSH 只改变客户端怎样连到服务器，鉴权始终由环境自己负责。能连上不等于被授权。

**项目与文件系统边界**。项目是组织边界，不是沙箱。`filesystem:read` 允许读服务器操作系统用户能读的任何文件；写入仍受工作区规则约束。

来源：[glossary](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/internals/00_glossary.md)、[architecture](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/internals/01_architecture.md)、[environment auth](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/internals/04_environment-auth.md)。
