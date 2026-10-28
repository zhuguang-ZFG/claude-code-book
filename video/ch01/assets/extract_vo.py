import re, pathlib
p = pathlib.Path(r"D:\Users\claude\claude-code-book-main\docs\video\ch01\long-script.md")
text = p.read_text(encoding="utf-8")
lines = []
for line in text.splitlines():
    s = line.strip()
    if not s:
        lines.append("")
        continue
    if s.startswith("#") or s.startswith(">") or s.startswith("---"):
        continue
    if s.startswith("[ANIM:") or s.startswith("[CODE:"):
        continue
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    lines.append(s)
vo = "\n".join(lines)
vo = re.sub(r"\n{3,}", "\n\n", vo).strip() + "\n"
out = pathlib.Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\full-script.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(vo, encoding="utf-8")
# also split into ~paragraph segments for TTS
paras = [x.strip() for x in re.split(r"\n\s*\n", vo) if x.strip()]
seg_dir = pathlib.Path(r"D:\Users\claude\claude-code-book-main\video\ch01\assets\vo\segments")
seg_dir.mkdir(parents=True, exist_ok=True)
for i, para in enumerate(paras, 1):
    (seg_dir / f"{i:02d}.txt").write_text(para + "\n", encoding="utf-8")
han = len(re.findall(r"[\u4e00-\u9fff]", vo))
print(f"chars={len(vo)} hanzi={han} est_min={han/220:.2f} segments={len(paras)}")
