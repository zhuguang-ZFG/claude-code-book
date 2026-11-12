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

| 章 | 长版大小 | 结果 |
|----|------|------|
| ch01 | 725,570 B | SHA-256 与发货文件一致（d8d0cc15…） |
| ch02 | 445,725 B | 一致（6282995e…） |
| ch03 | 438,226 B | 一致（13616f16…） |
| ch04 | 331,454 B | 一致（b42e0704…） |

短版字幕页有三个发货变体，全部移植并逐字节验证（`short_captions_html`
v1=ch01、`short_captions_v2_html`=ch02–04、`short_captions_ch05_html`）：

| 章 | 短版大小 | 结果 |
|----|------|------|
| ch01 | 7,657 B | 一致（8d6cf570…） |
| ch02 | 4,543 B | 一致（5e0d6bfb…） |
| ch03 | 5,552 B | 一致（5c5f5440…） |
| ch04 | 5,011 B | 一致（2e0851d9…） |
| ch05 | 7,448 B | 一致（613061e2…） |

**消费链证明**：删除五章全部 `compositions/captions-zh.html`、
`compositions/watermark.html`、`short/compositions/captions-zh.html`
后执行 `build --assets`，上述文件全部由流水线从录制 cue 轨重新生成，
SHA-256 与发货见证一致。独立渲染消费的即这些生成物。

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
- ch02–ch04 long：378/359/294（legacy 见证由发货 `transcript.json` 转 SRT；该文件
  2026-11-12 从标签 `legacy/pre-platform-2026-11-03` 恢复到工作树，按本地录制媒体
  由 `.gitignore` 排除）
- ch01–ch05 short：24/14/18/16/26（legacy 见证由发货 `short-caps.json` 转 SRT）
- ch05 long 无发货视频（scripted），不参与媒体对照。

报告：`video/.build/<ch>/compare-<fmt>.json`。早期记录写的是 `.scratch/p64/`，
那是临时工位，2026-11-12 重跑后改落到 `.build/` 并沿用至今。

## 5. 时长与关键帧对照

2026-11-12 完成：9 条发货轨全部以钉住的 HyperFrames 0.8.210 独立重渲，并做时间线、
字幕、时长、关键帧四类对照。严格哈希不同只说明字节不同——发货片用 `-q looks` 一类
档位，本次统一 `-q standard`，判定见「关键帧与允许差异」；三个采样点的 PSNR 只是
描述，全片逐帧 PSNR 才是整片度量。

| 轨道 | 见证片（`out/`） | 新片 帧数 / 字节 | 时长 新片 = 见证（声明） | 字幕 | 严格哈希 | 三点 PSNR | 全片 PSNR avg / min |
|---|---|---|---|---|---|---|---|
| ch01 长 | `ch01-long-v4.mp4` 205 205 029 B | 34 451 / 165 976 823 B | 1148.3667 = 1148.3667（1148.352） | 147 = 147 | 0/3 | 45.14–46.82 dB | 51.33 / 47.64 dB |
| ch01 短 | `ch01-short.mp4` 5 311 073 B | 979 / 5 304 056 B | 32.6333 = 32.6333 | 24 = 24 | 2/3 | 49.65 dB（1 点不同） | 61.95 / 53.06 dB |
| ch02 短 | `ch02-short-v3.mp4` | 1 031 / 6 400 358 B | 34.367 = 34.367（34.352） | 14 = 14 | 0/3 | 45.02–46.17 dB | 51.20 / 48.80 dB |
| ch02 长 | `ch02-long-v1.mp4` 100 082 335 B | 18 829 / 78 899 832 B | 627.633 = 627.633（627.624） | 378 = 378 | 0/3 | 43.30–43.86 dB | 48.52 / 42.66 dB |
| ch03 短 | `ch03-short-v1.mp4` | 1 384 / 7 433 765 B | 46.133 = 46.133（46.112） | 18 = 18 | 0/3 | 48.29–48.36 dB | 53.15 / 50.38 dB |
| ch03 长 | `ch03-long-v2.mp4` | 17 911 / 127 384 986 B | 597.033 = 597.033（597.024） | 359 = 359 | 0/3 | 45.29–53.20 dB | 51.99 / 47.71 dB |
| ch04 短 | `ch04-short-v1.mp4` | 1 164 / 6 681 806 B | 38.800 = 38.800（38.792） | 16 = 16 | 0/3 | 46.87–48.95 dB | 52.89 / 49.12 dB |
| ch04 长 | `ch04-long-v2.mp4` | 13 592 / 111 829 930 B | 453.067 = 453.067（453.048） | 294 = 294 | 0/3 | 44.46–58.94 dB | 52.59 / 47.44 dB |
| ch05 短 | `ch05-short-v1.mp4` | 1 529 / 8 621 895 B | 50.967 = 50.967（50.936） | 26 = 26 | 0/3 | 47.71–48.35 dB | 53.23 / 49.81 dB |

ch05 长版在 `video/chapters/ch05/episode.yaml` 是 `status: scripted`，没有发货片，不参与
对照。9 条轨道的字幕逐条文字与时码全等、时长与见证片精确相等、与声明值差 ≤0.031 s；
时间线全部 `match`（ch01 另见 `compat-report.json`）。全片逐帧 PSNR 覆盖每一帧，
最小帧 42.66 dB，属于重编码级差异。

旧版见证视频在各章 `out/` 下；ch01 旧版见证选型：`ch01-long.mp4`（1148.3667s，与声明
时长 1148.352s 差 0.015s，容差内）；v4 版实测 34 451 帧 / 1148.3667 s，与
`ch01-long.mp4` 同长，是源定稿后渲染的最新见证，故用 v4。

## 6. 构建与测试

- `build --assets`：ch01–ch05 全部通过（真实录音 + 偏差登记）。
- 视频专项测试 59 项通过（新增四种布局绑定、CRLF 字节见证、
  dwell/chars kinds 隔离、短版 caps 回归）。
- 全仓两套件 280 + 585 项通过（2026-11-12 复跑）。
- `bookctl check --fast`：2026-11-12 实测 8 步全绿（content 428 个 Markdown /
  436 张 Mermaid 图 0 错误，视频配置 15/15，产物幂等 11 项逐字节一致）。
- `iter_doc()` 的注释扫描原本对每个分块重扫文档余部，属 O(n²)：1.08 MB 的 opencode 分册
  要 16.4 s、5.78 MB 的主书 381 s、60.35 MB 的 omp 564 s。改为记住下一个 `<!--` 的
  位置后，同一批文本分别 0.09 s / 0.55 s / 4.13 s，1500 例随机畸形文档与旧实现分块
  逐字节相同；回归用例在 `tests/test_render_anchors.py::CommentWalk`，用旧实现在同一
  文档上要 75.7 s，用例上限 3 s。合订本因此在 86 s 内完成（72.5 MB、9 卷 228 单元
  308 图版），此前 840 s / 865 s 两次都跑不完。
