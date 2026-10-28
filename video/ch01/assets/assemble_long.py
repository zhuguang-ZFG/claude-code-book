import json, subprocess
from pathlib import Path

root = Path(r"D:\Users\claude\claude-code-book-main\video\ch01")
beds = root / "assets" / "beds"
work = root / "assets" / "assemble"
out = root / "out"
work.mkdir(parents=True, exist_ok=True)
out.mkdir(parents=True, exist_ok=True)

audio = root / "assets" / "vo" / "full.mp3"
# get exact audio duration
def dur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

total = dur(audio)
# chapter plan (seconds), last absorbs remainder
plan = [
    ("hook", 46.0),
    ("paradigm", 245.0),
    ("arch", 306.0),
    ("principles", 367.0),
    ("practice", 123.0),
]
used = sum(d for _, d in plan)
plan.append(("outro", max(1.0, total - used)))
print("plan", plan, "sum", sum(d for _,d in plan), "audio", total)

parts = []
for name, length in plan:
    bed = beds / f"bed-{name}.mp4"
    part = work / f"part-{name}.mp4"
    # loop bed to fill length; re-encode for clean cuts
    cmd = [
        "ffmpeg","-y","-stream_loop","-1","-i",str(bed),
        "-t", f"{length:.3f}",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p",
        "-an","-c:v","libx264","-preset","veryfast","-crf","20",
        str(part),
    ]
    print("LOOP", name, length)
    subprocess.run(cmd, check=True)
    parts.append(part)

concat_list = work / "concat.txt"
concat_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
video_only = work / "video-only.mp4"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_list),"-c","copy",str(video_only)], check=True)

final = out / "ch01-long.mp4"
# mux audio; shortest to avoid overhang
subprocess.run([
    "ffmpeg","-y","-i",str(video_only),"-i",str(audio),
    "-map","0:v:0","-map","1:a:0",
    "-c:v","copy","-c:a","aac","-b:a","192k",
    "-shortest",
    str(final),
], check=True)
fd = dur(final)
print(f"FINAL={final} duration={fd:.3f}")
