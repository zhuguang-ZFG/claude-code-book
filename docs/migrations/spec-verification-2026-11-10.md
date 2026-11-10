# 规格核验记录：P6.4 媒体兼容审阅（2026-11-10）

工作树：`D:/Users/claude/.p64-wt`，分支 `feat/p6-media-acceptance`，起点 `origin/main` 4cedefa。
旧工作树 `claude-code-book-main`（dcdc395）仅作素材来源，未用于提交。
本文件只记录本轮新增验证；历史结论以 2026-11-09 记录为准。

## 1. 真实录音绑定（四种实录布局）

`video/pipeline/voice.py` 的 `recorded_cues` 按序支持四种已发货实录布局，
资产不全一律返回 None 回退估算轨（门禁语义无变化）：

| 章 | 格式 | 布局 | cues | 源 |
|----|------|------|------|----|
| ch01 | long | `vo/timeline.json` + `vo/mp3/<id>.vtt` | 147 | recorded-timeline |
| ch01 | short | `hf-remake/short/assets/short-caps.json` | 24 | recorded-short-caps |
| ch02 | long | `hf-remake/transcript.json` | 378 | recorded-transcript |
| ch02 | short | `short-caps.json` | 14 | recorded-short-caps |
| ch03 | long | `transcript.json` | 359 | recorded-transcript |
| ch03 | short | `short-caps.json` | 18 | recorded-short-caps |
| ch04 | long | `transcript.json` | 294 | recorded-transcript |
| ch04 | short | `short-caps.json` | 16 | recorded-short-caps |
| ch05 | long | `vo/c<NNN>.srt` + 时长偏移合并 | 339 | recorded-chunks |
| ch05 | short | `short-caps.json` | 26 | recorded-short-caps |

审阅要点：

- 各轨末条 cue 结束时刻与声明时长差 ≤ 0.08s（ch05 long 除外：
  实录覆盖 1054.885s，声明 1298.582s；该格式为 scripted、无发货长版，
  缺口为未录段，已如实保留）。
- ch02–ch04 的 `vo/c*.srt` 在发货树中即为 0 字节空文件，真正字幕源是
  `transcript.json`；`recorded_cues` 对此 layouts 优先序为
  timeline+VTT → transcript.json（仅 long）→ c* 合并。
- ch05 脚本（plain 模式）含录音中未念出的标点（「」22 处、/ 4 处、· 2 处），
  已按实录逐块重写 `script-long.txt` 并改 paragraph 模式；
  归一化后 script 与 recorded 逐字一致（4992→4956 字符差异全部为
  录音实际丢弃的标点）。

## 2. 字幕渲染器移植（评审意见 #2）

新增 `video/pipeline/captions.py`：逐字移植发货生成器
（ch01 `build_dense_v4.py` 与 ch02 `build_dense_v1.py` 的
`write_captions`/`write_watermark` 经 diff 核验完全一致），
由录制 cue 轨再生成 `compositions/captions-zh.html` 与
`compositions/watermark.html`，`build` 时写入渲染树。

字节级复现（CRLF 固定写入，与发货文件一致）：

| 章 | 大小 | 结果 |
|----|------|------|
| ch01 | 725,570 B | SHA-256 与发货文件一致（d8d0cc15…） |
| ch02 | 445,725 B | 一致（6282995e…） |
| ch03 | 438,226 B | 一致（13616f16…） |
| ch04 | 331,454 B | 一致（b42e0704…） |

独立渲染直接消费渲染树内的上述文件，因此新版渲染执行的是迁移后的
流水线生成器，而非复制的旧产物。

## 3. 偏差登记（schema_version 2）

`caption-deviations.json` 升级：行内 `kinds: ["chars"|"dwell"]`，
v1 行视为 chars。仅已登记 cue 降为 warning；未登记违规仍 error；
文件格式错 fail-closed。五章记录按录制轨完全枚举：

| 章 | long | short |
|----|------|-------|
| ch01 | 75 chars | 16 dwell |
| ch02 | 112 dwell | 2 dwell |
| ch03 | 108 dwell | 5 dwell + 1 chars |
| ch04 | 103 dwell | 4 dwell |
| ch05 | 27 dwell + 3 chars | 8 dwell |

dwell 偏差是卡拉 OK 逐词替换式字幕的自然属性（短语级 cue），
发货视频即以这些时码烧录；登记只豁免这些已钉住的 cue。

## 4. 字幕对照（legacy captions vs 当前 transcript）

`bookctl video compare` 全部 9 条已发货轨：**captions 全部 match**
（条数与逐条文字/时码全等，0 mismatches）：

- ch01 long：147 vs 147（legacy 见证 `ch01-long.srt`）
- ch02–ch04 long：378/359/294（legacy 见证由发货 `transcript.json` 转 SRT）
- ch01–ch05 short：24/14/18/16/26（legacy 见证由发货 `short-caps.json` 转 VTT）
- ch05 long 无发货视频（scripted），不参与媒体对照。

报告：`.scratch/p64/<ch>-<fmt>-compare.json`。

## 5. 时长与关键帧对照

待 9 个独立新版渲染完成后回填：

- ch01 long（渲染中）、ch01/02/03/04 short、ch02/03/04 long、ch05 short。
- 旧版见证视频：各章 `out/` 下发货 mp4（ch01-long 1148.3667s、
  ch02-long-v1、ch03-long-v1/v2、ch04-long-v1/v2、各 short-v*）。
- ch01 旧版见证选型：`ch01-long.mp4`（1148.3667s，与声明时长
  1148.352s 差 0.015s，容差内）；v4 版（约 1171s）非声明时长，不选。

## 6. 构建与测试

- `build --assets`：ch01–ch05 全部通过（真实录音 + 偏差登记）。
- 视频专项测试 59 项通过（新增四种布局绑定、CRLF 字节见证、
  dwell/chars kinds 隔离、短版 caps 回归）。
- 全仓两套件 238 + 570 项通过（渲染排队期间复跑）。
- `bookctl check --fast`：进行中。
