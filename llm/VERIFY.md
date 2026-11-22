# 构建与测试实测记录

本文件记录 **0.1.0 中文版**（第 1–16 章）在本机的实际构建结果。日期：2026-11-21。

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
| `yuyu-llm-zh.html` | 677877 | 17 个单元、31 张正文手绘图、145 条引用链接、17 枚章徽、10 幅篇题 |
| `yuyu-llm-zh.pdf` | 7998513 | 144 页、28 个书签、0 个索引页码项 |
| `yuyu-llm-zh.epub` | 249466 | 170 条导航、34 个文档、28 张图片（含 28 个转位图 SVG）、封面 `image-0` |

`build --check` 的审计行：

```text
yuyu-llm-zh.html: 0.6 MB, 17 units, 31 plates, 131 cited links,
0 glosses, 0 lead bands, 0 tier chips, 17 emblems, 10 headpieces, 0 keeper notes
CHECK OK
```

插图用 `yuyu-book/illustrations-agents/` 的墨线托盘：17 枚单元章徽、10 幅篇题、31 张正文手绘图、1 张独立封面。全部通过 `art._read()` 的 6000 字节、`viewBox`、`currentColor` 与禁用 `id/href/url()` 校验；封面走 `cover-llm.svg`，不借用御舆的四马图。

## 测试

| 命令 | 结果 |
| --- | --- |
| `python -m unittest discover -s yuyu-book/tests` | 628 项通过 |
| `python -m unittest discover -s tests` | 443 项通过 |
| `python scripts/bookctl.py check --fast` | 通过（内容检查、两套测试） |
| `python scripts/bookctl.py build --product llm --lang zh --check` | `CHECK OK` |

新增测试：

- `tests/test_llm_examples.py`：加载全部示例模块，检查 BPE round-trip、训练可复现、余弦与 top-k、softmax/过滤器的归一化、固定 seed、因果遮罩、注意力参数与 KV cache 公式、Norm 与残差、模型参数账、RoPE 相对位置、预训练算力公式、SFT 损失掩码与 LoRA 更新、偏好损失、decode 显存与批处理利用率、会话账单（轮次增长、缓存单价、策略排序、分项求和）、IVF 分桶覆盖与 nprobe 单调性、检索指标（理想排序、位置惩罚、MRR 位置）、RAG 切块与混合召回、工具 schema 校验与 MCP 消息、自洽投票、Wilson 区间与评测口径、patch 切块与图像 token 预算，并实际执行脚本。
- `yuyu-book/tests/test_llm_product.py`：检查产品注册、前缀、单语、`plain_optional`、章节与磁盘文件一致、卷规划仍是 16 章、RoPE 图的旋转几何与 q/k 端点约定、GitHub 来源为完整 SHA 且与 `llm/facts/source-lock.json` 一致。

## 示例脚本实测输出

二十一个脚本都只用标准库。关键数字已写入正文；本节保留完整命令以便复核。

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
python llm/examples/serving_demo.py
python llm/examples/session_ledger.py
python llm/examples/rag_demo.py
python llm/examples/retrieval_metrics.py
python llm/examples/toolcall_demo.py
python llm/examples/cot_demo.py
python llm/examples/eval_demo.py
python llm/examples/multimodal_demo.py
```

- `bpe_demo.py`：7 行语料训练 32 条合并规则，词表 288；五个样本全部 round-trip 成功。`青禾工作坊` 为 5 字符 / 15 字节 / 8 toy tokens；`🙂` 为 1 字符 / 4 字节 / 4 toy tokens。
- `embedding_demo.py`：`[3,0]` 查询下，短向量 A 的点积 3.000、余弦 1.000，长向量 B 的点积 6.000、余弦 0.707，两种排序相反；“退款”的近邻为“不退款”1.000、“退货”0.991、“换货”0.827；`cosine(退款, 不退款)=0.9997`。词表 32000、`d=4096` 的 embedding 为 131 072 000 个参数、fp16 250.0 MiB；10 万条 4096 维 fp32 向量约 1.5 GiB，精确扫描 409 600 000 次乘加。
- `ann_demo.py`：400 个二维点、8 个 k-means 桶（桶大小 29 / 52 / 92）；`nprobe` 为 1 / 2 / 4 / 8 时分别扫描 13.2% / 25.0% / 51.9% / 100.0% 的向量，`recall@10` 为 0.865 / 0.997 / 1.000 / 1.000；最差的一条 `nprobe=1` 查询只扫 58 个点、召回 0.30，top-10 里有 7 个落在被探测桶之外。
- `attention_demo.py`：三个二维向量、单位投影；因果权重第二行为 `[0.465, 0.535, 0.000]`，去掉遮罩后第一行从 `[1.000, 0.000]` 变为 `[0.718, 0.429]`。两个一维头的拼接输出为 `[1.000, 0.000]`、`[0.908, 0.353]`、`[0.600, 0.688]`。`d_model=4096`、32 个 Q 头时，MHA/GQA/MQA 的每层注意力参数分别为 67 108 864 / 41 943 040 / 34 603 008，每 token KV cache 为 512 / 128 / 16 KiB。
- `transformer_demo.py`：`x=[1.0, 2.0, 3.0]` 经 RMSNorm 得 `[0.463, 0.926, 1.389]`，经 LayerNorm 得 `[-1.225, 0.000, 1.225]`；两个 pre-norm block 后残差流模长从 3.742 增至 4.030。`d_model=4096`、32 层、`d_ff=11008` 的 SwiGLU 配置每层 202 383 360 个参数，未共享词嵌入时整模 6 738 411 520。二维 RoPE 在偏移 0–3 上的点积为 +1.000 / +0.540 / -0.416 / -0.990。
- `sampling_demo.py`：`T=0.2` 时分布最高概率 0.865，`top-p=0.90` 保留 2 个候选；`T=1.0` 时最高概率 0.371，同一 `top-p` 保留 5 个候选。固定 seed 的两次八连抽完全一致。
- `context_budget.py`：默认预算用掉 87 444 / 128 000 token，剩 40 556；128K 上下文、32 层 / 8 KV 头 / 128 维 / fp16 的 KV cache 为 16.0 GiB；每层因果注意力 8 590 000 128 个 pair；1 000 次调用、每次 81 300 输入 token、每百万 0.15 美元时账单 12.19 美元。
- `scaling_demo.py`：按 6ND 算 7B 模型，140B / 300B / 2T token 的训练量分别为 5.88e21 / 1.26e22 / 8.40e22 FLOPs，GPU-days 为 170 / 365 / 2 431；按 20 token/参数分配，1e22 / 1e23 / 1e24 算力对应 9.1B / 28.9B / 91.3B 参数与 183B / 577B / 1.83T token；7B 模型推理每 token 约 14 GFLOP。
- `sft_demo.py`：五个位置的 SFT 损失在全部 token 上平均 0.367，只算 assistant 时 0.520；LoRA rank 2、`alpha=4` 把输出从 `[0.300, 0.400, 0.300, 0.500]` 改为 `[0.300, 0.500, 0.300, 0.540]`，合并检查通过。`4096×4096` 矩阵上 r=8 的可训练参数为 65 536（0.391%），fp16 每层 128 KiB，32 层约 4 MiB；r=d 时为 200%，并不省。
- `alignment_demo.py`：四组奖励对的平均 Bradley-Terry 损失 0.681，成对准确率 1/4；差值 1.0 的损失 0.313，差值 0 的损失 0.693。DPO 在偏好正确时，`β=0.1` 的边际 0.05、损失 0.668，`β=1.0` 的边际 0.50、损失 0.474；偏好反转且 `β=1.0` 时边际 -0.30、损失 0.854。
- `serving_demo.py`：7B 配置的 KV cache 为 128 KiB/token；权重 fp16 / int8 / int4 分别为 14.0 / 7.0 / 3.5 GB。8K 上下文下批大小 1 / 8 / 32 的 decode 时间为 5.02 / 7.53 / 16.12 ms，吞吐为 199 / 1 062 / 1 985 tok/s；32K 上下文、32 路批处理需要 128 GiB KV cache，80 GiB 卡装不下。四请求两槽位的静态/连续批处理利用率为 60.9% / 97.5%。
- `session_ledger.py`：四轮会话共 19 500 个输入 token，其中 6 450（33.1%）是新增内容、13 050（66.9%）是原样重发；无缓存 / 只缓存稳定前缀 / 缓存整段前文的账单为 $0.07575 / $0.05145 / $0.04052（−32.1% / −46.5%），模型计算时间 32.75 / 28.25 / 26.23 s；峰值上下文 6 850 token，按 320 KiB/token 计单请求 2.1 GiB KV cache，八路并发 16.7 GiB。
- `rag_demo.py`：6 份文档切成 13 块，按版本过滤后剩 12 块；块大小 10 会把“原路退回”切断，20 不会。BM25 第一是 `refund-faq#0`，向量第一是 `refund-policy#0`，RRF 第一是 `refund-policy#0`，玩具重排第一是 `refund-policy#2`（到账时间 1–3 个工作日）。
- `retrieval_metrics.py`：5 条查询、两套排序，`k=3`。关键词优先的 `recall@3` / MRR / `NDCG@3` / `MAP@3` 为 1.00 / 0.90 / 0.77 / 0.92，向量优先为 0.93 / 1.00 / 0.97 / 0.90；首条查询上关键词排序 1.00 / 1.00 / 0.81 / 1.00，向量排序 0.67 / 1.00 / 0.91 / 0.67。
- `toolcall_demo.py`：两个工具的 schema 分别为 181 / 241 字符；第一次调用把 `order_id` 传成整数，返回 `validation failed: order_id must be a string`；第二次传字符串成功，返回“退款处理中，预计 1–3 个工作日到账”。MCP 消息包含 `initialize` / `tools/list` / `tools/call`，协议版本 `2026-07-28`。
- `cot_demo.py`：假设单条样本正确率 0.60，1 / 3 / 5 / 9 / 15 条多数投票的模拟准确率为 60.7% / 66.0% / 69.4% / 75.2% / 79.5%；每题 token 从 400 涨到 6 000。按每百万输出 token 0.60 美元，直接回答 / CoT 一次 / CoT 五次 / CoT 十五次的每道正确题成本为 $0.000133 / $0.000369 / $0.001561 / $0.004053。
- `eval_demo.py`：200 题上 82.0% 与 86.0% 的 Wilson 区间为 [76.1%, 86.7%] 与 [80.5%, 90.1%]，两者重叠；20 条测试题在训练中见过，把 80.0% 的干净准确率抬到 82.0%；回答 80 题、对 72 题时覆盖率 80.0%、回答内准确率 90.0%、整体 72.0%、错答率 8.0%；教师/学生每道正确题成本约 $0.0071 / $0.0015。
- `multimodal_demo.py`：6×4 玩具图按 2×2 切成 6 个 patch，经 4×3 投影得到 6 个 3 维图像 token，位置按行主序展平；1920×1080 截图按 patch 16 直切为 8 160 token，缩到最长边 1568 后直切 5 488、像素计价 1 844；4032×3024 照片直切 47 628；2480×3508 A4 扫描直切 34 100；同一截图低档（768）442 token、高档（1568）1 844 token，差约四倍。
- `train_demo.py`：7 440 参数字符级 Transformer（435 字节语料、vocab 54、d_model 24、一层因果注意力 + FFN），手写前向与反向、warmup 12 步再余弦衰减到 10% 的 SGD、240 步约 6 秒；梯度检查 8 个抽检参数解析梯度 vs 中心差分最大偏差 7.31e-06；loss 从 3.99（=ln 54）降至训练后同窗口 1.49（step 60/120/180/240 为 3.92/2.20/2.28/3.24，batch=1 的正常抖动）；恒定 lr=0.6 的对照可到 1.12——玩具尺度上调度吃亏、长训练后期才兑现收益，正文如实记录。贪心采样从“青禾工作坊”续写出语料的重复句式。
- `embedding_train_demo.py`：12 词、16 维 skip-gram 负采样，36 句三主题语料训练 30 轮约 1 秒；训练前“退款”近邻为随机取向（换货 +0.39、配送 +0.32），训练后为售后 +0.99、换货 +0.99、退货 +0.98，12 个词 top-3 全部落回自己主题组；开发中 sigmoid 在点积增大后真实溢出，已改为分段稳定版并把 log(sigmoid) 换成 softplus。

## 未实测范围

以下内容没有在本轮运行，正文中按“练习”或“待测”标注，未写成结论：

- 真实厂商模型上的温度 / top-p 对比与 seed 复现实验；
- 生产 tokenizer（如 `tiktoken`）与本书玩具 BPE 的跨模型计数对比；
- 真实编码器的语义检索质量（第 2 章的向量是手设三维玩具）；
- 真实预训练实验与集群吞吐（第 7 章只算 FLOPs 与显存粗账）；
- 真实推理框架的吞吐、延迟与显存占用（第 10 章只算显存流量与槽位占用）；
- 真实 RAG 检索质量（第 11 章的语料、向量与重排权重都是手设的）；
- 真实 MCP 服务器、权限、传输与幂等（第 12 章只演示协议形状）；
- 真实模型的自洽投票收益（第 13 章用独立错误假设模拟）；
- 真实评测集的置信区间、污染检查与蒸馏效果（第 14 章的计数与价格是手设的）；
- 真实多模态模型的识读对比与视觉幻觉率（第 15 章的 patch、投影与预算公式是手设玩具，未在真实 VLM 上验证）；
- 真实 LLM-as-judge 的偏差实测（第 14 章的位置偏差与自偏好只引论文证据，未在自己的 judge 管线上复测）；
- 真实 SFT / LoRA / QLoRA 训练实验（第 8 章只有手设概率与矩阵）；
- 真实偏好对齐实验与奖励模型训练（第 9 章只有手设分数与 log 概率）；
- 训练好的模型里注意力头实际学到了什么（本书示例的权重是手设的）；
- 反向传播、损失函数与优化器（本卷只走前向算术）；
- 长上下文位置效应（Lost in the Middle）的复现实验；
- GPU 显存占用、吞吐、延迟与并发压测；
- 真实价格与账单核对（脚本中的价格是输入参数，不是报价）。

这些缺口不影响正文的可运行性，但不能把本章的示意数字当作生产容量规划。
