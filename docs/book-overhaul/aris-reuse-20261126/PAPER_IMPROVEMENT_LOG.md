# 第五轮：复用 minbpe，核对注意力与缓存

日期：2026-11-26。范围为 LLM 第 1、3、16 章、BPE 与注意力示例、两幅图及相关来源和验证。按本地 ARIS 书稿适配执行两次新上下文审读，均为 same-family / provisional；原生工具只返回任务标识，未把请求模型名冒充实际身份。没有外部写作服务或消息通知。

## 来源与直接复用

- minbpe 固定提交 `1acefe89412b20245db5a22d2a02001e547dc602`。原样引入 `base.py`、`basic.py`、MIT `LICENSE`，直接调用 `merge` 和 `BasicTokenizer.encode`。本地入口只导出基础接口，不加载 regex/tiktoken；多文本训练、字典序并列处理和严格 UTF-8 解码保留本书语义。Git blob 与 SHA-256 记录在 `llm/examples/vendor/minbpe/UPSTREAM.json`，测试防止换行转换或改写破坏原文件。
- nanoGPT 固定提交 `3adf61e154c3fe3fca428ad6bc3818b27a3b8291` 的 `model.py` 用于核对投影、分头、缩放、遮罩、输出投影与 SDPA 调用；仅引用与独立讲解，没有复制代码。
- PyTorch `v2.14.1` 固定提交 `5c4886908584029761b579af026dcfb627c84070` 的 `functional.py` 用于核对非方阵左上对齐遮罩。另以本机 `2.14.1+cpu`、float64 实际对照三个 token：完整注意力最大差 `1.1102230246251565e-16`；错误地重置查询位置时，两边都只返回 `[1.0, 0.0]`。这不是性能基准，也没有为书稿新增 PyTorch 必需依赖。
- 独立审读实际读取 DeepSeek-V2 `2405.04434v5` 的 §2.1.2–2.1.4、Table 1 与 GQA `2305.13245v3`。执行器复抓 arXiv 受网络权限限制，复读审读者转交的原始段落；登记明确区分获取者。公开 GitHub 资料通过 CLI 取得，连接器的 Bad credentials 没有通过改凭据或安全设置解决。

## 第一次审读

冻结输入：`.scratch/aris-reuse-20261126/round0/`，原始 HTML/PDF 来自已完成的上一轮成品。报告：[review1.md](review1.md)，评分 7/10、Almost。

修复客服错误的未经验证归因及订单读取后文地址的因果矛盾；改正 MLA 缓存内容与投影吸收，去掉相对 MQA 固定再省一档的表述。统一矩阵方向，明确 0.6 来自三个可见位置平均值；注意力 pair 数限定到每层、每个查询头。两图改为可见标签的 3×3 因果遮罩和真实算术流程。参数表合并相同投影列。

新增 `query_start` 展示缓存查询的绝对位置，用单 token 与分块输入比较完整因果计算。加入错误位置、维度和 head 配置回归。BPE 复用另核对重叠 pair、合并排名与文档边界，正文可运行短实现与复用后的脚本输出一致。

## 第二次审读

冻结输入：`.scratch/aris-reuse-20261126/round1/`，HTML/PDF 共 163 页；报告：[review2.md](review2.md)，评分 8/10、Almost。审读者独立执行 17 项相关测试，核对上游三个文件字节，并实际查看 8 页 PDF 与桌面、手机截图。

审读后的修复：Unicode 组合字符先赋值，避免旧 Python 的 f-string 解析错误；章节写明全书 Python 3.12+ 环境。多头表在手机保留完整向量并容器内滚动。打印代码统一深色，第 3 章短代码保持同页。收尾区分手设投影与计算出的注意力权重，术语表补回等宽头条件。执行器发现“试三组”对应四项，改为“下面几组”。未进行第三次评分，也未把执行器验证写成独立审读通过。

## 验证与发布

最终结果和产物哈希见 [final-validation.json](final-validation.json)。修改前后的章节标题、稳定 block ID 与插图引用保持一致。生成产物位于忽略目录 `.scratch/aris-reuse-20261126/round2/`，源码为 Markdown、Python 与 SVG；没有手动修改 dist 或缓存。

上一轮 PR #59 已合并。其 main Book CI 的完整构建成功，但产物声明检查发现 README 写 541 页，实际 CI/Noto CJK 为 542 页、30.7 MB；本轮按 run `45729453753` 的 Full job 原始日志修正该声明，未用 Windows/微软雅黑或 LLM 分册页数替代主书 CI 数值。
