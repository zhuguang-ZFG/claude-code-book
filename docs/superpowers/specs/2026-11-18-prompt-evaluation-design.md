# 规格：提示词卷的外部任务评估（第一批）

建立：2026-11-18。基线是已发布 `v0.3.8`，提交 `b9acef731b28c0406bf49f2cb68acdc3198e9806`。本文件只定义设计和验收，不授权实现、不授权调用模型、不授权改已经出版的正文。

用户已批准三批补齐的顺序。本规格只覆盖第一批里的一个子项目：用青禾工作坊已有的固定题目，对两个提示变体做配对对照。Hermes、Codex、DeepSeek、Kimi、Pi 的宿主端到端验证不在本批。脑健康读物不纳入。参考书只提供实验设计原则，不提供可搬用的题目、插图或章节结构。

## 要解决的缺口

`prompt/ch16.md` 第 10 行写明：离线程序有输出，新册模型对照还未运行。`prompt/VERIFY.md` 第 54–58 行写明：模型 A/B、跨模型迁移、宿主权限组合和独立读者试读都没做；28 份模型请求只是准备好的输入；旧课程里的 DMX 实验本轮不复跑。`prompt/evidence/unrun-comparison.json` 把 A、B 各 14 次记为 `missing`，`complete` 为 false，通过数差值是 null。`prompt/examples/lab.py` 的 `prepare()` 固定返回 `executed_model_calls: 0`。

离线名额检查（`prompt/examples/workshop.py`）和机械 JSON 检查（`lab.check_response`）已经能跑。它们证明不了「提示 B 比提示 A 让模型答得更好」。

## 目标

在不预设哪一版胜出的前提下，让同一次实验能够：

1. 冻结题目、材料、两段提示、重复次数和采样配置。
2. 默认停在离线。只有读者显式打开在线模式，并先写出模型标识和调用次数上限，才允许发出请求。
3. 把每一次请求记成 `pass`、`fail`、`error` 或仍为 `missing`。服务失败留在分母里。
4. 用配对而不是只看总分：两版都过、仅 A 过、仅 B 过、两版都不过、未完成。
5. 在正文里用原创中文说明词元、上下文窗口和温度为什么会搅乱这次对照，并指向已有章节，不新开一册。

未跑完或未授权时，对外句子保持现在的「还未运行」。不得把离线通过率写成模型成绩。

## 非目标

- 不调用真实模型，不登录，不读取或搜索凭据，不估算或填写价格。
- 不复跑 DMX / EVALUATION-04，也不把该记录的 5/8 算进青禾题。
- 不把模型自己的「我答对了」当作真值。
- 不证明某个宿主能拦住提示注入或完成沙箱审批。那是另一批，证据必须是该宿主的日志。
- 不修改英文稿，不新增分册，不把参考书的例题写进正文。
- 不在本规格的实施完成前改 `prompt/ch16.md` 或 `prompt/VERIFY.md` 里「还未运行」的结论。实施计划里的正文改动，要等用户书面确认本规格之后才做。

## 已有实现（以仓库文件为准）

| 物件 | 作用 | 边界 |
| --- | --- | --- |
| `prompt/prompts/a.txt` | 变体 A：按材料作答、不编造、JSON、只读任务的 `actions` 为空 | 与 B 的差别只是 B 多一句「回答前逐项核对材料是否足够」 |
| `prompt/prompts/b.txt` | 变体 B | 同上 |
| `prompt/cases/validation.json` | 验证集 7 题：V01–V07 | `lab.prepare` 默认用这个集合 |
| `prompt/cases/holdout.json` | 留出集 | 准备阶段可选，不进默认对照 |
| `prompt/cases/development.json` | 开发集 | `prepare` 的 `--split` 不允许 development，避免边看答案边调提示又混进成绩 |
| `prompt/evaluation/criteria.json` | 人工判据，按题列出必须出现的事实和禁止的动作 | `evaluation/README.md` 写明判据不进入导出的模型输入 |
| `prompt/examples/lab.py` | `context` / `check` / `prepare` / `review` / `compare` | 无网络。`check_response` 只做字段、类型、引文是否逐字出现、`actions` 是否为空；语义仍要人工看 |
| `tests/test_prompt_workshop.py` | 机械失败不能记 pass、缺响应只能记 error、重复评审被拒绝、未完成时差值为 null | 使用合成响应，不是模型输出 |

请求数已经由代码决定，不另造：

```text
计划请求数 = 该 split 的题目数 × 2 个变体 × repeats
```

验证集 7 题、`repeats` 默认 2，得到 28。这就是 `unrun-comparison.json` 里 A、B 各 `planned: 14` 的来源（7×2）。留出集是 `prompt/cases/holdout.json` 的 2 题（H01、H02）。同样 repeats=2 时计划请求数是 8，不是 28。实施时以 `len(cases(split))` 为准，不把 28 写死成所有 split 的常数。

`bundle()` 已记录 `request_sha256`、字符数和 UTF-8 字节数，并写明「字符数不是 token 数」。

## 四层证据，不能互相顶替

| 层 | 问的问题 | 现有或计划中的证据 | 不能推出 |
| --- | --- | --- | --- |
| 格式正确 | JSON 字段、引文是否出现在本次材料里、只读任务是否没有动作 | `lab.check_response` | 答案在事实上正确 |
| 任务正确 | 是否满足 `criteria.json` 里该题的必需项 | 人工 `review`，结果为 pass 或 fail | 换一个模型或宿主仍然成立 |
| 安全行为 | 是否拒绝越权、不声称已导出数据或已发送 | 人工按判据看回答文字；V02 的判据已包含这一点 | 真实宿主已经拒绝了工具调用 |
| 宿主端到端 | 登录、续会话、审批、沙箱、持久化是否发生 | 本批不产生 | 提示对照已完成 |

`pass` 必须先通过机械检查，再由人按判据勾完。模型拒绝回答但返回了文本，这是一份响应：人把它记为 fail 或（若判据允许这种拒绝）pass，不记成网络 error。没有响应的超时、连接失败、额度用尽，记 error。还没发出的请求保持 missing，不能并进 error，也不能写成零分。`compare()` 已实现：存在 missing 则 `complete` 为 false，`pass_count_delta_b_minus_a` 为 null。

## 两种实现，以及推荐

### 方案甲：把在线调用加进 `lab.py`

在现有子命令旁增加 `run`。优点是读者只记一个入口。缺点是今天所有测试都假设这个文件不碰网络；一个默认路径若读到环境变量里的密钥，就会破坏「默认离线」。采样、重试和供应商差异也会堆进已经负责记账的文件。

### 方案乙：单独的运行器，只消费已冻结的计划

新增 `prompt/examples/model_run.py`。它只读取 `lab.prepare` 写出的目录，核对 `plan.sha256` 与每条 `request.txt`。没有 `--online` 时打印计划请求数和将要锁定的配置，然后以退出码 0 结束，且 `executed_model_calls` 仍为 0。有 `--online` 时还要同时给出模型标识、调用次数上限和采样配置文件；缺任何一项就退出码 2，并且不打开网络。

记账仍由 `lab.review` 和 `lab.compare` 完成。运行器不写 pass/fail，只写响应原文或失败记录。

### 推荐方案乙

失败面隔开：离线测试继续导入 `lab`，不会因为新文件多了一个 HTTP 客户端而在 CI 里发请求。CI 只运行注入的假传输对象。真实传输在未实现前不存在；实现时也不得在导入模块时读环境、列环境或打印密钥。

## 锁定什么，失败时怎样记

一次在线实验在第一条请求之前写入 `sampling.json`，之后不得改：

- `model_id`：调用方原样使用的模型标识字符串，另加读者填写的 `model_card_date`（YYYY-MM-DD）。本规格不代选厂商或型号。
- `temperature`：数字，或显式的 `null` 表示「不发送该字段」。
- `top_p`：同样。不发送的字段必须写出来，不能靠缺省偷偷换一套。
- `seed_policy`：`required` 或 `unavailable`。`required` 时还要有整数 `seed`。
- `max_output_tokens`：整数上限，只作为请求参数，不换算成价格。
- `repeats`：与 `plan.json` 一致。

请求数公式在真正连接前打印：

```text
计划请求数 = 题目数 × 2 × repeats
若 计划请求数 > max_calls：退出码 2，已发出次数 = 0
```

不写单价，不写「约合多少元」。用量只在供应商响应里确实返回了 token 计数时，把数字记入该槽的 `usage`；没有就记 `usage: null`，不估算。

失败分类（都算该槽已尝试，除「尚未发出」外都进入分母）：

| 状况 | 记录 | 是否重试 |
| --- | --- | --- |
| 锁定文件本身不合法（例如 `seed_policy=required` 但没有 `seed`） | 退出码 2，已发出次数为 0 | 否。尚未连接 |
| 供应商拒绝某个已锁定参数，或明确表示没有种子而政策为 `required` | 该次请求记 1，状态 `blocked_unsupported_parameter`，不再发后续槽。其余槽保持 missing | 否。不得删掉该参数再发 |
| `seed_policy=unavailable` | 允许跑，报告写明「采样未固定，差异不能只归因于提示」 | 按下面的传输重试 |
| 网络超时、连接重置、5xx | 同一请求最多再试 2 次（共 3 次）。仍失败则该槽 `transport_error`，人记 error | 仅此传输类 |
| 模型返回文本但拒绝作答 | 保存原文，槽状态 `response_received`。人按判据记 pass 或 fail | 否 |
| 只完成一部分槽 | 已完成的保留；未发出的保持 missing。`compare` 保持不完整，差值保持 null | 不自动补跑缺失槽，除非读者用新的实验目录重跑全部 |

重试必须把每一次的开始时间、结束时间、结果类别写入该槽的 `attempts.json`，不写密钥，不把材料全文复制进提交到仓库的摘要。

## 可提交的记录和不可提交的记录

本地实验目录（建议 `.scratch/prompt-ab/`，已被仓库忽略）保留 `request.txt`、`response.txt`、`attempts.json`。这些可能含任务材料，不进入 git。

可以提交的摘要至少包含：模型标识、`model_card_date`、采样配置的 SHA-256、计划请求数、实际发出数、pass/fail/error/missing、配对五格、每槽的 `request_sha256` 与 `response_sha256`、失败类别、起止时间、返回的 usage 数字或 null。摘要不含 `answer` 正文、不含材料引文、不含密钥。没有真实运行时，不新增一份假装完成的摘要；继续引用 `unrun-comparison.json`。

## 正文插在哪里

实施得到用户书面确认之后，只动这两处，且在真实运行完成前不改「还未运行」这句判断：

- `omp/ch02.md` 第 2.2 节之后新增一小节，原创说明：温度把下一个词元的概率拉平或收紧；同一提示因此会得到不同下文；做 A/B 时温度、top-p 和种子政策必须先锁定。交叉引用 `prompt/ch16.md`。第 2.1–2.2 节已经讲了词元和上下文窗口，不重写，不从参考书抄分词表或数字。
- `prompt/ch16.md`「冻结要比较的输入」一节补上请求数公式、采样锁定和四层证据。保留第 10 行和第 186 行的未运行声明，直到摘要文件存在且 `executed_model_calls` 与计划数一致。

## 最小验收（实现阶段，不是本文件）

1. 现有 `python -m unittest tests.test_prompt_workshop` 仍通过，且不打开套接字。
2. 新测试使用假传输：缺 `--online` 时发出次数为 0；`max_calls` 小于计划数时退出码 2 且发出次数为 0；参数被拒时发出次数为 0；三次传输失败后该槽为 error 类记录；部分槽完成后 `lab.compare` 的差值为 null。
3. 假传输的 pass 不能绕过 `check_response`。机械失败记成 pass 时，`lab.review` 仍然拒绝。
4. 测试不读取环境变量清单，源码审阅确认没有搜索常见密钥名。
5. 正文在没有摘要文件时仍写「模型对照还未运行」。离线 workshop 的 12/12 不得出现在模型成绩句子里。

## 读者或用户在实现在线模式之前必须决定的事

只这些，本规格不代选：

1. 模型标识字符串，以及该标识对应说明的日期。
2. `max_calls`（整数上限）。验证集默认全套是 28，可以更小，但不能在跑完后删掉失败再重算。
3. `seed_policy` 用 `required` 还是 `unavailable`。
4. 是否授权某一次付费或本地服务调用。未授权时运行器保持离线。

未决定前，实施计划可以合并文档，但不得开始写运行器，更不得发请求。
