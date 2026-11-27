# 构建与测试实测记录

本文件记录中文第 1–16 章的构建与示例验证。前两张产物与测试表保留 2026-11-21 初版记录；后续章节修订的验证另记日期，不能用旧产物体积和页数代表当前书稿。

## 环境

| 项 | 值 |
| --- | --- |
| 平台 | Windows 10.0.26100 |
| Python | 3.13（`python`） |
| PDF 渲染 | 本机 Edge + 系统中文字体（微软雅黑） |
| 构建入口 | `python scripts/bookctl.py build --product llm --lang zh --pdf --epub` |

页数会随字体与渲染器变化；CI 使用 Noto CJK，分页通常与本机不同。体积与单元数在同一份正文下是可复核的。

## 初版构建产物（2026-11-21）

| 产物 | 字节 | 实测 |
| --- | ---: | --- |
| `yuyu-llm-zh.html` | 677877 | 17 个单元、31 张正文手绘图、145 条引用链接、17 枚章徽、10 幅篇题 |
| `yuyu-llm-zh.pdf` | 7998513 | 144 页、28 个书签、0 个索引页码项 |
| `yuyu-llm-zh.epub` | 249466 | 170 条导航、34 个文档、28 张图片（含 28 个转位图 SVG）、封面 `image-0` |

初版另一次 `build --check` 留存的审计行（131 条引用，与上表 145 条不是同一快照，不能互作校验）：

```text
yuyu-llm-zh.html: 0.6 MB, 17 units, 31 plates, 131 cited links,
0 glosses, 0 lead bands, 0 tier chips, 17 emblems, 10 headpieces, 0 keeper notes
CHECK OK
```

插图用 `yuyu-book/illustrations-agents/` 的墨线托盘：17 枚单元章徽、10 幅篇题、31 张正文手绘图、1 张独立封面。全部通过 `art._read()` 的 6000 字节、`viewBox`、`currentColor` 与禁用 `id/href/url()` 校验；封面走 `cover-llm.svg`，不借用御舆的四马图。

## 初版测试（2026-11-21）

| 命令 | 结果 |
| --- | --- |
| `python -m unittest discover -s yuyu-book/tests` | 628 项通过 |
| `python -m unittest discover -s tests` | 443 项通过 |
| `python scripts/bookctl.py check --fast` | 通过（内容检查、两套测试） |
| `python scripts/bookctl.py build --product llm --lang zh --check` | `CHECK OK` |

新增测试：

- `tests/test_llm_examples.py`：加载全部示例模块，检查 BPE round-trip、训练可复现、余弦与 top-k、softmax/过滤器的归一化、固定 seed、因果遮罩、注意力参数与 KV cache 公式、Norm 与残差、模型参数账、RoPE 相对位置、预训练算力公式、SFT 损失掩码与 LoRA 更新、偏好损失、decode 显存与批处理利用率、会话账单（轮次增长、缓存单价、策略排序、分项求和）、IVF 分桶覆盖与 nprobe 单调性、检索指标（理想排序、位置惩罚、MRR 位置）、RAG 切块与混合召回、工具 schema 校验与 MCP 消息、自洽投票、Wilson 区间、精确 McNemar 配对对照与评测口径、patch 切块与图像 token 预算，并实际执行脚本。
- `yuyu-book/tests/test_llm_product.py`：检查产品注册、前缀、单语、`plain_optional`、章节与磁盘文件一致、卷规划仍是 16 章、RoPE 图的旋转几何与 q/k 端点约定、GitHub 来源为完整 SHA 且与 `llm/facts/source-lock.json` 一致。

## 第三轮构建（2026-11-26）

按 ARIS 两次新上下文审读修订第 12、13、15 章及术语、示例与六张解释图。完整来源范围与原始审读见 [本轮记录](../docs/book-overhaul/aris-tools-20261126/PAPER_IMPROVEMENT_LOG.md)。

本机 Edge 与中文字体构建：HTML 759 607 字节、17 个单元、31 幅正文图、172 条引用；PDF 8 165 273 字节、157 页、28 个书签。局部视觉检查 36 组通过，手机预算表完整、六张图标签无越界，PDF 短流程与三行表保持同页。

最终验证：`check --fast` 九步通过，通用测试 460 项（1 项跳过）、构建器测试 629 项通过；其中 LLM 示例测试 112 项。485 份 Markdown、280 个 Mermaid 零错误；`ruff` 与合订本组装检查通过。

本轮 HTML/PDF 输出目录为 `.scratch/aris-tools-20261126/round2/`。干净检出可运行：

```bash
python scripts/bookctl.py build --product llm --lang zh --pdf --out-dir .scratch/aris-tools-20261126/round2
```

## 词向量训练与检索修订（2026-11-26）

第 2 章对照固定提交的 word2vec、D2L 和 Faiss 源码，修正两张 embedding 表使用不同状态计算梯度的问题。正、负标签分别以中心差分检查两个向量的 SGD 更新。检索按记录身份排除自身，保留向量相同的其他记录；精确扫描与 IVF 统一等距时的 ID 次序。负采样从有限候选池有放回地抽取，候选耗尽或没有正词对时明确报错。

固定 seed=11、原始 36 句语料与 30 轮配置，修正后的在线平均 pair loss 在第 1／10／20／30 轮为 0.541866／0.002142／0.000823／0.000490。该均值包含每轮重新抽取的负例，不是固定评测集曲线。12 个词的前三个近邻均属于自身主题；断言检查全部三个邻居。来源、两轮审读和构建记录见 [本轮记录](../docs/book-overhaul/aris-embedding-20261126/PAPER_IMPROVEMENT_LOG.md)。

最终本机 PDF 为 166 页、28 个书签，SGD 五行公式完整位于第 24 页；HTML 含 17 单元、31 幅正文图、188 条引用；EPUB 含 170 条导航与 34 个文档。`check --fast` 九步通过，通用测试 480 项（1 跳过）、构建器测试 629 项；其中 LLM 示例 131 项。全库 Ruff、合订本组装和 16 组桌面／手机明暗布局检查通过。最终输出在 `.scratch/aris-embedding-20261126/round2/`，哈希见本轮 `artifact-snapshots.json`。

## 第六轮：第 4 章架构深修与全书排版/绘图美化（2026-11-26）

按本地 ARIS 流程完成第 4 章及关联资产的两轮独立上下文审读（均属 `same-family / provisional`），并完成 LLM 分册排版美化与全套 59 幅矢量插图重绘。完整来源核对与审修明细见 [第 4 章修订与审读记录](../docs/book-overhaul/aris-ch04-20261126/PAPER_IMPROVEMENT_LOG.md)。

- **第 4 章内容与代码核对**：对照本地固定快照论文（LayerNorm `1607.06450`、RMSNorm `1910.07467`、Pre-LN `2002.04745`、GLU Variants `2002.05202`、RoPE `2104.09864`、PI `2306.15595`、YaRN `2309.00071`、RoPE 外推尺度律 `2310.05209`、稀疏 MoE `1701.06538`）及固定提交代码（Transformers `47b0e478...` Llama / Qwen2 / Mixtral / RoPE 工具、nanoGPT `3adf61e1...`、LLMs-from-scratch `22c637fd...`）。重写 `llm/ch04.md` 与 `llm/ch16.md`，补齐 Pre-LN 末尾 `Final Norm`、`RMSNorm` `eps` 防除零与半精度 `float32` 统计、`Swish = SiLU` 与 `GELU` 过渡、`d_ff=11008`（256 倍数对齐）、`RoPE` 每头 `d_rot` 与 `rotate_half` 配对布局兼容、GQA-8 投影减重及 Mixtral 与早期 MoE 路由顺序区别；`llm/examples/transformer_demo.py` 新增 `forward_block()`、`forward_model()`、`sparse_moe_forward()`、`rotate_half_rope()` 与 `params()` 边界校验，本机 PyTorch `2.14.1+cpu`（`float64`）逐项数值对照误差为 `0.0` 至 `1.78e-15`（仅作数值与路由验证，非性能基准）。
- **版式、EPUB 多墨水光栅化与 59 幅 SVG 插图重绘**：保持 `style_tokens.py` 调色盘十六进制常量不变，升级 `yuyu-book/yuyu_book/style_components.py`、`style_screen.py`、`style_print.py`、`render.py` 与 `docs/` 站点产物（放开 `.chapter-notes` 条目间分页以消除第 4 章尾部半页空白、优化引用斜杠换行、消除图注 `RoPE` 拆行并压缩表 4.5 防单字折行）；升级 `scripts/build_epub.py` 注入 `il-*` 语义墨水 CSS 与深色读图框规则，并新增 `tests/test_epub_paint.py` 对 `il-cinnabar` / `il-jade` / `il-sky` 精确 RGB 断言；重绘并校验 `yuyu-book/illustrations-agents/` 下全套 59 个 `*llm*.svg`（1 枚封面、10 幅篇题、17 枚章徽、31 张彩色正文图，全部以 `currentColor` + `il-*` 语义类渲染并植入 `pathLength="100"` 滚动绘线锚点），图 4-1 改为两次串行 Pre-LN 残差拓扑并回落第 41 页，图 4-2 改为双圆旋转与高低频坐标对。
- **本机终版产物与全量校验（`.scratch/aris-ch04-20261126/round2/`）**：Edge + 微软雅黑实测：`yuyu-llm-zh.html` 为 `957 772` 字节（17 单元、31 正文图、196 引用、17 章徽、10 篇题）；`yuyu-llm-zh.pdf` 为 `8 807 601` 字节（174 页、28 书签，0 越界块）；`yuyu-llm-zh.epub` 为 `3 407 473` 字节（34 文档、170 导航、59 张 PNG 经 Pillow 实测全部多墨水着色：`cinnabar` 195 200 像素、`jade` 220 150 像素、`sky` 495 011 像素，暗色模式补齐读图框乘色混合）。二次核查补修 12 幅图解中的正则（`^ORD-[0-9]{4}$`）、单位（`4 MiB`）、估算/教学标注及 `llm-ch12-mcp-bridge` / `llm-ch13-voting` 行距后，Playwright 桌面 1440px / 手机 390px（亮/暗主题）及打印态五模式 SVG 几何审计全部为 0 文本溢出、0 文本碰撞（手机最小字号 `10.02 px`）。`check --fast` 九步通过（通用测试 486 项含 1 跳过、构建器测试 632 项；含 LLM 示例 136 项、产品测试 9 项、`test_epub_paint` 2 项），合订本检查（12 卷、286 单元、366 图）与全库 `ruff` 通过。产物哈希与检验结果见 [artifact-snapshots.json](../docs/book-overhaul/aris-ch04-20261126/artifact-snapshots.json) 与 [final-validation.json](../docs/book-overhaul/aris-ch04-20261126/final-validation.json)。

## 可读性与插图精修（2026-11-27）

针对“讲得太深奥”的反馈，本卷十六章统一采用“先直观、后公式”的阅读层：每章开头压缩为一段白话，公式和实现细节前增加“选读”提示，前言与 README 明确第一次读可跳过公式。技术结论、代码、来源、实验数据和章节结构均保留。

十二卷共用插图框去掉渐变、投影、定位角标和悬浮效果；LLM、Omp、Pi、Prompt、Vibe、Kimi 六卷封面去掉重复双边框；T3 Code 四张篇题图修复曲线外推越界。按真实书页 CSS 在 390px 视口下，以 `getComputedStyle(fontSize) × getScreenCTM()` 测量全部 263 张 SVG：正文图可见文字均达到 10px；10 张封面的装饰性微标签原为 2.94–4.47px，已由图外 HTML 标题替代并隐藏；最终可见文字无小于 10px、无文字重叠、无内容越界。

本轮验证：LLM 示例测试 136 项通过；插图、视觉契约与 LLM 产品测试 40 项通过；LLM 装配检查 `CHECK OK`（17 单元、31 幅正文图、196 条引用）；十二卷合订本装配检查 `CHECK OK`（12 卷、286 单元、366 幅图版）；相关 Python 文件 Ruff 通过。浏览器实测覆盖 LLM 封面与第 3、4、9 章手机页面。

## 示例脚本实测输出

2026-11-26 第五轮对照开源实现：`bpe_demo.py` 的合并与编码直接复用 minbpe 固定提交，原始 MIT 文件与哈希随仓库保存；训练与严格解码保留本书口径。`attention_demo.py` 新增完整计算、单 token 和分块缓存的等价检查，以及查询位置重置的错误对照。本机 PyTorch 2.14.1 CPU/float64 的完整计算差为 `1.1102230246251565e-16`，只验证数值和遮罩，不测性能。BPE 在 Python 3.11.15 下以直接执行与包入口、禁用 site-packages 的方式运行成功；全书支持环境仍为 Python 3.12+。成品、审读和最终检查记录见 [第五轮验证](../docs/book-overhaul/aris-reuse-20261126/final-validation.json)。

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

- `bpe_demo.py`：7 行语料训练 32 条合并规则，词表 288；五个样本全部 round-trip 成功。`青禾工作坊` 为 5 字符 / 15 字节 / 8 toy tokens；`🙂` 为 1 字符 / 4 字节 / 4 toy tokens。
- `embedding_demo.py`：`[3,0]` 查询下，短向量 A 的点积 3.000、余弦 1.000，长向量 B 的点积 6.000、余弦 0.707，两种排序相反；“退款”的近邻为“不退款”1.000、“退货”0.991、“换货”0.827；`cosine(退款, 不退款)=0.9997`。词表 32000、`d=4096` 的 embedding 为 131 072 000 个参数、fp16 250.0 MiB；10 万条 4096 维 fp32 向量约 1.5 GiB，精确扫描 409 600 000 次乘加。
- `ann_demo.py`：400 个二维点、8 个 k-means 桶（桶大小 29 / 52 / 92）；`nprobe` 为 1 / 2 / 4 / 8 时分别扫描 13.2% / 25.0% / 51.9% / 100.0% 的向量，`recall@10` 为 0.865 / 0.997 / 1.000 / 1.000；最差的一条 `nprobe=1` 查询只扫 58 个点、召回 0.30，top-10 里有 7 个落在被探测桶之外。
- `attention_demo.py`：三个二维向量、单位投影；因果权重第二行为 `[0.465, 0.535, 0.000]`，去掉遮罩后第一行从 `[1.000, 0.000]` 变为 `[0.718, 0.429]`。两个一维头的拼接输出为 `[1.000, 0.000]`、`[0.908, 0.353]`、`[0.600, 0.688]`。`d_model=4096`、32 个 Q 头时，MHA/GQA/MQA 的每层注意力参数分别为 67 108 864 / 41 943 040 / 34 603 008，每 token KV cache 为 512 / 128 / 16 KiB。
- `transformer_demo.py`（2026-11-26）：`x=[1.0, 2.0, 3.0]` 经 RMSNorm 得 `[0.463, 0.926, 1.389]`（scale 2.160），经 LayerNorm 得 `[-1.225, 0.000, 1.225]`（scale 0.816）；两个标量代理 pre-norm block 后残差流模长从 3.742 增至 4.030；真实 2-token `forward_block` + `Final Norm` 后模长为 2.000。`d_model=4096`、32 层、`d_ff=11008` 的 SwiGLU 配置每层 202 383 360 个参数，tied 6 607 339 520，untied 6 738 411 520（含 Final Norm 为 6 738 415 616）；ReLU `d_ff=16384` 版 untied 6 704 857 088；GQA-8 每层注意力 41 943 040（总参 5 933 109 248）；MoE `8x-top2`（`d_ff=14336`）总参 46 702 792 704、激活 12 879 925 248；128K fp16 预算为权重 12.55 GiB（13.48 GB）+ KV 64.00 GiB = 76.55 GiB。二维 RoPE 偏移 0–3 点积为 +1.000 / +0.540 / -0.416 / -0.990；4D 偏移 10 下 `base=10000` 为 +0.156、`base=100` 为 -0.299；`rotate_half` 对齐得 -1.082 而未重排混用误得 +0.193；稀疏 MoE top-2 加权输出 `[0.216, -0.073]`。
- `sampling_demo.py`：`T=0.2` 时分布最高概率 0.865，`top-p=0.90` 保留 2 个候选；`T=1.0` 时最高概率 0.371，同一 `top-p` 保留 5 个候选。在 `T=1.0、top-p=0.90` 下，每段只初始化一次 seed=11，两次八连抽均为“城市 城市 地方 城市 城市 城市 首都 城市”。每段随机状态持续推进。
- `context_budget.py`：默认预算用掉 87 444 / 128 000 token，剩 40 556；128K 上下文、32 层 / 8 KV 头 / 128 维 / fp16 的 KV cache 为 16.0 GiB；每层因果注意力 8 590 000 128 个 pair；1 000 次调用、每次 81 300 输入 token、每百万 0.15 美元时账单 12.19 美元。
- `scaling_demo.py`：按 6ND 算 7B 模型，140B / 300B / 2T token 的训练量分别为 5.88e21 / 1.26e22 / 8.40e22 FLOPs，GPU-days 为 170 / 365 / 2 431；按 20 token/参数分配，1e22 / 1e23 / 1e24 算力对应 9.1B / 28.9B / 91.3B 参数与 183B / 577B / 1.83T token；7B 模型推理每 token 约 14 GFLOP。
- `sft_demo.py`：五个位置的 SFT 损失在全部 token 上平均 0.367，只算 assistant 时 0.520；LoRA rank 2、`alpha=4` 把输出从 `[0.300, 0.400, 0.300, 0.500]` 改为 `[0.300, 0.500, 0.300, 0.540]`，合并检查通过。`4096×4096` 矩阵上 r=8 的可训练参数为 65 536（0.391%），fp16 每层 128 KiB，32 层约 4 MiB；r=d 时为 200%，并不省。
- `alignment_demo.py`：四组奖励对的平均 Bradley-Terry 损失 0.681，成对准确率 1/4；差值 1.0 的损失 0.313，差值 0 的损失 0.693。示例的 chosen/rejected 概率之和不超过 1，极端负分差仍返回有限损失。DPO 在偏好正确时，`β=0.1` 的边际 0.05、损失 0.668，`β=1.0` 的边际 0.50、损失 0.474；偏好反转且 `β=1.0` 时边际 -0.30、损失 0.854。
- `rejection_demo.py`：固定 p=0.4 的候选模拟，过滤不更新策略；独立采样时 N=4 至少一个通过的理论概率为 0.8704，六题观测值会随 seed 波动。
- `serving_demo.py`：7B 配置的 KV cache 为 128 KiB/token；权重 fp16 / int8 / int4 分别为 14.0 / 7.0 / 3.5 GB。假设 `3e12 B/s`、每步一次权重读取及全量 KV 访问的带宽模型中，8K 上下文下批大小 1 / 8 / 32 的 decode 估算时间为 5.02 / 7.53 / 16.12 ms，吞吐为 199 / 1 062 / 1 985 tok/s；32K 上下文、32 路批处理需要 128 GiB KV cache，80 GiB 卡装不下。四请求两槽位的静态/连续批处理利用率为 60.9% / 97.5%。
- `session_ledger.py`：四轮会话共 19 500 个输入 token，其中 6 450（33.1%）是新增内容、13 050（66.9%）是原样重发；无缓存 / 只缓存稳定前缀 / 缓存整段前文的账单为 $0.07575 / $0.05145 / $0.04052（−32.1% / −46.5%），固定速率模型估计时间 32.75 / 28.25 / 26.23 s（不含缓存读取、排队和网络开销，费用假设无写入费且缓存存活）；峰值上下文 6 850 token，按 320 KiB/token 计单请求 2.1 GiB KV cache，八路并发 16.7 GiB。
- `rag_demo.py`：6 份文档切成 13 块，按版本过滤后剩 12 块；块大小 10 会把“原路退回”切断，20 不会。BM25 第一是 `refund-faq@v2#0`，向量第一是 `refund-policy@v2#0`，RRF 第一是 `refund-policy@v2#0`，玩具重排第一是 `refund-policy@v2#2`（到账时间 1–3 个工作日）。
- `retrieval_metrics.py`：5 条查询、两套排序，`k=3`。关键词优先的 `recall@3` / MRR / `NDCG@3` / `MAP@3` 为 1.00 / 0.90 / 0.77 / 0.92，向量优先为 0.93 / 1.00 / 0.97 / 0.90；首条查询的 recall@3 / RR / NDCG@3 / AP@3 为：关键词 1.00 / 1.00 / 0.81 / 1.00，向量 0.67 / 1.00 / 0.91 / 0.67。二值相关阈值为 grade > 0，RR 使用完整排序，AP@k 分母为 min(k,R)。
- `toolcall_demo.py`（2026-11-26）：紧凑 JSON 中 `description` 与 `inputSchema` 为 183 / 243 字符，不含工具名；订单号采用 ASCII 数字规则。整数订单号返回参数错误，字符串 `ORD-1001` 查询成功；非对象参数不再抛异常。MCP 2026-07-28 打印 `server/discover` / `tools/list` / `tools/call` 的三组请求与响应，每个请求含协议与能力元数据，完成结果含 `resultType`。未知工具返回顶层 `error`；不存在的订单返回 `result.isError`。
- `cot_demo.py`（2026-11-26）：第一组假设二元独立采样 `p=0.60`，1 / 3 / 5 / 9 / 15 次的模拟正确率为 60.7% / 66.0% / 69.4% / 75.2% / 79.5%，二项精确值为 60.0% / 64.8% / 68.3% / 73.3% / 78.7%；每题输出 400 至 6 000 token。成本表另设直接回答 p=.45、CoT p=.65；按每百万输出 token 0.60 美元，四策略的每道正确题输出成本为 $0.000133 / $0.000369 / $0.001561 / $0.004053，未计输入、工具和验证费用。
- `eval_demo.py`：200 题上 82.0% 与 86.0% 的 Wilson 区间为 [76.1%, 86.7%] 与 [80.5%, 90.1%]，两者重叠；相同总数下，不一致题目为 0/8 和 20/28 时，双侧精确 McNemar p 值分别为 0.0078 与 0.3123，说明区间重叠不能判定配对差异；20 条测试题在训练中见过，把 80.0% 的干净准确率抬到 82.0%；回答 80 题、对 72 题时覆盖率 80.0%、回答内准确率 90.0%、整体 72.0%、错答率 8.0%；教师/学生每道正确题成本约 $0.0071 / $0.0015。
- `multimodal_demo.py`（2026-11-26）：6×4 数值图按 2×2 切成 6 块，经手设 4×3 矩阵投影为 6 个 3 维向量；没有位置嵌入或 Transformer。1920×1080 原图的 patch 16 网格为 8 160 块，最长边限制到 1568 后为 5 488 块；缩放后面积 ÷750 的教学计数为 1 844。照片和扫描原图网格分别为 47 628、34 100 块。配置 A（768）/ B（1568）的面积计数为 442 / 1 844，不是当前 API 的 detail 档位或用量。额外验证不整除尺寸补零、小图不放大及投影维度不匹配时明确报错。
- `train_demo.py`：7 440 参数字符级 Transformer（435 个字符、743 个 UTF-8 字节、vocab 54、d_model 24、一层因果注意力 + FFN），手写前向与反向，SGD 经 warmup 12 步再余弦衰减到 10%，共 240 步。修正注意力输出和 Q/K/V 输入梯度的转置后，8 个抽样权重的解析梯度与中心差分最大偏差为 6.93e-12；训练语料内固定窗口的 loss 从 3.9886 降至 1.4882。step 60/120/180/240 的 3.92/2.19/2.32/3.20 来自不同抽样窗口，不能直接当作固定评测集曲线。相同初始化与抽样下，恒定 lr=0.6 的固定窗口 loss 为 1.1210；该单次对照不证明长训练或其他任务上的调度优劣。另在两组 seed 的缩小模型中放大非对称权重，逐项核对全部参数并覆盖重复 token 的嵌入梯度累加：修复前出现 152 处不一致，修复后在 1e-7 绝对容差内通过。
- `embedding_train_demo.py`（2026-11-26 修正 SGD 后）：12 词、16 维、36 句三主题语料训练 30 轮；训练前“退款”近邻为随机取向（换货 +0.39、配送 +0.32），训练后为售后 +0.99、换货 +0.99、退货 +0.98，12 个词 top-3 全部落回自己主题组。这里比较输入表的余弦；训练损失约束输入表与输出表之间的点积。sigmoid 使用分段稳定版，二元损失使用 softplus。

## 未实测范围

以下内容没有在本轮运行，正文中按“练习”或“待测”标注，未写成结论：

- 真实厂商模型上的温度 / top-p 对比与 seed 复现实验；
- 生产 tokenizer（如 `tiktoken`）与本书玩具 BPE 的跨模型计数对比；
- 真实编码器的语义检索质量（第 2 章的向量是手设三维玩具）；
- 真实预训练实验与集群吞吐（第 7 章只算 FLOPs 与显存粗账）；
- 真实推理框架的吞吐、延迟与显存占用（第 10 章只算显存流量与槽位占用）；
- 真实 RAG 检索质量（第 11 章的语料、向量与重排权重都是手设的）；
- 真实 MCP 服务器、权限、传输与幂等（第 12 章只演示协议形状）；
- 真实模型的自洽投票收益（第 13 章用二元独立过半模型模拟，未生成实际答案类别）；
- 真实评测集的置信区间、污染检查与蒸馏效果（第 14 章的计数与价格是手设的）；
- 真实多模态模型的识读对比与视觉幻觉率（第 15 章的 patch、投影与预算公式是手设玩具，未在真实 VLM 上验证）；
- 真实 LLM-as-judge 的偏差实测（第 14 章的位置偏差与自偏好只引论文证据，未在自己的 judge 管线上复测）；
- 真实 SFT / LoRA / QLoRA 训练实验（第 8 章只有手设概率与矩阵）；
- 真实偏好对齐实验与奖励模型训练（第 9 章只有手设分数与 log 概率）；
- 训练好的模型里注意力头实际学到了什么（本书示例的权重是手设的）；
- 大规模训练的梯度、优化器状态与分布式正确性；本卷已验证小模型的手写反向传播，不能据此推出生产训练结论；
- 长上下文位置效应（Lost in the Middle）的复现实验；
- GPU 显存占用、吞吐、延迟与并发压测；
- 真实价格与账单核对（脚本中的价格是输入参数，不是报价）。

这些缺口不影响正文的可运行性，但不能把本章的示意数字当作生产容量规划。

第四轮补充核对：`context_budget.py` 的 pair 数是每层、每查询头的有效位置对，费用仅算输入；`--calls 0` 输出零账单。`session_ledger.py` 将累计工具回执 4 800 与助手历史 1 500 分开列出，总输入仍为 19 500。BPE 表的长度列按 Unicode 码点计，脚本演示组合重音与严格 UTF-8 截断错误。
