"""ГЛУБИНА 40. Серия 1. Гибрид: 3D-фоны (million/render3d/frames_bg, сцены g1_*) + 2D-герой Олег.
Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4
Приёмы подачи: время в кадре, звук вместо картинки (рация), «правила» в стиле чертежа,
инвентарь с подписями, финальный крючок. Сюжет и текст — свои."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, os.path.join(ROOT, "million", "render"))
sys.path.insert(0, os.path.join(ROOT, "kurer", "render"))
from toonlib import *
import toonlib
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import denis_rig as DR
DR.use("oleg", hoodie=False, suit=True)

LINES = {
    "01": "Сорок метров под водой. Станция «Нерпа». Сюда не долетают ни звуки, ни новости.",
    "02": "Я Олег, инженер. Напарник поднялся наверх в 14:20. Обещал вернуться через час.",
    "03": "В 15:05 погас свет. Включились аварийные лампы. Генератора хватит на сутки.",
    "04": "Связь с поверхностью ещё работала. Диспетчер говорил быстро. И не договорил.",
    "05r": "«Олег, не поднимайся! Что бы ни случилось — не поднимайся. Наверху…»",
    "06": "Потом шипение. И тишина.",
    "07": "Правило первое под водой: не торопись наверх.",
    "08": "Поднимешься с сорока метров быстро — азот в крови закипит, как газировка в бутылке.",
    "09": "На подъём нужно сорок минут. С остановками на девяти, шести и трёх метрах.",
    "10": "Что у меня есть: воздух в баллонах на шесть часов. Два литра воды. Шоколад. Фонарь.",
    "11": "Правило второе: считай воздух, а не время.",
    "12": "В иллюминатор я увидел свет. Сверху, сквозь толщу воды, медленно падало что-то горящее.",
    "13": "А в 23:40 замигала лампа шлюза. Кто-то снаружи открывал люк. На глубине сорока метров.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[-1] = ("s13", [("13", 0.1)], 3.6)
setup(LINES, PLAN)

FR = os.path.join(ROOT, "million", "render3d", "frames_bg")
F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
ORANGE, CYAN, BLUEPR, GRID = (250, 170, 60), (120, 210, 255), (16, 28, 48), (34, 52, 80)
GY = 1250
_cache = {}


def bg(name, t, bright=1.25):
    f = int(t * 12)
    path = None
    while f >= 0:
        p = os.path.join(FR, f"g1_{name}_{f:04d}.png")
        if os.path.exists(p):
            path = p
            break
        f -= 1
    key = (path, bright)
    if key not in _cache:
        if len(_cache) > 30:
            _cache.clear()
        im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
        _cache[key] = ImageEnhance.Brightness(im).enhance(bright)
    return _cache[key].copy()


def char(img, fig, tint=None):
    a = fig.getchannel("A")
    bb = a.getbbox()
    if bb:
        x0, y0, x1, y1 = bb
        sh = Image.new("L", (W, H), 0)
        cx, w = (x0 + x1) / 2, (x1 - x0) * .55
        ImageDraw.Draw(sh).ellipse([cx - w, y1 - 16, cx + w, y1 + 18], fill=140)
        img.paste(Image.new("RGB", (W, H)), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    if tint:
        R, G, B = fig.convert("RGB").split()
        fig = Image.merge("RGBA", (R.point(lambda v: int(v * tint[0])), G.point(lambda v: int(v * tint[1])), B.point(lambda v: int(v * tint[2])), a))
    img.paste(fig, (0, 0), fig)
    return img


RED_T = (1.0, .62, .58)


def clock(img, txt, y=130):
    d = ImageDraw.Draw(img)
    f = F(56, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([(W - w) / 2 - 24, y, (W + w) / 2 + 24, y + 84], radius=16, fill=(12, 12, 14), outline=(230, 230, 230), width=3)
    d.text(((W - w) / 2, y + 10), txt, font=f, fill=(255, 255, 255))


def depth_plate(img, air="6:00"):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([430, 26, 700, 104], radius=14, fill=(10, 16, 26), outline=(60, 90, 120), width=2)
    d.text((446, 32), "ГЛУБИНА", font=F(18), fill=(130, 160, 190))
    d.text((446, 54), "40 м", font=F(36, FONT_SUB), fill=CYAN)
    d.text((580, 32), "ВОЗДУХ", font=F(18), fill=(130, 160, 190))
    d.text((580, 54), air, font=F(36, FONT_SUB), fill=ORANGE)


def tag(img, title, sub, y=1090):
    d = ImageDraw.Draw(img)
    f1, f2 = F(30, FONT_SUB), F(18)
    w = max(f1.getlength(title), f2.getlength(sub)) + 40
    d.rounded_rectangle([30, y, 30 + w, y + 74], radius=8, fill=(14, 14, 16))
    d.rectangle([30, y, 36, y + 74], fill=ORANGE)
    d.text((48, y + 6), title, font=f1, fill=(255, 255, 255))
    d.text((48, y + 44), sub, font=f2, fill=(160, 160, 166))


def water(img, t, k=1.0):
    """подводная атмосфера: синий тон, лучи сверху, взвесь"""
    lay = Image.new("RGB", (W, H), (10, 60, 100))
    img = Image.blend(img, lay, .35 * k)
    rays = Image.new("L", (W, H), 0)
    rd = ImageDraw.Draw(rays)
    for i in range(5):
        x = 80 + i * 150 + 40 * math.sin(t * .5 + i)
        rd.polygon([(x - 30, 0), (x + 30, 0), (x + 140, H), (x + 60, H)], fill=22)
    img.paste(Image.new("RGB", (W, H), (150, 210, 240)), (0, 0), rays.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    for _ in range(120):
        x0, y0, sp = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(10, 40)
        y = (y0 + sp * t) % H
        x = x0 + 8 * math.sin(t + y0)
        r = rnd.uniform(1, 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(180, 210, 230))
    return img


def blueprint(title=None, a=1.0):
    img = Image.new("RGB", (W, H), BLUEPR)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        d.line([x, 0, x, H], fill=GRID, width=1)
    for y in range(0, H, 40):
        d.line([0, y, W, y], fill=GRID, width=1)
    if title:
        f = F(54, FONT_SUB)
        col = tuple(int(c * a) for c in ORANGE)
        d.text(((W - f.getlength(title)) / 2, 170), title, font=f, fill=col)
        d.line([(W - f.getlength(title)) / 2, 240, (W + f.getlength(title)) / 2, 240], fill=col, width=4)
    return img


def oleg(x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), legs="idle", ground=GY):
    return DR.front((W, H), x, ground, s, t, arms, legs, expr, look)


# ---------- сцены ----------
def s01(t, L, cue):
    img = bg("s01", t, 1.0)
    img = water(img, t, .8)
    d = ImageDraw.Draw(img)
    f = F(34, FONT_SUB)
    d.rounded_rectangle([30, 30, 60 + f.getlength("ГЛУБИНА 40"), 90], radius=12, fill=(10, 16, 26))
    d.text((44, 38), "ГЛУБИНА 40", font=f, fill=CYAN)
    return img


def s02(t, L, cue):
    img = bg("s02", t, 1.2)
    img = char(img, oleg(260, .84, t, ("down", "down"), "neutral", (.5, 0)))
    p = (t - cue["02"]) / dur("02.mp3")
    clock(img, "14:20")
    if p > .55:
        tag(img, "напарник", "ушёл наверх", 1080)
    depth_plate(img)
    return img


def s03(t, L, cue):
    off = .5
    if t < off:
        img = bg("s02", t, 1.2)
        img = char(img, oleg(260, .84, t, ("down", "down"), "neutral", (0, -.6)))
    else:
        img = bg("s03", t, 1.5)
        img = char(img, oleg(260, .84, t, ("down", "down"), "worried", (0, -.8)), RED_T)
    if off - .1 < t < off + .15:   # моргнул свет
        img = Image.blend(img, Image.new("RGB", (W, H)), .85)
    clock(img, "15:05")
    if t > 2.5:
        tag(img, "генератор", "хватит на 24 часа", 1080)
    depth_plate(img)
    return img


def radio(img, t, level=1.0, label="ПОВЕРХНОСТЬ"):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 190, 300, 530, 980
    d.rounded_rectangle([x0, y0, x1, y1], radius=36, fill=(22, 24, 26), outline=INK, width=6)
    d.line([x1 - 60, y0, x1 - 50, y0 - 200], fill=INK, width=14)
    d.ellipse([x1 - 76, y0 + 30, x1 - 52, y0 + 54], fill=(240, 40, 40) if int(t * 3) % 2 else (90, 20, 20))
    d.rounded_rectangle([x0 + 40, y0 + 70, x1 - 40, y0 + 160], radius=12, fill=(30, 90, 50))
    f = F(34, FONT_SUB)
    d.text(((x0 + x1) / 2 - f.getlength("КАНАЛ 1") / 2, y0 + 86), "КАНАЛ 1", font=f, fill=(200, 255, 210))
    d.text(((x0 + x1) / 2 - F(20).getlength(label) / 2, y0 + 128), label, font=F(20), fill=(170, 230, 180))
    for k in range(10):
        d.line([x0 + 60, y0 + 210 + k * 26, x1 - 60, y0 + 210 + k * 26], fill=(10, 10, 12), width=10)
    rnd = random.Random(int(t * 20))
    cy = y0 + 560
    for k in range(18):
        x = x0 + 56 + k * 13
        h = (rnd.uniform(8, 70) if level > .05 else 2) * level + 2
        d.rectangle([x, cy - h, x + 7, cy + h], fill=(80, 230, 140))


def s04(t, L, cue):
    img = bg("s03", t, 1.1)
    img = img.filter(ImageFilter.GaussianBlur(6))
    radio(img, t, .6)
    depth_plate(img)
    return img


def s05r(t, L, cue):
    img = bg("s03", t, 1.1).filter(ImageFilter.GaussianBlur(6))
    end = cue["05r"] + dur("05r.mp3")
    radio(img, t, 1.0 if t < end - .3 else 0.0)
    depth_plate(img)
    return shake(img, t, 4 if t > end - .5 else 0)


def s06(t, L, cue):
    img = bg("s03", t, 1.0).filter(ImageFilter.GaussianBlur(6))
    radio(img, t, 0.0, "НЕТ СИГНАЛА")
    depth_plate(img)
    return img


def s07(t, L, cue):
    img = blueprint("ПРАВИЛО №1", min(1, t / .4))
    d = ImageDraw.Draw(img)
    cx = W / 2
    k = min(1, t / 1.0)
    d.line([cx, 900, cx, 900 - 420 * k], fill=CYAN, width=14)
    if k >= 1:
        d.polygon([(cx - 50, 490), (cx + 50, 490), (cx, 420)], fill=CYAN)
    if t > 1.3:
        d.line([cx - 160, 520, cx + 160, 840], fill=(255, 110, 100), width=18)
        d.line([cx + 160, 520, cx - 160, 840], fill=(255, 110, 100), width=18)
        f = F(60, FONT_SUB)
        d.text((cx - f.getlength("НЕ ТОРОПИСЬ") / 2, 950), "НЕ ТОРОПИСЬ", font=f, fill=CYAN)
    return img


def s08(t, L, cue):
    img = blueprint("ПРАВИЛО №1")
    d = ImageDraw.Draw(img)
    cx, top = W / 2, 330
    # контур человека
    d.ellipse([cx - 50, top, cx + 50, top + 100], outline=CYAN, width=4)
    d.line([cx, top + 100, cx, top + 420], fill=CYAN, width=4)
    d.line([cx - 120, top + 260, cx, top + 160, cx + 120, top + 260], fill=CYAN, width=4)
    d.line([cx - 90, top + 680, cx, top + 420, cx + 90, top + 680], fill=CYAN, width=4)
    # пузырьки азота в «крови»
    rnd = random.Random(3)
    k = min(1, t / (L * .7))
    for i in range(int(40 * k)):
        x = cx + rnd.uniform(-70, 70)
        y0 = rnd.uniform(top + 150, top + 650)
        y = y0 - (t * 60 + i * 13) % 120
        r = rnd.uniform(4, 11)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 120, 110), width=3)
    f = F(60, FONT_SUB)
    d.text((cx + 140, top + 200), "N₂", font=f, fill=(255, 120, 110))
    d.text((cx - F(40, FONT_SUB).getlength("кессонная болезнь") / 2, 1060), "кессонная болезнь", font=F(40, FONT_SUB), fill=CYAN)
    return img


def s09(t, L, cue):
    img = blueprint("ПОДЪЁМ")
    d = ImageDraw.Draw(img)
    x = 260
    d.line([x, 320, x, 1080], fill=CYAN, width=6)
    f, f2 = F(30, FONT_SUB), F(26)
    for depth in (0, 3, 6, 9, 20, 40):
        y = 320 + depth / 40 * 760
        d.line([x - 20, y, x + 20, y], fill=CYAN, width=4)
        d.text((x - 110, y - 16), f"{depth} м", font=f, fill=(170, 200, 230))
    stops = [(9, "3 мин"), (6, "5 мин"), (3, "10 мин")]
    p = (t - cue["09"]) / dur("09.mp3")
    yd = 320 + 760 * max(0, 1 - p * 1.1)
    d.ellipse([x - 22, yd - 22, x + 22, yd + 22], fill=ORANGE)
    for i, (depth, dt) in enumerate(stops):
        if p > .45 + i * .15:
            y = 320 + depth / 40 * 760
            d.rounded_rectangle([x + 50, y - 26, x + 280, y + 26], radius=10, fill=(30, 50, 80), outline=ORANGE, width=3)
            d.text((x + 66, y - 18), f"стоп · {dt}", font=f2, fill=(255, 255, 255))
    f3 = F(64, FONT_SUB)
    d.text((W - 60 - f3.getlength("40 мин"), 1110), "40 мин", font=f3, fill=ORANGE)
    return img


def item(d, kind, x, y):
    if kind == "tank":
        d.rounded_rectangle([x - 34, y - 200, x + 34, y], radius=30, fill=(230, 200, 60), outline=INK, width=4)
        d.rectangle([x - 12, y - 230, x + 12, y - 200], fill=(140, 140, 146), outline=INK, width=3)
        d.ellipse([x - 26, y - 150, x + 26, y - 98], fill=(240, 240, 236), outline=INK, width=3)
        d.line([x, y - 124, x + 16, y - 140], fill=(220, 40, 40), width=4)
    elif kind == "water":
        d.rounded_rectangle([x - 30, y - 160, x + 30, y], radius=14, fill=(150, 200, 240), outline=INK, width=4)
        d.rectangle([x - 14, y - 184, x + 14, y - 160], fill=(40, 90, 180), outline=INK, width=3)
    elif kind == "choc":
        d.rounded_rectangle([x - 70, y - 40, x + 70, y], radius=6, fill=(110, 60, 40), outline=INK, width=4)
        d.rectangle([x - 70, y - 40, x - 10, y], fill=(200, 40, 50), outline=INK, width=3)
    elif kind == "torch":
        d.rounded_rectangle([x - 70, y - 34, x + 50, y], radius=10, fill=(60, 60, 66), outline=INK, width=4)
        d.polygon([(x + 50, y - 40), (x + 80, y - 50), (x + 80, y + 16), (x + 50, y + 6)], fill=(80, 80, 86), outline=INK)


def s10(t, L, cue):
    img = bg("s03", t, 1.0).filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 900, W, 960], fill=(70, 50, 40), outline=INK, width=4)
    p = (t - cue["10"]) / dur("10.mp3")
    items = [("tank", 150, .1, "воздух", "6 часов"), ("water", 270, .5, "2 л", "вода"), ("choc", 390, .72, "шоколад", "1 плитка"),
             ("torch", 490, .86, "фонарь", "заряд 80%")]
    shown = None
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for kind, x, when, tt, sub in items:
        if p > when:
            item(ld, kind, x, 900)
            shown = (tt, sub)
    big = lay.resize((int(W * 1.35), int(H * 1.35)), Image.LANCZOS)
    img.paste(big, (int(-W * .175), int(900 - 900 * 1.35)), big)
    if shown:
        tag(img, *shown, 1000)
    depth_plate(img)
    return img


def s11(t, L, cue):
    img = blueprint("ПРАВИЛО №2", min(1, t / .4))
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, 640, 220
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=CYAN, width=8)
    for k in range(11):
        a = math.radians(225 - k * 27)
        d.line([cx + (R - 30) * math.cos(a), cy - (R - 30) * math.sin(a), cx + R * math.cos(a), cy - R * math.sin(a)], fill=CYAN, width=4)
    k = min(1, t / L)
    a = math.radians(225 - 270 * (1 - .35 * k))
    d.line([cx, cy, cx + (R - 50) * math.cos(a), cy - (R - 50) * math.sin(a)], fill=(255, 110, 100), width=10)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 110, 100))
    f = F(56, FONT_SUB)
    d.text((cx - f.getlength("ВОЗДУХ > ВРЕМЯ") / 2, 950), "ВОЗДУХ > ВРЕМЯ", font=f, fill=ORANGE)
    return img


def s12(t, L, cue):
    img = bg("s03", t, .8).filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(img)
    cx, cy, R = 430, 520, 230
    win = Image.new("RGB", (2 * R, 2 * R), (4, 20, 40))
    wd = ImageDraw.Draw(win)
    for i in range(3):   # горящие обломки тонут
        ph = (t * .08 + i * .33) % 1
        x, y = R + (i - 1) * 110 + 20 * math.sin(t + i), -40 + ph * (2 * R + 80)
        glow(win, (x, y), 60, (150, 80, 20), .9)
        wd = ImageDraw.Draw(win)
        wd.polygon([(x - 30, y - 10), (x + 26, y - 18), (x + 20, y + 16), (x - 24, y + 12)], fill=(40, 30, 26))
        wd.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 170, 60))
        for b in range(4):
            by = y - 30 - b * 24
            wd.ellipse([x - 4 + b * 3, by - 4, x + 4 + b * 3, by + 4], outline=(160, 200, 230), width=2)
    m = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * R, 2 * R], fill=255)
    img.paste(win, (cx - R, cy - R), m)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30], outline=(140, 146, 152), width=40)
    for k in range(8):
        a = k * math.pi / 4
        bx, by = cx + (R + 30) * math.cos(a), cy + (R + 30) * math.sin(a)
        d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(90, 94, 100), outline=INK, width=2)
    img = char(img, oleg(120, 1.1, t, ("down", "down"), "shock" if t > 2 else "worried", (1, -.6), ground=1700), RED_T)
    depth_plate(img, "5:10")
    return img


def s13(t, L, cue):
    vo_end = cue["13"] + dur("13.mp3")
    img = bg("s13", t, 1.3)
    on = int(t * 3) % 2 == 0
    if on:
        glow(img, (368, 320), 90, (200, 110, 20), 1)
    d = ImageDraw.Draw(img)
    p = (t - cue["13"]) / dur("13.mp3")
    if p > .45:   # штурвал люка проворачивается
        cx, cy, R = 368, 613, 92
        a0 = (t - (cue["13"] + dur("13.mp3") * .45)) * 1.6
        for k in range(4):
            a = a0 + k * math.pi / 4
            d.line([cx - R * math.cos(a), cy - R * math.sin(a), cx + R * math.cos(a), cy + R * math.sin(a)], fill=(220, 70, 50), width=8)
    clock(img, "23:40")
    depth_plate(img, "4:20")
    img = shake(img, t, 3 if p > .45 else 0)
    if t > vo_end + .6:
        a = min(1, (t - vo_end - .6) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(40, FONT_SUB), F(70, FONT_SUB), F(30, FONT_SUB)
            dd.text(((W - f1.getlength("ГЛУБИНА 40")) / 2, 470), "ГЛУБИНА 40", font=f1, fill=(240, 240, 244))
            dd.text(((W - f2.getlength("ДЕНЬ 1")) / 2, 530), "ДЕНЬ 1", font=f2, fill=ORANGE)
            dd.text(((W - f3.getlength("ПРОДОЛЖЕНИЕ СЛЕДУЕТ")) / 2, 630), "ПРОДОЛЖЕНИЕ СЛЕДУЕТ", font=f3, fill=(200, 200, 206))
            if t > vo_end + 1.6:
                dd.text(((W - F(28).getlength("кто открывает люк?")) / 2, 700), "кто открывает люк?", font=F(28), fill=(150, 150, 156))
    return img


if __name__ == "__main__":
    if os.environ.get("TIMELINE"):
        import json
        need = {"s01", "s02", "s03", "s13"}
        out = {"scenes": [{"name": "g1_" + n, "start": st, "length": l, "cue_start": sc[0][0], "cue_dur": sc[0][2]}
                          for n, st, l, sc in scenes if n in need]}
        json.dump(out, open(os.environ["TIMELINE"], "w"), indent=1)
        print("timeline saved")
        sys.exit()
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(span("s04")[0], span("s06")[0] + span("s06")[1])],
        hits=[span("s03")[0] + .5, span("s05r")[0] + dur("05r.mp3"), span("s07")[0] + 1.3, span("s13")[0] + .2])
