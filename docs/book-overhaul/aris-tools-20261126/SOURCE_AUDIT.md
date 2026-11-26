# 第三轮来源核对

阅读日期：2026-11-26。固定 GitHub 来源及用途见 `yuyu-book/sources-llm.json` 和 `llm/facts/source-lock.json`。不将书目搜索结果当作已阅读全文，不向书稿嵌入第三方图表或论文资产。

| 材料 | 实际读取范围 | 本轮用途 |
| --- | --- | --- |
| MCP 2026-07-28，提交 `5f5440bb26a62e2cf3440b92da5a667efa03b267` | versioning、discover、tools、stdio、schema.ts | 新旧协议边界、逐请求元数据、结果类型和错误分层 |
| Self-Consistency，arXiv:2203.11171 | PDF 方法节与答案 argmax 公式 | 多类别答案聚合不等于二元严格过半 |
| ViT，arXiv:2010.11929 | PDF §3.1、公式 1–4 | 位置嵌入、分类 token 和完整编码器 |
| LLaVA，arXiv:2304.08485 | PDF §4.2，两阶段训练；官方 README | 第一阶段与第二阶段更新参数不同 |
| BLIP-2，arXiv:2301.12597 | PDF §3，Q-Former 结构及 32 queries | 固定长度输出和冻结模块的训练路线 |
| Flamingo，arXiv:2204.14198 | PDF §2.1–2.2 | 64 个视觉输出、Perceiver Resampler、门控交叉注意力 |
| 《动手学深度学习》公开 ViT 章节 | Markdown 的模型说明、patch embedding 和 ViT 类 | 教材层次和完整实现对照，只作独立转述 |
| Claude Vision 官方文档 | Resolution and token cost、缩放与坐标说明 | 28×28 patch 规则；模型上限与教学面积计数分开 |
| Claude Structured outputs 官方文档 | 支持范围、SDK 转换、拒答与 max_tokens 处理 | 结构约束与业务正确性分开 |
| OpenAI Structured Outputs 官方文档 | JSON mode 对比及拒答、不完整响应处理 | JSON 语法与 schema adherence 分开 |
| Z-Library | 搜索返回 `Access denied`，未取得内容 | 未据此新增书籍内容或宣称阅读商业书全文 |

初次抓取部分网页失败；相同公开地址正常重试后取得 Claude 文档。MCP 的旧 lifecycle 路径在固定新版仓库不存在；改读该版本 versioning 原文，并据此纠正书稿。

本地来源原文保存在忽略目录 `.scratch/aris-tools-20261126/sources/`。以下哈希识别实际取到的快照，不代表第三方动态网页永远不变；论文只读方法部分，不声称复现其模型实验。

| 本地快照文件 | SHA-256 |
| --- | --- |
| `mcp-versioning.mdx` | `bc02f271700bdecd88034f2d7801eb09110a71d65876487378d94e48dfeb90dc` |
| `mcp-discover.mdx` | `3fe1f5b5f1528014216b1e49cc3363b3c689c36bcb80a6957ddca6a04cea409c` |
| `mcp-tools.mdx` | `ed550806a58eb7744b858fb9f26001aa5e55dac9e2babe88317cc81d9d4c490d` |
| `mcp-schema.ts` | `742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd` |
| `self-consistency.pdf` | `1a49ce0373afc89d2d6e97fb1aa8230f6b818c70590d732a3187f753f4df6aba` |
| `vit.pdf` | `8ce7b83971a14508ca711a27c875c9b6914c4f6767cf3150fb1ca6c07aa056d6` |
| `llava.pdf` | `dc8bace378a282ea78caa9b5959306202fbfa3b8cedaf8a66541a9af18f4d3bf` |
| `blip2.pdf` | `6bc5d399d6127a64ace5167a2f0c00112a49725d2475d80322dbf0083f139e80` |
| `flamingo.pdf` | `27af622bf50987fd98a03451a27a670adfaeefd5218a3e990b37abc326ba63f0` |
| `d2l-vit.md` | `290574b82b91f9efca4f90bb56d29a76db2de85666db5d1e38850cdf32709e07` |
| `llava-readme.md` | `bf7fbd57f27198308d9ed8fb2813267a9d18cf79198c5ac534fba1ad757a287b` |
| `claude-vision.html` | `d57c2715012d85331268255c14c42438660dba02aa0a804dbbab66eec84eef7e` |
| `structured-outputs-retry.html` | `5bde157f1de6bdc9e483afc4977b3c2fa87121c846af53bccbc8a1f7b1e4307b` |
| `openai-structured-outputs.html` | `9afbd3b421f8487015389bb6de3701c0ef77ba4f9057595284d1a75c2ef3a6d3` |
