# 示例说明

二十一个脚本都只依赖 Python 3.12+ 标准库，不需要 GPU、模型文件、API key 或网络。

| 脚本 | 用途 | 主要输出 |
| --- | --- | --- |
| `bpe_demo.py` | 在极小语料上训练 byte-level BPE，编码与解码样本 | 合并规则、字符/字节/token 对照表、round-trip 检查 |
| `embedding_demo.py` | 手设向量的余弦相似度与 top-k 检索 | 点积/余弦排序差异、近邻表、参数与扫描成本 |
| `ann_demo.py` | 用 IVF 分桶演示近似最近邻的召回率与扫描比例 | ASCII 桶图、nprobe 表、最差查询漏检分析 |
| `attention_demo.py` | 对三个手设向量计算单头/双头因果注意力 | 权重矩阵、输出向量、Q/K/V/O 参数与 KV cache |
| `transformer_demo.py` | 走一遍 pre-norm block，算 Norm、残差、RoPE 与参数账 | 归一化结果、残差流模长、参数表、RoPE 点积 |
| `sampling_demo.py` | 对合成的下一个 token 分布应用温度、top-k、top-p | 概率表、保留候选数、固定 seed 的抽样结果 |
| `context_budget.py` | 计算窗口预算、KV cache 与注意力 pair 数 | 预算余量、KV cache 大小、假设价格下的账单 |
| `scaling_demo.py` | 计算 6ND 训练算力、推理算力与参数/token 分配 | 三档预算表、7B 模型的 GPU-days、推理 FLOPs |
| `train_demo.py` | 用反向传播真训练一个 7 440 参数的小 Transformer | 损失曲线、梯度检查、更新前后预测 |
| `embedding_train_demo.py` | skip-gram 加负采样，把相似度从语料里学出来 | pair loss、同主题近邻的前后对比 |
| `sft_demo.py` | 比较 SFT 损失掩码，计算 LoRA 更新与参数账 | 两种损失均值、LoRA 前后输出、秩与适配器体积 |
| `alignment_demo.py` | 计算 Bradley-Terry 奖励损失与 DPO 损失 | 成对准确率、边际、β 对损失的影响 |
| `rejection_demo.py` | 固定成功概率下的候选生成与筛选 | keep 率、best-of-N 通过率与生成次数；不含训练 |
| `serving_demo.py` | 计算权重、KV cache、带宽模型耗时与槽位利用率 | 理想化显存与吞吐估算、静态/连续批处理对比 |
| `session_ledger.py` | 给一次四轮会话按轮记账 | 每轮输入/输出、三种缓存策略的账单与耗时、峰值 KV cache |
| `rag_demo.py` | 演示切块、BM25、向量召回、RRF 与重排 | 切块完整性、各阶段 top-3、过滤与去重计数 |
| `retrieval_metrics.py` | 用同一份标注比较两套排序 | 逐条 recall@k、RR、NDCG@k、AP@k；跨查询汇总 MRR/MAP |
| `toolcall_demo.py` | 演示工具 schema、参数校验、失败重试与 MCP 消息 | schema 字符数、校验错误、JSON-RPC 请求与结果 |
| `cot_demo.py` | 模拟自洽投票并计算每道正确题的成本 | 采样数/准确率表、策略成本表 |
| `eval_demo.py` | 计算置信区间、配对差异、污染偏差、弃权指标与蒸馏成本 | Wilson 区间、精确 McNemar 对照、覆盖率、成本 |
| `multimodal_demo.py` | 切 patch、算图像 token 预算与图文相似度 | patch 网格、token 数、预算表 |

从仓库根目录运行：

```bash
python llm/examples/bpe_demo.py
python llm/examples/embedding_demo.py
python llm/examples/ann_demo.py
python llm/examples/attention_demo.py
python llm/examples/transformer_demo.py
python llm/examples/sampling_demo.py
python llm/examples/context_budget.py
python llm/examples/scaling_demo.py
python llm/examples/train_demo.py
python llm/examples/embedding_train_demo.py
python llm/examples/sft_demo.py
python llm/examples/alignment_demo.py
python llm/examples/rejection_demo.py
python llm/examples/serving_demo.py
python llm/examples/session_ledger.py
python llm/examples/rag_demo.py
python llm/examples/retrieval_metrics.py
python llm/examples/toolcall_demo.py
python llm/examples/cot_demo.py
python llm/examples/eval_demo.py
python llm/examples/multimodal_demo.py
```

`context_budget.py` 接受 `--window`、`--retrieved`、`--kv-heads`、`--price-per-million` 等参数；运行 `python llm/examples/context_budget.py --help` 查看全部输入。

## 限制

- BPE 示例省略了生产 tokenizer 的预切分、特殊 token 和词表压缩，计数只用于说明机制；
- embedding 示例的向量是手设的三维玩具，不代表任何训练好的编码器；
- 注意力示例的输入向量与投影矩阵都是手设的，只演示算术，不代表任何训练好的模型；
- Transformer 示例只走前向算术，不包含反向传播、损失函数与优化器；
- 预训练示例只算 FLOPs 与显存粗账，不含真实训练吞吐或集群调度；
- 部署示例只算显存流量与槽位占用，不测真实框架的吞吐或延迟；
- 近似检索示例只有 400 个二维点和 8 个桶，召回数字不代表真实向量库；
- 检索指标示例的标注是手设的，只演示指标口径，不代表任何检索器；
- 会话账单示例的价格、速率与模型形状都是可替换的假设，不构成任何厂商报价；
- RAG 示例的语料、向量与重排权重都是手设的，不代表真实检索质量；
- 工具调用示例没有权限、传输、超时和幂等，只演示协议形状；
- 推理示例用独立错误假设模拟多数投票，不代表真实模型的采样相关性；
- 评测示例的计数与价格都是手设的，不代表真实模型的评测结果；
- SFT 示例用目标概率代替完整词表 softmax，LoRA 示例用 4×4 矩阵，不包含训练过程；
- 对齐示例的奖励分数与 log 概率都是手设的，不包含奖励模型或策略训练；
- 采样示例使用手工设定的 logits，不代表任何模型的真实分布；
- 预算示例中的层数、KV 头数、精度和价格都是可替换的输入，不是厂商规格或报价；
- 二十一个脚本不测量真实延迟、吞吐或显存占用。

测试位于仓库根目录的 `tests/test_llm_examples.py`，会检查 round-trip、余弦与 top-k、因果遮罩、归一化、参数公式、算力公式、损失掩码、LoRA 更新、偏好损失、显存公式、会话记账、切块与混合召回、工具校验、自洽投票、置信区间、固定 seed 和预算公式。
