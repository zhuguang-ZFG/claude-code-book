# LLM 卷：训练、微调与评测修订（2026-11-25）

接续同日两轮精修，本轮修改第 7、8、14 章，同步第 16 章术语、四个示例的说明或计算，以及示例说明与验证记录。主题是让教学结论与实际计算相符，删除缺乏依据的案例数字、效果保证和绝对判断。

后续 ARIS 审读发现并修复了 `train_demo.py` 的反向传播转置错误。本记录保留当时结果，不能作为当前训练实现正确性的依据；更新后的训练数值、回归检查和两轮审读见 [ARIS 修订记录](aris-20261125/PAPER_IMPROVEMENT_LOG.md)。

## 阅读的资料与范围

| 资料 | 固定版本或取得范围 | 本轮用途 |
| --- | --- | --- |
| Raschka《Build a Large Language Model (From Scratch)》[第 5 章](https://github.com/rasbt/LLMs-from-scratch/blob/22c637fdf9aa2f5fdd39c2cc80c1d36b4ab7d8d8/ch05/01_main-chapter-code/ch05.ipynb)、[第 6 章](https://github.com/rasbt/LLMs-from-scratch/blob/22c637fdf9aa2f5fdd39c2cc80c1d36b4ab7d8d8/ch06/01_main-chapter-code/ch06.ipynb) | 沿用提交 `22c637fdf9aa2f5fdd39c2cc80c1d36b4ab7d8d8`；阅读训练/验证损失与分类微调的公开 notebook 讲解和代码 | 区分训练窗口拟合与泛化；分类头、末 token 与主干冻结范围 |
| [TRL SFT 文档](https://github.com/huggingface/trl/blob/55f5433e15cc6203d3c731f9de5247b00878bebd/docs/source/sft_trainer.md) | `v0.25.0` 的注释 tag 继续解析到提交 `55f5433e15cc6203d3c731f9de5247b00878bebd`，另读 `sft_config.py` | assistant-only 与 completion-only 的不同含义、完整序列目标和模板前提 |
| [PEFT LoRA 文档](https://github.com/huggingface/peft/blob/53c25fe4fdd7c6aa4b40db0560815ea570d32303/docs/source/developer_guides/lora.md) | `v0.17.1`，提交 `53c25fe4fdd7c6aa4b40db0560815ea570d32303`；另读 `layer.py` | 初始化、合并与撤销、卸载适配器功能的区别 |
| Transformers [BERT](https://github.com/huggingface/transformers/blob/47b0e478f324b54f177ea7998a0791870fdd0324/src/transformers/models/bert/modeling_bert.py)与[分类公共实现](https://github.com/huggingface/transformers/blob/47b0e478f324b54f177ea7998a0791870fdd0324/src/transformers/modeling_layers.py) | 沿用 `v4.57.3` 提交 `47b0e478f324b54f177ea7998a0791870fdd0324`，另核 Llama 的继承关系 | 首 token pooler 与 decoder 最后非 padding token 的区别 |
| [NIST Wilson 手册](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)、[statsmodels McNemar 文档](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html) | 阅读比例区间公式、配对列联表、精确二项检验与原假设说明 | 修正“两个置信区间重叠便不能分胜负”的错误推断 |
| [DeepSpeed ZeRO 教程](https://www.deepspeed.ai/tutorials/zero/)、[PyTorch FSDP 2.15](https://docs.pytorch.org/docs/2.15/distributed.fsdp.fully_shard.html) | 前者读取当日教程；后者从 stable 跳转到明确版本，阅读收集参数与梯度归约说明 | 分开 ZeRO 三个阶段，说明分片节省显存也需要通信 |
| [Chinchilla](https://arxiv.org/abs/2203.15556)、[QLoRA](https://arxiv.org/abs/2305.14314) | 本轮复读论文摘要，未将其写成全文审读 | 收紧固定算力最优与量化训练的适用条件 |

另阅读《动手学深度学习》公开站点关于验证损失与早停的讲解，作为行文核对。Context7 用于发现当前 TRL 掩码文档，写入书稿的版本细节以固定提交为准。TRL 与 PEFT 的 tag/SHA 文档逐字节一致。来源登记与锁定表已同步，外部材料只保存在忽略目录，不复制到版本管理。

上一轮 Z-Library 检索返回 `Access denied`，本轮沿用实际可访问的公开教材与官方材料，没有取得或声称读过 Z-Library 全文，也没有新编书籍页码。

## 主要修改

- 训练章明确 `6ND` 的近似范围与 FLOP/s、MFU 的量纲，拆出 16 字节训练状态假设；“累计 token”与去重语料规模不再混用。梯度抽查不再写成证明所有反向公式正确，训练窗口 loss 不再当作泛化结论。
- 同 seed、初始化和抽样下复跑 240 步实验：当前学习率调度的固定训练窗口 loss 为 1.4921，恒定 `lr=0.6` 为 1.1211。保留原数值，撤下“长训练才兑现收益”的未经验证解释。修正验证记录把 435 个字符写成 435 字节的问题；实际 UTF-8 为 743 字节。
- 微调章去掉无出处的“八成合规、两千条轨迹”故事，改为明确假设的任务。说明损失掩码仅去掉某些目标位置的直接损失，prompt 仍参与回答计算和梯度路径；不再把全序列训练写成必然续写用户。
- 分类微调区分 BERT 的首 token 与 decoder 的有效末 token，并区分损失计算位置和可训练参数范围；删去无依据的样本量、成本倍数保证。LoRA 区分可撤销合并与卸载，补回缩放因子；QLoRA 区分存储位宽与计算精度。
- LoRA 示例改为独立计算未合并分支与合并权重，并在浮点容差内比较；此前的检查重复同一表达式。练习不再要求只改 `RANK` 就改变矩阵秩，明确需要同步形状。
- 评测章新增两组相同总准确率、不同逐题结果：不一致项 0/8 的精确 McNemar p 值为 0.0078，20/28 为 0.3123。定义检验条件与 p 值边界，同时澄清弃权分母、每道正确题成本、judge 冲突样本和后续章节导航。

## 验证记录

| 检查 | 结果 |
| --- | --- |
| LLM 示例 | 102 项通过，包含矩形 LoRA 合并一致性及两项配对检验 |
| 全仓 `check --fast` | 9 步通过；通用测试运行 450 项（1 项跳过），构建器测试 629 项通过；480 份 Markdown、280 张 Mermaid 图检查为 0 错误 |
| 合集装配 | `--check --mermaid source` 通过：12 卷、286 个单元、366 幅图版；未据此声明 PDF 排版通过 |
| 独立 HTML | LLM 卷完整渲染通过：17 个单元、31 幅图版、160 处引用链接 |
| 衍生资料 | 7 项输出重复生成一致，站内锚点通过 |
| 修订说明 | 追加本轮记录后，9 项文档声明检查通过 |
| 结构与排版 | 四章标题、block ID、插图引用保留；三章在 390/1440 像素、浅色/深色下共 12 组检查无整页横向溢出，配对比较表完整容纳于两种宽度；已目视检查窄屏评测表与宽屏损失掩码说明 |

日志、外部核对材料和预览位于 `.scratch/training-review-20261125/`。没有提交、推送、发布，也没有重建 PDF、EPUB 或视频成片。
