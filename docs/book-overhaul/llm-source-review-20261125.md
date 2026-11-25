# LLM 卷：教材与官方实现核对记录（2026-11-25）

本轮接续同日的行文精修，修改 LLM 卷第 2、4、16 章，以及第 4 章的标准库示例。重点是区分教学模型、数学性质和真实部署条件；没有重新评测真实大模型的检索、长上下文或推理性能。

## 实际取得的资料

| 资料 | 阅读范围与固定版本 | 用于本轮的依据 |
| --- | --- | --- |
| [《动手学深度学习》15.1](https://d2l.ai/chapter_natural-language-processing-pretraining/word2vec.html) | 公开教材站点标示 1.0.3；阅读词嵌入章节，重点为 15.1.3；另读取 15.2 核对负采样背景 | skip-gram 从中心词预测上下文词，不能直接等同于现代句子检索模型 |
| [Raschka 作者学习指南](https://sebastianraschka.com/llms-from-scratch/)及[第 2 章 notebook](https://github.com/rasbt/LLMs-from-scratch/blob/22c637fdf9aa2f5fdd39c2cc80c1d36b4ab7d8d8/ch02/01_main-chapter-code/ch02.ipynb) | 提交 `22c637fdf9aa2f5fdd39c2cc80c1d36b4ab7d8d8`；重点阅读 2.7–2.8 的讲解和代码 | 输入 embedding 查表、模型训练中的嵌入参数与位置表示；取得的是公开配套内容，未取得商业书全文 |
| [Sentence Transformers 训练总览](https://github.com/huggingface/sentence-transformers/blob/3b17a2c948120350315245030f71d52f356d0c05/docs/sentence_transformer/training_overview.md) | 沿用提交 `3b17a2c948120350315245030f71d52f356d0c05`；复读模块结构与损失组合 | Transformer、Pooling 与检索训练目标的关系，批内负例和难负例的作用 |
| [Transformers RoPE](https://github.com/huggingface/transformers/blob/47b0e478f324b54f177ea7998a0791870fdd0324/src/transformers/modeling_rope_utils.py)及[Mixtral 实现](https://github.com/huggingface/transformers/blob/47b0e478f324b54f177ea7998a0791870fdd0324/src/transformers/models/mixtral/modeling_mixtral.py) | `v4.57.3` 对应提交 `47b0e478f324b54f177ea7998a0791870fdd0324`；tag 与 SHA 获取的文件逐字节一致 | 线性、动态 NTK、YaRN 的不同计算；YaRN 的注意力缩放；逐 token 专家选择与加权合并 |
| [PI](https://arxiv.org/abs/2306.15595)、[YaRN](https://arxiv.org/abs/2309.00071) | 重新读取论文摘要页，没有把摘要核对写成全文审读 | 论文报告的长上下文扩展包含训练前提；实现细节另由固定版本源码核对 |
| [Accelerate 大模型推理文档](https://huggingface.co/docs/accelerate/v1.11.0/en/concept_guides/big_model_inference) | 固定 `v1.11.0`；阅读设备映射、CPU/磁盘卸载过程与限制 | 完整权重存储量不等于单张 GPU 的常驻显存；卸载会引入搬运成本 |

Context7 用于找到当前 Transformers 的 RoPE 文档；当前字段与旧版配置不同，本轮不把滚动文档的接口写成 `v4.57.3` 的接口。GitHub 连接器返回 `Bad credentials`，随后从公开 GitHub API 与 raw 地址取得文件；没有修改连接器凭据。

Z-Library 使用英文书名与作者检索《Build a Large Language Model (From Scratch)》，返回 `EAPI search failed: Access denied`。只读域名探测显示当前域名可达，但检索仍未取得书目或正文。因此本轮没有“读过 Z-Library 书籍”的结论，也没有把猜测的版本、页码或引文写入书稿。教材依据来自上述实际读取的公开内容。

来源登记在 `yuyu-book/sources-llm.json`，两个新增 GitHub 仓库的完整提交同步登记在 `llm/facts/source-lock.json`。外部文件只保存在被忽略的 `.scratch/research-20261125/sources/` 供核对，没有把第三方正文、代码或插图加入版本管理。

## 书稿修改

- 第 2 章区分输入查表、上下文表示和检索向量；说明 skip-gram 的 36 条语料来自三个序列重复，12/12 分组结果只适用于该实验。删除“真实编码器只是扩大数据量”和“训练损失下降即可判断过训”的推断，收紧重排、批内负例、Matryoshka 与 ANN 的效果承诺。
- 第 4 章用公式说明 RoPE 的相对位置性质以内容向量固定为前提；按表格分开 PI、NTK-aware、YaRN 的计算和训练条件，撤下缺少直接依据的“位置截断无需重训”保证。
- 第 4 章统一参数和缓存预算：表中标准多头注意力有 32 个 KV 头，单条 128K fp16 缓存为 64 GiB；8 头 GQA 的 16 GiB 另作比较，不再拼接成同一模型配置。说明 Norm 示例的仿射参数取值、参数表省略项，以及 FLOPs 估算的适用范围。
- MoE 分开讨论完整权重、激活计算量、设备分片与卸载、实际延迟；不再要求所有专家必须常驻单卡，也不保证激活 6B 就有 6B 稠密模型的速度。
- RoPE 示例保留原二维结果，新增四维 base 对照与共同平移；修正“本卷不讲训练”的旧提示。第 16 章的 RoPE、YaRN、MoE 与路由术语同步更新。

## 验证

| 检查 | 结果 |
| --- | --- |
| LLM 示例测试 | 99 项通过；包含新增的两项 RoPE 数学性质回归检查 |
| `python scripts/bookctl.py check --fast` | Windows 下与 `make check` 使用同一检查入口；9 步通过，通用测试 447 项、构建器测试 629 项；479 份 Markdown、280 张 Mermaid 图均为 0 错误 |
| 十二卷合集装配 | `--check --mermaid source` 通过：12 卷、286 个单元、366 幅图版；没有据此声明 PDF 排版或 Mermaid 成品渲染通过 |
| LLM 独立 HTML | 完整渲染通过：17 个单元、31 幅图版、150 处引用链接 |
| 正文结构与数值 | 三章标题、稳定 block ID、插图引用均保留；独立重算 32/8 KV 头的缓存为 64/16 GiB，MHA 配置的权重加缓存约 76.6 GiB |
| 衍生资料 | 最后修改后重新生成，7 项输出重复生成一致，站内锚点通过 |
| 修订说明 | 追加本轮记录后，`test_docclaims.py` 的 9 项检查通过 |
| 浏览器抽查 | 第 2、4 章在 390/1440 像素、浅色/深色的 8 组检查中无整页横向溢出；新增缩放表在两个宽度下均完整容纳于容器；目视检查窄屏表格和宽屏 RoPE 公式 |

第一次截图显示三列缩放表在手机上需横向滚动，随后收紧为两列并把训练条件放到表后。该调整后重做独立 HTML、浏览器检查和衍生资料检查；全仓测试的程序逻辑未再变更。最后一轮文档格式检查与差异检查也通过。

日志和预览位于 `.scratch/research-20261125/`。本轮不重建 PDF、EPUB 或视频成片。原有未提交修改与计划保留，没有提交、推送或发布。
