# -*- coding: utf-8 -*-
"""Render full VO with locked YunyangNeural settings + per-chunk SRT."""
from __future__ import annotations
import asyncio, json, re, subprocess, sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[4]  # .../claude-code-book-main
# build -> assets -> ch01 -> video -> repo  => parents[4]
BUILD = Path(__file__).resolve().parent
CHUNKS = BUILD / "chunks.json"
VO_DIR = BUILD.parent / "vo"
VOICE = "zh-CN-YunyangNeural"
RATE = "-10%"
PITCH = "-5Hz"

def ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

async def synth_one(text: str, mp3: Path, vtt: Path):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    submaker = edge_tts.SubMaker()
    with open(mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
    # write vtt via SubMaker
    vtt.write_text(submaker.get_srt(), encoding="utf-8")

def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip()
    return float(out)

async def main():
    VO_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(CHUNKS.read_text(encoding="utf-8"))
    chunks = data["chunks"]
    timeline = []
    t = 0.0
    for i, c in enumerate(chunks):
        cid = c["id"]
        mp3 = VO_DIR / f"{cid}.mp3"
        srt = VO_DIR / f"{cid}.srt"
        txt = VO_DIR / f"{cid}.txt"
        txt.write_text(c["text"], encoding="utf-8")
        print(f"[{i+1}/{len(chunks)}] {cid} slide={c['slide']} hanzi={c['hanzi']}")
        # retry up to 3
        for attempt in range(3):
            try:
                await synth_one(c["text"], mp3, srt)
                if mp3.stat().st_size < 500:
                    raise RuntimeError("mp3 too small")
                break
            except Exception as e:
                print("  retry", attempt, e)
                await asyncio.sleep(1.5)
        else:
            raise SystemExit(f"failed TTS for {cid}")
        dur = probe_duration(mp3)
        timeline.append({
            "id": cid,
            "slide": c["slide"],
            "text": c["text"],
            "hanzi": c["hanzi"],
            "mp3": str(mp3),
            "srt": str(srt),
            "start": t,
            "duration": dur,
            "end": t + dur,
        })
        t += dur
        print(f"  dur={dur:.2f}s total={t:.1f}s")

    # concat audio
    list_file = VO_DIR / "concat.txt"
    with list_file.open("w", encoding="utf-8") as f:
        for item in timeline:
            # ffmpeg concat demuxer needs forward slashes / escaped
            p = Path(item["mp3"]).resolve().as_posix().replace("'", "'\\''")
            f.write(f"file '{p}'\n")
    full_mp3 = VO_DIR / "full.mp3"
    subprocess.check_call([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(full_mp3)
    ])
    full_dur = probe_duration(full_mp3)

    # merged SRT with absolute times
    srt_lines = []
    idx = 1
    for item in timeline:
        # parse per-chunk srt and shift
        raw = Path(item["srt"]).read_text(encoding="utf-8").strip()
        if not raw:
            # fallback one cue for whole chunk
            srt_lines.append(f"{idx}\n{ts(item['start'])} --> {ts(item['end'])}\n{item['text']}\n")
            idx += 1
            continue
        blocks = re.split(r"\n\s*\n", raw)
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) < 2:
                continue
            # find timing line
            timing_i = 0
            if re.match(r"^\d+$", lines[0].strip()):
                timing_i = 1
            if timing_i >= len(lines):
                continue
            timing = lines[timing_i]
            m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", timing)
            if not m:
                continue
            def to_sec(h, m_, s, ms):
                return int(h) * 3600 + int(m_) * 60 + int(s) + int(ms) / 1000.0
            a = to_sec(*m.groups()[:4]) + item["start"]
            b = to_sec(*m.groups()[4:]) + item["start"]
            text = "\n".join(lines[timing_i + 1:]).strip()
            if not text:
                continue
            srt_lines.append(f"{idx}\n{ts(a)} --> {ts(b)}\n{text}\n")
            idx += 1

    meta = {
        "voice": VOICE,
        "rate": RATE,
        "pitch": PITCH,
        "full_mp3": str(full_mp3),
        "full_duration": full_dur,
        "timeline": timeline,
    }
    (BUILD / "timeline.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (BUILD / "merged.srt").write_text("\n".join(srt_lines) + "\n", encoding="utf-8")
    print(f"FULL duration={full_dur:.2f}s cues={idx-1}")

if __name__ == "__main__":
    asyncio.run(main())
