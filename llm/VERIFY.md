# 构建与测试实测记录

本文件记录 **0.1.0 中文试读版**（第 1–6、8–9 章）在本机的实际构建结果。日期：2026-11-21。

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
| `yuyu-llm-zh.html` | 373 566 | 9 个单元、3 张图版、34 条引用链接 |
| `yuyu-llm-zh.pdf` | 4 124 135 | 62 页、14 个书签、0 个索引页码项 |
| `yuyu-llm-zh.epub` | 178 882 | 87 条导航、20 个文档、4 张图片（含 4 个转位图 SVG）、封面 `image-0` |

`build --check` 的审计行：

```text
yuyu-llm-zh.html: 0.4 MB, 9 units, 3 plates, 34 cited links,
0 glosses, 0 lead bands, 0 tier chips, 0 emblems, 0 headpieces, 0 keeper notes
CHECK OK
```

## 测试

| 命令 | 结果 |
| --- | --- |
| `python -m unittest discover -s yuyu-book/tests` | 624 项通过 |
| `python -m unittest discover -s tests` | 381 项通过 |
| `python scripts/bookctl.py check --fast` | 通过（内容检查、两套测试） |
| `python scripts/bookctl.py build --product llm --lang zh --check` | `CHECK OK` |

新增测试：

- `tests/test_llm_examples.py`：加载八个示例模块，检查 BPE round-trip、训练可复现、余弦与 top-k、softmax/过滤器的归一化、固定 seed、因果遮罩、注意力参数与 KV cache 公式、Norm 与残差、模型参数账、RoPE 相对位置、SFT 损失掩码与 LoRA 更新、偏好损失，并实际执行脚本。
- `yuyu-book/tests/test_llm_product.py`：检查产品注册、前缀、单语、`plain_optional`、章节与磁盘文件一致、卷规划仍是 15 章、GitHub 来源为完整 SHA 且与 `llm/facts/source-lock.json` 一致。

## 示例脚本实测输出

八个脚本都只用标准库。关键数字已写入正文；本节保留完整命令以便复核。

```bash
python llm/examples/bpe_demo.py
python llm/examples/embedding_demo.py
python llm/examples/attention_demo.py
python llm/examples/transformer_demo.py
python llm/examples/sampling_demo.py
python llm/examples/context_budget.py
python llm/examples/sft_demo.py
python llm/examples/alignment_demo.py
```

- `bpe_demo.py`：7 行语料训练 32 条合并规则，词表 288；五个样本全部 round-trip 成功。`青禾工作坊` 为 5 字符 / 15 字节 / 8 toy tokens；`🙂` 为 1 字符 / 4 字节 / 4 toy tokens。
- `embedding_demo.py`：`[3,0]` 查询下，短向量 A 的点积 3.000、余弦 1.000，长向量 B 的点积 6.000、余弦 0.707，两种排序相反；“退款”的近邻为“不退款”1.000、“退货”0.991、“换货”0.827；`cosine(退款, 不退款)=0.9997`。词表 32000、`d=4096` 的 embedding 为 131 072 000 个参数、fp16 250.0 MiB；10 万条 4096 维 fp32 向量约 1.5 GiB，精确扫描 409 600 000 次乘加。
- `attention_demo.py`：三个二维向量、单位投影；因果权重第二行为 `[0.465, 0.535, 0.000]`，去掉遮罩后第一行从 `[1.000, 0.000]` 变为 `[0.718, 0.429]`。两个一维头的拼接输出为 `[1.000, 0.000]`、`[0.908, 0.353]`、`[0.600, 0.688]`。`d_model=4096`、32 个 Q 头时，MHA/GQA/MQA 的每层注意力参数分别为 67 108 864 / 41 943 040 / 34 603 008，每 token KV cache 为 512 / 128 / 16 KiB。
- `transformer_demo.py`：`x=[1.0, 2.0, 3.0]` 经 RMSNorm 得 `[0.463, 0.926, 1.389]`，经 LayerNorm 得 `[-1.225, 0.000, 1.225]`；两个 pre-norm block 后残差流模长从 3.742 增至 4.030。`d_model=4096`、32 层、`d_ff=11008` 的 SwiGLU 配置每层 202 383 360 个参数，未共享词嵌入时整模 6 738 411 520。二维 RoPE 在偏移 0–3 上的点积为 +1.000 / +0.540 / -0.416 / -0.990。
- `sampling_demo.py`：`T=0.2` 时分布最高概率 0.865，`top-p=0.90` 保留 2 个候选；`T=1.0` 时最高概率 0.371，同一 `top-p` 保留 5 个候选。固定 seed 的两次八连抽完全一致。
- `context_budget.py`：默认预算用掉 87 444 / 128 000 token，剩 40 556；128K 上下文、32 层 / 8 KV 头 / 128 维 / fp16 的 KV cache 为 16.0 GiB；每层因果注意力 8 590 000 128 个 pair；1 000 次调用、每次 81 300 输入 token、每百万 0.15 美元时账单 12.19 美元。
- `sft_demo.py`：五个位置的 SFT 损失在全部 token 上平均 0.367，只算 assistant 时 0.520；LoRA rank 2、`alpha=4` 把输出从 `[0.300, 0.400, 0.300, 0.500]` 改为 `[0.300, 0.500, 0.300, 0.540]`，合并检查通过。`4096×4096` 矩阵上 r=8 的可训练参数为 65 536（0.391%），fp16 每层 128 KiB，32 层约 4 MiB；r=d 时为 200%，并不省。
- `alignment_demo.py`：四组奖励对的平均 Bradley-Terry 损失 0.681，成对准确率 1/4；差值 1.0 的损失 0.313，差值 0 的损失 0.693。DPO 在偏好正确时，`β=0.1` 的边际 0.05、损失 0.668，`β=1.0` 的边际 0.50、损失 0.474；偏好反转且 `β=1.0` 时边际 -0.30、损失 0.854。

## 未实测范围

以下内容没有在本轮运行，正文中按“练习”或“待测”标注，未写成结论：

- 真实厂商模型上的温度 / top-p 对比与 seed 复现实验；
- 生产 tokenizer（如 `tiktoken`）与本书玩具 BPE 的跨模型计数对比；
- 真实编码器的语义检索质量（第 2 章的向量是手设三维玩具）；
- 真实 SFT / LoRA / QLoRA 训练实验（第 8 章只有手设概率与矩阵）；
- 真实偏好对齐实验与奖励模型训练（第 9 章只有手设分数与 log 概率）；
- 训练好的模型里注意力头实际学到了什么（本书示例的权重是手设的）；
- 反向传播、损失函数与优化器（本卷只走前向算术）；
- 长上下文位置效应（Lost in the Middle）的复现实验；
- GPU 显存占用、吞吐、延迟与并发压测；
- 真实价格与账单核对（脚本中的价格是输入参数，不是报价）。

这些缺口不影响试读版的可运行性，但不能把本章的示意数字当作生产容量规划。
