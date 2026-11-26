# 第 2 章词向量与检索示例独立审读

审读日期：2026-11-26。冻结材料：`.scratch/aris-embedding-20261126/round1/`。

**评分：9.0 / 10。结论：Ready。CRITICAL：0；MAJOR：0；MINOR：2。**

本结论适用于本次指定的词向量、训练与 ANN 教学内容，不是全书或生产检索系统的认证。核心算术、负例抽样、检索记录身份、排序和书中数字均通过实际复现。两项轻微问题分别是速查表的类别混写和 PDF 的公式跨页，可在正常编辑中修整，不构成阻止交付的问题。

## 独立性与身份

本次以独立子代理的新上下文审读，仅收到评审范围及约束；未读取 round0、review1、旧评语、旧执行日志、聊天历史或 git diff。审读以冻结正文、代码、成品和固定上游源文件为依据。没有修改正文、示例、测试或构建配置，没有提交。

身份标记：**same-family / provisional**。可见会话将本代理标为 Codex / GPT-6 系列，但没有可独立核验的实际推理后端及 reasoning 档位证明。因此不以请求的 `gpt-6-astra xhigh` 名称证明实际身份，也不把这次审读计为已证明的异模型独立评审。

## 实际审读与执行范围

实读 `source/llm/ch02.md` 全章，`ch16.md` 的第 2 章关联术语；实读 `embedding_demo.py`、`embedding_train_demo.py`、`ann_demo.py` 和示例 README；实读 `test_llm_examples.py` 中 EmbeddingExample、EmbeddingTrainExample、AnnExample 及导入/执行入口。核对 `source-lock.json`、`sources-llm.json` 中相关固定来源及 `manifest-llm.json` 的产品说明。

实读固定上游 `word2vec.c` 的噪声表与 skip-gram 更新段、D2L 数据准备和训练的相关实现、Faiss Flat/IVF 教程，并核对 `IndexFlat.cpp` 的平方 L2 调用。7 个上游文件的大小、SHA-256 与 `source-evidence.json` 全部一致。没有将本例逐词对 SGD 冒称为对上游训练曲线的复现。

运行命令：

```powershell
python -B .scratch/aris-embedding-20261126/reviewer2/reproduce.py
python -B .scratch/aris-embedding-20261126/reviewer2/render.py
python -B .scratch/aris-embedding-20261126/reviewer2/mobile-detail.py
```

`reproduce.py` 用冻结路径依次启动三个示例，并仅运行三个相关测试类。**21 项测试通过**，包括正、负标签下同时核对输入/输出向量的数值梯度、重复向量的不同记录、空负例池和等距 ANN 结果的 ID 排序。另独立遍历全部 144 个句子/中心词组合，确认每个负例池恰有 8 个词，且全部属于其他主题。

在内存中把 `ann_demo.NOISE` 改为 1.4 后运行，`nprobe=1` 的召回从 0.865 降为 0.825，符合小实验的方向；未改冻结文件。没有扩展为生产级参数健壮性、Faiss 性能或真实语料评测，也没有运行整库测试，以保持指定审读边界。

PDF 通过 PyMuPDF 渲染，并**实际查看第 21–28 页及第 133 页图像**：覆盖第 2 章完整正文、两幅插图、全部公式、表格、小实验，以及 embedding 相关术语表。HTML 用本机 Edge 实际渲染到 **390 × 844 CSS px**，查看参数表、余弦近邻表、SGD 公式、InfoNCE、ANN 结果及词向量术语。宽表的右侧也实际滚动并截图查看。文档总宽度为 390 px；近邻表和术语表各自在 `.table-scroll` 内横向滚动，右侧列可达，没有整页横向溢出。

截图工具起初因全局 Playwright 安装目录的 Node 路径权限失败。随后只把已有驱动普通复制到自己的 `reviewer2/playwright-driver/`，由已有系统 Node 启动，未修改安全配置；截图已完成，不存在未完成的视觉检查。

## 核心核对结论

| 核对点 | 实际证据与结论 |
| --- | --- |
| 两张表的梯度 | `sgd_pair` 先计算同一步的 score/grad，每个坐标保留 old_center 与 old_context，再分别更新；正、负标签的数值差分都核对两侧参数。与 `g = sigmoid(s) - y` 一致。逐正负词对各做一次更新的范围已明确，不与 word2vec.c 的累计输入误差混淆。 |
| 负采样 | 有限候选池排除中心词和当前句子中该中心词已知的上下文，`rng.choice` 逐次有放回均匀抽样；空池明确报错。正文准确解释默认语料为何只得到跨主题负例，也提醒修改语料后不再保证这个性质。 |
| 训练结果口径 | seed=11 时，退款训练前近邻为换货 +0.39、配送 +0.32、物流 +0.17；训练后为售后 +0.99、换货 +0.99、退货 +0.98；同主题 top-3 为 12/12，与正文一致。pair loss 是在线、更新前、包含新负例的平均损失，正文未误称独立验证损失。 |
| 检索记录身份 | `exclude_name` 仅排除指定记录，默认不排除；不同名称的相同向量保留。外部查询和库内自查询的行为清楚。 |
| 点积与余弦 | A 的点积 3、余弦 1；B 的点积 6、余弦约 0.707；退款/不退款余弦 0.9997，表中三位小数为 1.000。两组四条近邻和正文逐项一致。没有把“含否定的近邻”泛化为余弦必定不能区分极性。 |
| 存储与扫描 | 131,072,000 / 24,576,000 参数，fp16 为 250.0 / 46.9 MiB；100,000 × 4096 × 4 bytes 约 1.5 GiB；409,600,000 次乘加，计算正确。 |
| ANN 与排序 | 固定数据下 nprobe 1/2/4/8 的扫描比例为 13.2%/25.0%/51.9%/100.0%，recall@10 为 0.865/0.997/1.000/1.000；最差查询 0.30，均吻合正文。精确搜索和 IVF 以距离、ID 共同排序，覆盖等距反例；全桶与精确结果一致。 |
| 距离与成本口径 | 自编示例用欧氏距离，Faiss METRIC_L2 对应平方 L2，正文准确区分数值与排序。扫描比例排除中心比较，且明确不等于耗时比例。 |
| 教学边界 | 静态输入嵌入、上下文表示、检索表示分开说明；受控 skip-gram 的聚类不被当作现代检索质量证明。两表点积目标也未被写成输入表余弦聚类的一般保证。 |
| 来源追溯 | word2vec 0.75 幂见上游 55–64 行；累计误差与最后更新输入表见 521–542 行；D2L 排除已知上下文见数据文件 305–318 行，批反向/优化器步骤见训练文件 299–303 行；Faiss `knn_L2sqr` 见 IndexFlat.cpp 43–45 行。固定提交与两个注册表一致。 |

复现原始输出位于 `.scratch/aris-embedding-20261126/reviewer2/reproduction.txt`；修改噪声的输出位于 `ann-noise-1.4.txt`。

## Findings

### MINOR-1：术语表把 ANN 与 HNSW 写成同一项，层级不够明确

证据：冻结 `source/llm/ch16.md:33`：

> `ANN / HNSW | 近似最近邻索引，用召回率换检索速度`

PDF 第 133 页也显示这一合并词条。ANN 是近似最近邻问题/方法的总称，HNSW 是其中一种基于分层图的具体方法；同一表里的 IVF 又独立成项。正文 2.7 已明确区分四类结构，速查表在这里反而丢失了层级，对跳读术语表的初学者容易形成“ANN 就是 HNSW”的误解。

最小建议：拆为两条，ANN 写“近似最近邻搜索，在召回、延迟和内存之间取舍”；HNSW 写“以分层近邻图实现 ANN 的方法”。无需扩展算法推导。

### MINOR-2：五行 SGD 核心公式在 PDF 第 23–24 页间拆开

证据：冻结 `source/llm/ch02.md:76` 起的公式块。实际图像 `pdf-page-23.png` 页底只显示 `s`、`loss`、`g`，`pdf-page-24.png` 页首显示 `v_new`、`u_new`。两页没有丢字，公式正确，但读者需翻页才能把梯度与两侧更新对应起来。

最小建议：排版时将这一个短公式块整体移到下一页，或为短公式块使用不跨页的规则；不必改变公式或正文解释。该意见基于成品视觉，不是推测构建器实现。

## 视觉证据与产物身份

实际查看的主要图像都位于 `.scratch/aris-embedding-20261126/reviewer2/`：

- PDF：`pdf-page-21.png` 至 `pdf-page-28.png`、`pdf-page-133.png`。
- 390px HTML：`mobile390-chapter2.png`、`mobile390-sgd.png`、`mobile390-contrastive.png`、`mobile390-ann-table.png`、`mobile390-neighbours.png`、`mobile390-neighbours-right.png`、`mobile390-glossary.png`、`mobile390-glossary-embedding-detail.png`。
- 宽表尺寸与滚动证据：`mobile-table-evidence.json`；所有指定文件的独立哈希：`reviewed-hashes.json`。

冻结 HTML SHA-256：`7dc0e6f1416dc5e929fe7719f9688d48b364a4ef0eac5ebe1a7be52515c795bb`。

冻结 PDF SHA-256：`e6fac45f6aecf6e84b7f72883cf0ca258dac3a7d7c0804c4502a73b061da4c36`。

除上述两项轻微编辑意见外，没有发现需要修改训练逻辑、采样逻辑、检索身份或 ANN 排序的证据。手机端宽表横向滚动属于有效布局，不能据初始截图的右侧截断误报为内容缺失。
