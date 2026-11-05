"""Рендер серии 1 «Вахта» — плоская мультяшная 2D-анимация кодом (PIL + ffmpeg).

Стиль: толстый чёрный контур, большие белые глаза, плоские цвета,
размытый серый фон с оранжевыми огоньками, жёлтые субтитры по 2–3 слова.

Запуск:  python3 render.py <папка_с_озвучкой> <выходной.mp4>
Превью:  PREVIEW=3.0,10.5 python3 render.py ../tts out   → out_3.0.png …
"""
import math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 720, 1280, 24
TTS = sys.argv[1] if len(sys.argv) > 1 else "tts"
OUT = sys.argv[2] if len(sys.argv) > 2 else "vakhta_s01.mp4"
FONT_SUB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

# ---------- палитра ----------
INK = (26, 24, 28)            # контур
SKIN = (226, 178, 140)
SKIN_D = (206, 156, 120)
BLUSH = (232, 150, 140)
COVER = (232, 108, 38)        # оранжевый комбинезон
COVER_D = (196, 84, 28)
REFL = (214, 218, 222)        # светоотражающие полосы
NAVY = (44, 58, 92)
GREY = (150, 150, 156)
YELLOW = (250, 226, 90)
DECK = (92, 96, 104)
SEA = (44, 54, 72)
O = 5                         # толщина контура (при масштабе 1)

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


def dur(name):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", os.path.join(TTS, name)])
    return float(out)


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

scenes, cues = [], []
T = 0.0
for name, clips, tail in PLAN:
    local, sc = 0.0, []
    for clip, delay in clips:
        d = dur(clip + ".mp3")
        start = (local + 0.4) if delay is None else delay
        sc.append((start, clip, d))
        local = start + d
    length = local + tail
    scenes.append((name, T, length, sc))
    cues += [(T + s, c, d) for s, c, d in sc]
    T += length
TOTAL = T

# ---------- субтитры: по 2–3 слова, строчными ----------
SUBS = []
for start, clip, d in cues:
    words = LINES[clip].replace("«", "").replace("»", "").lower().split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        n = len(" ".join(cur))
        if (len(cur) >= 3 or n >= 14 or w[-1] in ".,!?—") and not (len(cur) == 1 and w == "—"):
            chunks.append(" ".join(cur)); cur = []
    if cur:
        chunks.append(" ".join(cur))
    chunks = [c.rstrip(".,") for c in chunks]
    weights = [len(c) + 4 for c in chunks]
    tw = sum(weights)
    t = start
    for c, wgt in zip(chunks, weights):
        dd = d * wgt / tw
        SUBS.append((t, t + dd, c, clip == "09r"))
        t += dd

F_SUB = ImageFont.truetype(FONT_SUB, 62)


def draw_subs(img, t):
    for s, e, text, radio in SUBS:
        if s <= t < e:
            lines, cur = [], ""
            for w in text.split():
                test = (cur + " " + w).strip()
                if F_SUB.getlength(test) > W - 90 and cur:
                    lines.append(cur); cur = w
                else:
                    cur = test
            lines.append(cur)
            pop = min(1, (t - s) / 0.08)
            y0 = int(H * 0.64)
            col = (150, 255, 170) if radio else YELLOW
            mask = Image.new("L", (W, H), 0)
            md = ImageDraw.Draw(mask)
            pos = []
            for i, ln in enumerate(lines):
                x = (W - F_SUB.getlength(ln)) / 2
                y = y0 + i * 74 + (1 - pop) * 10
                pos.append((x, y, ln))
                md.text((x, y), ln, font=F_SUB, fill=255, stroke_width=10)
            gl = mask.filter(ImageFilter.GaussianBlur(14))
            img.paste(Image.new("RGB", (W, H), tuple(int(c * 0.8) for c in col)), (0, 0), gl.point(lambda v: int(v * 0.55)))
            d = ImageDraw.Draw(img)
            for x, y, ln in pos:
                d.text((x, y), ln, font=F_SUB, fill=col, stroke_width=4, stroke_fill=(58, 50, 14))
            return


# ---------- утилиты ----------
def vgrad(w, h, top, bottom):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - a) + np.array(bottom)[None, None, :] * a
    return Image.fromarray(np.repeat(arr, w, axis=1).astype(np.uint8), "RGB")


def glow(img, xy, r, color, k=1.0):
    r = int(r); size = r * 4
    layer = Image.new("RGB", (size, size))
    ImageDraw.Draw(layer).ellipse([r, r, 3 * r, 3 * r], fill=tuple(int(c * k) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.6))
    bx, by = int(xy[0] - 2 * r), int(xy[1] - 2 * r)
    img.paste(ImageChops.add(img.crop((bx, by, bx + size, by + size)), layer), (bx, by))


def zoom(img, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-3:
        return img
    w, h = W / z, H / z
    x0, y0 = (W - w) * cx, (H - h) * cy
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def shake(img, t, amt):
    return ImageChops.offset(img, int(amt * math.sin(t * 37) * math.cos(t * 13)), int(amt * math.sin(t * 29 + 1)))


_y, _x = np.mgrid[0:H, 0:W]
VIG = np.clip(1.12 - 0.42 * (((_x - W / 2) / (W / 2)) ** 2 + ((_y - H / 2) / (H / 2)) ** 2), 0.45, 1.0)[:, :, None]


def grade(img):
    return Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * VIG, 0, 255).astype(np.uint8))


class Snow:
    def __init__(self, n, seed, size=(2, 5), speed=(80, 200), wind=120):
        rnd = random.Random(seed)
        self.p = [(rnd.random() * W, rnd.random() * H, rnd.uniform(*size), rnd.uniform(*speed), rnd.uniform(.6, 1.4), rnd.random() * 6.3) for _ in range(n)]
        self.wind = wind

    def draw(self, img, t, wind=None, streak=False, col=(236, 238, 242)):
        wind = self.wind if wind is None else wind
        d = ImageDraw.Draw(img)
        for x0, y0, s, sp, wf, ph in self.p:
            x = (x0 + wind * wf * t + 12 * math.sin(t * 1.7 + ph)) % (W + 40) - 20
            y = (y0 + sp * t) % (H + 40) - 20
            if streak:
                d.line([x, y, x - 60 * wf, y - 8], fill=(200, 204, 212), width=max(2, int(s * .6)))
            else:
                d.ellipse([x - s, y - s, x + s, y + s], fill=col)


SNOW = Snow(120, 1)
SNOW_BIG = Snow(60, 2, size=(4, 7), speed=(150, 280), wind=180)
STORM = Snow(90, 3, size=(2, 4), speed=(200, 400), wind=900)


# ---------- фоны (рисуются один раз и размываются) ----------
_BG = {}


def smoke(img, seed, n=14, alpha=70):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        side = rnd.choice([0, 1])
        x = rnd.uniform(-60, 160) if side == 0 else rnd.uniform(560, 780)
        y = rnd.uniform(80, 900)
        r = rnd.uniform(70, 130)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(40, 40, 46, alpha), outline=(30, 30, 34, alpha + 20), width=4)
    return Image.alpha_composite(img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(2))).convert("RGB")


def bg_sea(key="sea", horizon=720, lights=True, blur=5, seed=11):
    if key in _BG:
        return _BG[key]
    img = vgrad(W, H, (104, 104, 112), (70, 72, 82))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    d.rectangle([0, horizon, W, H], fill=SEA)
    # «пиксельное» море: блоки разной высоты
    for _ in range(260):
        x = rnd.randrange(0, W, 18); y = rnd.uniform(horizon, H)
        w = rnd.choice([18, 36, 54]); h = rnd.uniform(10, 60)
        c = rnd.randint(36, 70)
        d.rectangle([x, y, x + w, y + h], fill=(c, c + 8, c + 22))
    if lights:  # далёкие платформы с огнями
        for (px, ps) in ((110, .20), (520, .14), (660, .24)):
            paste_platform(img, px + rnd.uniform(-20, 20), horizon + 4, ps)
    img = img.filter(ImageFilter.GaussianBlur(blur))
    img = smoke(img, seed)
    _BG[key] = img
    return img


def bg_room(key, top, bottom, seed=5):
    if key in _BG:
        return _BG[key]
    img = vgrad(W, H, top, bottom)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(90):
        x = rnd.randrange(0, W, 24); y = rnd.uniform(0, H)
        c = tuple(max(0, v - rnd.randint(4, 18)) for v in top)
        d.rectangle([x, y, x + rnd.choice([24, 48]), y + rnd.uniform(20, 90)], fill=c)
    img = img.filter(ImageFilter.GaussianBlur(6))
    _BG[key] = img
    return img


# ---------- персонаж ----------
def limb(d, a, b, w, color, s):
    o = O * s
    d.line([a, b], fill=INK, width=int(w + 2 * o))
    for p in (a, b):
        r = w / 2 + o
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=INK)
    d.line([a, b], fill=color, width=int(w))
    for p in (a, b):
        r = w / 2
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


def hand(d, p, s):
    r = 20 * s
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=SKIN, outline=INK, width=int(O * s))


def toon(img, x, y, s, who="ilya", face="neutral", arms=("down", "down"), look=(0, 0),
         t=0.0, talk=False, blink=True, walk=None, bob=0.0, legs=True):
    """Мультяшный человек. (x, y) — точка между ступнями. s — масштаб."""
    d = ImageDraw.Draw(img)
    o = int(O * s)
    y = y - bob * s
    look_x, look_y = look
    outfit = {"ilya": COVER, "timur": COVER, "misha": NAVY, "dasha": (52, 120, 128)}[who]
    pants = {"ilya": COVER_D, "timur": COVER_D, "misha": (70, 72, 80), "dasha": (60, 62, 72)}[who]
    # ноги
    if legs:
        for side in (-1, 1):
            k = 0 if walk is None else math.sin(walk * 9 + (0 if side < 0 else math.pi))
            lx = x + side * 30 * s + k * 24 * s
            d.rectangle([lx - 26 * s, y - 190 * s, lx + 26 * s, y - 28 * s], fill=pants, outline=INK, width=o)
            if who in ("ilya", "timur"):
                d.rectangle([lx - 26 * s + o, y - 95 * s, lx + 26 * s - o, y - 82 * s], fill=REFL)
            d.rounded_rectangle([lx - 34 * s, y - 34 * s, lx + 34 * s, y], radius=int(10 * s), fill=(106, 66, 34), outline=INK, width=o)
    # руки (за туловищем)
    sh_y = y - 350 * s
    hands = []
    for side, pose in zip((-1, 1), arms):
        sx = x + side * 62 * s
        sw = 0 if walk is None else math.sin(walk * 9 + (math.pi if side < 0 else 0)) * 0.5
        ang = {"down": 1.45 + sw, "out": 0.5, "up": -0.6, "point": 0.15, "hip": 1.0,
               "front": 1.2, "ear": -1.2, "shrug": 0.9}[pose]
        ln = 175 * s
        if pose == "ear":
            ex, ey = sx + side * 15 * s, sh_y - 120 * s
        elif pose == "front":
            ex, ey = x + side * 20 * s, sh_y + 150 * s
        else:
            ex, ey = sx + side * ln * math.cos(ang), sh_y + ln * math.sin(ang)
        limb(d, (sx, sh_y), (ex, ey), 46 * s, outfit if who != "dasha" else (52, 120, 128), s)
        hands.append((ex, ey))
    # туловище
    d.rounded_rectangle([x - 78 * s, y - 380 * s, x + 78 * s, y - 175 * s], radius=int(18 * s), fill=outfit, outline=INK, width=o)
    if who in ("ilya", "timur"):
        for yy in (-300, -240):
            d.rectangle([x - 78 * s + o, y + yy * s, x + 78 * s - o, y + (yy + 14) * s], fill=REFL)
        d.rectangle([x - 6 * s, y - 376 * s, x + 6 * s, y - 180 * s], fill=COVER_D)
        d.rounded_rectangle([x + 18 * s, y - 360 * s, x + 64 * s, y - 334 * s], radius=int(4 * s), fill=(40, 44, 56), outline=INK, width=max(2, o // 2))
    elif who == "misha":
        d.polygon([(x - 30 * s, y - 380 * s), (x, y - 330 * s), (x + 30 * s, y - 380 * s)], fill=(210, 210, 214), outline=INK)
        d.line([x, y - 330 * s, x, y - 180 * s], fill=INK, width=max(2, o // 2))
    elif who == "dasha":
        d.polygon([(x - 34 * s, y - 380 * s), (x, y - 345 * s), (x + 34 * s, y - 380 * s)], fill=(36, 92, 100), outline=INK)
    # шея
    d.rectangle([x - 22 * s, y - 410 * s, x + 22 * s, y - 376 * s], fill=SKIN_D, outline=INK, width=o)
    # голова
    hx, hy, R = x, y - 505 * s, 92 * s
    if who == "dasha":  # волосы сзади (каре)
        d.rounded_rectangle([hx - R - 14 * s, hy - R - 10 * s, hx + R + 14 * s, hy + 62 * s], radius=int(50 * s), fill=(34, 28, 30), outline=INK, width=o)
    for side in (-1, 1):  # уши
        d.ellipse([hx + side * R - 16 * s, hy - 6 * s, hx + side * R + 16 * s, hy + 34 * s], fill=SKIN, outline=INK, width=o)
    d.ellipse([hx - R, hy - R * 1.05, hx + R, hy + R * 1.05], fill=SKIN, outline=INK, width=o)
    if who == "ilya":  # рыжая щетина
        d.chord([hx - R + o, hy - R * 1.05 + o, hx + R - o, hy + R * 1.05 - o], 15, 165, fill=(214, 150, 108))
    if who == "misha":
        d.chord([hx - R + o, hy - R * 1.05 + o, hx + R - o, hy + R * 1.05 - o], 25, 155, fill=(210, 168, 134))
    # румянец
    for side in (-1, 1):
        d.ellipse([hx + side * 52 * s - 20 * s, hy + 18 * s, hx + side * 52 * s + 20 * s, hy + 36 * s], fill=BLUSH)
    # глаза
    big = face in ("shock", "scared")
    ew, eh = (30 if big else 27) * s, (36 if big else 31) * s
    closed = blink and (t % 3.3) < 0.1 and not big
    for side in (-1, 1):
        ex, ey = hx + side * 36 * s, hy - 14 * s
        if closed:
            d.line([ex - ew, ey, ex + ew, ey], fill=INK, width=o)
        else:
            d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh], fill=(255, 255, 255), outline=INK, width=o)
            pr = (9 if big else 11) * s
            px, py = ex + look_x * 10 * s, ey + look_y * 10 * s + 4 * s
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=INK)
        if face in ("worried", "scared"):
            d.line([ex - 24 * s, ey - eh - 10 * s - side * 6 * s, ex + 24 * s, ey - eh - 10 * s + side * 6 * s], fill=INK, width=o)
        if face == "serious" or who == "misha":
            d.line([ex - 26 * s, ey - eh - 6 * s + side * 8 * s, ex + 26 * s, ey - eh - 6 * s - side * 8 * s], fill=INK, width=int(o * 1.4))
    # нос
    d.arc([hx - 10 * s, hy + 14 * s, hx + 12 * s, hy + 36 * s], 270, 120, fill=INK, width=max(2, o - 1))
    # рот
    my = hy + 58 * s
    if who == "misha":  # седые усы
        d.chord([hx - 44 * s, my - 26 * s, hx + 44 * s, my + 14 * s], 180, 360, fill=(220, 220, 224), outline=INK, width=max(2, o - 1))
    open_ = talk and (math.sin(t * 17) + math.sin(t * 11.3)) > 0.3
    if face in ("shock", "scared") or open_:
        rw, rh = (16 * s, 22 * s) if face in ("shock", "scared") else (14 * s, 10 * s)
        d.ellipse([hx - rw, my - rh + 4 * s, hx + rw, my + rh + 4 * s], fill=(150, 40, 40), outline=INK, width=max(2, o - 1))
    elif face == "smile":
        d.arc([hx - 26 * s, my - 22 * s, hx + 26 * s, my + 8 * s], 30, 150, fill=INK, width=o)
    elif face in ("worried", "sad"):
        d.arc([hx - 22 * s, my, hx + 22 * s, my + 26 * s], 210, 330, fill=INK, width=o)
    else:
        d.line([hx - 18 * s, my + 4 * s, hx + 18 * s, my + 4 * s], fill=INK, width=o)
    # головной убор / причёска
    if who in ("ilya",):  # чёрная вязаная шапка
        d.chord([hx - R - 6 * s, hy - R * 1.12, hx + R + 6 * s, hy + 10 * s], 180, 360, fill=(36, 36, 42), outline=INK, width=o)
        d.rounded_rectangle([hx - R - 8 * s, hy - 62 * s, hx + R + 8 * s, hy - 32 * s], radius=int(8 * s), fill=(48, 48, 56), outline=INK, width=o)
        for k in range(-80, 85, 16):
            d.line([hx + k * s, hy - 58 * s, hx + k * s, hy - 36 * s], fill=(30, 30, 36), width=max(2, int(3 * s)))
    elif who == "timur":  # каска
        d.chord([hx - R, hy - R * 1.25, hx + R, hy + 20 * s], 180, 360, fill=(232, 170, 60), outline=INK, width=o)
        d.rounded_rectangle([hx - R - 22 * s, hy - 46 * s, hx + R + 22 * s, hy - 30 * s], radius=int(6 * s), fill=(232, 170, 60), outline=INK, width=o)
        d.arc([hx - 60 * s, hy - 100 * s, hx + 10 * s, hy - 40 * s], 200, 260, fill=(250, 220, 150), width=int(9 * s))
    elif who == "misha":
        d.chord([hx - R + 2, hy - R * 1.06, hx + R - 2, hy - 10 * s], 180, 360, fill=(196, 196, 202), outline=INK, width=o)
    elif who == "dasha":
        d.chord([hx - R - 4 * s, hy - R * 1.12, hx + R + 4 * s, hy - 10 * s], 180, 360, fill=(34, 28, 30), outline=INK, width=o)
        d.arc([hx - R - 12 * s, hy - R - 22 * s, hx + R + 12 * s, hy + 40 * s], 190, 350, fill=(40, 40, 46), width=int(14 * s))
        for side in (-1, 1):
            d.rounded_rectangle([hx + side * (R + 4 * s) - 18 * s, hy - 20 * s, hx + side * (R + 4 * s) + 18 * s, hy + 34 * s], radius=int(10 * s), fill=(54, 54, 62), outline=INK, width=o)
    # кисти — поверх всего, если руки подняты к лицу
    for hp in hands:
        hand(d, hp, s)
    return hands


# ---------- объекты ----------
def flame(img, x, y, t, s=1.0):
    d = ImageDraw.Draw(img)
    f = 1 + .15 * math.sin(t * 11) + .08 * math.sin(t * 23)
    glow(img, (x, y - 20 * s), 90 * s * f, (120, 60, 20), .8)
    r = 26 * s * f
    sway = 8 * s * math.sin(t * 7)
    d.polygon([(x - r, y), (x + r, y), (x + sway, y - r * 3)], fill=(244, 120, 40), outline=INK)
    d.ellipse([x - r, y - r * .8, x + r, y + r * .5], fill=(244, 120, 40), outline=INK, width=int(4 * s))
    d.polygon([(x - r * .5, y), (x + r * .5, y), (x + sway * .6, y - r * 1.8)], fill=(255, 214, 90))


def platform_top(img, cx, cy, s, t):
    """платформа вид сверху, в стиле схемы"""
    d = ImageDraw.Draw(img)
    o = int(5 * s)
    d.rounded_rectangle([cx - 160 * s, cy - 220 * s, cx + 160 * s, cy + 220 * s], radius=int(10 * s), fill=DECK, outline=INK, width=o)
    for k in range(-200, 220, 40):
        d.line([cx - 155 * s, cy + k * s, cx + 155 * s, cy + k * s], fill=(84, 88, 96), width=2)
    # жилой блок
    d.rectangle([cx - 140 * s, cy + 40 * s, cx + 20 * s, cy + 200 * s], fill=(196, 196, 200), outline=INK, width=o)
    d.rectangle([cx - 120 * s, cy + 60 * s, cx, cy + 180 * s], fill=(176, 176, 182))
    # вертолётная площадка
    d.regular_polygon((cx + 230 * s, cy + 130 * s, 110 * s), 8, rotation=22.5, fill=(70, 84, 72), outline=INK)
    d.ellipse([cx + 160 * s, cy + 60 * s, cx + 300 * s, cy + 200 * s], outline=YELLOW, width=int(6 * s))
    fh = ImageFont.truetype(FONT_B, int(90 * s))
    d.text((cx + 230 * s - fh.getlength("H") / 2, cy + 78 * s), "H", font=fh, fill=YELLOW)
    # вышка
    d.rectangle([cx + 40 * s, cy - 160 * s, cx + 130 * s, cy - 70 * s], fill=(212, 92, 40), outline=INK, width=o)
    d.line([cx + 40 * s, cy - 160 * s, cx + 130 * s, cy - 70 * s], fill=INK, width=o)
    d.line([cx + 130 * s, cy - 160 * s, cx + 40 * s, cy - 70 * s], fill=INK, width=o)
    # факельная стрела
    d.line([cx - 150 * s, cy - 200 * s, cx - 270 * s, cy - 330 * s], fill=(120, 124, 132), width=int(14 * s))
    flame(img, cx - 275 * s, cy - 320 * s, t, s * .9)
    # контейнеры
    for i, c in enumerate([(70, 110, 170), (190, 60, 60), (210, 170, 60)]):
        d.rectangle([cx - 140 * s + i * 50 * s, cy - 180 * s, cx - 100 * s + i * 50 * s, cy - 90 * s], fill=c, outline=INK, width=int(4 * s))


def railing(d, y, col=(226, 110, 40)):
    d.line([0, y, W, y + 6], fill=col, width=7)
    for x in range(20, W, 130):
        d.line([x, y, x + 10, y + 180], fill=col, width=7)



# ---------- морская платформа сбоку (дальний план) ----------
_PLAT = {}


def platform_layer(s, lit):
    """RGBA-слой платформы. Якорь: центр по x, ватерлиния по y → (ax, ay)."""
    key = (round(s, 3), lit)
    if key in _PLAT:
        return _PLAT[key]
    Wl, Hl = int(820 * s), int(720 * s)
    ax, ay = 400 * s, 680 * s
    lay = Image.new("RGBA", (Wl, Hl), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    o = max(1, int(5 * s))
    P = lambda u, v: (ax + u * s, ay + v * s)
    R = lambda u0, v0, u1, v1: [ax + u0 * s, ay + v0 * s, ax + u1 * s, ay + v1 * s]
    LIGHT, MID, DARKG = (214, 216, 222), (184, 188, 196), (150, 154, 162)
    WIN = (255, 214, 110) if lit else (110, 114, 124)
    lights = []
    # раскосы между опорами
    d.rectangle(R(-260, -150, 180, -122), fill=None, outline=INK, width=o)
    for u in range(-260, 180, 44):
        d.line([P(u, -150), P(u + 44, -122)], fill=INK, width=o)
        d.line([P(u, -122), P(u + 44, -150)], fill=INK, width=o)
    # опоры
    for u in (-250, -110, 30, 170):
        d.rectangle(R(u - 26, -150, u + 26, -66), fill=LIGHT, outline=INK, width=o)
        d.rectangle(R(u - 26, -66, u + 26, -56), fill=(232, 96, 60), outline=INK, width=max(1, o // 2))
        d.rectangle(R(u - 26, -56, u + 26, 10), fill=(40, 42, 48), outline=INK, width=o)
        d.polygon([P(u - 34, -150), P(u + 34, -150), P(u + 24, -168), P(u - 24, -168)], fill=MID, outline=INK)
    # диагональная подпорка и лестница
    d.line([P(370, -190), P(176, -70)], fill=DARKG, width=max(2, int(9 * s)))
    d.line([P(200, -190), P(200, 0)], fill=DARKG, width=max(1, int(5 * s)))
    for v in range(-180, 0, 18):
        d.line([P(192, v), P(212, v)], fill=DARKG, width=max(1, int(3 * s)))
    # нижняя палуба
    d.rectangle(R(-300, -215, 100, -160), fill=LIGHT, outline=INK, width=o)
    d.rectangle(R(-300, -215, -160, -160), fill=MID, outline=INK, width=o)
    for u in (-120, -50, 20, 80):
        d.rounded_rectangle(R(u - 14, -202, u + 14, -176), radius=max(1, int(4 * s)), fill=WIN, outline=INK, width=max(1, o // 2))
        lights.append(P(u, -189))
    # перила
    d.line([P(-300, -232), P(100, -232)], fill=INK, width=max(1, o // 2))
    for u in range(-300, 101, 20):
        d.line([P(u, -232), P(u, -215)], fill=INK, width=max(1, o // 2))
    # модуль с обшивкой
    d.rectangle(R(-20, -330, 375, -190), fill=LIGHT, outline=INK, width=o)
    for u in range(0, 375, 22):
        d.line([P(u, -326), P(u, -194)], fill=DARKG, width=max(1, int(3 * s)))
    for u in (40, 150, 260):
        d.rectangle(R(u, -300, u + 22, -284), fill=WIN, outline=INK, width=max(1, o // 2))
        lights.append(P(u + 11, -292))
    # надстройка справа
    d.rectangle(R(270, -400, 335, -330), fill=MID, outline=INK, width=o)
    for v in (-388, -366, -344):
        d.rectangle(R(282, v, 296, v + 10), fill=WIN)
        lights.append(P(289, v + 5))
    # буровая вышка
    def lattice(ub, vb, vt, wb, wt, lean=0):
        pts_l = [P(ub - wb + lean * 0, vb), P(ub - wt + lean, vt)]
        pts_r = [P(ub + wb, vb), P(ub + wt + lean, vt)]
        d.line(pts_l, fill=INK, width=max(1, int(4 * s)))
        d.line(pts_r, fill=INK, width=max(1, int(4 * s)))
        n = 9
        for k in range(n):
            f0, f1 = k / n, (k + 1) / n
            v0, v1 = vb + (vt - vb) * f0, vb + (vt - vb) * f1
            w0, w1 = wb + (wt - wb) * f0, wb + (wt - wb) * f1
            l0, l1 = lean * f0, lean * f1
            d.line([P(ub - w0 + l0, v0), P(ub + w0 + l0, v0)], fill=INK, width=max(1, int(3 * s)))
            d.line([P(ub - w0 + l0, v0), P(ub + w1 + l1, v1)], fill=INK, width=max(1, int(2 * s)))
            d.line([P(ub + w0 + l0, v0), P(ub - w1 + l1, v1)], fill=INK, width=max(1, int(2 * s)))
    d.rectangle(R(100, -350, 180, -330), fill=MID, outline=INK, width=o)
    lattice(140, -350, -580, 36, 12)
    d.rectangle(R(126, -600, 154, -580), fill=MID, outline=INK, width=max(1, o // 2))
    d.line([P(140, -600), P(140, -680)], fill=INK, width=max(1, int(4 * s)))
    if lit:
        d.ellipse(R(132, -692, 148, -676), fill=(255, 70, 60))
    lights.append(P(140, -684))
    # левая решётчатая башня (стрела)
    lattice(-250, -232, -530, 26, 7, lean=18)
    _PLAT[key] = (lay, ax, ay, lights)
    return _PLAT[key]


def paste_platform(img, x, base, s, lit=True, alpha=1.0, light_k=1.0):
    lay, ax, ay, lights = platform_layer(s, lit)
    if alpha < 1:
        a = lay.getchannel("A").point(lambda v: int(v * alpha))
        lay = lay.copy(); lay.putalpha(a)
    ox, oy = int(x - ax), int(base - ay)
    img.paste(lay, (ox, oy), lay)
    if lit and light_k > 0:
        for (lx, ly) in lights:
            glow(img, (ox + lx, oy + ly), max(6, 26 * s), (150, 100, 30), light_k * .8)


# ---------- отпечаток ботинка ----------
SOLE = [(-9, 4), (-14, -10), (-16, -24), (-13, -34), (-6, -40), (2, -41), (10, -37), (15, -28), (16, -16), (13, -4), (9, 4)]
HEEL = [(-11, 14), (-12, 24), (-10, 33), (-4, 37), (4, 37), (10, 33), (12, 24), (11, 14), (6, 11), (-6, 11)]
WET = (34, 50, 70)


def boot_print(d, x, y, s, ang=0.0, left=False):
    ca, sa = math.cos(ang), math.sin(ang)
    m = -1 if left else 1

    def tr(v, u):
        v *= m
        return (x + (v * ca - u * sa) * s * 1.6, y + (v * sa + u * ca) * s * 1.6)
    for shape in (SOLE, HEEL):
        d.polygon([tr(v, u) for v, u in shape], fill=WET, outline=INK, width=max(2, int(4 * s)))
    # протектор
    for u in range(-34, 2, 6):
        half = 12 if -30 < u < -12 else 9
        d.line([tr(-half, u), tr(half, u - 2)], fill=(22, 32, 46), width=max(2, int(3 * s)))
    for u in (18, 24, 30):
        d.line([tr(-8, u), tr(8, u)], fill=(22, 32, 46), width=max(2, int(3 * s)))
    # мокрый блик и капли
    d.line([tr(-8, -30), tr(-10, -18)], fill=(150, 196, 226), width=max(2, int(4 * s)))
    d.line([tr(-6, 16), tr(-7, 24)], fill=(150, 196, 226), width=max(2, int(3 * s)))
    rnd = random.Random(int(x * 7 + y))
    for _ in range(3):
        v, u = rnd.uniform(-26, 26), rnd.uniform(-46, 44)
        cx, cy = tr(v, u)
        r = rnd.uniform(2, 4.5) * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WET, outline=INK, width=1)


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


def window(img, box, t, glow_xy=None):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    sub = vgrad(x1 - x0, y1 - y0, (40, 48, 66), (26, 30, 44))
    sn = sub.copy()
    s = Snow(30, 9)
    tmp = Image.new("RGB", (W, H)); s.draw(tmp, t)
    sn = ImageChops.lighter(sub, tmp.crop(box))
    img.paste(sn, (x0, y0))
    if glow_xy:
        glow(img, glow_xy, 60, (110, 60, 20), .8)
    d.rectangle(box, outline=INK, width=8)
    d.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], outline=(200, 200, 204), width=10)
    d.line([(x0 + x1) / 2, y0, (x0 + x1) / 2, y1], fill=(200, 200, 204), width=12)


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


def s09(t, L, rt):
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


FUNCS = {n: globals()[n] for n, *_ in PLAN}


def frame(t):
    for name, start, length, sc in scenes:
        if start <= t < start + length:
            lt = t - start
            if name == "s09":
                img = s09(lt, length, [s for s, c, d in sc if c == "09r"][0])
            else:
                img = FUNCS[name](lt, length)
            img = grade(img)
            k = min(lt / .15, (length - lt) / .15, 1)
            if name != "s01" and k < 1:
                img = Image.blend(Image.new("RGB", (W, H)), img, max(0, k) * .6 + .4)
            draw_subs(img, t)
            return img
    return Image.new("RGB", (W, H))


def build_audio(path):
    inputs, filters, mix = [], [], []
    for i, (start, clip, d) in enumerate(cues):
        inputs += ["-i", os.path.join(TTS, clip + ".mp3")]
        ms = int(start * 1000)
        if clip == "09r":
            filters.append(f"[{i}:a]highpass=f=450,lowpass=f=2600,acrusher=bits=6:mix=0.35,volume=1.6,aecho=0.8:0.5:40:0.25,adelay={ms}|{ms}[v{i}]")
        else:
            filters.append(f"[{i}:a]volume=1.35,adelay={ms}|{ms}[v{i}]")
        mix.append(f"[v{i}]")
    n, D = len(cues), f"{TOTAL:.2f}"
    st = {nm: (s, l) for nm, s, l, _ in scenes}
    inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.6:d={D}:seed=4"]
    filters.append(f"[{n}:a]lowpass=f=500,volume='0.32+0.16*sin(t*0.7)+0.1*sin(t*1.9)':eval=frame[wind]")
    inputs += ["-f", "lavfi", "-i", f"aevalsrc='0.08*sin(2*PI*55*t)+0.06*sin(2*PI*82.4*t)+0.03*sin(2*PI*110.3*t)':d={D}"]
    filters.append(f"[{n+1}:a]volume=0.8[drone]")
    s6, l6 = st["s06"]; s9, l9 = st["s09"]
    inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=white:amplitude=0.25:d={D}:seed=7"]
    filters.append(f"[{n+2}:a]highpass=f=1500,lowpass=f=6000,volume='if(between(t,{s6:.2f},{s6+l6:.2f})+between(t,{s9:.2f},{s9+l9:.2f}),0.3,0)':eval=frame[stat]")
    hit = int((st["s11"][0] + .3) * 1000)
    inputs += ["-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(42+30*exp(-t*6))*t)*exp(-t*1.6)':d=3"]
    filters.append(f"[{n+3}:a]adelay={hit}|{hit}[hit]")
    filters.append("".join(mix) + f"[wind][drone][stat][hit]amix=inputs={n+4}:normalize=0,alimiter=limit=0.95,afade=t=out:st={TOTAL-1.5:.2f}:d=1.5[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filters), "-map", "[out]",
                                                                     "-ac", "2", "-ar", "44100", "-t", D, path])


if __name__ == "__main__":
    print(f"длительность {TOTAL:.1f} c", flush=True)
    only = os.environ.get("PREVIEW")
    if only:
        for ts in only.split(","):
            frame(float(ts)).save(f"{OUT}_{ts}.png")
        sys.exit()
    audio = OUT + ".wav"
    build_audio(audio)
    nframes = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    for i in range(nframes):
        ff.stdin.write(frame(i / FPS).tobytes())
        if i % 480 == 0:
            print(f"{i}/{nframes}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(audio)
    print("готово:", OUT)
