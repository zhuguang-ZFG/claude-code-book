# T3 Code 验证记录

日期：2026-11-24。基线：`pingdotgg/t3code` 的 HEAD 提交 `3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1`，许可 MIT（`LICENSE`，Copyright 2026 T3 Tools Inc.）。

## 已完成

读取固定提交的官方文档：`README.md`、`docs/README.md`、`docs/internals/00_glossary.md`、`01_architecture.md`、`03_providers.md`、`04_environment-auth.md`、`05_remote.md`、`09_connection-runtime.md`，以及 `docs/user/` 下的 composer、thread-sidebar、permission-modes、source-control、outside-agents、remote-access、devices、secrets、telemetry、updating、background-service 等页面。第 17 章的性能回归路径按 docs README 索引确认为 `docs/internals/16_performance-regressions.md`（契约草稿里猜测的 `16_performance.md` 实测 404，已更正）。

事实边界：只陈述上游文档明说的事实；由事实推出的理解用「可以这么理解」「不妨把它看成」标出；上游未写明的实现不作断言。不编造命令、菜单项或数值。

## 装配

| 项 | 值 |
| --- | --- |
| 阅读单元 | 23（前言 + 18 章 + 附录 A–D） |
| 每章二级小节 | 恰好 8 个 |
| 引导块 | 每单元一个 `<unit>.b-opening`，供通俗层证据引用 |
| 通俗层 | guides 23 条、reading-paths 每章 8 档、术语/按语为空壳、索引 15 条 |
| 图版 | 24 幅手绘 SVG（18 章徽 + 4 篇题 + 前言徽 + 封面） |

装配命令：

```bash
python scripts/bookctl.py build --product t3code --lang zh --check --mermaid source
python scripts/bookctl.py build --product t3code --lang zh --pdf --epub
```

本地 HTML/PDF/EPUB 由统一构建主线生成，最终文件位于主工作区 `yuyu-book/dist/`。

## 未验证

本册为文档分析，没有随书实验驱动。未在本机安装 T3 Code，也未验证首次安装、provider 真实登录、模型请求、权限审批 UI、手机配对、Tailscale/T3 Connect 连通性、MCP 外部 agent 实跑或实际回滚行为。界面名称与命令参数以固定提交文档为准，不保证与更新版本一致。
