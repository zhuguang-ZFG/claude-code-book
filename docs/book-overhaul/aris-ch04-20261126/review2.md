# 第 4 章《一层一层读懂模型卡》独立同行审稿报告（Round 1）

- **评审对象**：`round1/source/ch04.md`（配套 `round1/source/transformer_demo.py`、`round1/source/ch16.md`、两幅 SVG 插图，以及编译产物 `round1/yuyu-llm-zh.html`、`round1/yuyu-llm-zh.pdf` 第 40–48 页）
- **审稿身份**：独立上下文资深技术图书编辑（只读审计；未查阅任何既有审稿记录与变更日志）
- **总评分数**：**7 / 10**（注：按 `6 = Weak Accept`、`7 = Accept`、`8 = Strong Accept`、`9+ = Outstanding` 标尺，本章正文、数学与代码质量达 `8+` 水准，受制于 PDF 第 47 页大片留白、图 4-2 `φ`/`φ'` 标注碰撞及少量表格与代码边界瑕疵，综合评定为 `7 / 10`）
- **出版结论（Verdict）**：**Almost**（修复两项 `MAJOR` 视觉/分页缺陷及主要 `MINOR` 细节后可 `Ready`）

---

## 1. 评审摘要

第 4 章以“拆解 7B 模型卡参数、架构变体与显存账”为工程主线，将 Pre-LN 残差流、RMSNorm/LayerNorm、SwiGLU、RoPE（含长上下文扩展与布局兼容）及稀疏 MoE 串联为一套可手算、可复现的核对框架；正文全部数值均与纯标准库脚本 `round1/source/transformer_demo.py` 严格咬合，并在 PyTorch CPU 等价对照（`0.0` 到 `4.44e-16` 精度）与 144 项自动化测试中全部通过。技术论证校准得当，既无夸大外推，也未强求教学脚本承担生产特性。但编译版 PDF 仍存在两处直接影响成书观感的 `MAJOR` 问题——第 47 页因 `.chapter-notes` 整块禁断分页而留下 `61.6%` 空白，以及图 4-2（`round1/source/llm-ch04-rope-rotation.svg`）中角度标签 `φ'` 与 `φ` 分别直接穿过向量线段与虚线圆，需先修复后再定稿。

---

## 2. 审稿范围、核验方法与局限声明

### 2.1 核验范围与运行环境

- **冻结输入文件**：`round1/source/ch04.md`、`round1/source/ch16.md`、`round1/source/transformer_demo.py`、`round1/source/test_llm_examples.py`、`round1/source/test_llm_product.py`、`round1/source/llm-ch04-transformer-block.svg`、`round1/source/llm-ch04-rope-rotation.svg`、`round1/source/sources-llm.json`、`round1/source/source-lock.json`、`round1/source/manifest-llm.json`、`round1/source/llm-volume-plan.md`、`round1/source/README.md`、`round1/source/VERIFY.md`、`round1/source/style_print.py`。
- **编译与检查产物**：`round1/yuyu-llm-zh.html`、`round1/yuyu-llm-zh.pdf`（全书 `168` 页，第 4 章占第 `40–48` 页）、`visual-round1/report.json`。
- **固定参考快照**：`sources/` 目录下所钉原始论文文本与代码实现，包括 `rmsnorm-1910.07467.txt`、`preln-2002.04745.txt`、`swiglu-2002.05202.txt`、`rope-2104.09864.txt`、`pi-2306.15595.txt`、`yarn-2309.00071.txt`、`rope-extrap-2310.05209.txt`、`moe-1701.06538.txt`、`hf-llama.py`、`hf-llama-config.py`、`hf-qwen2.py`、`hf-rope-pinned.py`、`hf-mixtral-pinned.py`、`nanogpt-model.py`、`raschka-gpt.py`、`raschka-ch04-ipynb.txt`。
- **实际运行工具链**：Python `3.13.14`、PyTorch `2.14.1+cpu`、PyMuPDF `1.28.0`、BeautifulSoup4。

### 2.2 已执行的只读验证

1. **仓库既有单测**：在只读状态下运行 `python -B -m unittest tests.test_llm_examples yuyu-book.tests.test_llm_product`，全部 `144` 项测试通过（含 `TransformerExample` 12 项与全书构建/SVG 几何契约 8 项，`31.691s OK`）。
2. **代码与正文内嵌片段实跑**：直接运行冻结版 `round1/source/transformer_demo.py`（核对全部 35 条非空打印行）及 `round1/source/ch04.md:80-85` 的 Python 代码块（通过内存模块映射，未写磁盘）。
3. **PyTorch CPU 逐项等价对照**：将 `transformer_demo.py` 的 `rms_norm`、`layer_norm`、`silu`、`gelu`、`rotate_half_rope`、`forward_block`（含 GQA 4/2 + QKV bias + RoPE + SwiGLU）及 `sparse_moe_forward` 与 PyTorch 原生实现及钉住版本的 `LlamaRMSNorm`、`rotate_half`、`apply_rotary_pos_emb`、`MixtralSparseMoeBlock` 对比，最大数值误差为 `0.0` 至 `4.44e-16`（`float64`）；`RMSNorm(float32_stats=True)` 与 `hf-llama.py` `LlamaRMSNorm` 在 `float32` 下最大误差为 `0.0`。
4. **PDF 与 SVG 几何定量审计**：利用 PyMuPDF 提取 `yuyu-llm-zh.pdf` 第 `40–48` 页全部文本行、Span 渲染字号、矢量绘图路径包围盒，并通过线段/圆弧采样计算图 4-1 与图 4-2 标签到相邻矢量元素、端点圆点及外框的精确最小距离；利用 HTML 解析检查 `#llm-ch04` DOM 与打印/屏幕 CSS 规则。

### 2.3 诚实局限声明

- **视觉位图感知局限**：当前文件读取工具无法直接解析光栅 PNG 像素内容（读取 `pages/page-040.png`–`page-048.png` 及 `visual-round1/*.png` 仅返回二进制文件类型提示）。因此本文对页面留白、表格断行、SVG 碰撞的判断均严格基于**PyMuPDF 从 PDF 抽取的实际矢量路径/文本包围盒坐标**、HTML/CSS 源码分析以及 `visual-round1/report.json` 记录，未作未观测到的栅格像素渲染主观推断（如字体抗锯齿微瑕或暗黑模式网页人眼对比度观感）。
- **模型身份不可自证**：本会话无法独立核验底层推理模型运行时标识符。

---

## 3. 突出优点（按重要程度排序）

1. **数学推导、代码实现与模型卡/源码高度自洽**
   `round1/source/ch04.md` 给出的每一组数字（`6 738 411 520`、`6 738 415 616`、`5 933 109 248`、`46 702 792 704`、`12 879 925 248`、`12.55 GiB`、`64.00 GiB`、`76.55 GiB`、`16.00 GiB`、`d_extra = 92` 等）均可由 `round1/source/transformer_demo.py` 及标准公式精确复现；不仅在 `forward_block`（`ch04.md:185`）给出纯标准库多 token 前向实现，还在 `ch04.md:49,75,118,120,142` 精确捕捉到工程实践中极易忽略的细节——如 RMSNorm 半精度下内部 `float32` 求平方均值、Qwen2 的 `q/k/v` bias、RoFormer 相邻配对 `(2i, 2i+1)` 与 HuggingFace `rotate_half` `(i, i+d_rot/2)` 的布局等价性及混用陷阱、以及 Mixtral 先 `softmax` 后 `topk` 再归一化与早期 Shazeer MoE 路由差异。
2. **双向校准克制准确，彻底避开常见教学误区**
   作者多处主动收窄边界而非空泛免责：`ch04.md:4` 与 `140` 清晰区分十进制 `GB` 与二进制 `GiB`；`ch04.md:49` 指出可学习 `gamma`/`beta` 存在时输出不必保持单位方差或零均值；`ch04.md:103` 明确说明“只有 `q = k` 时点积才仅依赖 `|m - n|`，不可把注意力分数简化为只由距离决定”；`ch04.md:118` 强调 `θ_i` 决定不同转速但“不能把某几对坐标固定指派给某种语义角色”；`ch04.md:130` 严正区分“预训练长度、扩展配置上限与实测有效长度”；`ch04.md:138` 厘清输入侧 `embed_tokens` 是离散查表（不计 `2×` 乘加 FLOPs）而输出侧 `lm_head` 即使 `tied` 仍执行矩阵乘；`ch04.md:144` 说明 MoE 的 `active` 参数不保证等价稠密模型延迟。
3. **教学代码边界清晰、测试契约扎实**
   `round1/source/transformer_demo.py` 严格限定在 572 行纯标准库内，自包含实现了完整多 token Pre-LN Block（含因果遮罩、GQA、RoPE、SwiGLU）、`params()` 参数分解与 `sparse_moe_forward()`，同时将完整反向传播/训练留给第 7 章（`ch04.md:6,190`），既无多余生产框架包袱，又通过 `round1/source/test_llm_examples.py` 12 项与 `test_llm_product.py` 8 项单测锁死核心不变量。
4. **参考文献可追溯性强，图 4-1 结构清晰无碰撞**
   正文 `19` 处外链对应 `17` 个独立 URL，全部论文使用 arXiv 永久标识，全部 GitHub 代码（`transformers`、`nanoGPT`、`LLMs-from-scratch`）钉死至 40 位完整 commit SHA，官方文档钉死版本（`accelerate v1.11.0`）。图 4-1（`round1/source/llm-ch04-transformer-block.svg`，`3 300 B`）经 PDF 第 40 页实测，所有方框标签内外留白充足，无任何文字与线条遮挡，且严格遵循单色 `currentColor` 与无障碍 `<title>`/`<desc>` 规范。

---

## 4. 缺陷与修改建议（`CRITICAL` > `MAJOR` > `MINOR`）

本章未发现 `CRITICAL` 级事实错误或数学错误；以下列出全部 `2` 项 `MAJOR` 缺陷与 `7` 项 `MINOR` 缺陷。

### [MAJOR-1] PDF 第 47 页下部留白高达 61.6%（`518.9 / 841.9 pt`），尾部整页近乎空半张

- **证据**：
  - `visual-round1/report.json:91-112` 与 PyMuPDF 第 47–48 页实测：第 47 页（第 4 章正文结束页）最后一行文字落于 `y = 323.0 pt`（`算，读第 6 章。`），距页底仍有 **`518.9 pt`**（占 A4 页高 `841.9 pt` 的 **`61.6%`**，按前几页约 `y = 763–775 pt` 的版心高度推算，下方尚余约 `440–452 pt` 可用栏高）。
  - 第 48 页承载整块 `.chapter-notes`（`引用链接` 17 条，总高 `523.3 pt`，范围 `y = 70.7..594.0 pt`）。
  - 根因在 `round1/source/style_print.py:194-196`：全局打印样式设置了 `.chapter-notes{break-inside:avoid}`。由于第 4 章引用多达 17 条且多条包含完整 40 位 SHA 长 URL，整块高度 `523.3 pt` 超过第 47 页剩余栏高 `~450 pt`，导致 Chromium 将整个 `.chapter-notes` 推入第 48 页，第 47 页下半页全部留空。
- **影响**：成书排版观感明显割裂，读者翻至第 47 页骤见大段空白后紧接整页尾注，违背该文件注释本身欲消除“印刷失误感”的初衷。
- **可落地修复**：
  修改 `round1/source/style_print.py:194-196`，允许 `.chapter-notes` 在列表项之间自然跨页分页，同时禁止“引用链接”标题与首条分离、禁止单条 `<li>` 内部被截断：
  ```css
  .chapter-notes { break-inside: auto; }
  .chapter-notes .notes-title { break-after: avoid; }
  .notes-list li { break-inside: avoid; orphans: 2; widows: 2; }
  ```
  按此规则，第 47 页下半页（`y ≈ 340..765 pt`）可自然容纳前约 `12–13` 条引用，仅余 `4–5` 条与章末收尾自然顺延至第 48 页，既消除单条截断，又彻底填平 `61.6%` 空洞（修改后需重跑全书空白页闸门与相邻章分页回归检查）。

### [MAJOR-2] 图 4-2（RoPE 示意图）角度符号 `φ'` 与 `φ` 分别压线穿过向量线段及虚线圆

- **证据**：
  - 源文件：`round1/source/llm-ch04-rope-rotation.svg:1`（`viewBox="0 0 420 342"`，`4 347 B`）及打印放大规则 `round1/source/style_print.py:212`（`.illu-frame svg text{font-size:14px}`）。
  - PDF 第 43 页 PyMuPDF 矢量与 Span 坐标实测（左圆圆心 PDF `(226.45, 497.75)`、右圆圆心 `(368.55, 497.75)`、半径 `35.25 pt`，缩放比 `S = 35.25/52 ≈ 0.6779`）：
    1. **右侧 `φ'` 直接与实线 `q'`（及同向虚线 `k`）相交**：SVG 中 `<text x="331" y="102">φ'</text>` 在 PDF 第 43 页渲染包围盒为 `[373.8, 466.4, 383.3, 478.8]`（映射回 SVG 坐标约 `[323.7, 337.7] × [87.7, 106.0]`），而旋转后矢量 `q'` 线段从 `(316, 134)` 连向 `(345.8, 91.4)`（PDF `(368.5, 497.8) -> (388.5, 469.25)`）。该线段在 `y = 478.8` 处横坐标为 `381.8`、进入字形右下角区，**几何最小距离 `d = 0.00`**；同时该文字框距离 `r = 52` 右侧虚线圆仅 `0.74 SVG px`（`~0.5 pt`）。
    2. **左侧 `φ` 直接横跨左侧虚线圆**：SVG 中 `<text x="146" y="112">φ</text>` 在 PDF 第 43 页包围盒为 `[251.0, 473.1, 258.2, 485.5]`（SVG 坐标 `[140.2, 150.8] × [97.6, 115.9]`），其中心距左圆心 `(226.45, 497.75)` 仅 `33.73 pt`，而框角径向跨 `29.4–37.9 pt`，**直接骑跨在 `r = 35.25 pt`（SVG `r = 52`）的虚线圆周上（`d = 0.00`）**。
  - 既有单测 `round1/source/test_llm_product.py:92-112` 仅校验两对向量旋转角度与 `q`/`k` 标记数量，未校验 `<text>` 与矢量路径/圆弧的碰撞，故测试通过而未检出。
- **影响**：图 4-2 是全章最核心的几何直觉图，字母 `φ'` 被线段斜劈、`φ` 压在虚线圆上会直接影响印刷可读性。
- **可落地修复（两种已验证方案，不改变向量角度、不触发 `test_llm_product.py` 几何断言失败）**：
  - **方案 A（推荐：收缩内角标弧至 `r = 18` 并将符号留于扇区内清晰无碰区）**：
    将内角弧线从 `r = 26` 收至 `r = 18`：
    - 左弧 `M121.7 130.9A18 18 0 0 0 114.3 119.3`；左 `φ` 移至 `x="136" y="118"`。按 PDF `14px` 最坏字框实测，距 `q` 线段 `5.45 SVG px`、距 `k` 线段 `4.46 SVG px`、距外虚线圆 `3.88 SVG px`、距内弧 `r=18` `> 11 SVG px`。
    - 右弧 `M326.3 119.3A18 18 0 0 0 312.9 116.3`；右 `φ'` 移至 `x="323" y="103"`。实测距 `q'` 线段 `4.00 SVG px`、距 `k'` 线段 `4.67 SVG px`、距外虚线圆 `4.59 SVG px`、距内弧 `r=18` `9.00 SVG px`。
    - 可选叠加：在 `round1/source/style_print.py:212` 后补充 `.illu-frame svg text.il-sub{font-size:12px}` 并将角符号标注设为 `class="il-sub"`，可在印刷端再多出约 `2 SVG px` 余量。
  - **方案 B（更大留白：移出圆外扇区中线，仅当允许符号标于圆周外时选用）**：
    维持 `r = 26` 弧不变，将 `φ` 置于 `x="158" y="97"`（距所有线段、端点圆点及外圆均 `≥ 6.88 SVG px`），`φ'` 置于 `x="331" y="71"`（距所有线段、端点圆点及外圆均 `≥ 7.54 SVG px`，距上方副标题 `dy = 23 px`）。若选方案 A 则可保留角符号位于夹角扇区内部的直觉对应关系。

---

### [MINOR-1] PDF 表 4.5（第 45 页）与表 4.7（第 46 页）存在多处单汉字孤立折行（orphan wrap）

- **证据**：PyMuPDF 逐行抽取 `round1/yuyu-llm-zh.pdf` 第 45、46 页表格单元结果：
  1. **第 45 页表 4.5（对应 `ch04.md:150,153`）**：
     - 第 3 行第 2 列（`x = 193.6..340.6`）：`注意力并行度、KV cache 与 K/V 投影` 后单独折出孤立单字 **`量`**（`y = 628.4`）。
     - 第 6 行第 1 列：`上下文长度 /` 后折出 `rope_theta`（此处在 `/` 处断行尚可接受，但列宽明显受压）。
  2. **第 46 页表 4.7（对应 `ch04.md:172-173`）**：
     - 第 5 行第 3 列（`x = 324.2..512.3`）：`核对 tie_word_embeddings 、bias 与末尾` 后孤立折出英文词 **`Norm`**（`y = 500.0`）。
     - 第 6 行第 1 列（`x = 59.5..171.8`）：`调大 RoPE 范围就当作质量保` 后单独折出孤立单字 **`证`**（`y = 541.4`）。
     - 第 6 行第 2 列（`x = 200.7..295.3`）：`长输入能运行，却可能答` 后单独折出孤立单字 **`错`**（`y = 541.4`）。
     注意同表第 3 列（`核对预训练长度、缩放方案与长输入评测`）与第 5 行 `tie_word_embeddings` 拉宽了第 3 列，导致前两列各仅剩约 `112 pt` 与 `95 pt`，把末尾一个汉字挤到下一行。
- **修复建议**：
  可通过两处轻量调整同时消除以上孤字折行：
  1. 精简原文单格冗字：`ch04.md:150` 将 `K/V 投影量` 改为 `K/V 投影`（`投影参数` 已包含在上下文中）或把 `与` 前移使两行均衡；`ch04.md:173` 将 `调大 RoPE 范围就当作质量保证` 改为 `调大 RoPE 范围就当质量保证`，`长输入能运行，却可能答错` 改为 `长输入能跑，但易答错`（或给三列表在打印 CSS `#llm-ch04 .table-scroll[data-cols="3"] th:nth-child(1),...` 设定合理列宽比，如 `28% / 26% / 46%`）。

### [MINOR-2] 第 4.5 节 MoE 叙述“先 KeepTopK 再 softmax 加噪声路由”语序易误解执行顺序

- **证据**：`round1/source/ch04.md:142` 写为：
  > “`[稀疏门控 MoE](https://arxiv.org/abs/1701.06538)` 早期论文按先 `KeepTopK` 再 `softmax` 加噪声路由，而 `[Mixtral 实现](https://github.com/huggingface/transformers/blob/47b0e478f324b54f177ea7998a0791870fdd0324/src/transformers/models/mixtral/modeling_mixtral.py)` 先对全部本地专家做 `softmax` 再选 `topk` 并重新归一化权重”
  对比固定原始论文 `sources/moe-1701.06538.txt` 公式 (3)–(5)：
  - Eq. (4)：`H(x)_i = (x · W_g)_i + StandardNormal() · Softplus((x · W_noise)_i)`（**先加可调高斯噪声**）；
  - Eq. (5) & (3)：`G(x) = Softmax(KeepTopK(H(x), k))`（**再做 `KeepTopK`，最后 `Softmax`**）。
  原文把“加噪声路由”置于“先 KeepTopK 再 softmax”之后，字面上容易被读者误解为“在 `KeepTopK` 甚至 `softmax` 之后才加噪声”。
- **修复建议**：将 `ch04.md:142` 改为：“早期论文采用加噪声门控（先向路由 logits 加可调高斯噪声、执行 `KeepTopK`，再做 `softmax`）”，与 `moe-1701.06538.txt` Eq. (3)–(5) 严格一致。

### [MINOR-3] NTK-aware 公式 `b' = b · s^(d/(d-2))` 沿用裸 `d`，未对齐全节的 `d_rot` 记号

- **证据**：
  - `round1/source/ch04.md:118` 明确定义旋转维度记号为 `d_rot`（并特别警示其不是 `d_model = 4096`）；`ch04.md:130` 的临界维度公式亦写作 `d_rot`。
  - 但中间夹着的 `round1/source/ch04.md:127`（及词汇表 `round1/source/ch16.md:60`）在 NTK-aware 缩放表中写作 `b' = b · s^(d/(d-2))`。虽然 `sources/yarn-2309.00071.txt` 第 3.1 节原式用 `d` 表示单头隐藏/旋转维，但在本章已把 `d` 分化为 `d_model` 与 `d_rot` 的上下文中，裸 `d` 存在下标丢失或被误读为 `d_model`（`4096`）的风险（特别当 `partial_rotary_factor < 1` 时，`d_rot != head_dim`）。
- **修复建议**：将 `round1/source/ch04.md:127` 与 `round1/source/ch16.md:60` 统一改写为 `b' = b · s^(d_rot/(d_rot-2))`（或括号加注 `d = d_rot`）。

### [MINOR-4] `RMSNorm` 原论文公式与工程稳定化形式未加一句对照说明

- **证据**：
  - `round1/source/ch04.md:38` 写为 `RMSNorm(x) = x / sqrt(mean(x²) + eps) * gamma`，紧贴前文引用 “RMSNorm 论文（arXiv:1910.07467）”。
  - 实查 `sources/rmsnorm-1910.07467.txt` Eq. (4) 原文，论文定义为 `RMS(a) = sqrt(1/n sum_{i=1}^n a_i^2)`，并未在根号内写出 `+ eps`；而 `sources/hf-llama.py` `LlamaRMSNorm`（默认 `eps = 1e-6`）及工程实现加上 `+ eps` 防止全零输入除零。
- **修复建议**：无须改公式，仅在 `ch04.md:39` 后或 `ch04.md:49` 首提 `eps = 1e-6` 处补半句标注即可，例如：“（其中 `+ eps` 为工程防除零项，原论文 Eq. (4) 省略该项，主流实现如 Llama 默认取 `eps = 1e-6`）”。

### [MINOR-5] `transformer_demo.py` 在 MoE + `mlp_bias=True` 时偏置计错，且两处接口校验偏弱

- **证据**（只读核查 `round1/source/transformer_demo.py`，当前 `test_llm_examples.py` 与正文默认关闭 `mlp_bias` 故未触发，但公共函数接口存在隐蔽缺陷）：
  1. **MoE `mlp_bias=True` 漏算专家偏置（`round1/source/transformer_demo.py:384-385`）**：
     ```python
     ffn_per_expert = ...  # 仅矩阵权重，不含 bias
     bias = (d_model + 2 * d_ff if swiglu else d_model + d_ff) if mlp_bias else 0
     ...
     ffn_total = ffn_per_expert * (moe_experts + shared_experts) + bias
     active_ffn = ffn_per_expert * (moe_active + shared_experts) + bias
     ```
     当调用方传入 `moe_experts=4, moe_active=2, shared_experts=1, mlp_bias=True` 且 `d_model=64, d_ff=128` 时，`ffn_total` 仅加了 `1` 份偏置 `320`，漏掉了其余 `4` 个专家（应为 `5 × 320 = 1 600`）；`active_ffn` 同理应加 `3 × 320 = 960`（且 `router` 本身是否含 bias 通常固定无偏置，但各专家 FFN 均有独立线性层 bias）。此外第 `388` 行返回的 `"ffn"` 语义在单专家时为单层 FFN 参数，在 MoE 时直接等于 `ffn_total`（未单独返回 `active_ffn`），虽无错但字段命名略晦涩。
  2. **`causal_rope_attention()` 缺少 `w_v` 行数及权重列宽校验（`round1/source/transformer_demo.py:238-239,257`）**：
     第 238–239 行检查了 `len(w_q) != n_heads * head_dim` 与 `len(w_k) != n_kv_heads * head_dim`，却漏掉 `len(w_v) != n_kv_heads * head_dim`；传入错误形状的 `w_v` 会直接抛出 `IndexError: list index out of range` 而非清晰的 `ValueError`。同时 `linear()` 第 145 行与 `causal_rope_attention()` 第 238 行也未校验 `w_q`/`w_k`/`w_v` 列宽与 `d_model` 一致，导致隐式被 `zip` 截断或无提示错误。
  3. **`params()` 缺少非物理入参防守（`round1/source/transformer_demo.py:352-397`）**：
     允许传入 `layers=-1`、`d_model=4096, heads=30`、`heads=32, kv_heads=6` 或 `moe_active=4 > moe_experts=2` 并返回荒谬总数而非 `ValueError`。
  4. **小精度提示（`rms_norm(..., float32_stats=True)`，`round1/source/transformer_demo.py:92-97`）**：该函数对 `v` 与 `w` 作 `_f32()` 单精度舍入后在 Python `float`（64 位）下求平方均值；对常规尺度数值与 HF `float32` 统计行为完全一致（实测差值 `0.0`），但若用极端大数（`> 1.84e19`）测试，不会模拟 IEEE-754 `float32` 平方中间溢出。作为教学脚本无需强求 C 级溢出模拟，建议保持实现并在注释注明“模拟转换至 float32 后在高精度累加求均值”即可。
- **修复建议**：
  - 将 `mlp_bias` 拆算进每套专家的 `ffn_per_expert` 或分别乘以 `(moe_experts + shared_experts)` 与 `(moe_active + shared_experts)`；
  - 在 `causal_rope_attention()` 补全 `len(w_v) != n_kv_heads * head_dim` 及行向量长度 `!= d_model` 的 `ValueError` 校验；
  - 在 `params()` 入口补充基本整除与范围检查（如 `layers >= 1`、`d_model % heads == 0`、`heads % kv_heads == 0`、`1 <= moe_active <= moe_experts`），并在 `tests/test_llm_examples.py` 增加对应单测。

### [MINOR-6] HTML/PDF 细节排版三处微瑕（`<wbr>` 切分 `RoPE`、参考列表 `break-all` 断词、`ch04.md` 布尔位置实参可读性）

- **证据**：
  1. `round1/yuyu-llm-zh.html` 图 4-2 `<figcaption>` 原文为 `<span class="fig-cap">4.4 Ro<wbr>PE：把位置变成旋转</span>`（PDF 第 43 页正常显示 `RoPE`，但窄屏 HTML 断点可能把 `RoPE` 拆成 `Ro` 与 `PE`）。
  2. PDF 第 48 页（`引用链接`）第 4 条 `[4]` 被渲染为 `.../mo\ndel.py`，第 3、6、8、9、13、16 条亦在长 SHA 中间被 `word-break: break-all` 任意硬断（虽然 `#llm-ch04 .notes-list li { flex-wrap: nowrap }` 成功保住了右侧 `↩` 回跳符号不掉行，表现良好）。改用 `word-break: normal; overflow-wrap: anywhere;` 可优先在 `/` 等斜杠边界换行，再对超长 SHA 段断行，避免 `mo/del.py` 这类文件扩展名割裂。
  3. `round1/source/ch04.md:82-83` 示例调用写成 `params(4096, 32, 32, 11008, 32000, True, False, ...)`，虽与 `transformer_demo.py:352` 签名完全一致且可运行无误，但 `True, False` 两个位置布尔量对初次阅读 `ch04.md` 的读者不够直观，改为 `swiglu=True, tie_embeddings=False` 可读性更佳。

### [MINOR-7] `VERIFY.md` 统计与输出摘要滞后于当前 `round1` 产物

- **证据**：
  - `round1/source/VERIFY.md:21,52,68` 仍记录历史版本数据（PDF `144` / `157` / `166` 页，单测 `443` / `480` 项等），而当前冻结产物 `round1/yuyu-llm-zh.pdf` 已更新至 **`168` 页**，`README.md` 与 `ch04.md` 已涵盖 `final_norm`、`GQA-8`、`MoE 8x-top2`、`rotate_half`、`sparse_moe_forward` 等新演示项。
  - `round1/source/VERIFY.md:104` 仅摘要了早期 `transformer_demo.py` 输出（`RMSNorm`、`LayerNorm`、代理 `block()`、标准 7B 与 2D/4D `base`），尚未同步最新输出中新增的 `forward_block()`、`final_norm=True`、`GQA-8`、`MoE 8x-top2`、`rotate_half_rope()` 与 `sparse_moe_forward()`。
- **修复建议**：在最终合版收尾时同步刷新 `VERIFY.md` 中的产物页数/字节数及第 4 章脚本校验摘要。

---

## 5. 缺失或校准不足的参考条目与术语对齐

1. **GitHub 仓库目录链接 vs 单文件链接粒度微差（`sources-llm.json` 对照）**
   `round1/source/ch04.md` 共有 `19` 处外链、`17` 个唯一 URL。其中 `16/17` 与 `round1/source/sources-llm.json` 的 `url` 字段逐字符严格一致；唯一差异是第 4 条（`round1/source/ch04.md:25`）正文引用了单文件 `https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/model.py`，而 `sources-llm.json` 键 `"nanogpt"` 的主 `url` 注册为仓库树目录 `https://github.com/karpathy/nanoGPT/tree/3adf61e154c3fe3fca428ad6bc3818b27a3b8291`（同提交 SHA，单文件 `model.py` 仅出现在 `snapshot` 描述字段中）。该引用指向真实精确且与 `source-lock.json` 同 SHA，属粒度登记差异而非错误，建议后续统一记录风格或在 `sources-llm.json` 中显式列明子文件路径。
2. **`round1/source/ch16.md`（第 16 章名词速查总表）对第 4 章术语的覆盖对齐**
   - `ch16.md:52-69`（`16.2` 节）已收录第 4 章 `17` 项核心词条（`Transformer block`、`residual stream`、`LayerNorm`、`RMSNorm`、`FFN`、`SwiGLU / GELU`、`RoPE`、`positional interpolation`、`NTK-aware scaling`、`YaRN`、`mixture of experts`、`router / load balancing`、`pre-norm / post-norm`、`model card`、`d_model`、`d_ff`、`tied embeddings`），含义与出处整体准确。
   - 缺口与建议：
     1. `ch16.md:60` 的 `NTK-aware scaling` 同样沿用了 `b' = b·s^(d/(d-2))` 裸 `d` 记号，建议与第 4 章同步改为 `d_rot`。
     2. `ch04.md` 重点解析并在第 4.6–4.8 节与模型卡核对表重复强调的 **`rope_theta`**、**`Final Norm`**、**`shared experts`** 与 **`partial_rotary_factor`**，以及论文出处 `RoPE 外推尺度律`（arXiv:2310.05209）、代码出处 `modeling_rope_utils.py`，目前在 `ch16.md` 均未单独成条或附注（`16.10` “读模型卡”清单亦未提及 `rope_theta` 或 `tied embeddings`），可在 `ch16.md:52-70` 增补 `rope_theta`、`Final Norm`（或并入 `pre-norm / post-norm` 说明）及 `shared experts`（并入 `mixture of experts`）以完善整书闭环。
     3. （注：经对照检查，`ch04.md` 所引 `2309.00071`、`2310.05209` 等在 `sources-llm.json` 均已钉死 SHA/版本；`ch04.md` 引用表全部 17 条均可追溯。）

---

## 6. 视觉与排版核查记录

### 6.1 PDF 第 40–48 页逐页版面度量（`round1/yuyu-llm-zh.pdf`，A4 `595.0 × 841.9 pt`）

| 页码 | 首个有效元素 | 末行 `y1 (pt)` | 底部留白 `(pt / %)` | 横向文本范围 `[min_x, max_x]` | 跨框垂直空隙 `>25pt` 及排版诊断 |
| --- | --- | --- | --- | --- | --- |
| p.40 | 章首 `一` | `775.1` | `66.9 (7.9%)` | `[48.0, 547.5]` | 正常（节标题/代码块/图 4-1 正常段距，`26.8–41.6 pt`） |
| p.41 | 接前段 `也` | `758.7` | `83.2 (9.9%)` | `[48.0, 547.5]` | 正常（含公式块、表 4.2；末尾代码块与 `4.3` 标题同页） |
| p.42 | 接前段 `其` | `730.2` | `111.7 (13.3%)` | `[48.0, 547.5]` | 正常（含 SwiGLU 公式、表 4.3、Python `params()` 块） |
| p.43 | `4.4 RoPE：把位置变成旋转` | `731.0` | `111.0 (13.2%)` | `[48.0, 547.5]` | 正常分段，**但图 4-2 内 `φ'` 与 `φ` 碰撞**（见 `MAJOR-2`） |
| p.44 | 表 4.4 `m - n \| 点积` | `747.5` | `94.5 (11.2%)` | `[48.0, 547.5]` | 正常（表 4.4、长上下文三法表、末尾 `4.5` 节头带两行引语不孤悬） |
| p.45 | 编号列表 `1.` | `767.3` | `74.6 (8.9%)` | `[48.0, 547.5]` | 基本紧凑，**表 4.5 第 3 行第 2 列单字 `量` 孤立换行**（`MINOR-1`） |
| p.46 | `4.6 Agent 工程落点` | `763.2` | `78.7 (9.3%)` | `[48.0, 547.5]` | 基本紧凑，**表 4.7 第 5–6 行出现 `Norm`、`证`、`错` 孤立换行**（`MINOR-1`） |
| p.47 | 编号列表续 `-` | **`323.0`** | **`518.9 (61.6%)`** | `[48.0, 547.5]` | **`MAJOR-1`：整章结束于 `y=323.0`，下半页 61.6% 全白** |
| p.48 | `引用链接` | `594.0` | `247.9 (29.4%)` | `[61.3, 537.2]` | `.chapter-notes` 整块推至本页；`↩` 未掉行（好），`mo/del.py` 硬断（微瑕） |

注：第 `40–48` 页**全部无横向溢出**（正文严格约束在 `[48.0, 547.5]` 内）。

### 6.2 SVG 结构、样式与几何碰撞检查

| 检查项 | 图 4-1 (`llm-ch04-transformer-block.svg`) | 图 4-2 (`llm-ch04-rope-rotation.svg`) |
| --- | --- | --- |
| 文件体积（`<= 6000 B`） | `3 300 B`（通过） | `4 347 B`（通过） |
| `viewBox` 与自适应类 | `0 0 460 258`，`class="llm-explainer"`（通过） | `0 0 420 342`，`class="llm-explainer"`（通过） |
| 无障碍语义 | `role="img"`、`aria-label`、`<title>`、`<desc>` 完备 | `role="img"`、`aria-label`、`<title>`、`<desc>` 完备 |
| 调色与引用隔离 | 全 `currentColor`，无外部资源/固定 `id` 冲突 | 全 `currentColor`，无外部资源/固定 `id` 冲突 |
| 矢量数学精度 | `x` 直通主干与两次 Pre-LN + Final Norm 拓扑准确 | 左 `10°/55°`、右 `55°/100°` 严格 `+45°`；条宽 `35.2 = 42×0.839`、`41.8 = 42×0.995` 与实际 `cos(10)=-0.839`、`cos(0.1)=+0.995` 精确一致 |
| 文本重叠与边距 | **0 碰撞**：`Final Norm` PDF 宽 `45.3 pt` 居于 `55.6 pt` 框内，左右各余 `~5.1 pt`；`x` 距残差线余 `1.91 SVG px` | **2 处 `d = 0.00` 碰撞**（`MAJOR-2`）：`φ'` `(331,102)` 直接穿过 `q'` 与虚线 `k`；`φ` `(146,112)` 直接压上左虚线圆 `r=52` |

### 6.3 HTML DOM 与响应式度量（`round1/yuyu-llm-zh.html` 与 `visual-round1/report.json`）

- `#llm-ch04` 结构完整：1 枚 `<h1>`、8 枚 `<h2>`（`4.1`–`4.8`）、1 枚 `<h4>`（`引用链接`）、6 张数据表、9 块 `<pre>`、2 幅正文 `llm-explainer` SVG、17 条 `.chapter-notes li`、`43` 个章内跳转/脚注锚点。
- `visual-round1/report.json` 记录桌面 `1440px` 与移动端 `390px`（亮/暗主题共 `24` 项 DOM 自动化校验）全数通过，打印模式下 `.codehilite span` 统一重着色为 `rgb(66, 54, 34)`，确保在纸面高对比可读。
- 潜在移动端 HTML 细节：`<figcaption>` 含 `4.4 Ro<wbr>PE`（见 `MINOR-6`）。

---

## 7. 已核验数值与公式台账（Checked Numerical Ledger）

全部数值均经独立 Python `64-bit float` / PyTorch `2.14.1+cpu` 重算并与 `round1/source/ch04.md`、`round1/source/transformer_demo.py` 及钉住参考源核对：

| 核验对象 | 书稿/图宣称值 | 独立验算值 / 对照结果 | 状态 |
| --- | --- | --- | --- |
| `x = [1, 2, 3]` 模长 | `3.742` | `sqrt(14) = 3.741657` | 通过 |
| `RMSNorm([1,2,3], eps=1e-6)` | `[0.463, 0.926, 1.389]`, `scale=2.160` | `[0.462910, 0.925820, 1.388730]`, `2.160247`；与 PyTorch 差 `0.0` | 通过 |
| `LayerNorm([1,2,3], eps=1e-6)` | `[-1.225, 0.000, 1.225]`, `mean=2.000`, `scale=0.816` | `[-1.224653, 0.0, 1.224653]`, `2.0`, `0.816497`；与 PyTorch 差 `0.0` | 通过 |
| 尺度不变性实验 `X0=[0.1,0.2,0.3]`（`ch04.md:185`） | 输出仍 `[0.463,0.926,1.389]` 与 `[-1.225,0.000,1.225]`；`scale`: `0.216` / `0.082` | RMS `[0.463,0.926,1.389]` (`0.216027->0.216`)；LN `[-1.225,0.0,1.225]` (`0.081656->0.082`) | 通过 |
| 残差代理两层范数递增（`ch04.md:25`） | `3.742 -> 3.850 -> 4.030` | block1 `[1.343, 2.010, 2.996]` (`3.850`)；block2 `[1.790, 2.018, 2.994]` (`4.030`) | 通过 |
| 真实 2-token `forward_block`（`d=4, h=1`）+ Final Norm | 1-block `[4.730,...]`；2-block+FinalNorm 模长 `2.000` | 与手写 PyTorch (`GQA 4/2 + bias + RoPE + SwiGLU`) 最大误差 `4.44e-16`；RMSNorm 后 `||y||_2 = sqrt(4) = 2.000` | 通过 |
| `4096 × 8/3` 对齐 `256` 倍数 | `≈ 10 923` 向上圆整 `43 × 256 = 11 008` | `10922.67` -> `43 * 256 = 11008` | 通过 |
| SwiGLU 7B 每层分解（`d=4096, d_ff=11008`） | Attn `67 108 864`；FFN `135 266 304`；Norm `8 192`；每层 `202 383 360` | `4*4096^2 = 67,108,864`；`3*4096*11008 = 135,266,304`；`2*4096 = 8,192`；和 `202,383,360` | 通过 |
| SwiGLU 7B 整模（tied / untied / +FinalNorm） | `6 607 339 520` / `6 738 411 520` / `6 738 415 616` | `32*202383360 + 131072000 = 6,607,339,520`；`+131072000 = 6,738,411,520`；`+4096 = 6,738,415,616` | 通过 |
| ReLU/GELU 7B（`d_ff=16384`） | FFN `134 217 728`；每层 `201 334 784`；tied `6 573 785 088`；untied `6 704 857 088` | `2*4096*16384 = 134,217,728`；`+67108864+8192 = 201,334,784`；32 层+词表全等 | 通过 |
| 词表差与两张词表（`32000 × 4096`） | 单张 `131 072 000`，两张 `262 144 000` | `32000*4096 = 131,072,000`；`2x = 262,144,000` | 通过 |
| GQA-8（`kv_heads=8`, 含 `final_norm`） | 每层 Attn `41 943 040`；每层省 `25 165 824`；32 层省约 `0.81B`；total `5 933 109 248` | `2*4096^2 + 2*4096*1024 = 41,943,040`；差 `25,165,824`；`32*差 = 805,306,368 ≈ 0.81B`；`6738415616 - 805306368 = 5,933,109,248` | 通过 |
| MoE 8×-top2（`d_ff=14336`, untied） | `total = 46 702 792 704`；`active = 12 879 925 248` | 按 `transformer_demo.py`：`router=32768`, `per_expert=176160768`, `total=46,702,792,704`, `active=12,879,925,248` | 通过 |
| 权重显存换算（`ch04.md:4,140`） | `7B*2B=14GB (13.0 GiB)`；`6.74B` 约 `12.6 GiB`；教学 untied fp16 `12.55 GiB (13.48 GB)`；4-bit `3.14 GiB` | `14e9/1024^3 = 13.0385 GiB (13.0)`；`6738411520*2/1024^3 = 12.5513 GiB (12.55 / 12.6)`；`/1e9 = 13.4768 GB`；`*0.5/1024^3 = 3.1378 GiB` | 通过 |
| 128K KV cache（32 头 vs GQA-8, fp16） | MHA `64.00 GiB`（合计 `76.55 GiB`）；GQA-8 `16.00 GiB` | `2*32*32*128*2*131072/1024^3 = 64.00 GiB`（`+12.55 = 76.55`）；`2*32*8*128*2*131072/1024^3 = 16.00 GiB` | 通过 |
| RoPE 2D `[1,0]` 点积（`m-n = 0..3`） | `+1.000, +0.540, -0.416, -0.990` | `cos(0..3) = 1.0, 0.540302, -0.416147, -0.989992` | 通过 |
| RoPE 4D 高低频与布局对照（图 4-2 与 `ch04.md:120,187`） | `i=0: -0.839`, `i=1: +0.995`；`base=10000` 和 `+0.156`、`base=100`: `-0.299`；布局对齐 `-1.082` vs 混用 `+0.193` | `cos(10) = -0.83907`, `cos(0.1) = +0.99500`, 和 `+0.15593`；`base=100` 为 `-0.29927`；`rotate_half` 与 HF 误差 `0.0` | 通过 |
| RoPE 临界维度（`base=10000, d_rot=128, T=4096`） | 前 `92` 维走过完整周期，后 `36` 维未走满 | `2 * ceil(64 * log_10000(4096 / (2*pi))) = 2 * ceil(45.02688) = 92`；`128 - 92 = 36` | 通过 |
| 稀疏 MoE top-2 示例（`transformer_demo.py` & PyTorch） | `[E0: 0.646, E1: 0.354] -> [0.216, -0.073]` | 与 `hf-mixtral-pinned.py` `MixtralSparseMoeBlock`（`float64`）最大误差 `1.11e-16` | 通过 |

---

## 8. 最终出版建议

第 4 章在核心原理、公式推导、纯标准库可复现性及模型卡工程落地上已达到很成熟的出版标准。建议按以下顺序完成收敛后再进入终校发布（**Verdict: Almost -> Ready**）：

1. **必改（`MAJOR`）**：修改 `round1/source/style_print.py:196` 让 `.chapter-notes` 允许条目间分页以消除 PDF 第 47 页 `61.6%` 空白；调整 `round1/source/llm-ch04-rope-rotation.svg` 角度弧半径及 `φ`/`φ'` 坐标（并视需要收紧打印 `.il-sub` 字号）消除第 43 页 `d = 0.00` 的标签穿线/骑圆碰撞，随后重新渲染 HTML/PDF 并抽检第 43、47、48 页效果。
2. **建议一并修齐（`MINOR`）**：优化表 4.5 与表 4.7 的第 3/5/6 行避免单字孤立折行；修正 `ch04.md:142` MoE 加噪声路由语序；统一 `ch04.md:127` 与 `ch16.md:60` 的 `d_rot` 符号；补全 `transformer_demo.py` 中 MoE `mlp_bias=True` 计算、`causal_rope_attention()` `w_v` 校验及 `params()` 入参校验并加测；顺带刷新 `VERIFY.md` 页码与输出摘要。
