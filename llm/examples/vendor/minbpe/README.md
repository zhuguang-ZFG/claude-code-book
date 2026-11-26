# minbpe 基础实现

`base.py`、`basic.py` 和 `LICENSE` 原样取自 [karpathy/minbpe](https://github.com/karpathy/minbpe/tree/1acefe89412b20245db5a22d2a02001e547dc602)，提交为 `1acefe89412b20245db5a22d2a02001e547dc602`，版权与 MIT 许可见同目录 [LICENSE](LICENSE)。`UPSTREAM.json` 记录上游路径、Git blob SHA 与文件 SHA-256。

本地新增的 `__init__.py` 只导出 `BasicTokenizer` 和 `merge`，没有复制上游会导入 `regex`、`tiktoken` 的入口。正文示例因此仍能只靠标准库离线运行。不要用格式化工具重写这两个上游文件；升级时按新提交替换、重新核验文件哈希并运行行为测试。

`bpe_demo.py` 直接复用 `merge` 和 `BasicTokenizer.encode`；训练仍按本书的多文本边界与字典序处理并列候选，解码仍严格检查 UTF-8。这与上游单字符串训练、首次出现顺序解并列以及 `errors="replace"` 的解码有区别，不能据此宣称两者独立训练会得到相同词表。

复用范围不包含生产预切分、特殊 token、GPT-4 词表、模型权重或训练数据。
