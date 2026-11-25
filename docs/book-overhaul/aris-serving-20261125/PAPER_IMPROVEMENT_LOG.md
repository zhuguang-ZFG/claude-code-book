# LLM 书稿：对齐、推理服务与检索复核

本轮范围为第 9–11 章、第 16 章相关术语和五个教学示例。使用已安装的 ARIS auto-paper-improvement-loop 书稿适配：两个 fresh-context 审读者，审读后修订并构建。本地修改不发布、不提交。

## 审读记录

| 审读输入 | 评分 | 判断 | 状态 |
| --- | --- | --- | --- |
| round0 原稿与页面 | 5/10 | No | 2 CRITICAL、7 MAJOR、2 MINOR；已修订 |
| round1 修订稿与页面 | 9.1/10 | Ready | 无 CRITICAL/MAJOR，3 MINOR 已修订 |

请求模型均为 gpt-6-astra / xhigh，工具未返回实际模型身份，记为 null。此审读为 same-family / provisional；分数是对应输入快照的判断，不代表修订后的自动加分。

## 第一轮审读原文

<details>
<summary>完整报告</summary>

本次评分：**5/10；结论：No**。范围仅为第 9–11 章、对应示例及第 16 章相关术语。审读为 **same-family / provisional**，不是跨模型家族独立验收。未修改文件。

主要优点：

- 第 10 章把权重、KV cache、吞吐和槽位利用率分开计算，假设与实测的边界基本明确。
- 第 11 章的玩具检索链路完整，BM25、向量、RRF 与重排的输出能复现正文。
- Bradley–Terry、DPO 损失和检索指标的默认数表均可复现。
- 工程建议能连接实际问题，例如奖励黑客、版本过滤、检索与生成分开评测。

以下问题按严重程度排序。同一来源或概念混淆造成的问题已合并。

**CRITICAL 1：GRPO 的定义、来源与训练机制混淆。**

位置：`llm/ch09.md:157–179`，相关复述见 `:117`、`:173`、`:229`；`llm/ch16.md:146–147`。

原句包括：

> “既不要奖励模型，也不要 critic”
> “DeepSeekMath 的 GRPO 用的是脚本规则赏值”
> “DeepSeek-R1……要跳过监督微调、直接走纯 GRPO”
> `loss = -mean_i(A_i · log π_theta(y_i | x))`

核对 [DeepSeekMath](https://arxiv.org/abs/2402.03300) §4.1–4.2，原文明确使用奖励模型；§4.2 还说明初始奖励模型基于 DeepSeekMath-Base 7B 训练。GRPO 去掉的是独立价值模型，奖励可来自规则，也可来自模型。其原始目标包含策略概率比、裁剪、序列内 token 聚合与 KL 项，正文公式只是未注明条件的奖励加权策略梯度简式。

此外：

- 原文中的 β 是 KL 系数，不是“赏值放大”的开关。
- 全组同分时，减去均值后的优势已经为零；`eps` 防止除零，并不能恢复学习信号。
- 对奖励统一乘正数时，标准化优势基本不变，不能推出“赏值跨度变大”导致 `A` 与输出长度“二次相关”。实测 `[0,1]` 与 `[0,100]` 的标准化优势均约为 `[-1,1]`。
- 跳过 SFT 的是 **DeepSeek-R1-Zero**。[R1 论文](https://arxiv.org/abs/2501.12948)明确区分它与包含冷启动、拒绝采样、SFT、RL 的 DeepSeek-R1。
- “比 DPO 稍轻”没有依据：GRPO 需要在线采样，成本取决于组大小、输出长度、奖励实现和更新配置。

修法：围绕“省掉价值模型、用组内奖励构造优势”重写本节；补上原始目标，或明确标注简式省略了哪些项。区分 DeepSeekMath、R1-Zero、R1 的训练流程。保留 **51.7%**，同时注明其对应 DeepSeekMath-RL 7B 的 MATH 结果及原文评测条件。同步修改术语表。

**CRITICAL 2：PRM/ORM 段落把实现、标注来源和实验设置归错给原论文。**

位置：`llm/ch09.md:184–195`，相关汇总见 `:230`；`llm/ch16.md:145、148–149`。

原句包括：

> “Lightman 的实现……损失只放在终点 token 上。”
> “用一个三分类头（num_classes=3）……”
> “用 ORM 合成步骤训练数据（见……PRM800K）。”
> “PRM 78.2% vs ORM 72.4%”

核对 [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050)：

- 附录 E 明确说明：ORM **训练时对回答中的每个 token 使用相同的结果标签**，测试时才取最终 token 的分数。正文将训练位置与推理取分位置混淆。
- §2.6 描述 PRM 在步骤之后预测标签 token，可用标准语言模型训练流程；不能把自行设想的 `nn.Linear`、`num_classes=3` 写成论文实现。
- §2.4 和官方 PRM800K README 明确为人工步骤标注，不能作为“ORM 自动合成步骤标签”的例子。
- **78.2% 与 72.4% 是 best-of-1860 的结果**，评测为保留的 500 道 MATH 测试题；不是普通单次生成准确率。
- 规则验证器可以提供结果或过程奖励，但不能因此直接等同于“学习出的 ORM/PRM”。术语表将 verifier 限定为精确判错程序，也与其所引 GSM8K 学习型 verifier 不符。

修法：分别解释监督信号粒度、奖励模型训练、推理评分及策略优化；删除未经来源支持的实现细节。保留原数值，补足候选数量和测试范围；将 PRM800K 改为人工标注案例。

**MAJOR 1：DPO 的 β 与策略漂移关系写反。**

位置：`llm/ch09.md:79、126–127`。

原句：

> “β 越大……策略更容易偏离参考模型”
> “β 过大｜策略偏离参考，输出模式坍塌”

[DPO 原论文](https://arxiv.org/abs/2305.18290)式 (3)–(5) 中，β 对应 KL 正则强度，最优策略满足：

```text
π*(y|x) ∝ π_ref(y|x) · exp(r(x,y) / β)
```

固定 gap 时增大 β 确实改变损失和局部梯度，但不能据此推出训练后的 KL 更大；固定奖励下，较大 β 对应更强的参考约束。

修法：保留现有损失表，分开讲“固定输入的损失形状”和“优化目标中的正则作用”；替换翻车表中的方向性结论，说明实际漂移还取决于学习率、步数与数据。

**MAJOR 2：DPO 示例的“log 概率”不是合法的回答概率。**

位置：`llm/examples/alignment_demo.py:20–22`，正文关联 `llm/ch09.md:72–79`。

两组 chosen/rejected 被视为同一 prompt 下不同完整回答，但指数和分别为：

| 案例 | 策略概率和 | 参考概率和 |
|---|---:|---:|
| 偏好正确 | 1.367542 | 1.276851 |
| 偏好反转 | 1.489051 | 1.155342 |

两条互斥完整回答的概率和不能超过 1。手设数据也必须满足所声称的概率含义。

修法：把每组四个 log 概率统一减去适当常数，例如 2，可以保留所有 log 比、gap、边际和损失数值，同时使概率合法；同步修改末尾 worked example。无需为了修正概率而删除现有表格。

**MAJOR 3：拒绝采样示例把人为上调概率写成学习效果，并混淆过滤与训练梯度。**

位置：`llm/examples/rejection_demo.py:81–87、122–123`；`llm/ch09.md:199、208、220、231–234`。

原句：

> “self-taught 循环四轮把 p 从 0.4 抬到约 0.86”
> “拒绝采样没有梯度穿过生成过程，只有一道过滤门槛”
> “梯度落在哪：无（过滤数据）”

实际代码直接执行：

```python
p = p + ALPHA * (kept / attempts) * (1.0 - p)
```

没有拟合模型，也没有在过滤样本上执行 SFT。`0.862` 是人为更新规则的结果，不能支持自训练有效的结论。GRPO 同样通常不对离散采样做路径导数；区别在于策略梯度加权与过滤后的监督学习，而非是否“穿过生成过程”。本节已定义“过滤后再 SFT”，汇总表却把整个方法写成无梯度。

此外，`1-(1-p)^N` 需要明确“独立采样、同一成功概率、完美验证器”的假设。`WRONG` 中的 `FF`、`0xff` 对“用十六进制写 255”并非数学错误，当前 p 实际是命中指定字符串的概率。

修法：明确称为概率模拟，展示人为更新式，并说明没有训练或验证泛化；或者实现真正的小型拟合过程。区分过滤无梯度与后续 SFT 有梯度。给十六进制题补充小写、无前缀的格式要求；将“天花板只由验证器决定”改为同时受候选覆盖和验证器限制。

**MAJOR 4：投机解码的加速条件被绝对化。**

位置：`llm/ch10.md:105`。

原句：

> “起草被接受的步数等于这步白赚的算力”
> “加速比完全取决于……分布的吻合度”
> “两个模型的词表和分词必须对齐”

即使接受率相同，草稿模型耗时、目标模型验证成本、草稿长度、批量和硬件不同，也会改变加速比。接受 token 并非免费计算。另据 Transformers **v4.57.3** 官方 [generation_strategies.md](https://github.com/huggingface/transformers/blob/v4.57.3/docs/source/en/generation_strategies.md)，Universal Assisted Decoding 已支持不同 tokenizer，经重编码和匹配完成验证。

修法：解释接受率与草稿/验证成本共同决定收益；把共享词表限定为基础实现的条件，并注明存在支持不同 tokenizer 的扩展。“模板、代码快，开放生成慢”应写成待负载验证的经验判断。

**MAJOR 5：prefix caching 的 2.2× 被写成无条件收益。**

位置：`llm/ch10.md:113、123–125`。

原句：

> “prefix caching 命中后重复调用同样块做到 2.2× 的吞吐提升”

缺少模型、硬件、前后缀长度、输出长度、并发、基线和框架版本。本次未取得 Hands-On 指定页或对应基准，**2.2× 尚未核实**。

已读取 vLLM 官方 APC 文档：它减少共享前缀的 **prefill** 工作，不减少 decode；输出很长或没有可复用前缀时，收益可能很小。PagedAttention 的分页管理与 APC 的计算复用也应分别说明。

修法：找到原始基准后，保留 2.2× 并补齐条件；若无法定位，改为机制说明和可复现实测步骤。框架选型建议及命令应绑定版本，避免由单一功能直接推出固定首选框架。

**MAJOR 6：按章内练习恢复旧版本后，RRF 会把新旧片段合并并返回旧政策。**

位置：`llm/examples/rag_demo.py:80–87、141–149`；练习入口 `llm/ch11.md:168`。

片段 ID 为：

```python
f'{doc["id"]}#{index}'
```

把 `min_version` 改为 1 后，两个版本同时使用 `refund-policy#0`。RRF 按这个 ID 累加两份文档的分数，并由后出现的内容覆盖前者。

实际复现结果：

```text
duplicate IDs: {'refund-policy#0': 2}
retained refund-policy#0:
version=1
退款政策（旧版）：退款审核通过后 7 天内退回。
score=0.06327607388058208
```

这会把“比较新旧版本”变成身份碰撞。此外，“再打开 dedupe”与当前代码不符：默认已经调用 dedupe，原始语料也没有可被它删除的同文重复块。

修法：将版本纳入块 ID，或先按显式策略选版本再建索引；增加对应行为检查。调整练习，使重复去除确有可观察对象。

**MAJOR 7：检索指标的解释与实现、术语表不一致。**

位置：`llm/ch11.md:79–86、109`；`llm/ch16.md:192、195`；`llm/examples/retrieval_metrics.py:52–85`。

原句：

> “怕‘用户第一眼看到的是次要答案’，盯 NDCG@k 与 MRR”
> `recall@k`：“前 k 个结果里包含正确片段的比率”

实现将 `grade > 0` 都计作相关。因此“退款多久到账”的关键词排序把 grade=1 放第一，MRR 仍为 **1.0**。MRR 不能区分此处的“完整答案”和“相关但不完整”。术语表中的 recall 定义也容易被理解为 precision@k 或 hit@k；实际分母是标注相关文档总数。

修法：明确二值相关性阈值；让 NDCG 负责分级排序，MRR 负责首个二值相关命中的位置。把 recall 写为“前 k 中相关文档数 / 标注相关文档总数”。补充本例 AP@k 分母采用 `min(k,R)`、MAP 再跨查询平均的约定，避免读者复算采用另一种截断定义。

**MINOR 1：量化零点定义不足以复算，术语表也不准确。**

位置：`llm/ch10.md:85–93`；`llm/ch16.md:166`。

> “Z = 把 α 对齐到整数零点的偏移”
> “零点对齐与否的两类均匀量化”

零点是浮点 0 对应的整数编码；非对称量化也需要表示浮点 0，并非“不对齐零点”。建议给出带 `q_min/q_max` 的 Z 定义，并在量化公式中补上范围裁剪。对称量化的 `Z=0` 应注明这里采用有符号整数编码。该项属公式完整性问题，不影响已复现的显存数表。

**MINOR 2：第 9 章有明显的术语与编辑残留。**

位置：`llm/ch09.md:117、157、165、175–184`。

“赏值／奖值／奖励”“批评者／评论器／critic”混用；“只赚组内相对性”“β 门板”“赏值的方差充分”含义不清。第 157 行多余方括号、第 184 行未闭合方括号已原样进入成书 HTML。“后面的幻觉率（见 9.7）”既指向前文，也没有对应内容。

修法：统一为“奖励”“价值模型（critic）”“组内相对优势”，删除编辑括号，修正具体交叉引用。无需改动已经通顺的段落。

需要补足或重新定位的来源：

- GRPO、DeepSeekMath 与 R1-Zero/R1：使用上述原论文具体小节，修正已有误引。
- PRM800K 的人工标注、ORM token 监督位置、best-of-1860 设置：引用论文 §2.4–2.6、图 3、附录 E–F。
- vLLM 的 **2.2×**：缺少可核对的原始实验位置和配置；官方 APC 文档只能支持机制与适用条件。
- RRF 的公式和 `k=60`：建议补 Cormack、Clarke、Buettcher 的 RRF 原始文献。
- NDCG：说明使用指数增益版本，避免把所有具体公式约定都无区分地归于 2002 年论文。
- “N=4–32 常见”“拒绝采样是最便宜的自我改进”等比较性说法，需给出范围或依据。

实际运行结果：

- 五个指定脚本均运行成功。
- 对齐平均损失 **0.681**，成对准确率 **1/4**；DPO 四项损失与正文一致。
- 拒绝采样模拟最终 **p=0.862**；它来自手设更新规则。
- 服务示例的 KV、时延、吞吐数表及 **60.9% / 97.5%** 利用率均复现。
- RAG 默认排序与正文一致；恢复旧版本后复现上述 ID 冲突。
- 检索指标均值为关键词 **1.00 / 0.90 / 0.77 / 0.92**，向量 **0.93 / 1.00 / 0.97 / 0.90**，与正文一致。
- `python -B -X utf8 -m unittest discover -s tests -p test_llm_examples.py -v`：**103 项通过，60.153 秒**。本次未运行完整 `make check`，这些测试通过不能证明来源归属与教学解释正确。

视觉覆盖：

已通过 `view_image` 实际检查三张指定的 **1440×1000** 截图，并读取 round0 HTML 对应段落。截图覆盖第 9 章约 **9.6–9.8**、第 10 章约 **10.4–10.5**、第 11 章约 **11.4–11.5**。这些区域的正文、代码块、表格、导航和中文字体可读，未见明显横向裁切。

截图没有覆盖 GRPO/PRM 全节、全部插图、章末来源、移动端或打印分页，因此不能据此认定全章视觉验收通过。当前阻止交付的主要问题是第 9 章的技术错误，以及 RAG 练习中的版本身份冲突。


</details>

## 第一轮处理

- 重写 GRPO、PRM/ORM、DPO β 与拒绝采样的解释，区分奖励模型、价值模型、评分和策略训练。PRM 实验保留 78.2% / 72.4%，补齐 500 题与 best-of-1860。DeepSeekMath 的 51.7% 非本节论证所需，移除性能旁枝，保留算法原始出处。
- 损失使用稳定的 softplus 形式；手设回答 log 概率统一下移，保留原 gap 与损失表；删除通过手设公式提高 p 的伪训练曲线。
- 推理表明确为带宽模型，补全仿射量化的零点、舍入、裁剪，改正投机解码与前缀缓存的收益条件；未能核对的 2.2× 性能倍数与书籍章号归因已移除。
- 片段 ID 纳入版本，新增新旧文档融合回归；修正去重练习、索引新鲜度、权限检查位置、RR/AP 与 MRR/MAP 口径。
- 同步术语、示例说明、来源登记与固定提交。公开 RLHF Book 的第 9 章实际读取；Z-Library 本次返回 Access denied，未将其记为全文证据。GitHub MCP 鉴权失败时用固定提交的公开 raw 地址读取。
- 新增两项行为回归先失败、修复后通过。105 项 LLM 示例测试通过；round1 HTML 构建成功。四章标题、block ID 与插图引用均与 round0 相同。

## 视觉检查

round1 在 390 / 1440 宽度及 light / dark 下完成 24 项章节位置检查，没有整页水平溢出。主代理实际查看 GRPO 窄屏浅色、指标宽屏暗色、缓存窄屏暗色、量化宽屏浅色截图。窄屏代码块与缓存表存在局部横向滚动，待最终修订时缩短行宽与表格标签。未检查整本 PDF 或打印分页。

## 来源与产物

- 原始来源及提取文本：`.scratch/aris-serving-20261125/sources/`。
- 原稿、第一轮稿与 HTML：`.scratch/aris-serving-20261125/round0/`、`round1/`。
- 可见布局截图：`.scratch/aris-serving-20261125/visual-round1/`。
- 回归红/绿日志、示例与构建日志：`.scratch/aris-serving-20261125/`。
- 完整审读调用与路由：`.aris/traces/auto-paper-improvement-loop/2026-11-25_run02/`。

## 第一轮完整验证

- `python scripts/bookctl.py check --fast`：9 步通过。仓库测试 453 项（1 项跳过），构建器测试 629 项；483 个 Markdown、280 个 Mermaid 图检查通过。视频检查仅验证配置，不代表媒体渲染验收。
- `python scripts/bookctl.py build --product collected --lang zh --check --mermaid source`：12 卷、286 单元组装通过。
- `git -c core.safecrlf=false -c core.whitespace=cr-at-eol diff --check`：通过。
- 原始来源文件的 SHA-256 清单保存在 `sources/artifact-hashes.json`，只用于本次读取记录，不将可变 URL 描述成永久版本。

## 第二轮审读原文

<details>
<summary>完整报告</summary>

**审读结论：9.1 / 10；Ready。** 本次范围内未发现 CRITICAL 或 MAJOR 问题，发现 3 项非阻断的 MINOR 问题。第 9–11 章的关键公式、数字和示例行为能够对应，正文已足以作为带有明确假设的入门教材交付；术语表和辅助说明还有少量需要同步的地方。

评审日期：2026-11-25。评审性质：**same-family / provisional**，不是跨模型家族验收。`requested_model=gpt-6-astra`，`requested_reasoning_effort=xhigh`，`actual_returned_identity=null`；工具未提供可核实的实际返回模型身份。

本报告从当前书稿和指定资料独立审读，未读取旧报告、其他轮次、状态日志或其他代理消息。未修改书稿、示例或生成产物。建议均可在保持章节标题、块 ID 与插图引用稳定的情况下完成。

**优点**

- 第 9 章区分了偏好标签、奖励模型分数与任务正确性。DPO 的完整回答 log 概率、固定 gap 下的 β 效应、对应 KL 正则化目标以及梯度，都没有混为同一结论。手设案例的概率质量也合法。
- GRPO 的介绍包含组内优势、新旧策略概率比、裁剪和参考 KL，并将原论文与 TRL 的实现选项分开。全组同奖励、G=1 和生成成本的限制写在相应公式附近，有助于防止读者照抄一个简化损失便宣称实现了完整算法。
- PRM/ORM 的归属和实验口径准确：结果标签不等于损失只能放在最后一个 token；78.2% 与 72.4% 是指定候选集上的选择结果。拒绝采样示例也明确说明过滤不更新 p、生成全部候选后再筛选。
- 第 10 章把 GB/GiB、权重/KV、理想带宽模型/设备基准区分清楚；APC 的 prefill 收益、完整块与计算上下文匹配、多 LoRA 的 KV 成本都有明确边界。
- 第 11 章的权限过滤位置、版本化块 ID、手设向量的平局、玩具重排公式都能从程序验证。指标明确给出二值相关阈值、AP 分母、完整排序上的 RR、零相关查询的处理，解释了指标之间为何互有胜负。
- 中文整体连贯，开篇问题能够连接后续算例。多数限定直接服务于当前例子，未发现需要仅因“像修订记录”或个人措辞偏好而重写的段落。

**按严重度发现**

CRITICAL：无。

MAJOR：无。

**MINOR-1：术语表仍把学习模型写成部分方法的唯一实现，与正文及同表定义不一致。**

位置与短引：`llm/ch16.md:151` 的 best-of-N 定义为“按奖励模型选一个”；`llm/ch16.md:221` 的 verifier 定义为“给候选答案或步骤打分的模型”。但 `llm/ch16.md:145` 已定义 verifier 为“规则程序或学习模型”，`llm/ch09.md:207` 同样明确两种实现，`llm/ch09.md:245` 将 best-of-N 的依据写为“候选分数或验证结果”。

可复现证据：运行 `python llm/examples/rejection_demo.py`，会得到 best-of-N 结果；其 `passes()`（`rejection_demo.py:46`）仅做字符串精确比较，没有奖励模型。两处简短定义会让只查术语表的读者误以为该示例不属于所介绍的方法，或把 verifier 等同于神经网络。

最小修法：将 best-of-N 的“按奖励模型”改为“按评分器或验证结果”；将第二个 verifier 定义也写为“判断候选答案或步骤的规则程序或学习模型”，或明确该行只指“学习型 verifier”。无需增加新小节。

**MINOR-2：RAG 示例最后一行把 cross-encoder 写成生产系统的必需组件。**

位置与短引：`llm/examples/rag_demo.py:199` 至其后两行打印：`a production stack needs trained encoders, a cross-encoder and an evaluation set`。

可复现证据：运行 `python llm/examples/rag_demo.py`，最后一行确实出现上述断言。正文 `llm/ch11.md:70` 则允许“交叉编码器或一个小模型”，并把本例标为玩具重排；`llm/ch11.md:62` 也允许先从现成编码器加 BM25 起步。检索链路可以按任务选择是否使用稠密编码器和重排，cross-encoder 并不是 RAG 成为生产系统的定义性要求。该输出把可选架构收窄成了硬性条件。

最小修法：把结尾改为“生产系统应使用真实语料与评测集验证检索质量；稠密检索和重排组件按任务选型”，或者保留英文并将 trained encoders / cross-encoder 改为条件性说明。计算与排序逻辑不需要变化。

**MINOR-3：实测记录的完整复跑清单漏掉拒绝采样脚本。**

位置与短引：`llm/VERIFY.md:50` 称“二十一个脚本……本节保留完整命令以便复核”，但命令块在 `llm/VERIFY.md:64` 的 alignment 后直接接 serving；`llm/VERIFY.md:85` 又记录了 rejection 的实测结论。`llm/examples/README.md:44` 与 `llm/ch09.md:142` 均包含该命令。

可复现证据：按正则 `^python llm/examples/(\S+\.py)$` 提取两份文档的命令，VERIFY 为 20 条，README 为 21 条，集合差恰好是 `rejection_demo.py`。读者复制 VERIFY 的完整清单时会遗漏第 9 章的一项实验。

最小修法：在 VERIFY 的 alignment 命令后补上 `python llm/examples/rejection_demo.py`。不需要改动历史测试数字来掩盖这项清单遗漏。

**实际运行与核对范围**

实际阅读了 `llm/ch09.md`、`ch10.md`、`ch11.md`，第 16 章中相关术语和重复的 verifier 定义；五个指定示例、对应测试类、VERIFY、示例 README，以及 `yuyu-book/sources-llm.json` 和 `llm/facts/source-lock.json` 的相关条目。

实际逐一运行以下五个入口，均正常退出；使用 `PYTHONDONTWRITEBYTECODE=1` 避免写入缓存：

```bash
python llm/examples/alignment_demo.py
python llm/examples/rejection_demo.py
python llm/examples/serving_demo.py
python llm/examples/rag_demo.py
python llm/examples/retrieval_metrics.py
```

复现的主要结果：BT 平均损失 0.681、准确率 1/4；DPO 四项损失为 0.668、0.474、0.708、0.854；KV 为 128 KiB/token，32K × 32 路为 128 GiB，槽位利用率为 60.9%/97.5%；RAG 从 13 块过滤到 12 块，重排首位为 `refund-policy@v2#2`；检索均值分别为 `1.00/0.90/0.77/0.92` 与 `0.93/1.00/0.97/0.90`。这些值与正文一致。

通过 importlib 加载 `tests/test_llm_examples.py`，实际运行 `AlignmentExample`、`ServingExample`、`RagExample`、`RejectionExample`、`RetrievalMetricsExample` 五个测试类，**26 项全部通过**。另用只在内存中执行的针对性检查验证：

- 两组 DPO 案例中，策略与参考各自的 chosen/rejected 概率之和均小于 1。
- β=0.7、gap=-0.3/0/0.5 时，中心差分与 `-β·sigmoid(-β·gap)` 一致，误差小于 `3e-11`。
- p=0.2/0.4/0.6、N=4 的理论通过概率为 0.5904/0.8704/0.9744；p=1、N=16 时，六题仍生成 96 个候选，未因第一个通过而节省生成。
- 无相关文档时 recall、NDCG、AP 均返回 0；截断 AP 的分母和完整排序 RR 的行为符合正文约定。

来源核对使用 `.scratch/aris-serving-20261125/sources/` 中的原始论文转文本与官方文档，核对重点如下：

| 来源 | 实际核对的内容与结论 |
| --- | --- |
| DPO，§4、附录 A 与实现 | 最优策略中的 `exp(r/β)`、偏好损失和参考约束支持第 9.4 节。 |
| DeepSeekMath v3，§4.1–4.2、式 3–4、Algorithm 1 | 确实省去独立价值模型，并使用、训练奖励模型；组内标准化、token 平均、概率比裁剪与 KL 支持正文。 |
| TRL v0.25.0，固定 SHA `55f5433…` 的 GRPOTrainer 文档 | 奖励模型/函数、默认 β=0、长度归一化与奖励缩放选项均有依据；另从固定 GitHub 原始 URL 读取，确认与本地文档在换行规范化后完全一致。 |
| DeepSeek-R1 报告 | R1-Zero 的无前置 SFT 与 R1 的多阶段训练有明确区分，正文没有把两者混写。 |
| Let's Verify Step by Step，§2.4–2.6、图 3、附录 C/E/F；PRM800K README | 核实人工步骤标签、ORM 的逐 token 同标签训练与末 token 评分、500 题/1 860 候选、78.2%/72.4% 及步骤概率乘积。 |
| RLHF Book 第 9 章，固定 SHA `b0926fd…` | 生成、评分、筛选、随后 SFT 的阶段划分支持正文；筛选本身不等于策略训练。 |
| vLLM v0.11.0 的 prefix caching、APC、LoRA 文档 | 核实完整块、父块/token/附加哈希、LoRA 与缓存盐、APC 的 prefill 收益范围及按请求指定 adapter。相关源码 SHA 与登记项一致。 |
| 投机解码论文 §2.3；Transformers v4.57.3 generation strategies | 接受判定与残差分布支持精确采样说明；UAD 文档明确允许不同 tokenizer 并进行重编码。 |
| ONNX Runtime 量化文档；RRF 原论文 | 量化缩放与零点解释相符；RRF 公式及常数 60 的实验来源相符。 |
| Burges 等，Learning to Rank using Gradient Descent，式 16 | 从 Microsoft Research 原始 PDF 在线核实指数增益与位置折扣形式，独立支持示例采用的 NDCG 变体。 |

对 Järvelin 与 Kekäläinen 2002 年论文，本轮只核实了书目信息，作者旧站全文获取失败；不声称已完成该全文的逐式核对。登记文件 `sources-llm.json:896` 对具体指数增益版本的来源范围写得较强，进一步来源清理时宜与正文“思想来源/本例变体”的区分保持一致；本轮不以未取得的全文为依据判定其错误。未重新核验本范围内所有背景链接的全文，例如 InstructGPT、DPR、Ragas 和 GPTQ。

**视觉观察与限制**

实际通过 `view_image` 查看以下 6 张截图，目录均为 `.scratch/aris-serving-20261125/visual-round1/`：

| 截图 | 覆盖 |
| --- | --- |
| `grpo-390-light.png` | 第 9 章，390 px，浅色 |
| `prm-1440-dark.png` | 第 9 章，1440 px，深色 |
| `quantization-390-dark.png` | 第 10 章，390 px，深色 |
| `cache-1440-light.png` | 第 10 章，1440 px，浅色 |
| `metrics-1440-light.png` | 第 11 章，1440 px，浅色 |
| `retrieval-390-dark.png` | 第 11 章，390 px，深色 |

所见范围中文字、上下标引用、表格和段落层级清楚；桌面侧栏未遮挡正文，手机长 ID 能换行，量化公式在手机截图中完整显示。GRPO 的长概率比和裁剪公式在 390 px 初始视图中需要横向查看。已检查指定 HTML：代码块使用 `overflow-x:auto`、`white-space:pre`，并有 `tabindex="0"`，因此没有把截图右缘截断直接判成公式丢失。

本轮没有实际操纵浏览器验证横向滚动、键盘焦点或主题切换，也没有覆盖全部 24 张截图、整本 PDF/EPUB 分页、打印效果和辅助技术。未重新运行完整 `make check` 或整本构建；上述 26 项针对性测试与六张截图不能代替全仓库发布门禁。未运行真实 GPU serving、真实模型对齐训练或生产 RAG，这与本次示例所承诺的范围一致。

**交付判断：Ready（限定于本次审读范围，same-family / provisional）。** 三项 MINOR 均有局部修法，不影响已核对的核心解释和算例；发布前宜完成这些同步，并由主流程完成整本检查与独立验收。


</details>

## 第二轮处理

- best-of-N 与两处 verifier 定义统一为评分器/验证结果、规则程序/学习模型；修正 RAG 结尾的强制 cross-encoder 断言。
- VERIFY 补齐拒绝采样命令，复跑清单与示例 README 同为 21 项。
- NDCG 来源登记与正文一致，区分思想来源和本例的指数增益变体，不声称已逐式读取未取得的原论文。
- GRPO、PPO、量化与检索公式按手机宽度分行，GRPO 写明最大化 J；缓存表压短标签。章节标题、块 ID、插图引用不变。

第二轮评分针对修订前的 round1 输入；上述三项修复与版式改进由主代理验证，不追加第三次评分。

## 最终验证与产物

- 最终 `check --fast` 9 步全部通过：仓库 453 项测试（1 项跳过），构建器 629 项；483 个 Markdown 文件及 280 个 Mermaid 图零错误。
- 第 9–11 章所有代码/公式块在 390 px 宽度无需横向滚动，压缩后的缓存表也完整适配。24 项位置/宽度/主题检查通过。主代理实际查看最终 GRPO 窄屏浅色、缓存窄屏暗色、检索指标窄屏浅色截图；多列数表仍使用已有的表内横向滚动。未验证 PDF/EPUB 分页及真实 GPU 性能。
- 21 条复跑命令与 README 完全一致；四章标题、block ID、插图引用均保持稳定。
- `round2/yuyu-llm-zh.html` 构建通过：17 单元、31 图版、167 引用链接。源稿与示例快照保存到 `round2/`。
- 十二卷合订本组装检查通过：12 卷、286 单元、366 图版。仅检查组装，未发布。
- 两项新增回归分别验证极端负分差的有限损失、新旧文档版本的独立融合；最终完整测试包含 105 项 LLM 示例测试。
- 最终验证摘要及 HTML SHA-256：`.scratch/aris-serving-20261125/final-verification.json`；日志为 `check-final.log`、`build-round2.log`、`collected-final.log`、`visual-final.log`。
- 最终预览：[LLM 卷 HTML](../../../.scratch/aris-serving-20261125/round2/yuyu-llm-zh.html)。

两轮审读完成：首轮 2 CRITICAL / 7 MAJOR / 2 MINOR、次轮 3 MINOR 均已处理。未进行第三轮模型打分；最终结论仍限定于本轮范围及 same-family / provisional 审读。保留工作区原有改动，未提交、推送或发布。
