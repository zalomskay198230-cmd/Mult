"""Три пробы собственного стиля на одной сцене («открываю фургон — а там хлам»):
1) «Тетрадь в клетку» — шариковая ручка на тетрадном листе, дрожащие линии, рукописные подписи;
2) «Вебтун» — вертикальный комикс: панели, жирный контур, растровые точки, облачка;
3) «Неон» — чёрный фон, светящиеся контуры, один акцентный цвет.
Запуск: python3 style_test.py <out_prefix>"""
import sys, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 720, 1280
OUT = sys.argv[1]
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FI = "/usr/share/fonts/opentype/inter/Inter-MediumItalic.otf"
F = lambda s, f=FB: ImageFont.truetype(f, s)


def wobble(pts, amp=1.6, seed=0, step=8):
    r = random.Random(seed)
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + r.uniform(-amp, amp), y0 + (y1 - y0) * t + r.uniform(-amp, amp)))
    out.append(pts[-1])
    return out


def pen(d, pts, col, w=3, seed=0, twice=True):
    d.line(wobble(pts, 1.4, seed), fill=col, width=w, joint="curve")
    if twice:   # как ручкой — линия обведена дважды
        d.line(wobble(pts, 1.8, seed + 7), fill=col, width=max(1, w - 1), joint="curve")


def ell(cx, cy, rx, ry, n=40):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in [i * 2 * math.pi / n for i in range(n + 1)]]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


# ---------- сцена как набор линий (общая для стилей) ----------
def scene_lines():
    L = []   # (точки, тип)
    L.append((rect(90, 420, 630, 980), "van"))                    # проём фургона
    L.append((rect(70, 400, 650, 1000), "van"))
    rnd = random.Random(3)
    for i in range(16):                                            # коробки хлама
        x, y = rnd.uniform(110, 560), rnd.uniform(470, 900)
        w, h = rnd.uniform(60, 120), rnd.uniform(50, 90)
        L.append((rect(x, y, x + w, y + h), "box"))
        L.append(([(x + w / 2, y), (x + w / 2, y + h)], "tape"))
    for i in range(3):                                             # шины
        L.append((ell(170 + i * 20, 900 - i * 40, 70, 26), "tire"))
        L.append((ell(170 + i * 20, 900 - i * 40, 34, 12), "tire"))
    L.append(([(470, 600), (600, 580), (620, 900), (490, 920), (470, 600)], "matt"))   # матрас
    # Тимур со спины, руки вверх
    L.append((ell(360, 1030, 70, 72), "hero"))                    # голова
    L.append(([(300, 1095), (250, 1280)], "hero")); L.append(([(420, 1095), (470, 1280)], "hero"))
    L.append(([(300, 1110), (230, 980), (215, 900)], "hero")); L.append(([(420, 1110), (490, 980), (505, 900)], "hero"))
    return L


# ---------- 1. Тетрадь в клетку ----------
def notebook():
    img = Image.new("RGB", (W, H), (250, 250, 246))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 26):
        d.line([x, 0, x, H], fill=(196, 214, 232), width=1)
    for y in range(0, H, 26):
        d.line([0, y, W, y], fill=(196, 214, 232), width=1)
    d.line([600, 0, 600, H], fill=(236, 150, 150), width=2)       # поля
    blue = (36, 52, 140)
    for i, (pts, kind) in enumerate(scene_lines()):
        pen(d, pts, blue, 3 if kind != "tape" else 2, seed=i)
    # штриховка внутри фургона (тень)
    r = random.Random(5)
    for k in range(40):
        x = 100 + k * 13
        pen(d, [(x, 430), (x - 30, 470)], blue, 1, seed=100 + k, twice=False)
    # красная ручка — акцент
    red = (196, 40, 40)
    pen(d, ell(360, 260, 250, 70), red, 3, seed=300)
    d.text((170, 222), "40 000 ₽ за ЭТО?!", font=F(40, FI), fill=red)
    pen(d, [(560, 520), (640, 470)], red, 3, seed=301)
    d.text((540, 430), "хлам!!", font=F(34, FI), fill=red)
    d.text((40, 1180), "день 1. фургон.", font=F(30, FI), fill=blue)
    return img


# ---------- 2. Вебтун ----------
def halftone(img, box, col, step=10, rmax=4):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for y in range(y0, y1, step):
        for x in range(x0 + (step // 2 if (y // step) % 2 else 0), x1, step):
            r = rmax * (y - y0) / max(1, y1 - y0)
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def webtoon():
    img = Image.new("RGB", (W, H), (245, 242, 236))
    d = ImageDraw.Draw(img)
    # панель 1 — широкая: фургон снаружи
    d.rectangle([30, 40, 690, 330], fill=(255, 214, 90), outline=(10, 10, 10), width=8)
    halftone(img, (34, 44, 686, 326), (230, 150, 40), 12, 5)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([140, 140, 520, 300], radius=18, fill=(250, 250, 250), outline=(10, 10, 10), width=7)
    d.rectangle([520, 170, 610, 300], fill=(250, 250, 250), outline=(10, 10, 10), width=7)
    for wx in (210, 540):
        d.ellipse([wx - 34, 270, wx + 34, 338], fill=(20, 20, 20))
    d.rectangle([150, 220, 600, 236], fill=(220, 50, 40))
    # облачко
    d.rounded_rectangle([60, 60, 360, 130], radius=30, fill=(255, 255, 255), outline=(10, 10, 10), width=5)
    d.text((84, 74), "40 000 ₽...", font=F(36), fill=(10, 10, 10))
    # панель 2 — большая, наклонная: хлам
    d.polygon([(30, 360), (690, 400), (690, 1240), (30, 1200)], fill=(250, 250, 250), outline=(10, 10, 10))
    d.line([(30, 360), (690, 400), (690, 1240), (30, 1200), (30, 360)], fill=(10, 10, 10), width=8)
    halftone(img, (40, 420, 680, 1180), (200, 200, 210), 14, 6)
    d = ImageDraw.Draw(img)
    for i, (pts, kind) in enumerate(scene_lines()):
        pts2 = [(x, y + 20) for x, y in pts]
        col = {"box": (214, 160, 100), "tire": (40, 40, 40), "matt": (160, 200, 230)}.get(kind)
        if col and kind in ("box", "matt"):
            d.polygon(pts2, fill=col)
        d.line(pts2, fill=(10, 10, 10), width=6 if kind in ("van", "hero") else 4, joint="curve")
    # звуковой эффект
    t = Image.new("RGBA", (520, 200), (0, 0, 0, 0))
    td = ImageDraw.Draw(t)
    td.text((10, 10), "ХЛАМ!!", font=F(120), fill=(230, 40, 40), stroke_width=10, stroke_fill=(10, 10, 10))
    t = t.rotate(8, expand=True)
    img.paste(t, (180, 380), t)
    return img


# ---------- 3. Неон ----------
def neon():
    base = Image.new("RGB", (W, H), (6, 6, 12))
    lines = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(lines)
    cols = {"van": (60, 200, 255), "box": (255, 170, 60), "tape": (255, 170, 60), "tire": (180, 120, 255), "matt": (120, 255, 200), "hero": (255, 60, 120)}
    for i, (pts, kind) in enumerate(scene_lines()):
        d.line(pts, fill=cols[kind], width=5 if kind in ("van", "hero") else 3, joint="curve")
    glow = lines.filter(ImageFilter.GaussianBlur(10))
    glow2 = lines.filter(ImageFilter.GaussianBlur(28))
    img = ImageChops.add(ImageChops.add(base, glow2), ImageChops.add(glow, lines))
    t = Image.new("RGB", (W, H))
    td = ImageDraw.Draw(t)
    f = F(62)
    txt = "40 000 ₽ ЗА ЭТО?!"
    td.text(((W - f.getlength(txt)) / 2, 220), txt, font=f, fill=(255, 60, 120))
    img = ImageChops.add(img, ImageChops.add(t.filter(ImageFilter.GaussianBlur(14)), t))
    return img


notebook().save(OUT + "_1.png")
webtoon().save(OUT + "_2.png")
neon().save(OUT + "_3.png")
ims = [Image.open(OUT + f"_{i}.png").resize((360, 640)) for i in (1, 2, 3)]
sheet = Image.new("RGB", (1080, 640))
for i, im in enumerate(ims):
    sheet.paste(im, (i * 360, 0))
sheet.save(OUT + "_sheet.png")
