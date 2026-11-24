# 附录 D：来源与版本

<!-- block: t3code-apxd.b-opening -->
这一册固定引用 `pingdotgg/t3code` 的提交 `3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1`（2026-11-24 读取的 HEAD）。上游许可为 MIT，Copyright 2026 T3 Tools Inc.。本书只做链接引用，不转载源码或文档正文。

## 主要来源

| 类别 | 路径 | 支撑章节 |
| --- | --- | --- |
| 项目定位 | `README.md` | 1 |
| 架构 | `docs/internals/01_architecture.md` | 1、4、7、16、17 |
| Provider | `docs/internals/03_providers.md` | 3、6、18 |
| 环境鉴权 | `docs/internals/04_environment-auth.md` | 12、13、15 |
| 远程架构 | `docs/internals/05_remote.md` | 11、12 |
| 连接运行时 | `docs/internals/09_connection-runtime.md` | 14 |
| 术语表 | `docs/internals/00_glossary.md` | 1、16、附录 B |
| 消息与上下文 | `docs/user/composer.md` | 5、7、14 |
| 线程 | `docs/user/thread-sidebar.md` | 2、4 |
| 权限 | `docs/user/permission-modes.md` | 6 |
| 源码控制 | `docs/user/source-control.md` | 7、8 |
| 外部 agent | `docs/user/outside-agents.md` | 2、13、15、附录 A、C |
| 远程访问 | `docs/user/remote-access.md` | 11 |
| 设备 | `docs/user/devices.md` | 14 |
| 秘密与遥测 | `docs/user/secrets.md`、`docs/user/telemetry.md` | 12、15 |
| 更新与后台 | `docs/user/updating.md`、`docs/user/background-service.md` | 18 |

## 版本边界

官方文档是滚动更新的；本册只保证上述固定提交那一版的表述。遇到界面名称、命令参数、档位默认值与实际软件不一致时，先检查软件版本，再回到该提交的文档核对，不要据本册推断更新版本的行为。

书中的「可以这么理解」是基于已核实事实的解释，不是上游文档的原文结论；上游没有写明的行为，本书不作断言。这一点在权限、性能与内部实现三处尤其重要。

来源：[README](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/README.md)、[docs README](https://github.com/pingdotgg/t3code/blob/3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1/docs/README.md)。
