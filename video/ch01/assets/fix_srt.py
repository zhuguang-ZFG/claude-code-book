import re, json
from pathlib import Path

mp3_dir = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\mp3")
out_dir = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\out")
timeline = json.loads(Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\timeline.json").read_text(encoding="utf-8"))
by_id = {t["id"]: t for t in timeline}

def parse_vtt(path: Path):
    text = path.read_text(encoding="utf-8")
    cues = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for b in blocks:
        lines = [x for x in b.splitlines() if x.strip() and not x.startswith("WEBVTT")]
        # drop cue index lines that are only digits
        lines = [x for x in lines if not re.fullmatch(r"\d+", x.strip())]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})", lines[0])
        if not m:
            continue
        cues.append((m.group(1).replace(",", "."), m.group(2).replace(",", "."), " ".join(lines[1:]).strip()))
    return cues

def ts_to_sec(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def sec_to_srt(t: float) -> str:
    if t < 0: t = 0
    h = int(t // 3600); t -= h * 3600
    m = int(t // 60); t -= m * 60
    s = int(t); ms = int(round((t - s) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

items = []
idx = 1
for t in timeline:
    vtt = mp3_dir / f"{t['id']}.vtt"
    for a, b, txt in parse_vtt(vtt):
        s = t["start"] + ts_to_sec(a)
        e = t["start"] + ts_to_sec(b)
        items.append((idx, s, e, txt))
        idx += 1

srt_path = out_dir / "ch01-long.srt"
with srt_path.open("w", encoding="utf-8") as fh:
    for i, s, e, txt in items:
        fh.write(f"{i}\n{sec_to_srt(s)} --> {sec_to_srt(e)}\n{txt}\n\n")
print(f"SRT_CUES={len(items)} path={srt_path}")
