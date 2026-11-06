"""Лист персонажей «Вернуть миллион». Запуск: python3 cast_sheet.py ../personazhi.png"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vakhta", "render"))
OUT = sys.argv[1] if len(sys.argv) > 1 else "personazhi.png"
sys.argv = [sys.argv[0], ".", OUT]
from toonlib import FONT_SUB, FONT_B, YELLOW, INK, vgrad, glow
from PIL import Image, ImageDraw, ImageFont
import person

SW, SH = 2160, 1280
img = vgrad(SW, SH, (60, 66, 80), (28, 30, 38))
d = ImageDraw.Draw(img)
for x in range(0, SW, 120):   # окна ночного города на фоне
    for y in range(160, 900, 70):
        if (x * 7 + y * 3) % 11 < 3:
            d.rectangle([x + 20, y, x + 44, y + 30], fill=(90, 96, 110))
d.rectangle([0, 1180, SW, SH], fill=(36, 38, 44))
F1, F2 = ImageFont.truetype(FONT_SUB, 60), ImageFont.truetype(FONT_B, 28)
setup = [("denis", "tense", (0, 0)), ("artem", "smug", (.5, 0)), ("mama", "worried", (-.4, 0)), ("owner", "neutral", (0, 0))]
for i, (who, expr, look) in enumerate(setup):
    cx = 270 + i * 540
    if who == "owner":
        glow(img, (cx, 520), 220, (40, 70, 110), .9)   # свечение мониторов
    fig, _ = person.figure((SW, SH), cx, 210, .93, who, expr, look)
    img.paste(fig, (0, 0), fig)
    d = ImageDraw.Draw(img)
    c = person.CAST[who]
    d.text((cx - F1.getlength(c["name"]) / 2, 40), c["name"], font=F1, fill=YELLOW, stroke_width=5, stroke_fill=(40, 34, 14))
    d.text((cx - F2.getlength(c["sub"]) / 2, 120), c["sub"], font=F2, fill=(240, 240, 236), stroke_width=3, stroke_fill=INK)
img.save(OUT)
print("готово:", OUT)
