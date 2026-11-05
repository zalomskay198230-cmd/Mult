"""Лист персонажа «Курьер» в полуреалистичном стиле. Запуск: python3 character_sheet_real.py ../kurer_personazh.png"""
import os, sys
sys.argv = [sys.argv[0], *(sys.argv[1:] or ["kurer_personazh.png"])]
OUT = sys.argv[1]
sys.argv = [sys.argv[0], ".", OUT]
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vakhta", "render"))
from toonlib import FONT_SUB, FONT_B, YELLOW, INK
from PIL import Image, ImageDraw, ImageFont
import realman
from character_sheet import bg_city, parcel

SW, SH = 2160, 1280
sheet = bg_city(SW, SH)
sheet = Image.eval(sheet, lambda v: int(v * .85))


def label(d, x, y, txt, size=34, col=YELLOW):
    f = ImageFont.truetype(FONT_SUB, size)
    d.text((x - f.getlength(txt) / 2, y), txt, font=f, fill=col, stroke_width=4, stroke_fill=(40, 34, 14))


def note(d, x, y, txt, size=26):
    f = ImageFont.truetype(FONT_B, size)
    d.text((x, y), txt, font=f, fill=(244, 244, 240), stroke_width=3, stroke_fill=INK)


# 1. в полный рост
fig, _ = realman.max_figure((SW, SH), 360, 200, 1.06)
sheet.paste(fig, (0, 0), fig)
d = ImageDraw.Draw(sheet)
label(d, 360, 24, "МАКС", 78)
label(d, 360, 112, "курьер · 26 лет", 32, (244, 244, 240))

# 2. мимика — крупные планы
for i, (expr, look, cap) in enumerate((("neutral", (0, 0), "спокоен"), ("smile", (0, 0), "сделка"),
                                        ("tense", (.8, 0), "что-то не так"), ("shock", (0, 0), "беги"))):
    cx, cy = 900 + (i % 2) * 360, 330 + (i // 2) * 520
    pane = sheet.crop((cx - 165, cy - 235, cx + 165, cy + 235))
    pane = Image.eval(pane, lambda v: int(v * .75))
    head, _ = realman.max_figure((330, 470), 165, 92, 1.85, expr=expr, look=look, head_only=True)
    pane.paste(head, (0, 0), head)
    sheet.paste(pane, (cx - 165, cy - 235))
    d = ImageDraw.Draw(sheet)
    d.rectangle([cx - 165, cy - 235, cx + 165, cy + 235], outline=INK, width=6)
    label(d, cx, cy + 178, cap, 32)

# 3. в деле — с посылкой
fig, hands = realman.max_figure((SW, SH), 1640, 420, .84, expr="smile", arms=("down", "out"), look=(1, 0))
sheet.paste(fig, (0, 0), fig)
d = ImageDraw.Draw(sheet)
hx, hy = hands[1]
parcel(d, hx + 30, hy - 6, .8)
label(d, 1790, 24, "СНАРЯЖЕНИЕ", 50)
for k, t in enumerate(("• гогглы — от пыли и пепла", "• респиратор на лямке", "• термо-рюкзак: любой груз",
                       "• бандана, пластырь, шрам", "• оплата: патроны, лекарства,", "   батарейки, информация")):
    note(d, 1500, 110 + k * 40, t)
sheet.save(OUT)
print("готово:", OUT)
