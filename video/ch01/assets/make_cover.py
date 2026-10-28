from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

out = Path(r"D:\Users\claude\claude-code-book-main\video\ch01\out\ch01-cover.png")
W, H = 1920, 1080
img = Image.new("RGB", (W, H), (7, 11, 20))
d = ImageDraw.Draw(img)
# gradient-ish bands
for y in range(H):
    c = int(7 + (y/H)*18)
    d.line([(0,y),(W,y)], fill=(c, c+8, c+20))
# accent circle
d.ellipse([150, 180, 430, 460], outline=(94,234,212), width=6)
d.ellipse([230, 260, 350, 380], fill=(94,234,212))

def font(size):
    for name in [
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]:
        p = Path(name)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except Exception:
                continue
    return ImageFont.load_default()

f1, f2, f3, f4 = font(72), font(44), font(36), font(28)
d.text((520, 250), "智能体编程的新范式", font=f1, fill=(232,238,252))
d.text((520, 360), "驭者·Agent Harness  01", font=f2, fill=(94,234,212))
d.text((520, 450), "基于开源书稿 · 小电讲电路", font=f3, fill=(159,180,217))
d.text((120, 980), "B站长讲样片  ·  Chatbot胶水 → Agent编排 → 五大原则", font=f4, fill=(127,145,176))
# stats chips
d.rounded_rectangle([520, 560, 860, 650], radius=18, outline=(94,234,212), width=3)
d.text((545, 585), "1,884  TS files", font=f3, fill=(232,238,252))
d.rounded_rectangle([900, 560, 1400, 650], radius=18, outline=(94,234,212), width=3)
d.text((925, 585), "512,664  LOC", font=f3, fill=(232,238,252))
img.save(out, "PNG")
print("COVER", out, out.stat().st_size)
