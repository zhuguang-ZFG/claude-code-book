# -*- coding: utf-8 -*-
"""Assemble ch01-long.mp4 from slides + VO timeline."""
from __future__ import annotations
import json, subprocess, shutil
from pathlib import Path

BUILD = Path(__file__).resolve().parent
ASSETS = BUILD.parent
SLIDES = ASSETS / "slides"
ANIM = ASSETS / "anim"
OUT = ASSETS.parent / "out"
VO = ASSETS / "vo"

ANIM_MAP = {
    "chatbot-glue": ("chatbot-glue_", 24, 8),      # prefix, count, fps
    "scale-1884-512664": ("scale_", 30, 10),
    "principles": ("principles_", 25, 5),
    "one-tool-call": ("toolcall_", 24, 6),
    # also map principle-* to static; doctor-flow static is fine
}

def probe(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip())

def slide_for(key: str) -> Path:
    p = SLIDES / f"{key}.png"
    if p.exists():
        return p
    # fallbacks
    for alt in ("open", "paradigm", "architecture", "principles", "practice", "outro"):
        q = SLIDES / f"{alt}.png"
        if q.exists():
            return q
    raise FileNotFoundError(key)

def make_segment(idx: int, item: dict, seg_dir: Path) -> Path:
    """Create a video segment matching audio duration for one chunk."""
    slide_key = item["slide"]
    dur = item["duration"]
    # pad tiny durations
    if dur < 0.4:
        dur = 0.4
    out = seg_dir / f"seg_{idx:03d}.mp4"
    mp3 = Path(item["mp3"])

    if slide_key in ANIM_MAP:
        prefix, count, fps = ANIM_MAP[slide_key]
        # build short looping anim then trim/pad to dur
        pattern = str(ANIM / f"{prefix}%03d.png")
        anim_mp4 = seg_dir / f"anim_{idx:03d}.mp4"
        # generate anim video (may be shorter than dur) then loop
        subprocess.check_call([
            "ffmpeg", "-y", "-framerate", str(fps), "-i", pattern,
            "-vf", "scale=1920:1080", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", "30", str(anim_mp4)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # loop anim to cover audio, mux audio
        subprocess.check_call([
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", str(anim_mp4),
            "-i", str(mp3),
            "-t", f"{dur:.3f}",
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(out)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        img = slide_for(slide_key)
        subprocess.check_call([
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img),
            "-i", str(mp3),
            "-t", f"{dur:.3f}",
            "-vf", "scale=1920:1080",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(out)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    timeline = meta["timeline"]
    seg_dir = BUILD / "segments"
    if seg_dir.exists():
        shutil.rmtree(seg_dir)
    seg_dir.mkdir()

    segs = []
    for i, item in enumerate(timeline):
        print(f"seg {i+1}/{len(timeline)} {item['id']} {item['slide']} {item['duration']:.2f}s")
        segs.append(make_segment(i, item, seg_dir))

    concat_list = seg_dir / "list.txt"
    with concat_list.open("w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"file '{s.resolve().as_posix()}'\n")

    raw = OUT / "ch01-long.raw.mp4"
    final = OUT / "ch01-long.mp4"
    subprocess.check_call([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(raw)
    ])
    # remux to ensure moov etc; burn nothing (soft srt separate)
    subprocess.check_call([
        "ffmpeg", "-y", "-i", str(raw),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        str(final)
    ])
    # copy srt
    srt_src = BUILD / "merged.srt"
    srt_dst = OUT / "ch01-long.srt"
    shutil.copy2(srt_src, srt_dst)
    dur = probe(final)
    print(f"FINAL {final} duration={dur:.2f}s")
    (BUILD / "assemble-meta.json").write_text(json.dumps({
        "duration": dur, "segments": len(segs), "out": str(final)
    }, indent=2), encoding="utf-8")
    if not (900 <= dur <= 1200):
        print(f"WARNING: duration {dur} outside 900-1200")
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
