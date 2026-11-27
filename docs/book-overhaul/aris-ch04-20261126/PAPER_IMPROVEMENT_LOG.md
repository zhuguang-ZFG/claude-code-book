# 第六轮：第 4 章架构深修与全书版式、全套 LLM 绘图美化

日期：2026-11-26。范围为 LLM 第 4、16 章、前言、第 4 章示例、全库印刷/屏幕样式、`yuyu-book/illustrations-agents/` 下全部 59 个 LLM 矢量图，以及对应参考来源与测试。按本地 ARIS 书稿适配流程执行两次新上下文审读，均为 `same-family / provisional`；原生子代理工具只返回任务标识，报告不冒充模型外部签名身份，没有外部写作服务或自动通知动作。

## 来源与一手核对

- **论文原文快照**：[LayerNorm `1607.06450`](https://arxiv.org/abs/1607.06450)、[RMSNorm `1910.07467`](https://arxiv.org/abs/1910.07467)、[Pre-LN `2002.04745`](https://arxiv.org/abs/2002.04745)、[GLU Variants `2002.05202`](https://arxiv.org/abs/2002.05202)、[RoPE `2104.09864`](https://arxiv.org/abs/2104.09864)、[PI `2306.15595`](https://arxiv.org/abs/2306.15595)、[YaRN `2309.00071`](https://arxiv.org/abs/2309.00071)、[RoPE Extrapolation `2310.05209`](https://arxiv.org/abs/2310.05209) 与 [Sparse MoE `1701.06538`](https://arxiv.org/abs/1701.06538)。
- **固定提交源码**：Hugging Face Transformers 固定提交 `47b0e478f324b54f177ea7998a0791870fdd0324`（`modeling_llama.py`、`configuration_llama.py`、`modeling_qwen2.py`、`modeling_rope_utils.py`、`modeling_mixtral.py`）、nanoGPT 固定提交 `3adf61e154c3fe3fca428ad6bc3818b27a3b8291`（`model.py`）与 LLMs-from-scratch 固定提交 `22c637fdf9aa2f5fdd39c2cc80c1d36b4ab7d8d8`（`ch04.ipynb`、`gpt.py`）。
- **PyTorch CPU 独立复核（`2.14.1+cpu`，`float64`）**：`rms_norm` 与 PyTorch 原生差 `2.22e-16`、`layer_norm` 差 `4.44e-16`、含 GQA + QKV 偏置 + RoPE + SwiGLU 的 `forward_block` 差 `1.78e-15`、Mixtral 路由顺序的 `sparse_moe_forward` 差 `0.0`。仅校验数学与路由顺序，不作性能基准或新增运行依赖。

## 第一次审读与第一轮修订

- 冻结输入：`.scratch/aris-ch04-20261126/round0/`（166 页）。审读报告：[review1.md](review1.md)（7/10、Almost，0 项 Critical、5 项 Major、3 项 Minor）。
- 核心修复：重绘 `llm-ch04-transformer-block.svg` 为 Pre-LN 两次串行残差加法并配简洁节点标签；重绘 `llm-ch04-rope-rotation.svg` 并把插图位置上移至 §4.4 旋转讲解旁，消除 p.43 大片留白。
- 正文与代码补齐：`llm/ch04.md` 点明末尾 `Final Norm`、区分 §4.4 每头 `d_rot` 与 `d_model`、补充 HF `rotate_half` 配对兼容、定义 `Swish = SiLU` 并过渡 `GELU`、注明 `d_ff=11008` 来自硬件 256 倍数对齐、接入 Llama/Qwen2/RMSNorm/nanoGPT/LLMs-from-scratch 一手来源并更新 `llm/ch16.md`、`yuyu-book/sources-llm.json` 与 `llm/facts/source-lock.json`；`llm/examples/transformer_demo.py` 新增真实多 token `forward_block()`、`forward_model()`、`sparse_moe_forward()`、`rotate_half_rope()` 与 GQA/MoE 参数统计，`tests/test_llm_examples.py` 与 `yuyu-book/tests/test_llm_product.py` 扩展单测。

## 第二次审读与第二轮修订

- 冻结输入：`.scratch/aris-ch04-20261126/round1/`（168 页）。审读报告：[review2.md](review2.md)（7/10、Almost，0 项 Critical、2 项 Major、7 项 Minor）。
- 解决两项 Major：`yuyu-book/yuyu_book/style_print.py` 将 `.chapter-notes` 改为允许条目间跨页而保留标题绑定与单条完整，消除第 4 章 PDF 尾页 61.6% 半页空白，同时改用 `overflow-wrap: anywhere` 改善长 GitHub URL 断词；缩小并重排图 4-2 内角标弧，`φ` 与 `φ'` 完全脱离向量线段与虚线圆。
- 修齐七项 Minor：精简表 4.5 / 4.7 避免单汉字孤立折行；修正 §4.5 MoE 加噪声门控语序；统一 §4.4 与 §16 NTK-aware 公式内的 `d_rot` 记号；补充 RMSNorm Eq.(4) 与实现 `+ eps` 对照；在 `transformer_demo.py` 中修复 MoE `mlp_bias=True` 多专家计数、补齐 `w_v` 与列宽校验及 `params()` 非物理参数校验；消除图注中的 `Ro<wbr/>PE` 断点并更新 `llm/ch04.md` 关键字布尔调用、`llm/VERIFY.md` 实测摘要。

## 全书版式美化、EPUB 多墨水修复与 59 幅 LLM 矢量图系统升级

- 在严格保留 `yuyu-book/yuyu_book/style_tokens.py` 调色盘十六进制常量的前提下，升级 `style_components.py`、`style_screen.py`、`style_print.py`、`render.py` 并通过 `bookctl.py build --product site` 同步 `docs/`（包括 `sample-chapter.html`、`illustration-gallery.html`、`search-index.json` 等）；增强 `.table-scroll` 与代码块阴影/圆角节奏，并收紧表 4.5 第 3 行消除最后一处单字折行（`影`）。
- 升级 `scripts/build_epub.py`：SVG 光栅化前注入 `--ink` / `--cinnabar` / `--jade` / `--sky` 与 `.illu-frame svg .il-*` 样式、补充暗色模式读图框/底衬修复，并新增 `tests/test_epub_paint.py`（含 `il-cinnabar` / `il-jade` / `il-sky` 光栅化精确 RGB 断言，2 项全过）。
- 重绘 `yuyu-book/illustrations-agents/` 下全套 **59** 个 `*llm*.svg`（1 枚封面 `cover-llm.svg`、10 幅篇题 `part-llm-p1..p10.svg`、17 枚章徽 `llm-front` / `llm-ch01..16.svg`、31 张彩色正文图解），全部遵守 `currentColor`、`role="img"`、`<title>`/`<desc>` 及无外部依赖硬契约，结构类图标保持零汉字；正文图同步植入 `pathLength="100"` 滚动绘线动画锚点，图 4-1 微调版面尺寸后成功回落第 41 页（`p.41` `y=80.8..771.3`，消除原 `298 pt` 空隙）。
- 视觉与排版核验范围说明：文件读取工具仅能识别二进制文件类型而不直接解析 PNG 位图内容，因此本轮视觉排查基于 Playwright（桌面 `1440px` 亮/暗、手机 `390px` 亮/暗、打印态五模式）实测 DOM 包围盒与路径采样、`PyMuPDF` 矢量/文本坐标解析以及 `Pillow` PNG 像素统计。全套 31 张正文图实现 **0** 文本溢出、**0** 文本碰撞、**0** 边框侵入（`rect_crossings`）、**0** 前景曲线交叉（`path_crossings`）、**0** 手机端过小字体（最小 `10.02 px`）；PDF（174 页、第 4 章 41–49 页）**0** 越界页；EPUB（34 文档、170 导航、59 张 PNG）**59/59** 全部通过多墨水着色像素校验（`cinnabar` 466 137 像素、`jade` 221 739 像素、`sky` 401 210 像素）。

## 最终验证指标

最终未再发起第三次审读；两轮既有独立审读（`review1.md` / `review2.md`）提出的所有问题及全书 59 幅插图与 EPUB 管线收尾修正均已在 `round2` 与闭环自检中核销。完整命令、测试计数与产物校验哈希见 [final-validation.json](final-validation.json) 与 [artifact-snapshots.json](artifact-snapshots.json)。最终构建输出落在忽略目录 `.scratch/aris-ch04-20261126/round2/`，没有手动编辑 `yuyu-book/dist/` 或 `.cache/`，所有章节 ID、block 锚点与插图引用保持完整。
