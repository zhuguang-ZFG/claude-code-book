# 构建与测试实测记录

本文件记录 **0.1.0 中文试读版**（第 1、3、5、6 章）在本机的实际构建结果。日期：2026-11-21。

## 环境

| 项 | 值 |
| --- | --- |
| 平台 | Windows 10.0.26100 |
| Python | 3.13（`python`） |
| PDF 渲染 | 本机 Edge + 系统中文字体（微软雅黑） |
| 构建入口 | `python scripts/bookctl.py build --product llm --lang zh --pdf --epub` |

页数会随字体与渲染器变化；CI 使用 Noto CJK，分页通常与本机不同。体积与单元数在同一份正文下是可复核的。

## 构建产物

| 产物 | 字节 | 实测 |
| --- | ---: | --- |
| `yuyu-llm-zh.html` | 261 155 | 5 个单元、2 张图版、20 条引用链接 |
| `yuyu-llm-zh.pdf` | 2 858 694 | 36 页、8 个书签、0 个索引页码项 |
| `yuyu-llm-zh.epub` | 135 338 | 50 条导航、14 个文档、3 张图片（含 3 个转位图 SVG）、封面 `image-0` |

`build --check` 的审计行：

```text
yuyu-llm-zh.html: 0.3 MB, 5 units, 2 plates, 20 cited links,
0 glosses, 0 lead bands, 0 tier chips, 0 emblems, 0 headpieces, 0 keeper notes
CHECK OK
```

## 测试

| 命令 | 结果 |
| --- | --- |
| `python -m unittest discover -s yuyu-book/tests` | 624 项通过 |
| `python -m unittest discover -s tests` | 361 项通过 |
| `python scripts/bookctl.py check --fast` | 通过（内容检查、两套测试） |
| `python scripts/bookctl.py build --product llm --lang zh --check` | `CHECK OK` |

新增测试：

- `tests/test_llm_examples.py`：加载四个示例模块，检查 BPE round-trip、训练可复现、softmax/过滤器的归一化、固定 seed、因果遮罩、注意力参数与 KV cache 公式，并实际执行脚本。
- `yuyu-book/tests/test_llm_product.py`：检查产品注册、前缀、单语、`plain_optional`、章节与磁盘文件一致、卷规划仍是 15 章、GitHub 来源为完整 SHA 且与 `llm/facts/source-lock.json` 一致。

## 示例脚本实测输出

四个脚本都只用标准库。关键数字已写入正文；本节保留完整命令以便复核。

```bash
python llm/examples/bpe_demo.py
python llm/examples/attention_demo.py
python llm/examples/sampling_demo.py
python llm/examples/context_budget.py
```

- `bpe_demo.py`：7 行语料训练 32 条合并规则，词表 288；五个样本全部 round-trip 成功。`青禾工作坊` 为 5 字符 / 15 字节 / 8 toy tokens；`🙂` 为 1 字符 / 4 字节 / 4 toy tokens。
- `attention_demo.py`：三个二维向量、单位投影；因果权重第二行为 `[0.465, 0.535, 0.000]`，去掉遮罩后第一行从 `[1.000, 0.000]` 变为 `[0.718, 0.429]`。两个一维头的拼接输出为 `[1.000, 0.000]`、`[0.908, 0.353]`、`[0.600, 0.688]`。`d_model=4096`、32 个 Q 头时，MHA/GQA/MQA 的每层注意力参数分别为 67 108 864 / 41 943 040 / 34 603 008，每 token KV cache 为 512 / 128 / 16 KiB。
- `sampling_demo.py`：`T=0.2` 时分布最高概率 0.865，`top-p=0.90` 保留 2 个候选；`T=1.0` 时最高概率 0.371，同一 `top-p` 保留 5 个候选。固定 seed 的两次八连抽完全一致。
- `context_budget.py`：默认预算用掉 87 444 / 128 000 token，剩 40 556；128K 上下文、32 层 / 8 KV 头 / 128 维 / fp16 的 KV cache 为 16.0 GiB；每层因果注意力 8 590 000 128 个 pair；1 000 次调用、每次 81 300 输入 token、每百万 0.15 美元时账单 12.19 美元。

## 未实测范围

以下内容没有在本轮运行，正文中按“练习”或“待测”标注，未写成结论：

- 真实厂商模型上的温度 / top-p 对比与 seed 复现实验；
- 生产 tokenizer（如 `tiktoken`）与本书玩具 BPE 的跨模型计数对比；
- 训练好的模型里注意力头实际学到了什么（本书示例的权重是手设的）；
- 长上下文位置效应（Lost in the Middle）的复现实验；
- GPU 显存占用、吞吐、延迟与并发压测；
- 真实价格与账单核对（脚本中的价格是输入参数，不是报价）。

这些缺口不影响试读版的可运行性，但不能把本章的示意数字当作生产容量规划。
