"""ВАХТА. Серия 1. Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
from toonlib import *
import toonlib

LINES = {
    "02": "Я оператор на буровой. Двести километров от берега, Баренцево море.",
    "03": "Вчера у нас закончилась вахта. Двадцать восемь дней. Сумки собраны, все ждут вертолёт.",
    "04": "Вертолёт не прилетел.",
    "05": "Михалыч сказал — шторм, перенесли. Нормально, бывает.",
    "06": "Только Даша с утра не может поймать берег. Ни Мурманск, ни соседние платформы. Тишина.",
    "07": "А ночью я вышел покурить и понял, что не так.",
    "08": "На горизонте всегда видно огни — танкеры, соседние платформы. Сегодня там ничего. Как будто мира больше нет.",
    "09": "В три ночи рация ожила.",
    "09r": "«Северная-семь, вижу вас. Захожу на посадку».",
    "10": "Мы выбежали на площадку. Ветер с ног сбивает. Ни вертолёта, ни шума винтов.",
    "11": "Только мокрые следы. От самого края площадки — внутрь платформы.",
    "12": "Под нами двадцать метров. И внизу — только море.",
}


# ---------- таймлайн ----------
PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2)], 0.4),
    ("s03", [("03", 0.1)], 0.4),
    ("s04", [("04", 0.5)], 1.0),
    ("s05", [("05", 0.2)], 0.4),
    ("s06", [("06", 0.2)], 0.5),
    ("s07", [("07", 0.2)], 0.6),
    ("s08", [("08", 0.2)], 0.8),
    ("s09", [("09", 0.1), ("09r", None)], 0.6),
    ("s10", [("10", 0.2)], 0.4),
    ("s11", [("11", 0.4)], 0.6),
    ("s12", [("12", 0.2)], 2.2),
]

setup(LINES, PLAN)

# ---------- сцены ----------
def s01(t, L):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    rnd = random.Random(1)
    for i in range(70):  # волны-чёрточки вид сверху
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        x = (x0 + 30 * t) % W
        d.line([x, y0, x + 40, y0], fill=(70, 84, 104), width=5)
    platform_top(img, W / 2 + 30, H / 2 + 120, 1.0, t)
    SNOW.draw(img, t)
    img = zoom(img, 1.12 - .1 * t / L)
    d = ImageDraw.Draw(img)
    a = min(1, max(0, (t - .3) / .5))
    f = ImageFont.truetype(FONT_SUB, 140)
    tw = f.getlength("ВАХТА")
    mask = Image.new("L", (W, H)); ImageDraw.Draw(mask).text(((W - tw) / 2, 170), "ВАХТА", font=f, fill=int(255 * a), stroke_width=12)
    img.paste(Image.new("RGB", (W, H), (200, 170, 50)), (0, 0), mask.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .6)))
    d.text(((W - tw) / 2, 170), "ВАХТА", font=f, fill=tuple(int(c * a) for c in YELLOW), stroke_width=5, stroke_fill=(58, 50, 14))
    f2 = ImageFont.truetype(FONT_SUB, 46)
    d.text(((W - f2.getlength("серия 1")) / 2, 340), "серия 1", font=f2, fill=(int(255 * a),) * 3, stroke_width=4, stroke_fill=INK)
    return img


def s02(t, L):
    img = bg_sea("sea_hi", horizon=560).copy()
    glow(img, (650, 300), 150, (110, 60, 20), .7)
    toon(img, W / 2, 1560, 1.9, "ilya", "neutral", ("down", "down"), (0, 0), t, talk=True, bob=3 * math.sin(t * 2))
    SNOW_BIG.draw(img, t)
    return zoom(img, 1 + .05 * t / L, .5, .4)


def s03(t, L):
    img = bg_room("canteen", (128, 136, 130), (90, 96, 92)).copy()
    d = ImageDraw.Draw(img)
    # иллюминатор и часы
    d.ellipse([70, 180, 230, 340], fill=(150, 150, 156), outline=INK, width=6)
    d.ellipse([92, 202, 208, 318], fill=(40, 48, 66), outline=INK, width=5)
    d.ellipse([480, 170, 610, 300], fill=(244, 244, 238), outline=INK, width=6)
    a = -math.pi / 2 + t * 1.2
    d.line([545, 235, 545 + 46 * math.cos(a), 235 + 46 * math.sin(a)], fill=(200, 40, 40), width=4)
    d.line([545, 235, 545 + 30 * math.cos(-1.1), 235 + 30 * math.sin(-1.1)], fill=INK, width=7)
    d.rectangle([0, 880, W, H], fill=(86, 88, 92))
    d.line([0, 880, W, 880], fill=INK, width=6)
    cast = [(150, 1000, .62, "timur", "neutral", (-1, 0)), (370, 985, .6, "misha", "serious", (0, 0)),
            (580, 1005, .62, "dasha", "neutral", (-1, 0))]
    for i, (x, y, s, who, face, lk) in enumerate(cast):
        d.rounded_rectangle([x - 100, y - 60, x + 100, y + 30], radius=28, fill=(60, 84, 140), outline=INK, width=5)
        d.line([x - 40, y - 60, x + 40, y - 60], fill=INK, width=6)
        toon(img, x, y - 40, s, who, face, ("down", "down"), lk, t + i, bob=2 * math.sin(t * 1.5 + i), legs=False)
    # Илья на переднем плане, сидит на сумке
    x, y = 360, 1500
    d.rounded_rectangle([x - 150, y - 90, x + 150, y + 40], radius=40, fill=(48, 70, 120), outline=INK, width=6)
    toon(img, x, y - 30, .95, "ilya", "neutral", ("front", "front"), (0, -.3), t, talk=True, legs=False)
    return zoom(img, 1 + .06 * t / L, .5, .55)


def s04(t, L):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, H / 2 - 60, 320
    d.regular_polygon((cx, cy, R), 8, rotation=22.5, fill=(70, 84, 72), outline=INK)
    d.regular_polygon((cx, cy, R - 4), 8, rotation=22.5, outline=INK)
    d.ellipse([cx - 230, cy - 230, cx + 230, cy + 230], outline=YELLOW, width=14)
    f = ImageFont.truetype(FONT_B, 290)
    d.text((cx - f.getlength("H") / 2, cy - 190), "H", font=f, fill=YELLOW, stroke_width=5, stroke_fill=INK)
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        x, y = cx + (R - 24) * math.cos(a), cy + (R - 24) * math.sin(a)
        on = int(t * 2 + k) % 2 == 0
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(90, 255, 140) if on else (30, 70, 40), outline=INK, width=3)
    STORM.draw(img, t, streak=True)
    return zoom(img, 1.02 + .04 * t / L)


def s05(t, L):
    img = bg_room("office", (120, 120, 128), (84, 84, 92)).copy()
    window(img, (90, 160, 630, 760), t, (520, 420))
    toon(img, W / 2, 1230, 1.35, "misha", "serious", ("front", "front"), (.4, 0), t, talk=True)
    return zoom(img, 1 + .06 * t / L, .5, .5)


def s06(t, L):
    img = bg_room("radio", (70, 92, 88), (46, 58, 56)).copy()
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(int(t * 24))
    for (x, y, w, h) in [(50, 220, 290, 210), (380, 220, 290, 210)]:
        d.rectangle([x - 10, y - 10, x + w + 10, y + h + 10], fill=(60, 64, 66), outline=INK, width=6)
        n = Image.fromarray(rng.integers(30, 200, (h // 6, w // 6), dtype=np.uint8), "L").resize((w, h), Image.NEAREST)
        img.paste(Image.merge("RGB", (n.point(lambda v: v * .4), n, n.point(lambda v: v * .6))), (x, y))
    d.rectangle([0, 960, W, H], fill=(84, 88, 90), outline=INK, width=6)
    d.rectangle([60, 980, 660, 1040], fill=(20, 40, 28), outline=INK, width=5)
    px = 80 + (math.sin(t * .8) * .5 + .5) * 560
    d.line([px, 984, px, 1036], fill=(255, 80, 60), width=4)
    toon(img, W / 2 + 20, 1290, 1.45, "dasha", "worried", ("down", "ear"), (-.6, .2), t)
    return zoom(img, 1 + .05 * t / L, .5, .45)


def s07(t, L):
    img = bg_sea("sea_mid", horizon=700).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1060, W, H], fill=(112, 116, 124)); d.line([0, 1060, W, 1060], fill=INK, width=6)
    railing(d, 940)
    hands = toon(img, W / 2, 1110, 1.0, "ilya", "neutral" if t < L * .6 else "worried", ("down", "ear" if t > .6 else "down"), (0, 0) if t < L * .6 else (.8, -.2), t)
    if t > .6:  # сигарета и огонёк
        hx, hy = hands[1]
        cig = .6 + .4 * math.sin(t * 2.5)
        d.line([hx - 4, hy - 4, hx - 30, hy + 4], fill=(240, 240, 240), width=7)
        glow(img, (hx - 32, hy + 4), 14, (int(220 * cig), int(90 * cig), 20), 1)
        if t < 1.5:
            flame(img, hx + 4, hy - 26, t, .35)
    SNOW.draw(img, t)
    return zoom(img, 1 + .04 * t / L, .5, .6)


FAR = [(150, .30, 3.4), (420, .20, 4.3), (610, .36, 5.2)]  # x, масштаб, когда гаснет


def s08(t, L):
    img = bg_sea("sea_dark", horizon=700, lights=False, seed=12).copy()
    for i, (x, sc, off) in enumerate(FAR):
        k = 1 - min(1, max(0, (t - off) / .35))          # свет
        fade = 1 - min(1, max(0, (t - off - .3) / .9))   # силуэт
        if k > 0:
            paste_platform(img, x, 704, sc, lit=True, light_k=k * (.85 + .15 * math.sin(t * 5 + i)))
        else:
            paste_platform(img, x, 704, sc, lit=False, alpha=.12 + .88 * fade)
    toon(img, 590, 1620, 1.05, "ilya", "worried" if t > 4 else "neutral", ("down", "down"), (-.8, -.3), t, legs=False)
    SNOW.draw(img, t)
    return zoom(img, 1.06 - .05 * t / L, .5, .5)


def s09(t, L, cue):
    rt = cue["09r"]
    on = t > rt - .3
    img = bg_room("radio2", (54, 66, 64), (34, 40, 40)).copy()
    d = ImageDraw.Draw(img)
    if t < rt + .4:  # рация крупно
        d.rounded_rectangle([110, 300, 610, 780], radius=30, fill=(80, 86, 84), outline=INK, width=8)
        d.rounded_rectangle([140, 330, 580, 440], radius=12, fill=(20, 40, 28), outline=INK, width=5)
        for gx in range(160, 520, 26):
            for gy in range(480, 740, 26):
                d.ellipse([gx, gy, gx + 12, gy + 12], fill=(50, 54, 52))
        led_on = (on and int(t * 8) % 2 == 0) or (not on and int(t * 1.5) % 4 == 0)
        d.ellipse([530, 520, 580, 570], fill=(90, 255, 140) if led_on else (30, 70, 40), outline=INK, width=5)
        if led_on:
            glow(img, (555, 545), 60, (20, 140, 60), 1)
        d.line([500, 300, 540, 120], fill=INK, width=14)
        if on:
            rnd = random.Random(int(t * 20))
            for k in range(18):
                h = rnd.uniform(6, 80)
                d.rectangle([160 + k * 23, 430 - h, 174 + k * 23, 430], fill=(90, 255, 140))
        img = zoom(img, 1 + .03 * t, .5, .45)
    else:  # Даша в шоке
        toon(img, W / 2, 1300, 1.5, "dasha", "shock", ("up", "up"), (0, -.2), t)
        rnd = random.Random(int(t * 20))
        for k in range(18):
            h = rnd.uniform(6, 60)
            d.rectangle([150 + k * 23, 1250 - h, 164 + k * 23, 1250], fill=(90, 255, 140))
        img = zoom(img, 1.08 - .04 * min(1, (t - rt) / 2), .5, .45)
    if on:
        img = shake(img, t, 8 * max(0, 1 - (t - rt) / 1.2))
    return img


def s10(t, L):
    img = vgrad(W, H, (100, 102, 110), (70, 72, 80))
    d = ImageDraw.Draw(img)
    d.polygon([(-260, H), (W + 260, H), (W - 90, 720), (90, 720)], fill=(70, 84, 72), outline=INK)
    d.line([90, 720, -260, H], fill=YELLOW, width=10)
    d.line([W - 90, 720, W + 260, H], fill=YELLOW, width=10)
    who = [("ilya", 230, 1240, .78, 0), ("timur", 480, 1200, .72, 1.6), ("misha", 600, 1020, .5, 3.1), ("dasha", 140, 1010, .5, 4.4)]
    for i, (w, x, y, s, ph) in enumerate(sorted(who, key=lambda v: v[2])):
        hands = toon(img, x + 15 * math.sin(t + i), y - 20 * t, s, w, "scared" if t > 3 else "worried",
                     ("down", "point"), (0, -1), t + ph, walk=t + ph, bob=8 * abs(math.sin((t + ph) * 9)))
        hx, hy = hands[1]
        lay = Image.new("L", (W, H)); ImageDraw.Draw(lay).polygon(
            [(hx, hy), (hx + 520, hy - 560 + 60 * math.sin(t * 1.3 + i)), (hx + 300, hy - 700 + 60 * math.sin(t * 1.3 + i))], fill=90)
        img.paste(Image.new("RGB", (W, H), (255, 246, 210)), (0, 0), lay.filter(ImageFilter.GaussianBlur(16)))
    STORM.draw(img, t, streak=True)
    return zoom(shake(img, t, 5), 1.06, .5, .6)


def _path_x(k):
    return 330 + 40 * math.sin(k * .5)


STEPS = []
for _k in range(11):
    _ang = math.atan2(40 * .5 * math.cos(_k * .5), 78) * -1
    _side = 1 if _k % 2 else -1
    STEPS.append((_path_x(_k) + _side * 24 * math.cos(_ang), 1200 - _k * 78, _ang, _k % 2 == 0))


def s11(t, L):
    base = Image.new("RGB", (W, H), DECK)
    d = ImageDraw.Draw(base)
    for y in range(0, H, 46):
        d.line([0, y, W, y], fill=(80, 84, 92), width=3)
    d.rectangle([230, 90, 490, 420], fill=(176, 176, 182), outline=INK, width=8)
    gap = 22 + 6 * math.sin(t * 2)
    d.rectangle([360 - gap / 2, 104, 360 + gap / 2, 414], fill=(255, 210, 120))
    for (x, y, ang, left) in STEPS:
        boot_print(d, x, y, .7 + .45 * y / H, ang, left)
    dark = Image.eval(base, lambda v: int(v * .32))
    p = min(1, t / (L * .8))
    ty = 1240 - p * 1000
    tx = _path_x((1200 - ty) / 78)
    m = Image.new("L", (W, H)); md = ImageDraw.Draw(m)
    md.polygon([(W / 2 - 40, H + 40), (W / 2 + 40, H + 40), (tx + 170, ty - 100), (tx - 170, ty - 100)], fill=255)
    md.ellipse([tx - 190, ty - 200, tx + 190, ty + 140], fill=255)
    img = Image.composite(base, dark, m.filter(ImageFilter.GaussianBlur(26)))
    glow(img, (360, 260), 80, (100, 70, 20), .6)
    SNOW.draw(img, t, wind=300)
    return zoom(img, 1.04)


def s12(t, L):
    half = L * .42
    if t < half:  # Илья смотрит вниз
        img = bg_sea("sea_mid", horizon=700).copy()
        d = ImageDraw.Draw(img)
        toon(img, W / 2, 1330, 1.55, "ilya", "scared", ("down", "down"), (0, 1), t)
        SNOW_BIG.draw(img, t)
        return zoom(img, 1 + .05 * t / half, .5, .4)
    tt = t - half
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    rnd = random.Random(9)
    for i in range(80):  # пена, вид сверху
        x0, y0 = rnd.uniform(0, W), rnd.uniform(380, H)
        ph = rnd.random() * 6.3
        a = .5 + .5 * math.sin(tt * 1.6 + ph)
        w = rnd.uniform(30, 90) * (.6 + .4 * a)
        x = x0 + 18 * math.sin(tt * .7 + ph)
        d.rounded_rectangle([x - w / 2, y0 - 7, x + w / 2, y0 + 7], radius=7, fill=(150 + int(60 * a),) * 2 + (220,))
    for x1, x2 in [(90, 250), (630, 470)]:
        d.polygon([(x1 - 46, 380), (x1 + 46, 380), (x2 + 14, H), (x2 - 14, H)], fill=(110, 114, 124), outline=INK)
    d.rectangle([0, 0, W, 380], fill=DECK, outline=INK, width=8)
    for k in range(-40, W + 60, 64):
        d.polygon([(k, 340), (k + 32, 340), (k + 12, 380), (k - 20, 380)], fill=YELLOW)
    d.line([0, 380, W, 380], fill=INK, width=8)
    # мокрый след у самого края
    boot_print(d, 330, 330, .85, 0, True)
    boot_print(d, 380, 240, .85, .05, False)
    boot_print(d, 336, 150, .85, 0, True)
    img = zoom(img, 1 + .12 * tt / (L - half), .5, .7)
    fade = max(0, (t - (L - 1.6)) / 1.2)
    if fade:
        img = Image.blend(img, Image.new("RGB", (W, H)), min(1, fade))
    return img


if __name__ == "__main__":
    s6, l6 = span("s06"); s9, l9 = span("s09")
    run({n: globals()[n] for n, *_ in PLAN}, static=[(s6, s6 + l6), (s9, s9 + l9)], hits=[span("s11")[0] + .3])
