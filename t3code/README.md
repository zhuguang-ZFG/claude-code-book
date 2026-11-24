# T3 Code：coding agent 的控制平面

1.0.0 首版含前言、18 章与附录 A–D，围绕线程、权限、工作树、远程入口与事件溯源展开。前半册建立所有权边界与一条任务走过的路径；后半册读鉴权、MCP、设备与秘密，最后用事件溯源解释一次「已确认」承诺了什么。

基线为 `pingdotgg/t3code` 的 HEAD 提交 `3b3b662f3c601ba6ce3f2435c7b5e20e9d6841f1`（2026-11-24 读取），上游许可 MIT。全书只做链接引用，不转载上游文档或源码；每个机制都区分「文档明说的事实」与「基于事实的理解」。

[前言](00-前言.md) · [来源与版本](appendix-d.md) · [验证记录](VERIFY.md) · [来源锁](../docs/agent-series/sources.lock.json)

在仓库根目录生成三种格式：

```bash
python scripts/bookctl.py build --product t3code --lang zh --pdf --epub
```

输出为 `yuyu-book/dist/yuyu-t3code-zh.html`、`.pdf`、`.epub`。本机统一交付目录为 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`。

本册不设随书实验驱动。文中的「可以这么理解」是解释，不是上游结论；界面名称、命令参数与默认档位会随版本变化，核对时以固定提交的官方文档为准。
