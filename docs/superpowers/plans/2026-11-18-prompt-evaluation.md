# 提示词外部评估 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在青禾验证集上，为已有的提示 A/B 增加默认为离线的运行记录，使真实模型对照可以复现，并在未跑之前继续标明未运行。

**Architecture:** 保留 `prompt/examples/lab.py` 的出题、机械检查和人工记账。新增 `prompt/examples/model_run.py` 只消费冻结计划；网络客户端由调用方注入，默认不存在。正文只在 `omp/ch02.md` 与 `prompt/ch16.md` 各补一小节。

**Tech Stack:** 仓库现有 Python 3.12、`unittest`、标准库 `json`/`hashlib`/`argparse`。不新增依赖。不使用 pytest。

**规格：** [2026-11-18-prompt-evaluation-design.md](../specs/2026-11-18-prompt-evaluation-design.md)

## Global Constraints

- 基线提交是 `b9acef731b28c0406bf49f2cb68acdc3198e9806`。未得到用户对本文和规格的书面确认前，不实现本计划。
- 默认离线。在线模式必须同时具备 `--online`、模型标识、`max_calls` 和采样配置。缺一则退出码 2，发出次数为 0。
- 不探测、不列举、不打印凭据。测试不得读取环境变量清单。
- 不预设变体 B 胜出。不把单次差值写成普适结论。不把 `workshop.py` 或业务用例的离线通过率写成模型成绩。不用模型自评当真值。
- 计划请求数 = 该 split 题目数 × 2 × `repeats`。验证集 7 题且 repeats=2 时为 28。不要把 28 写死到留出集。
- 不写价格。用量只记录供应商确实返回的数字，否则 null。
- 不复跑 DMX。不新增分册，不改英文稿，不搬用参考书例题。
- 没有与计划数一致的真实 `executed_model_calls` 之前，`prompt/ch16.md` 第 10 行和 `prompt/VERIFY.md` 第 56 行的「还未运行 / 尚未完成」保持不变。
- 仓库检查用 `python -m unittest`，不用 pytest。

---

### Task 1: 采样锁定与请求数，仍然零网络

**Files:**
- Create: `prompt/examples/model_run.py`
- Test: `tests/test_prompt_model_run.py`

**Interfaces:**
- Consumes: `lab.prepare(folder, split, repeats, environment)` 写出的 `plan.json`、`plan.sha256`、各槽 `request.txt`。
- Produces: `load_lock(path) -> dict`；`plan_size(plan) -> int`；`dry_run(folder, lock, max_calls) -> dict`，键为 `planned_requests`、`executed_model_calls`、`status`。`status` 为 `offline` 时后者为 0。

- [ ] **Step 1: 写失败测试**

```python
def test_dry_run_prints_the_formula_and_sends_nothing(self):
    folder = self.prepared_validation(repeats=2)  # 7 题
    lock = {"model_id": "reader-chosen", "model_card_date": "2026-11-18",
            "temperature": 0, "top_p": None, "seed_policy": "required",
            "seed": 7, "max_output_tokens": 512, "repeats": 2}
    result = model_run.dry_run(folder, lock, max_calls=28)
    self.assertEqual(result["planned_requests"], 28)
    self.assertEqual(result["executed_model_calls"], 0)
    self.assertEqual(result["status"], "offline")
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `python -m unittest tests.test_prompt_model_run.DryRun.test_dry_run_prints_the_formula_and_sends_nothing -v`

Expected: FAIL，`model_run` 不存在。

- [ ] **Step 3: 实现最小的离线路径**

`dry_run` 调用 `lab.load_plan`，用 `len(plan["runs"])` 作为计划数。`repeats` 与计划不一致则抛 `ValueError`。不导入 HTTP 库。

- [ ] **Step 4: 再跑该测试，确认通过**

Run: 同上。Expected: PASS。

- [ ] **Step 5: 提交**

只提交这个任务的测试和 `model_run.py`。

### Task 2: 假传输下的拒绝、重试和部分完成

**Files:**
- Modify: `prompt/examples/model_run.py`
- Test: `tests/test_prompt_model_run.py`

**Interfaces:**
- Consumes: Task 1 的 `dry_run`。
- Produces: `run_online(folder, lock, max_calls, transport) -> dict`。`transport(slot, request_bytes, lock) -> Attempt`。`Attempt` 是含 `kind` 的字典：`ok`、`unsupported_parameter`、`transport_error`、`refusal_text`。

- [ ] **Step 1: 写四条失败测试**

1. `max_calls` 为 27 而计划为 28：退出语义用返回值 `status=refused_over_budget`，`executed_model_calls=0`，且 transport 不被调用。
2. 锁定文件缺 `seed` 且政策为 `required`：`executed_model_calls=0`，不调用 transport。供应商在第一次请求返回 `unsupported_parameter`：该次记 1，状态 `blocked_unsupported_parameter`，后续槽不发送，那些槽保持 missing。不得删掉被拒参数再试。
3. 同一槽连续三次 `transport_error` 后停止该槽，`attempts` 长度为 3，不开始第 4 次。
4. 只给一半槽返回 `ok`：对应目录出现 `response.txt`；`lab.compare` 在缺评审时 `pass_count_delta_b_minus_a is None`。

- [ ] **Step 2: 运行新测试，确认失败**

Run: `python -m unittest tests.test_prompt_model_run -v`

Expected: 新测试 FAIL，旧的 dry_run 仍 PASS。

- [ ] **Step 3: 实现**

传输对象由参数注入。`run_online` 在缺少注入对象时抛 `ValueError`，不创建套接字。拒答文本写入 `response.txt`，槽标记为已收到响应，不调用 `lab.review`。机械检查仍只在人记 pass 时由现有 `lab.review` 执行。

- [ ] **Step 4: 运行 `tests.test_prompt_workshop` 与 `tests.test_prompt_model_run`**

Expected: 全部 PASS。确认测试进程没有新增对外连接（假传输不使用 socket）。

- [ ] **Step 5: 提交**

### Task 3: 正文只解释对照条件，不宣布结果

**Files:**
- Modify: `omp/ch02.md`（第 2.2 节之后）
- Modify: `prompt/ch16.md`（「冻结要比较的输入」一节，约第 77 行之后）
- Test: 人工核对，外加现有 `python scripts/check_book.py` 若改了 Markdown

**Interfaces:**
- Consumes: 规格里的四层表和请求数公式。
- Produces: 读者能从第 2 章跳到第 16 章，并看到「字符数不是 token 数」已在 `lab.bundle` 的 note 里。

- [ ] **Step 1: 在 `omp/ch02.md` 第 2.2 节后写一小节**

原创短文，不超过一页：温度改变下一个词元分布的陡峭程度；不固定种子时，两段提示的差异可能来自抽样。点名 `prompt/ch16.md`。不写参考书例题，不写各家词表大小。

- [ ] **Step 2: 在 `prompt/ch16.md` 补公式和四层表**

保留第 10 行「新册模型对照还未运行」和第 162 行对 `unrun-comparison.json` 的解释。增加：验证集默认 28 次的公式；error 与 missing 的差别（本章第 115 行已有，与之一致，不另起矛盾定义）。

- [ ] **Step 3: 检查没有把离线 12/12 写成模型成绩**

Run: `python -m unittest tests.test_prompt_workshop tests.test_prompt_model_run -v`

并阅读 diff，确认没有删除「还未运行」。

- [ ] **Step 4: 提交**

### Task 4: 真实运行的开关仍关着

**Files:**
- Modify: `prompt/VERIFY.md` 只在未来真实摘要落地之后
- Modify: `prompt/evidence/` 下新的摘要文件，仅在同一次真实运行之后

**Interfaces:**
- Consumes: Task 2 写出的本地目录。可提交摘要不含回答正文。

本任务在用户另行书面授权模型与 `max_calls` 之前保持未勾选。授权前不要创建客户端，不要搜索环境里的密钥名。

- [ ] **Step 1: 用户书面给出模型标识、日期、`max_calls` 和 `seed_policy`**
- [ ] **Step 2: 先跑 dry_run，核对计划数不超过 `max_calls`**
- [ ] **Step 3: 才实现或调用真实传输，并把原始响应留在 `.scratch/`**
- [ ] **Step 4: 人按 `criteria.json` 记 pass/fail；传输失败记 error**
- [ ] **Step 5: 若计划数全部有响应且评审齐全，再改 VERIFY 与第 16 章的「还未运行」。否则保持原句，并写明完成了多少槽**

## 本计划现在不做

- 不合并本文件以外的行为变更。
- 不发布、不打标签。
- 不把本计划的勾选当成第 16 章已经有了模型结果。
