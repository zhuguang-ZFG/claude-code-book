import json, re, subprocess
from pathlib import Path

mp3_dir = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\mp3")
out_dir = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\out")
assets = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets")
out_dir.mkdir(parents=True, exist_ok=True)

def dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def parse_vtt(path: Path):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    cues = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for b in blocks:
        lines = [x for x in b.splitlines() if x.strip() and not x.startswith("WEBVTT") and not x.strip().isdigit()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})", lines[0])
        if not m:
            continue
        cues.append((m.group(1), m.group(2), " ".join(lines[1:])))
    return cues

def ts_to_sec(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def sec_to_srt(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600); t -= h * 3600
    m = int(t // 60); t -= m * 60
    s = int(t); ms = int(round((t - s) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

files = sorted(mp3_dir.glob("*.mp3"))
timeline = []
offset = 0.0
srt_items = []
idx = 1
# Windows ffmpeg concat needs escaped paths; use absolute with forward slashes
concat_lines = []
for f in files:
    d = dur(f)
    timeline.append({"id": f.stem, "file": str(f), "start": round(offset, 3), "duration": round(d, 3)})
    for a, b, txt in parse_vtt(f.with_suffix(".vtt")):
        s = offset + ts_to_sec(a)
        e = offset + ts_to_sec(b)
        srt_items.append((idx, s, e, txt))
        idx += 1
    # ffmpeg concat demuxer on Windows prefers single quotes carefully; use path as-is with forward slash
    p = str(f).replace("\\", "/")
    concat_lines.append(f"file '{p}'")
    offset += d

(assets / "vo" / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
concat_path = assets / "vo" / "concat.txt"
concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
srt_path = out_dir / "ch01-long.srt"
with srt_path.open("w", encoding="utf-8") as fh:
    for i, s, e, txt in srt_items:
        fh.write(f"{i}\n{sec_to_srt(s)} --> {sec_to_srt(e)}\n{txt}\n\n")

full_mp3 = assets / "vo" / "full.mp3"
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(concat_path),
    "-c", "copy", str(full_mp3),
], check=True)
print(f"TOTAL_DURATION={offset:.3f}")
print(f"SEGMENTS={len(files)}")
print(f"SRT_CUES={len(srt_items)}")
