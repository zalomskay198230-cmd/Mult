"""КУРЬЕР. Серия 1 — «Заказ без отправителя». Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vakhta", "render"))
from toonlib import *
import rig, realman as R
from zina import zina_bust
from character_sheet import bg_city

LINES = {
    "01": "За эту коробку мне заплатили ящиком антибиотиков. А получатель на ней — я.",
    "02": "Сутки назад. Пункт выдачи тёти Зины. Я курьер. Хожу между кварталами, когда больше никто не ходит.",
    "03": "У курьеров три правила. Курьера не трогают. Посылку не открывают. В Мёртвую зону не ходят.",
    "04z": "Макс, есть заказ. Садовая, четырнадцать. Квартира девять.",
    "05": "Садовая — это центр. Мёртвая зона. Оттуда не возвращаются.",
    "06z": "Платят ящиком антибиотиков. Квартал полгода проживёт. Ну?",
    "07": "Я взял коробку. Лёгкая. Отправителя нет.",
    "08": "В Мёртвой зоне пепел стоит туманом. Трамваи замерли там, где их застала вспышка.",
    "09": "А на земле — следы. Курьерские ботинки. Все ведут туда. Обратно — ни одного.",
    "10": "Сзади кто-то зарычал. Я побежал.",
    "11": "Садовая, четырнадцать. Квартира девять. Дверь открыта.",
    "12": "Я достал накладную, чтобы сверить получателя. Получатель: Макс Воронов.",
    "13": "В квартире горел свет. На столе — две кружки. Чай ещё тёплый.",
    "14": "Меня здесь ждали.",
}

PLAN = [
    ("s01", [("01", 0.05)], 0.3),
    ("s02", [("02", 0.1)], 0.3),
    ("s03", [("03", 0.1)], 0.3),
    ("s04", [("04z", 0.1)], 0.3),
    ("s05", [("05", 0.1)], 0.3),
    ("s06", [("06z", 0.1)], 0.3),
    ("s07", [("07", 0.1)], 0.3),
    ("s08", [("08", 0.1)], 0.3),
    ("s09", [("09", 0.1)], 0.3),
    ("s10", [("10", 0.4)], 1.4),
    ("s11", [("11", 0.1)], 0.3),
    ("s12", [("12", 0.1)], 0.4),
    ("s13", [("13", 0.1)], 0.4),
    ("s14", [("14", 0.6)], 2.6),
]
setup(LINES, PLAN)

ASH = Snow(140, 21, size=(1.5, 4), speed=(40, 110), wind=40)
ASH_FOG = Snow(200, 22, size=(1.5, 4.5), speed=(50, 120), wind=90)
F_HAND = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBoldItalic.otf", 30)
F_PRINT = ImageFont.truetype(FONT_B, 30)
GROUND = int(H * .72) + 140


def ash(img, t, snow=ASH):
    snow.draw(img, t, col=(196, 192, 188))


def corner_plate(img, a=1.0):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 30)
    txt = "КУРЬЕР · серия 1"
    d.rounded_rectangle([24, 30, 48 + f.getlength(txt), 82], radius=12, fill=(20, 18, 18))
    d.text((36, 38), txt, font=f, fill=tuple(int(c * a) for c in YELLOW))


def paste(img, fig):
    img.paste(fig, (0, 0), fig)
    return img


# ---------- накладная ----------
def waybill(img, t, hl=0.0, x0=80, y0=300, s=1.12):
    d = ImageDraw.Draw(img)
    w, h = 500 * s, 330 * s
    d.polygon([(x0 + 10, y0 + 14), (x0 + w + 16, y0 + 4), (x0 + w + 10, y0 + h + 16), (x0 + 4, y0 + h + 10)], fill=(30, 26, 24))
    d.polygon([(x0, y0), (x0 + w, y0 - 8), (x0 + w + 4, y0 + h), (x0 - 4, y0 + h + 6)], fill=(226, 214, 186), outline=INK)
    rows = [("НАКЛАДНАЯ № 0417", F_PRINT, INK), ("Отправитель: —", F_HAND, (60, 70, 110)),
            ("Адрес: Садовая 14, кв. 9", F_HAND, (60, 70, 110)), ("Получатель:", F_HAND, (60, 70, 110))]
    for i, (txt, f, col) in enumerate(rows):
        d.text((x0 + 26 * s, y0 + (22 + i * 58) * s), txt, font=f, fill=col)
    fn = ImageFont.truetype(FONT_SUB, int(40 * s))
    name = "МАКС ВОРОНОВ"
    nx, ny = x0 + 26 * s, y0 + 258 * s
    d.text((nx, ny), name, font=fn, fill=(170, 40, 36))
    if hl > 0:   # красный круг вокруг имени
        d.arc([nx - 20, ny - 20, nx + fn.getlength(name) + 20, ny + 66], -90, -90 + 360 * hl, fill=(220, 50, 40), width=6)
    # грязь и пепел на бумаге
    rnd = random.Random(3)
    for _ in range(40):
        x, y = x0 + rnd.uniform(0, w), y0 + rnd.uniform(0, h)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(150, 140, 126))
    # рука в перчатке снизу слева
    g = (44, 42, 44)
    d.rounded_rectangle([x0 - 70, y0 + h - 40, x0 + 90, y0 + h + 60], radius=36, fill=g, outline=INK, width=4)
    d.rounded_rectangle([x0 - 50, y0 + h - 34, x0 + 20, y0 + h + 16], radius=22, fill=g, outline=INK, width=4)   # большой палец
    d.polygon([(x0 - 80, y0 + h + 40), (x0 + 60, y0 + h + 50), (x0 + 40, H + 20), (x0 - 140, H + 20)], fill=(150, 116, 44), outline=INK)  # рукав


def s01(t, L, cue):
    img = Image.eval(bg_city(W, H, seed=9), lambda v: int(v * .55))
    waybill(img, t, hl=min(1, max(0, (t - (cue["01"] + 3.4)) / .6)))
    ash(img, t)
    img = zoom(img, 1.08 - .05 * t / L, .45, .4)
    corner_plate(img)
    return img


# ---------- подвал пункта выдачи ----------
_BASE = {}


def basement_bg():
    if "b" in _BASE:
        return _BASE["b"].copy()
    img = vgrad(W, H, (58, 46, 40), (34, 28, 26))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    for row in range(0, H, 34):   # кирпич
        off = 0 if (row // 34) % 2 else 40
        for x in range(-off, W, 80):
            c = rnd.randint(48, 66)
            d.rectangle([x + 2, row + 2, x + 78, row + 32], fill=(c + 12, c, c - 6))
    # стеллажи с посылками
    for sx in (430,):
        for k in range(4):
            y = 260 + k * 150
            d.rectangle([sx, y, W, y + 14], fill=(90, 74, 60), outline=INK, width=3)
            x = sx + 10
            while x < W - 20:
                bw, bh = rnd.uniform(40, 90), rnd.uniform(50, 120)
                c = rnd.choice([(196, 160, 110), (176, 140, 96), (150, 120, 84), (120, 140, 150)])
                d.rectangle([x, y - bh, x + bw, y], fill=c, outline=INK, width=3)
                d.rectangle([x + bw * .4, y - bh, x + bw * .55, y], fill=(200, 196, 186))
                x += bw + 8
    _BASE["b"] = img.filter(ImageFilter.GaussianBlur(2))
    return _BASE["b"].copy()


def stove(img, t, x=90, y=900):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 70, y - 160, x + 70, y + 40], fill=(40, 38, 40), outline=INK, width=5)
    d.rectangle([x - 18, y - 600, x + 18, y - 160], fill=(50, 48, 50), outline=INK, width=4)
    fl = .8 + .2 * math.sin(t * 9) * math.sin(t * 5)
    d.rectangle([x - 40, y - 90, x + 40, y - 20], fill=(int(250 * fl), int(130 * fl), 40))
    glow(img, (x, y - 60), 220 * fl, (130, 60, 16), .9)


def counter(img, y=1020):
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, W, H], fill=(84, 64, 50), outline=INK, width=6)
    d.rectangle([0, y, W, y + 26], fill=(110, 86, 66), outline=INK, width=4)


def s02(t, L):
    img = basement_bg()
    stove(img, t)
    img = paste(img, zina_bust((W, H), 540, 600, .95, t, look=(-.6, 0)))
    counter(img, 1000)
    img = paste(img, rig.front_figure((W, H), 230, 1420, .72, t, "idle", "neutral", (.5, 0)))
    d = ImageDraw.Draw(img)
    lamp_x = 360
    d.line([lamp_x, 0, lamp_x, 120], fill=INK, width=4)
    d.polygon([(lamp_x - 40, 160), (lamp_x + 40, 160), (lamp_x + 20, 120), (lamp_x - 20, 120)], fill=(60, 60, 64), outline=INK)
    glow(img, (lamp_x, 170), 120, (90, 76, 40), .8)
    return zoom(img, 1.03 + .04 * t / L, .5, .5)


def s03(t, L, cue):
    img = vgrad(W, H, (40, 34, 30), (26, 22, 20))
    d = ImageDraw.Draw(img)
    d.rectangle([50, 120, 670, 1120], fill=(34, 56, 44), outline=(110, 80, 56), width=22)
    f1 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-BoldItalic.otf", 46)
    f2 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBoldItalic.otf", 40)
    d.text((110, 180), "ПРАВИЛА КУРЬЕРА", font=f1, fill=(236, 236, 226))
    d.line([110, 244, 610, 240], fill=(236, 236, 226), width=4)
    p = (t - cue["03"]) / dur("03.mp3")
    rules = [(.2, "1. Курьера не трогают."), (.45, "2. Посылку не открывают."), (.7, "3. В Мёртвую зону"), (.7, "    не ходят.")]
    for i, (when, txt) in enumerate(rules):
        if p > when:
            k = min(1, (p - when) / .08)
            n = int(len(txt) * k)
            d.text((110, 300 + i * 70 + (20 if i == 3 else 0) - (10 if i == 3 else 0)), txt[:n], font=f2,
                   fill=(236, 120, 110) if i >= 2 else (236, 236, 226))
    # меловая пыль
    rnd = random.Random(1)
    for _ in range(300):
        x, y = rnd.uniform(70, 650), rnd.uniform(140, 1100)
        d.point((x, y), fill=(70, 96, 84))
    return zoom(img, 1.02 + .04 * t / L, .5, .3)


def s04(t, L):
    img = basement_bg()
    stove(img, t, x=-20)
    img = paste(img, zina_bust((W, H), 360, 400, 1.75, t, talk=True, look=(0, 0)))
    return zoom(img, 1.0 + .05 * t / L, .5, .4)


def city_map(img, t, p):
    d = ImageDraw.Draw(img)
    d.rectangle([40, 120, 680, 900], fill=(214, 204, 176), outline=INK, width=6)
    rnd = random.Random(4)
    for k in range(14):   # улицы
        y = 140 + k * 56 + rnd.uniform(-10, 10)
        d.line([60, y, 660, y + rnd.uniform(-30, 30)], fill=(186, 176, 150), width=8)
        x = 70 + k * 46
        d.line([x, 140, x + rnd.uniform(-40, 40), 880], fill=(186, 176, 150), width=6)
    d.line([60, 700, 660, 520], fill=(120, 150, 180), width=26)   # река
    cx, cy = 380, 480
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.ellipse([cx - 180, cy - 160, cx + 180, cy + 160], fill=(200, 40, 30, 90), outline=(200, 40, 30, 255), width=6)
    for k in range(-200, 200, 26):
        ld.line([cx + k - 160, cy + 160, cx + k + 160, cy - 160], fill=(200, 40, 30, 70), width=4)
    img.paste(Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB"))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 36)
    d.text((cx - f.getlength("МЁРТВАЯ ЗОНА") / 2, cy - 30), "МЁРТВАЯ ЗОНА", font=f, fill=(170, 30, 24))
    if p > .2:   # булавка Садовая 14
        px, py = cx + 40, cy + 70
        d.line([px, py, px, py - 60], fill=INK, width=5)
        d.ellipse([px - 16, py - 84, px + 16, py - 52], fill=(240, 200, 60), outline=INK, width=4)
        d.text((px + 24, py - 80), "Садовая 14", font=ImageFont.truetype(FONT_B, 26), fill=INK)


def s05(t, L, cue):
    img = basement_bg()
    p = (t - cue["05"]) / dur("05.mp3")
    city_map(img, t, p)
    img = paste(img, rig.front_figure((W, H), 520, 2080, 1.25, t, "idle", "tense", (-.6, -.4)))
    return zoom(img, 1.0 + .08 * min(1, p), .55, .4)


def crate(img, x, y, s=1.0):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 150 * s, y - 100 * s, x + 150 * s, y + 100 * s], fill=(150, 110, 70), outline=INK, width=6)
    for k in range(-2, 3):
        d.line([x - 150 * s, y + k * 40 * s, x + 150 * s, y + k * 40 * s], fill=(120, 86, 54), width=4)
    d.rectangle([x - 40 * s, y - 70 * s, x + 40 * s, y + 10 * s], fill=(236, 232, 222), outline=INK, width=4)
    d.rectangle([x - 12 * s, y - 62 * s, x + 12 * s, y + 2 * s], fill=(200, 40, 36))
    d.rectangle([x - 32 * s, y - 42 * s, x + 32 * s, y - 18 * s], fill=(200, 40, 36))
    f = ImageFont.truetype(FONT_SUB, int(28 * s))
    d.text((x - f.getlength("АНТИБИОТИКИ") / 2, y + 30 * s), "АНТИБИОТИКИ", font=f, fill=(40, 30, 24))


def s06(t, L):
    img = basement_bg()
    stove(img, t, x=-20)
    img = paste(img, zina_bust((W, H), 470, 470, 1.25, t, talk=True, look=(-.4, .3)))
    counter(img, 1000)
    crate(img, 220, 1000 - 30 + 0, .95)
    return zoom(img, 1.02 + .04 * t / L, .45, .55)


def parcel_box(d, x, y, s=1.0):
    d.polygon([(x - 120 * s, y - 40 * s), (x + 40 * s, y - 90 * s), (x + 160 * s, y - 50 * s), (x, y)], fill=(214, 176, 124), outline=INK)
    d.polygon([(x - 120 * s, y - 40 * s), (x, y), (x, y + 110 * s), (x - 120 * s, y + 70 * s)], fill=(186, 146, 98), outline=INK)
    d.polygon([(x, y), (x + 160 * s, y - 50 * s), (x + 160 * s, y + 60 * s), (x, y + 110 * s)], fill=(160, 124, 82), outline=INK)
    d.line([(x - 40 * s, y - 64 * s), (x + 100 * s, y - 20 * s)], fill=(200, 196, 186), width=int(16 * s))
    d.polygon([(x - 90 * s, y + 10 * s), (x - 20 * s, y + 34 * s), (x - 20 * s, y + 80 * s), (x - 90 * s, y + 56 * s)], fill=(236, 230, 210), outline=INK)
    f = ImageFont.truetype(FONT_B, int(16 * s))
    d.text((x - 84 * s, y + 24 * s), "отпр.: —", font=f, fill=(170, 40, 36))


def s07(t, L):
    img = basement_bg()
    counter(img, 760)
    d = ImageDraw.Draw(img)
    rise = min(1, max(0, (t - 1.2) / 1.2))
    parcel_box(d, 380, 800 - 120 * rise, 1.6)
    if t > .6:   # рука в перчатке тянется
        k = min(1, (t - .6) / .6)
        gx, gy = 120 + 120 * k, H + 100 - 520 * k - 120 * rise
        d.polygon([(gx - 160, H + 80), (gx - 10, gy + 60), (gx + 60, gy + 100), (gx - 40, H + 80)], fill=(150, 116, 44), outline=INK)
        d.rounded_rectangle([gx - 40, gy - 20, gx + 90, gy + 80], radius=34, fill=(44, 42, 44), outline=INK, width=4)
    return zoom(img, 1.05 + .06 * t / L, .5, .55)


# ---------- Мёртвая зона ----------
def tram(d, x, base, s, col=(70, 74, 80)):
    d.rounded_rectangle([x, base - 220 * s, x + 520 * s, base], radius=int(26 * s), fill=col, outline=(40, 42, 46), width=4)
    for k in range(6):
        wx = x + 30 * s + k * 80 * s
        d.rectangle([wx, base - 190 * s, wx + 60 * s, base - 110 * s], fill=tuple(max(0, c - 26) for c in col))
    d.line([x + 200 * s, base - 220 * s, x + 260 * s, base - 300 * s, x + 320 * s, base - 220 * s], fill=(40, 42, 46), width=4)
    for wx in (x + 80 * s, x + 420 * s):
        d.ellipse([wx - 30 * s, base - 30 * s, wx + 30 * s, base + 30 * s], fill=(40, 42, 46))


def fog_scene(t, scroll, dogs=0.0, eyes=0.0):
    img = vgrad(W, H, (150, 148, 146), (110, 108, 108))
    d = ImageDraw.Draw(img)
    # дальний план: силуэты домов
    for k in range(-1, 6):
        x = k * 220 - (scroll * .2) % 220
        hgt = 300 + (k * 97) % 260
        d.rectangle([x, GROUND - 120 - hgt, x + 180, GROUND - 120], fill=(128, 126, 128))
    # средний план: трамваи
    for k in range(-1, 3):
        x = k * 900 - (scroll * .55) % 900
        tram(d, x, GROUND - 40, .9, (96, 100, 104))
    # земля, рельсы
    d.rectangle([0, GROUND - 40, W, H], fill=(96, 94, 94))
    for y in (GROUND - 10, GROUND + 30):
        d.line([0, y, W, y], fill=(70, 70, 72), width=6)
    for k in range(-1, 20):
        x = k * 70 - (scroll % 70)
        d.line([x, GROUND - 14, x + 10, GROUND + 34], fill=(80, 78, 78), width=8)
    # глаза собак в тумане
    if eyes > 0:
        for i, (ex, ey) in enumerate([(60, GROUND - 90), (150, GROUND - 70), (250, GROUND - 100)]):
            a = eyes * (.7 + .3 * math.sin(t * 6 + i))
            for dx in (0, 22):
                d.ellipse([ex + dx - 6, ey - 4, ex + dx + 6, ey + 4], fill=(int(255 * a), int(220 * a), int(80 * a)))
    # туман поверх
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for i in range(10):
        y = GROUND - 400 + i * 60
        x = (i * 130 - scroll * (.3 + .05 * i)) % (W + 400) - 200
        fd.ellipse([x - 400, y - 80, x + 400, y + 80], fill=(186, 184, 182, 70))
    img = Image.alpha_composite(img.convert("RGBA"), fog.filter(ImageFilter.GaussianBlur(30))).convert("RGB")
    return img


def dog(d, x, y, t, ph):
    """силуэт собаки сбоку, бежит вправо"""
    k = math.sin(t * 14 + ph)
    c = (40, 38, 40)
    d.ellipse([x - 70, y - 70, x + 50, y - 20], fill=c)
    d.polygon([(x + 40, y - 70), (x + 90, y - 80), (x + 104, y - 60), (x + 60, y - 40)], fill=c)
    d.polygon([(x + 60, y - 84), (x + 70, y - 104), (x + 78, y - 80)], fill=c)
    d.line([x - 70, y - 60, x - 110, y - 80 - 10 * k], fill=c, width=8)
    for lx, ph2 in ((-50, 0), (-30, math.pi), (20, math.pi / 2), (40, 3 * math.pi / 2)):
        a = 30 * math.sin(t * 14 + ph + ph2)
        d.line([x + lx, y - 30, x + lx + 40 * math.sin(math.radians(a)), y + 10], fill=c, width=9)
    d.ellipse([x + 80, y - 72, x + 88, y - 66], fill=(255, 220, 80))


def s08(t, L):
    img = fog_scene(t, 300 + t * 140)
    img = paste(img, rig.side_figure((W, H), W / 2 - 60, GROUND, .72, t, "walk"))
    ash(img, t, ASH_FOG)
    return img


def s09(t, L):
    img = Image.new("RGB", (W, H), (110, 108, 106))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(600):   # пепел на асфальте
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(1, 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(128, 126, 124))
    for trail in range(4):   # четыре дорожки следов — все вверх
        bx = 90 + trail * 170
        for k in range(9):
            y = H - 60 - k * 150 + (trail * 37) % 70
            boot_print(d, bx + (22 if k % 2 else -22) + 10 * math.sin(k + trail), y, .95, .06 * math.sin(trail), k % 2 == 0)
    ash(img, t, ASH_FOG)
    return zoom(img, 1.0 + .08 * t / L, .5, .3 + .3 * t / L)


def s10(t, L, cue):
    run0 = cue["10"] + 1.6
    if t < run0:   # глаза в тумане
        img = fog_scene(t, 700, eyes=min(1, t / 1.0))
        img = paste(img, rig.side_figure((W, H), W / 2 + 80, GROUND, .72, 0.0, "walk", expr="tense"))
        return shake(zoom(img, 1.0 + .1 * t / run0, .3, .7), t, 2)
    lt = t - run0
    img = fog_scene(t, 700 + lt * 520)
    d = ImageDraw.Draw(img)
    for i, (dx, ph) in enumerate(((-40, 0), (-200, 1.3))):   # собаки догоняют, но отстают
        dog(d, dx + 60 * math.sin(lt * 2 + i) + 30 * lt, GROUND + 6, lt, ph)
    img = paste(img, rig.side_figure((W, H), W / 2 + 40, GROUND, .72, lt, "run", expr="shock"))
    ash(img, t, ASH_FOG)
    return shake(img, t, 4)


# ---------- дом и квартира ----------
def s11(t, L, cue):
    p = (t - cue["11"]) / dur("11.mp3")
    if p < .45:   # панельный дом в тумане
        img = vgrad(W, H, (150, 148, 146), (110, 108, 108))
        d = ImageDraw.Draw(img)
        d.rectangle([90, 120, 630, GROUND], fill=(120, 118, 120), outline=(80, 80, 84), width=4)
        for row in range(9):
            for col in range(5):
                x, y = 120 + col * 104, 150 + row * 92
                lit = (row, col) == (4, 2)
                d.rectangle([x, y, x + 70, y + 60], fill=(250, 200, 120) if lit else (70, 72, 78), outline=(60, 60, 64), width=3)
        if True:
            glow(img, (363, 548), 80, (120, 90, 40), .8)
        d.rectangle([290, GROUND - 200, 430, GROUND], fill=(50, 52, 56), outline=INK, width=5)
        f = ImageFont.truetype(FONT_SUB, 40)
        d.rectangle([300, GROUND - 260, 420, GROUND - 210], fill=(60, 90, 140), outline=INK, width=4)
        d.text((360 - f.getlength("14") / 2, GROUND - 256), "14", font=f, fill=(240, 240, 240))
        ash(img, t, ASH_FOG)
        return zoom(img, 1.0 + .2 * p / .45, .5, .45)
    # дверь квартиры 9 приоткрыта, из щели тёплый свет
    img = vgrad(W, H, (70, 66, 64), (44, 42, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([150, 160, 570, 1100], fill=(60, 56, 54), outline=INK, width=6)
    gap = 60
    d.rectangle([570 - gap, 160, 570, 1100], fill=(255, 210, 140))
    d.rectangle([150, 160, 570 - gap, 1100], fill=(110, 74, 54), outline=INK, width=7)
    for y in (260, 560, 860):
        d.rectangle([190, y, 570 - gap - 40, y + 220], outline=(90, 60, 44), width=5)
    f = ImageFont.truetype(FONT_SUB, 70)
    d.ellipse([280, 190, 380, 290], fill=(200, 176, 110), outline=INK, width=4)
    d.text((330 - f.getlength("9") / 2, 196), "9", font=f, fill=INK)
    glow(img, (560, 640), 260, (130, 90, 40), .9)
    return zoom(img, 1.02 + .1 * (p - .45), .7, .5)


def s12(t, L, cue):
    img = Image.eval(vgrad(W, H, (70, 66, 64), (44, 42, 42)), lambda v: v)
    glow(img, (W, 600), 300, (110, 80, 40), .8)
    p = (t - cue["12"]) / dur("12.mp3")
    waybill(img, t, hl=min(1, max(0, (p - .62) / .2)))
    ash(img, t)
    return zoom(img, 1.05 + .2 * max(0, p - .5), .35, .6)


def mug(d, x, y, s, col):
    d.rounded_rectangle([x - 40 * s, y - 70 * s, x + 40 * s, y + 10 * s], radius=int(10 * s), fill=col, outline=INK, width=5)
    d.arc([x + 26 * s, y - 56 * s, x + 66 * s, y - 10 * s], -90, 90, fill=INK, width=8)
    d.ellipse([x - 40 * s, y - 80 * s, x + 40 * s, y - 62 * s], fill=(110, 70, 40), outline=INK, width=3)


def steam(img, t, x, y):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i in range(4):
        life = (t * .5 + i / 4) % 1
        yy = y - 30 - 180 * life
        xx = x + 20 * math.sin(life * 6 + i)
        ld.ellipse([xx - 16 - 20 * life, yy - 14, xx + 16 + 20 * life, yy + 14], fill=(240, 236, 230, int(110 * (1 - life))))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(6))).convert("RGB")


def s13(t, L):
    img = vgrad(W, H, (110, 84, 62), (60, 46, 38))
    d = ImageDraw.Draw(img)
    # окно с пеплом
    d.rectangle([420, 140, 680, 520], fill=(120, 118, 118), outline=INK, width=8)
    d.line([550, 140, 550, 520], fill=INK, width=6)
    # лампа
    d.line([200, 0, 200, 200], fill=INK, width=4)
    d.polygon([(130, 260), (270, 260), (230, 196), (170, 196)], fill=(210, 160, 80), outline=INK)
    glow(img, (200, 300), 260, (150, 100, 40), 1)
    # стол и кружки
    d = ImageDraw.Draw(img)
    d.rectangle([40, 900, 680, 950], fill=(120, 84, 56), outline=INK, width=5)
    d.rectangle([70, 950, 100, H], fill=(100, 70, 48), outline=INK, width=4)
    d.rectangle([620, 950, 650, H], fill=(100, 70, 48), outline=INK, width=4)
    mug(d, 270, 900, 1.2, (220, 220, 214))
    mug(d, 470, 900, 1.2, (170, 60, 50))
    img = steam(img, t, 270, 800)
    img = steam(img, t + .5, 470, 800)
    return zoom(img, 1.02 + .14 * t / L, .5, .62)


def s14(t, L, cue):
    end = cue["14"] + dur("14.mp3") + .9
    img = vgrad(W, H, (90, 70, 56), (44, 36, 32))
    glow(img, (W, 500), 300, (150, 100, 40), .9)
    img = paste(img, rig.front_figure((W, H), W / 2, 2280, 1.5, t, "idle", "tense" if t < cue["14"] else "shock", (.7, 0)))
    img = zoom(img, 1.0 + .1 * min(1, t / end), .5, .32)
    if t > end:
        a = min(1, (t - end) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f2 = ImageFont.truetype(FONT_SUB, 62)
            for j, line in enumerate(("серия 2", "скоро")):
                dd.text(((W - f2.getlength(line)) / 2, 520 + j * 82), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    s10s, _ = span("s10")
    c10 = {c: s for n, st, l, sc in scenes if n == "s10" for s, c, d in sc}
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + 3.6, s10s + c10["10"], span("s12")[0] + 4.6, span("s14")[0] + .6],
        static=[(s10s, s10s + 1.6)])
