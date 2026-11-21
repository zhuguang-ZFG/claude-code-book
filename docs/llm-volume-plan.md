# LLM 卷规划：写给 Agent 工程师的大模型原理与实战

日期：2026-11-20。状态：0.1.0 中文版已完稿（第 1–16 章），英文版与真实实验待后续。

## 为什么写、为什么不复刻现有赛道

GitHub 中文/英文 LLM 教学仓格局（星数为 2026-11 实测）：

| 仓库 | 星数 | 定位 |
|---|---|---|
| rasbt/LLMs-from-scratch | 108,701 | 英文 PyTorch 从零实现 ChatGPT |
| datawhalechina/happy-llm | 35,020 | 中文从零构建大模型（notebook 教程） |
| datawhalechina/self-llm | 32,830 | 中文部署微调实操指南 |
| datawhalechina/llm-cookbook | 24,918 | 吴恩达系列课程中文版 |
| ZJU-LLMs/Foundations-of-LLMs | 18,630 | 浙大理论教材 |
| datawhalechina/llm-universe | 14,323 | 大模型应用开发 |
| datawhalechina/so-large-lm | 7,790 | 大模型基础概念综述 |
| LLMBook-zh（中国人民大学） | 4,634 | 《大语言模型》（赵鑫、李军毅、周昆、唐天一、文继荣） |
| datawhalechina/llms-from-scratch-cn | 4,468 | Raschka 中文版 |
| datawhalechina/diy-llm | 3,024 | CS336 风格全栈作业 |

「从零造一个模型」已经饱和，那条路线回答的是"怎么训出一个模型"。本卷回答另一个问题：agent 工程师每天碰到的现象——token 为什么按量计费、temperature 为什么让同样的 prompt 跑出不同结果、KV cache 为什么决定吞吐、上下文窗口为什么越用越贵、RAG 和 agent 记忆怎么分工——底层机制到底是什么。每章一个概念簇 + 一段 CPU 可跑的最小实现（30–100 行）+ 一个明确的 agent 工程落点。全书代码无需 GPU，用随机初始化的 nano 尺寸模型演示机制，不以复现 SOTA 为目标。

## 读者基线

会写 prompt、会调 API、读过本书系列其他卷；没读过 attention 推导，不假设会 PyTorch（每章代码优先用 Python 标准库，必要时才用 numpy/torch 的最小子集，第一次出现处带三行注释）。

## 章节骨架（16 章）

1. **token 与分词**：UTF-8 字节、BPE 手写 30 行、词表与特殊 token；为什么上下文窗口按 token 计费。
2. **词嵌入与语义空间**：embedding 查表、余弦相似度、语义检索 mini 实现。
3. **注意力**：single-head 手写 → multi-head；KV cache 为什么存在。
4. **Transformer 整体**：block 堆叠、残差流、LayerNorm/RoPE；`n_layers × d_model` 怎么读模型卡。
5. **生成即采样**：temperature / top-p / top-k、seed 与确定性；agent 为什么需要低温度。
6. **上下文窗口的代价**：O(n²) 注意力、长上下文的真实成本；与卷一第 7 章上下文管理互引。
7. **预训练与 scaling law**：训练一个 nano-GPT（Karpathy 风格）；算力、数据配比、chinchilla 直觉。
8. **后训练 I——SFT**：指令微调是什么、LoRA 手写注入；「微调 vs prompt」的决策表。
9. **后训练 II——对齐**：reward model、RLHF/DPO 的机制直觉；模型为什么「听话」。
10. **推理与部署**：KV cache 复用、量化、continuous batching 的直觉；吞吐与延迟的取舍。
11. **RAG**：切块、向量库、重排；RAG 与 agent 记忆的关系（互引卷一）。
12. **工具调用与 MCP**：function calling 的 token 协议本质、MCP 架构；互引本书 MCP 卷。
13. **思维链与推理模型**：CoT、test-time compute、o1 式 RL 推理；agent 的 plan-then-execute。
14. **幻觉、评测与蒸馏**：为什么胡说、怎么量化、小模型怎么继承大模型。
15. **多模态**：图像怎样变成 token（patch、投影、ViT）、图文对齐（对比与交错预训练）、图像 token 预算与档位；截图调试、UI 定位、文档抽取的工程落点。
16. **名词速查总表**：全书 80+ 术语一页对照，每条带章节锚点与社区出处。

每章结构沿用系列惯例：`常见翻车 / 正确做法` 对照表 + `本章小实验` + 交叉参考框。

## 证据纪律

- 每个技术断言钉版本：rasbt/LLMs-from-scratch、datawhalechina/happy-llm、karpathy/nanoGPT、MCP 规范等一律 full SHA 或 tag，进 `yuyu-book/sources-llm.json`。
- 不嵌入第三方资产；代码示例自写或 MIT 许可并注明。
- 中英同步：`llm/`（zh）与 `en/llm/` 同步成稿，遵守 H1 格式、全角标点、中西文空格等仓库规范。0.1.0 中文版先出中文，英文版待后续同步，不把未翻译的章节挂进 manifest。

## 流水线复用与注册顺序

1. 章节源文件落 `llm/` 与 `en/llm/`。
2. 新增 `yuyu-book/manifest-llm.json`（中文版按篇分组、无附录、`plain_optional`），`sources-llm.json` 同前缀；`notes-llm.json` / `glosses-llm.json` 等通俗层文件留空，不登记未启用层。
3. `scripts/bookctl.py` 的 `AGENT_PRODUCTS`、Makefile 与 CI 的 `agent-volumes` 矩阵纳入 `llm`；门户与合订本暂不收录该分册，等英文版与合订决策再议。
4. `make check` 全绿后出第一册 HTML；合订本收录决策另议。

## 写作顺序

第 1、5、6 章先行（agent 工程师最高频痛点：token、采样、上下文），第 3、4 章已补注意力与 Transformer，第 2 章已补 embedding，第 8、9 章已补 SFT/LoRA 与对齐，第 7 章已补预训练算力账，第 10 章已补推理与部署，第 11 章已补 RAG，第 12 章已补工具调用与 MCP，第 13 章已补思维链与测试时计算，第 14 章已补评测与蒸馏，第 15 章已补多模态，第 16 章总表收官。十六章均已落地。

## 落地状态（2026-11-21）

- 已建 `llm/`：前言、第 1–16 章、`README.md`、`VERIFY.md` 与 `examples/` 十五个纯标准库脚本。
- 已注册独立产品 `llm`：`yuyu-book/manifest-llm.json`、`sources-llm.json`、`registry.py` 白名单、`scripts/bookctl.py` 的 `AGENT_PRODUCTS`、Makefile 的 `book-llm*`、CI 矩阵与 EPUB 流程。
- 产物前缀 `yuyu-llm`，当前只有中文版（`langs: ["zh"]`），不启用通俗层（`plain_optional: true`）；现已编入合订本卷二，并进入发布脚本的 `COMPANION_VOLUMES`。
- 实测：HTML 597 109 字节，PDF 123 页 / 7.1 MB（本机微软雅黑），EPUB 223 948 字节；构建器测试 628 项、仓库测试 413 项全部通过。详见 `llm/VERIFY.md`。
- 插图：`illustrations-agents/` 下 17 枚章徽、10 幅篇题、31 张正文手绘图与 1 张独立封面，全部通过墨线 SVG 硬契约。
- 知识点补全（2026-11-21 第二轮）：MoE 专家与路由机制（第 4 章）、长上下文扩展三法 PI/NTK/YaRN（第 4 章）、MLA 潜在注意力（第 3 章）、投机解码的命中条件与模型路由/级联（第 10 章）、约束解码（第 12 章）、LLM-as-judge 及位置与自偏好偏差（第 14 章）、视觉提示注入与视频帧预算（第 15 章）；术语表同步新增 13 条，七篇引用进 `sources-llm.json`。有意不收：音频模态（按范围决策只做图像）、扩散生成模型（非 Agent 输入通道）、分布式多机训练（超出单机教学定位）。
- 未做：英文版 `en/llm/`；真实 tokenizer 跨模型计数、真实预训练/微调/对齐实验、长上下文质量实验、GPU 吞吐压测、真实多模态模型识读、真实 LLM-as-judge 偏差实测。正文中未把未测内容写成结论。
