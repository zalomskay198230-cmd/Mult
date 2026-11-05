"""Лист персонажа «Курьер». Запуск: python3 character_sheet.py ../kurer_personazh.png"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vakhta", "render"))
sys.argv = [sys.argv[0], ".", *(sys.argv[1:] or ["kurer_personazh.png"])]
from toonlib import *

OUT = sys.argv[2]
SW, SH = 2160, 1280


def bg_city(w, h, seed=3):
    """разрушенный город: силуэты домов, пожары, дым"""
    img = vgrad(w, h, (120, 104, 96), (70, 66, 72))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    x = -20
    while x < w:
        bw, bh = rnd.uniform(60, 160), rnd.uniform(200, 620)
        c = rnd.randint(54, 84)
        top = h * .72 - bh
        d.rectangle([x, top, x + bw, h], fill=(c, c - 4, c + 4))
        if rnd.random() < .5:   # обрушенный угол
            d.polygon([(x + bw * .5, top), (x + bw, top), (x + bw, top + bh * .3)], fill=(120, 104, 96))
        for wy in range(int(top + 20), int(h * .72), 34):
            for wx in range(int(x + 10), int(x + bw - 14), 26):
                if rnd.random() < .12:
                    d.rectangle([wx, wy, wx + 12, wy + 16], fill=(240, 150, 60))
                else:
                    d.rectangle([wx, wy, wx + 12, wy + 16], fill=(c - 18, c - 20, c - 14))
        x += bw + rnd.uniform(4, 30)
    for _ in range(6):
        fx, fy = rnd.uniform(0, w), h * .72 - rnd.uniform(100, 400)
        d.ellipse([fx - 30, fy - 30, fx + 30, fy + 30], fill=(250, 140, 50))
    d.rectangle([0, h * .72, w, h], fill=(62, 60, 64))
    img = img.filter(ImageFilter.GaussianBlur(5))
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for _ in range(16):
        cx, cy, r = rnd.uniform(0, w), rnd.uniform(0, h * .6), rnd.uniform(60, 140)
        ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 38, 42, 80), outline=(30, 30, 34, 100), width=4)
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(2))).convert("RGB")


def parcel(d, x, y, s=1.0):
    d.rectangle([x - 70 * s, y - 50 * s, x + 70 * s, y + 50 * s], fill=(200, 160, 110), outline=INK, width=5)
    d.rectangle([x - 12 * s, y - 50 * s, x + 12 * s, y + 50 * s], fill=(170, 170, 176))
    d.rectangle([x - 50 * s, y - 30 * s, x + 10 * s, y + 4 * s], fill=(240, 240, 236), outline=INK, width=3)
    f = ImageFont.truetype(FONT_SUB, int(16 * s))
    d.text((x - 46 * s, y - 24 * s), "СРОЧНО", font=f, fill=(210, 50, 40))


def label(d, x, y, txt, size=34, col=YELLOW):
    f = ImageFont.truetype(FONT_SUB, size)
    d.text((x - f.getlength(txt) / 2, y), txt, font=f, fill=col, stroke_width=4, stroke_fill=(40, 34, 14))


def note(d, x, y, txt, size=24):
    f = ImageFont.truetype(FONT_B, size)
    d.text((x, y), txt, font=f, fill=(244, 244, 240), stroke_width=3, stroke_fill=INK)


sheet = Image.new("RGB", (SW, SH))
bg = bg_city(SW, SH)
sheet.paste(bg)
d = ImageDraw.Draw(sheet)

# --- панель 1: в полный рост ---
toon(sheet, 360, 1180, 1.25, "kurer", "neutral", ("down", "down"), (0, 0), 0.5)
d = ImageDraw.Draw(sheet)
label(d, 360, 40, "МАКС", 80)
label(d, 360, 140, "курьер · 26 лет", 32, (244, 244, 240))

# --- панель 2: мимика ---
d.rectangle([740, 30, 1420, 1250], fill=None, outline=(240, 240, 236), width=0)
for i, (face, look, cap) in enumerate((("neutral", (0, 0), "спокоен"), ("smile", (0, 0), "сделка"),
                                        ("worried", (.6, -.3), "что-то не так"), ("shock", (0, 0), "беги"))):
    cx, cy = 900 + (i % 2) * 360, 330 + (i // 2) * 520
    pane = Image.new("RGB", (330, 470), (0, 0, 0))
    pane.paste(bg.crop((cx - 165, cy - 235, cx + 165, cy + 235)))
    pane = Image.eval(pane, lambda v: int(v * .8))
    toon(pane, 165, 900, 1.15, "kurer", face, ("down", "down"), look, 1.0, blink=False)
    sheet.paste(pane, (cx - 165, cy - 235))
    d = ImageDraw.Draw(sheet)
    d.rectangle([cx - 165, cy - 235, cx + 165, cy + 235], outline=INK, width=6)
    label(d, cx, cy + 180, cap, 32)

# --- панель 3: в деле + снаряжение ---
hands = toon(sheet, 1720, 1180, 1.0, "kurer", "smile", ("front", "point"), (1, 0), 0.5)
d = ImageDraw.Draw(sheet)
hx, hy = hands[1]
parcel(d, hx + 70, hy - 10, .9)
hand(d, (hx, hy), 1.0)
label(d, 1790, 40, "СНАРЯЖЕНИЕ", 50)
items = [
    (1960, 150, "гогглы — от пыли и пепла"),
    (1960, 205, "респиратор на лямке"),
    (1960, 260, "термо-рюкзак: любой груз"),
    (1960, 315, "бандана, пластырь, шрам"),
    (1960, 370, "оплата: патроны, лекарства,"),
    (1960, 410, "  батарейки, информация"),
]
for x, y, t in items:
    note(d, 1500, y, "• " + t, 26)

sheet = grade_sheet = Image.fromarray(np.clip(np.asarray(sheet).astype(np.float32) * 1.0, 0, 255).astype(np.uint8))
sheet.save(OUT)
print("готово:", OUT)
