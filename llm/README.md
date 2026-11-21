# LLM 卷：写给 Agent 工程师的大模型原理与实战

这是“大模型与智能体工程”系列的模型原理分册。它解释 Agent 每天调用、计费和约束的对象：token、embedding、注意力、采样、上下文、KV cache、训练与部署。

当前为 **0.1.0 中文版**，收录：

- [前言](00-前言.md)
- [第 1 章：token 不是字，也不是词](ch01.md)
- [第 2 章：向量空间里的“像”](ch02.md)
- [第 3 章：注意力在算什么](ch03.md)
- [第 4 章：一层一层读懂模型卡](ch04.md)
- [第 5 章：同一个提示，为什么每次答案不同](ch05.md)
- [第 6 章：上下文窗口不是免费的抽屉](ch06.md)
- [第 7 章：预训练：一笔算力账](ch07.md)
- [第 8 章：SFT 与 LoRA：把通用模型改成你的助手](ch08.md)
- [第 9 章：对齐：模型为什么“听话”](ch09.md)
- [第 10 章：推理与部署：吞吐、延迟与显存](ch10.md)
- [第 11 章：RAG：切块、检索与重排](ch11.md)
- [第 12 章：工具调用与 MCP：把动作写进协议](ch12.md)
- [第 13 章：思维链与推理模型：多想一步值不值](ch13.md)
- [第 14 章：幻觉、评测与蒸馏：怎样判断它真的变好](ch14.md)
- [第 15 章：名词速查总表](ch15.md)

完整十五章规划见 [`docs/llm-volume-plan.md`](../docs/llm-volume-plan.md)。

## 构建

```bash
python scripts/bookctl.py build --product llm --lang zh
python scripts/bookctl.py build --product llm --lang zh --pdf
python scripts/bookctl.py build --product llm --lang zh --pdf --epub
```

产物落在 `yuyu-book/dist/`，前缀为 `yuyu-llm-zh`。也可以使用 `make book-llm`、`make book-llm-pdf`、`make book-llm-all`。

## 示例

`llm/examples/` 下十四个脚本只用 Python 标准库：

```bash
python llm/examples/bpe_demo.py
python llm/examples/embedding_demo.py
python llm/examples/attention_demo.py
python llm/examples/transformer_demo.py
python llm/examples/sampling_demo.py
python llm/examples/context_budget.py
python llm/examples/scaling_demo.py
python llm/examples/sft_demo.py
python llm/examples/alignment_demo.py
python llm/examples/serving_demo.py
python llm/examples/rag_demo.py
python llm/examples/toolcall_demo.py
python llm/examples/cot_demo.py
python llm/examples/eval_demo.py
```

它们分别演示 byte-level BPE、embedding 与余弦检索、单头/多头注意力、Transformer block 与参数账、温度与 top-k/top-p 采样、上下文预算与 KV cache 估算、预训练算力分配、SFT 损失掩码与 LoRA 参数账、奖励模型与 DPO 损失、推理显存与批处理、RAG 切块与混合召回、工具调用与 MCP 消息、自洽投票与测试时计算成本、置信区间与评测口径。输出是教学数据，不是厂商 benchmark。

## 状态

- 正文：第 1–15 章已齐；英文版待后续同步。
- 插图：16 枚单元章徽、9 幅篇题、15 张正文手绘图与 1 张独立封面，源文件在 `yuyu-book/illustrations-agents/`，遵循仓库的墨线 SVG 硬契约。
- 构建与测试：`make check`、`python -m unittest tests.test_llm_examples yuyu-book.tests.test_llm_product -v`。
- 实测记录与未测范围见 [`VERIFY.md`](VERIFY.md)。
- 来源与许可见 [`yuyu-book/sources-llm.json`](../yuyu-book/sources-llm.json) 和 [`facts/source-lock.json`](facts/source-lock.json)。
