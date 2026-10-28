import subprocess
from pathlib import Path
seg_dir = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\segments")
out_dir = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\mp3")
out_dir.mkdir(parents=True, exist_ok=True)
files = sorted(seg_dir.glob("*.txt"))
VOICE = "zh-CN-YunyangNeural"

def synth(txt_path: Path):
    mp3 = out_dir / (txt_path.stem + ".mp3")
    if mp3.exists() and mp3.stat().st_size > 1000:
        print("SKIP", mp3.name)
        return mp3
    text = txt_path.read_text(encoding="utf-8").strip()
    vtt = out_dir / (txt_path.stem + ".vtt")
    cmd = [
        "edge-tts",
        "--voice", VOICE,
        "--rate=-10%",
        "--pitch=-5Hz",
        "--text", text,
        "--write-media", str(mp3),
        "--write-subtitles", str(vtt),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL", txt_path.name, (r.stderr or r.stdout)[-500:])
        raise SystemExit(1)
    print("OK", mp3.name, mp3.stat().st_size)
    return mp3

for f in files:
    synth(f)
print("ALL_DONE", len(files))
