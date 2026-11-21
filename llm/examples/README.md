# 示例说明

四个脚本都只依赖 Python 3.12+ 标准库，不需要 GPU、模型文件、API key 或网络。

| 脚本 | 用途 | 主要输出 |
| --- | --- | --- |
| `bpe_demo.py` | 在极小语料上训练 byte-level BPE，编码与解码样本 | 合并规则、字符/字节/token 对照表、round-trip 检查 |
| `attention_demo.py` | 对三个手设向量计算单头/双头因果注意力 | 权重矩阵、输出向量、Q/K/V/O 参数与 KV cache |
| `sampling_demo.py` | 对合成的下一个 token 分布应用温度、top-k、top-p | 概率表、保留候选数、固定 seed 的抽样结果 |
| `context_budget.py` | 计算窗口预算、KV cache 与注意力 pair 数 | 预算余量、KV cache 大小、假设价格下的账单 |

从仓库根目录运行：

```bash
python llm/examples/bpe_demo.py
python llm/examples/attention_demo.py
python llm/examples/sampling_demo.py
python llm/examples/context_budget.py
```

`context_budget.py` 接受 `--window`、`--retrieved`、`--kv-heads`、`--price-per-million` 等参数；运行 `python llm/examples/context_budget.py --help` 查看全部输入。

## 限制

- BPE 示例省略了生产 tokenizer 的预切分、特殊 token 和词表压缩，计数只用于说明机制；
- 注意力示例的输入向量与投影矩阵都是手设的，只演示算术，不代表任何训练好的模型；
- 采样示例使用手工设定的 logits，不代表任何模型的真实分布；
- 预算示例中的层数、KV 头数、精度和价格都是可替换的输入，不是厂商规格或报价；
- 四个脚本不测量真实延迟、吞吐或显存占用。

测试位于仓库根目录的 `tests/test_llm_examples.py`，会检查 round-trip、因果遮罩、固定 seed 和预算公式。
