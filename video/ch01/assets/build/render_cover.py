# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
OUT = Path(__file__).resolve().parents[2] / "out" / "ch01-cover.png"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"

def font(size, bold=False):
    return ImageFont.truetype(FONT_BD if bold else FONT_REG, size, index=0)

img = Image.new("RGB", (W, H), (10, 14, 22))
d = ImageDraw.Draw(img)
# accent bars
d.rectangle([0, 0, 24, H], fill=(64, 180, 255))
d.rectangle([0, H - 24, W, H], fill=(64, 180, 255))
d.text((80, 160), "智能体编程的新范式", font=font(72, True), fill=(230, 236, 245))
d.text((80, 280), "驭者·Agent Harness  01", font=font(48, True), fill=(64, 180, 255))
d.text((80, 380), "为什么需要 Agent Harness，而不是只包一层 API", font=font(32), fill=(140, 152, 170))
d.rounded_rectangle([80, 520, 900, 680], radius=18, fill=(22, 30, 44), outline=(64, 180, 255), width=2)
d.text((110, 560), "基于开源书稿", font=font(34, True), fill=(120, 220, 170))
d.text((110, 610), "小电讲电路 · B站长讲样片", font=font(28), fill=(230, 236, 245))
d.text((80, 780), "1,884 TS files  ·  512,664 LOC  ·  五大原则", font=font(28), fill=(140, 152, 170))
OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG")
print("cover ->", OUT)
