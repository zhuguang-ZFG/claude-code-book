# ch01–ch05 迁移对照审阅记录

对应计划 P6.4 / P6 Gate，以及规格 7.5「ch01–ch05 迁移后画面、字幕和时长允许的差异有审阅记录」。记录日期 2026-11-07，对照基线标签 `legacy/pre-platform-2026-11-03`；2026-11-12 补入独立新版渲染与关键帧实测。

## 结论

| 项目 | 结果 | 判定 |
|---|---|---|
| 时间线 | `ch01/compat-report.json` 的长版、短版均为 `match` | 通过 |
| 尺寸 / fps | 1920×1080 / 1080×1920，30 fps，与旧 `index.html` 一致 | 通过 |
| 时长 | 实测新版长版 1148.3667 s / 34 451 帧，短版 32.6333 s / 979 帧，与旧片逐帧同长 | 通过 |
| 字幕文本 | 归一化后 5021 字完全一致，相似度 1.0 | 通过 |
| 字幕切分 | 旧 147 条，当前 147 条，逐条文字与时码全等（`compare` 报 0 mismatches） | 通过 |
| 短版字幕 | ch01–ch05 录制轨 24/14/18/16/26 条；ch01 字幕页字节与发货见证一致（`8d6cf570…`） | 通过 |
| 画面来源 | ch01–ch05 的 115 个已跟踪渲染输入与基线逐字节一致（仅换行符归一）；0 个修改 | 通过 |
| 独立新版渲染 | 9 条发货轨全部重渲：ch01–ch04 长版与 ch01–ch05 短版；ch05 长版为 scripted 态，无发货片 | 已产出（2026-11-12） |
| 关键帧 | 严格 PNG 哈希：仅 ch01 短版 2/3 相同，其余 8 条 0/3；不同点 PSNR 43.3–58.9 dB（每次三个采样帧） | 允许差异（已记录，不声明全片等价） |
| 全片度量 | 9 条轨道全部做了逐帧 PSNR（979–34 451 帧不等），各片最小帧 42.66–53.06 dB | 重编码级 |
| 音频 / 成片质量 | AAC 48 kHz 立体声，码率与旧片相差 <0.1 kbps；未做人工审听与主观画质评审 | 仍然 unverified |

## 字幕比较

旧字幕只存在于本机工作树，不在基线标签里：`git ls-tree -r legacy/pre-platform-2026-11-03`
没有任何 `.srt`/`.vtt`，`git show legacy/pre-platform-2026-11-03:video/ch01/assets/build/merged.srt`
返回路径不存在。本机有两份 147 条旧长片字幕，归一化文本相同（5021 字）：
`video/ch01/assets/build/merged.srt`（SHA-256 `2323f9ccaca6dc63dd118465c4716b7d8e8096de6a103ded287d0a51629e98d0`，
末条止于 1147.516 s）与 `video/ch01/out/ch01-long.srt`（与 `hf-remake/ch01-long.srt` 同一文件，
SHA-256 `939f05388113f4d5c106c335142745baf7fc6cc9a73f65439ce74026420352f4`，末条止于
1148.284 s）。2026-11-11 的关键帧比较采用与旧片同批产出的 `out/ch01-long.srt` 作见证。
两份字幕都未入库，本记录保存的是审阅时的 SHA-256。

复现命令（`LEGACY_SRT` 指向本机任一份 147 条旧长片字幕；两份文本相同）：

```bash
export LEGACY_SRT=video/ch01/out/ch01-long.srt
python - <<'PY'
import os
import sys
from pathlib import Path
sys.path.insert(0, "video")
from pipeline import model, timeline, voice

chapter = Path("video/chapters/ch01")
episode = model.read_yaml(chapter / "episode.yaml")
current = voice.cues(
    episode, chapter, "long",
    total_s=episode["formats"]["long"]["duration_s"],
    audio_path=chapter / "full.mp3",
)
legacy = timeline.parse_captions(Path(os.environ["LEGACY_SRT"]))
left = voice.normalized("".join(cue["text"] for cue in legacy))
right = voice.normalized("".join(cue["text"] for cue in current))
print(len(legacy), len(current), len(left), len(right), left == right)
PY
```

结果：`147 147 5021 5021 True`（2026-11-12 复测；cue 源为 `recorded-timeline`）。
2026-11-07 首次审阅时同一命令输出 `147 389`：当时本机只有旧 chunk 布局
`assets/vo/c*.srt`，合并出 389 条 cue 并触发重新切分。2026-11-11 本机媒体对齐到
`vo/timeline.json` + `vo/mp3/<id>.vtt` 布局后，当前轨与旧片字幕同为 147 条，
`bookctl video compare` 对逐条文字和时码报 `match`、0 mismatches，不再存在切分
差异。渲染时字幕由同一条录制轨生成（`compositions/captions-zh.html`，725 570 B，
SHA-256 `d8d0cc15…`，与发货见证一致），不存在维护两份文本。

## 短版录制字幕（2026-11-12 恢复）

P6 导入提交 `dcf16c8` 把五章的 `hf-remake/short/assets/short-caps.json` 一并删除，
工作树的短版 cue 轨随后退回 `estimated`：`ch01` 只剩 10 条、起点 0.0，与旧片
24 条（起点 5.1）无法对齐，2026-11-12 的首轮短版比较报 `24 legacy cues != 10`。
基线标签仍保留五份录制文件，本次从 `legacy/pre-platform-2026-11-03` 恢复到
工作树；按「不提交中间媒体」的策略保持未跟踪，`.gitignore` 与
`assets/vo/timeline.json` 同处处理。

| 章节 | cue 数 | 末条止于 | 声明时长 | 差值 |
|---|---|---|---|---|
| ch01 | 24 | 32.556 s | 32.624 s | 0.068 s |
| ch02 | 14 | 34.292 s | 34.352 s | 0.060 s |
| ch03 | 18 | 46.056 s | 46.112 s | 0.056 s |
| ch04 | 16 | 38.722 s | 38.792 s | 0.070 s |
| ch05 | 26 | 50.881 s | 50.936 s | 0.055 s |

恢复后 `build --assets --chapter ch01` 重建的字幕页 7 657 B、SHA-256
`8d6cf570…`，与发货见证一致；`tests/test_video_pipeline.py` 的
`test_shipped_short_captions_match_witness_hashes` 由跳过变为实际比对并通过。

## 画面比较

已跟踪的渲染输入（`index.html`、`compositions/`、组件、`hyperframes*.json`、
`meta.json` 与 `assets/huashu-specs/*.json`）在 ch01–ch05 共 115 个文件上与基线
标签逐字节一致；比较前把 CRLF 归一为 LF，结果 0 个修改、0 个删除。五个
`short/compositions/dense-short.html` 是旧构建脚本的本机生成物，被 `.gitignore`
排除，从未进入 Git；它们不参与这项比较。

这意味着长版画面由与迁移前相同的输入文件渲染。短片的差异仅限这五个本机
生成场景，不来自对旧场景源的改写。

复现命令：

```bash
python - <<'PY'
import subprocess
from pathlib import Path

tag = "legacy/pre-platform-2026-11-03"
same = modified = 0
for number in range(1, 6):
    base = Path("video") / f"ch{number:02d}" / "hf-remake"
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix not in {".html", ".css", ".js", ".json"}:
            continue
        old = subprocess.run(["git", "show", f"{tag}:{path.as_posix()}"],
                             capture_output=True).stdout
        if not old:
            continue
        if old.replace(b"\r\n", b"\n") == path.read_bytes().replace(b"\r\n", b"\n"):
            same += 1
        else:
            modified += 1
print(same, modified)
PY
```

结果：`115 0`。

## 独立新版渲染（2026-11-12）

两版都用钉住的 HyperFrames 0.8.210 渲染，命令行与产物如下。长版启用分段捕获
（每段 3 000 帧，共 12 段）并在中断后 `--resume` 复用已验证段：本机先后两次
被外部挂断（`render_cancelled_by_sighup`，帧 225 与 9 904），第三次从第 3 段
续跑至完成。成品随后用 ffprobe 复核，帧数、时长、尺寸与下表一致。

| | 长版 | 短版 |
|---|---|---|
| 工程目录 | `video/ch01/hf-remake` | `video/ch01/hf-remake/short` |
| 命令 | `render . -f 30 -q standard -w 1 --low-memory-mode` | 同左 |
| 产物 | `video/.build/ch01/current-long.mp4` | `video/.build/ch01/current-short.mp4` |
| 大小 | 165 976 823 B | 5 304 056 B |
| 尺寸 / fps | 1920×1080 / 30 | 1080×1920 / 30 |
| 帧数 / 时长 | 34 451 / 1148.3667 s | 979 / 32.6333 s |
| 音频 | AAC 48 kHz 立体声 185.4 kbps | AAC 48 kHz 立体声 |
| 对比报告 | `video/.build/ch01/compare-long.json` | `video/.build/ch01/compare-short.json` |

### ch02–ch05 短版（2026-11-12 复现渲染）

同一命令在四章的 `short/` 工程重跑，产物落到各自 `video/.build/<ch>/`。四片都用
`--quality standard`；发货记录里 ch05 写明用 `--quality looks`
（`docs/video/ch05/STATUS.md`），编码参数不同本身就会改变字节，所以严格哈希不同
不能当作画面漂移的证据，下表同时给出三个采样点的 PSNR。

| 章节 | 见证片（`out/`） | 新片大小 / 帧数 | 时长 新旧（声明） | 字幕 | 严格哈希 | 三点 PSNR / 平均绝对差 | 全片逐帧 PSNR（avg / min） |
|---|---|---|---|---|---|---|---|
| ch02 | `ch02-short-v3.mp4` | 6 400 358 B / 1 031 | 34.367 = 34.367（34.352） | 14 = 14，0 差异 | 0/3 | 45.02–46.17 dB / 0.65–0.77 | 51.20 / 48.80 dB |
| ch03 | `ch03-short-v1.mp4` | 7 433 765 B / 1 384 | 46.133 = 46.133（46.112） | 18 = 18，0 差异 | 0/3 | 48.29–48.36 dB / 0.34–0.44 | 53.15 / 50.38 dB |
| ch04 | `ch04-short-v1.mp4` | 6 681 806 B / 1 164 | 38.800 = 38.800（38.792） | 16 = 16，0 差异 | 0/3 | 46.87–48.95 dB / 0.41–0.55 | 52.89 / 49.12 dB |
| ch05 | `ch05-short-v1.mp4` | 8 621 895 B / 1 529 | 50.967 = 50.967（50.936） | 26 = 26，0 差异 | 0/3 | 47.71–48.35 dB / 0.45–0.48 | 53.23 / 49.81 dB |

报告在 `video/.build/<ch>/compare-short.json`。四片的字幕轨都来自发货录制文件
`short-caps.json`（本地媒体，按 `.gitignore` 不入库），当前流水线按同一时码重建，
逐条文字与时码全等；新片时长与发货片精确相等，与 `episode.yaml` 的声明值差
≤0.031 s。

见证片按声明时长选定：`ch02` 的 v1/v2 只有 30.9/31.3 s，与声明 34.352 s 不符，
v3（34.367 s）才是发货片，与 `docs/video/ch02/short-script.md` 的记载一致；
ch03–ch05 各只有一个短版。ch01 的短版见证仍是 `ch01-short.mp4`，见上一张表；
它全片 979 帧逐帧 PSNR 为 61.95 / 53.06 dB（avg / min）。

全片一列用 `ffmpeg -lavfi "[0:v][1:v]psnr"` 覆盖两片的每一帧（帧数逐片相等：
979/1 031/1 384/1 164/1 529），是 yuv420p 三平面平均、与三点采样的 RGB 口径不同，
不能与本表的采样值直接比大小。它把「三个采样点」升级为整片度量：五片整片最小
帧 PSNR 也有 48.8 dB，与重编码一致。

### 长版（ch02–ch04，2026-11-12 复现渲染）

同一命令在长版工程重跑，产物落在各自 `video/.build/<ch>/current-long.mp4`，用
`bookctl video compare` 与 `out/` 里的发货见证片对表。见证片按声明时长选定：
ch02 用 `ch02-long-v1.mp4`（v2/v3 均短于声明值），ch03 用 `ch03-long-v2.mp4`，
ch04 用 `ch04-long-v2.mp4`。

| 章节 | 见证片 | 新片大小 / 帧数 | 时长 新旧（声明） | 字幕 | 严格哈希 | 三点 PSNR / 平均绝对差 | 全片逐帧 PSNR（avg / min） |
|---|---|---|---|---|---|---|---|
| ch02 | `ch02-long-v1.mp4` 100 082 335 B | 78 899 832 B / 18 829 | 627.633 = 627.633（627.624） | 378 = 378，0 差异 | 0/3 | 43.30–43.86 dB / 1.06–1.11 | 48.52 / 42.66 dB |
| ch03 | `ch03-long-v2.mp4` | 127 384 986 B / 17 911 | 597.033 = 597.033（597.024） | 359 = 359，0 差异 | 0/3 | 45.29–53.20 dB / 0.11–0.90 | 51.99 / 47.71 dB |
| ch04 | `ch04-long-v2.mp4` | 111 829 930 B / 13 592 | 453.067 = 453.067（453.048） | 294 = 294，0 差异 | 0/3 | 44.46–58.94 dB / 0.04–1.01 | 52.59 / 47.44 dB |

报告在 `video/.build/<ch>/compare-long.json`。三片的时间线都 `match`、零处不一致，
字幕逐条与时码全等，新片时长与发货片精确相等、与 `episode.yaml` 的声明值差
≤0.019 s。关键帧严格哈希全部不同：这与短片同源——发货片按 `-q looks` 一类档位
编码，本次统一 `-q standard`，字节差异不等于画面漂移；PSNR 与平均绝对差落在重编码
区间，全片逐帧最小帧也有 42.7 dB。ch04 的第二次采样点 58.94 dB、平均绝对差 0.04
是全片最接近的一帧，说明差异集中在编码细节而不是某段画面缺失。


ch02 的体积差最大：见证 100 082 335 B，新片 78 899 832 B。同一输入、同一帧数下，
体积差来自编码质量档，因此记「允许差异」，不声明逐字节等价。

## 关键帧与允许差异

`timeline.keyframe_report()` 只比较两个真实视频文件：在 10%、50%、90% 三处抽取
解码帧的 PNG 字节并比对 SHA-256；缺片或抽帧失败返回 `unverified`，不会伪造相同。
本仓库和基线标签仍不含视频，旧片只在本机 `video/ch01/out/`；本记录保存的是本次
实测结果。

见证片选择（修正 2026-11-10 记录）：

- 长版用 `ch01-long-v4.mp4`。它是最后一次源修改（2026-10-28 18:22）之后的渲染
  （19:31–20:41 捕获）。2026-11-10 记录称「v4 约 1171 s、非声明时长」有误：
  实测 34 451 帧、1148.3667 s。更早的 `ch01-long.mp4`（15:36）与 v3（17:39）
  都早于源文件定稿，属于不同剪法，只作旁证。
- 短版用 `ch01-short.mp4`。它由流水线绑定的 `short/index.html` 渲染；`short-v2/`
  与 `short-v3/` 是本机另两个独立工程，各自有 `dense-short-v2/v3.html` 和字幕页，
  不是当前流水线渲染的对象。此前用 `ch01-short-v3.mp4` 作短版见证属于比错工程。

实测（采样点同时刻）：

| 对比 | 10% | 50% | 90% |
|---|---|---|---|
| 新版长版 ↔ v4（PSNR / 平均绝对差） | 45.14 dB / 0.92 | 46.40 dB / 0.71 | 46.82 dB / 0.67 |
| 新版短版 ↔ v1（PSNR / 平均绝对差） | 完全一致（0.00） | 完全一致（0.00） | 49.65 dB / 0.31 |
| 旁证：新版长版 ↔ `ch01-long.mp4` | 17.96 dB / 16.03 | 17.95 dB / 16.02 | 19.05 dB / 14.17 |
| 旁证：新版长版 ↔ v3 | 20.72 dB / 4.26 | 20.93 dB / 4.05 | 20.86 dB / 5.66 |
| 旁证：新版短版 ↔ v3 | 23.69 dB / 2.64 | 15.66 dB / 14.5 | 7.70 dB / 63.3 |

结论：三处采样点的差异都很小（长版 45–47 dB；短版两点逐字节相同，一点 49.65 dB），
与同一内容重编码的表现相符。采样只有三帧，不能据此断言整片内容等价，也不能证明
差异仅来自编码；旁证对更早剪法的低 PSNR 只说明那几版画面不同，与本次迁移无关。
严格哈希仍按原规则判 `different`，不放宽阈值。

复现（先按上表路径生成两版渲染，再执行）：

```bash
python video/pipeline/cli.py compare --chapter ch01 --format long \
  --legacy-captions video/ch01/out/ch01-long.srt \
  --current-captions video/.build/ch01/transcript-long.json \
  --legacy-video video/ch01/out/ch01-long-v4.mp4 \
  --current-video video/.build/ch01/current-long.mp4 \
  --report video/.build/ch01/compare-long.json

python video/pipeline/cli.py compare --chapter ch01 --format short \
  --legacy-captions video/.build/ch01/legacy-short-captions.srt \
  --current-captions video/.build/ch01/transcript-short.json \
  --legacy-video video/ch01/out/ch01-short.mp4 \
  --current-video video/.build/ch01/current-short.mp4 \
  --report video/.build/ch01/compare-short.json
```

PSNR 复核（按 `compare` 报告里的三个 `*_at_s` 采样点取帧）：

```bash
python - <<'PY'
import subprocess
import numpy as np
from PIL import Image

def frame(path, at, out):
    subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ss", f"{at:.3f}",
                    "-frames:v", "1", "-y", out], check=True)
    return np.asarray(Image.open(out).convert("RGB")).astype(np.int16)

for at in (114.84, 574.18, 1033.53):
    old = frame("video/ch01/out/ch01-long-v4.mp4", at, "old.png")
    new = frame("video/.build/ch01/current-long.mp4", at, "new.png")
    diff = np.abs(old - new)
    mse = (diff.astype(float) ** 2).mean()
    print(at, round(10 * np.log10(255 ** 2 / mse), 2), round(float(diff.mean()), 2))
PY
```

## ch02–ch05 补充审阅

长版时间线、尺寸、fps、时长和音频时长在 `compat-report.json` 中均为 `match`；
画面来源按上一节同一比较脚本覆盖，115 个已跟踪输入 0 修改。

| 章节 | chunk SRT 见证 | 发货 `transcript.json` 见证 | 结果 |
|---|---|---|---|
| ch02 | `assets/vo/c*.srt` 31 个，全部 0 字节 | 378 条 | 378 = 378，0 差异 |
| ch03 | `assets/vo/c*.srt` 31 个，全部 0 字节 | 359 条 | 359 = 359，0 差异 |
| ch04 | `assets/vo/c*.srt` 24 个，全部 0 字节 | 294 条 | 294 = 294，0 差异 |
| ch05 | `assets/vo/c*.srt` 53 个，339 条 cue | 无（`status: scripted`，无发货片） | 归一化后 4 956 字与当前一致；仅 `「」`、`/`、`·` 标点差异 |

ch02–ch04 的 chunk SRT 是 0 字节的中间产物，本身不能作字幕见证。2026-11-12 从标签
`legacy/pre-platform-2026-11-03` 恢复的发货 `transcript.json` 才是长版字幕的真实见证：
当前流水线走 `recorded-transcript` 路径重建，条数与逐条文字/时码全等，见各章
`video/.build/<ch>/compare-long.json` 的 `captions` 段。ch05 的 chunk SRT 可读，
差异只在旧 SRT 省略了引号、斜杠与间隔号，文本没有增删。这些文件都是本机媒体，
从未进入 Git；记录保存的是本机实测结果，不把它伪装成干净克隆可复现的证据。

允许差异清单：

1. ch01 字幕切分：旧记录中的「147 条 → 389 条」来自已退役的 chunk 布局；对齐到
   `vo/timeline.json` + VTT 布局后两侧同为 147 条并逐条 `match`，此条差异已消失。
2. ch05 字幕标点：旧 SRT 省略 `「」`、`/`、`·`，归一化后文本相同。
3. ch02–ch04 字幕：chunk SRT 为 0 字节，改用发货 `transcript.json` 作见证，
   378/359/294 条逐条全等，切分差异不存在；人工审听仍未做。
4. 短片画面：五个 `dense-short.html` 本机生成物未入库，迁移后不再依赖旧脚本生成；
   长版画面输入不变。
5. 关键帧严格哈希：9 条轨道里只有 ch01 短版的第 3 点相同（2/3），其余 8 条 0/3；
   不同点的三点 PSNR 43.3–58.9 dB。采样本身不覆盖整片，因此另做逐帧 PSNR：
   9 条轨道全部覆盖每一帧，最小帧 42.66 dB。两项都指向编码档差异，仍不声明全片等价。
6. 渲染质量与音频：已产出独立新版渲染并记录帧级差异；未做人工审听与主观画质
   评审，音频与观感仍 unverified，发布声明不得写成已验证。
