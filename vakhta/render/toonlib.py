"""Общая библиотека «Вахты»: плоская мультяшная 2D-анимация кодом (PIL + ffmpeg).

Стиль: толстый чёрный контур, большие белые глаза, плоские цвета,
размытый серый фон с оранжевыми огоньками, жёлтые субтитры по 2–3 слова.

Серии лежат в seriyaNN.py и импортируют отсюда всё нужное.
Запуск:  python3 seriya01.py <папка_с_озвучкой> <выходной.mp4>
Превью:  PREVIEW=3.0,10.5 python3 seriya01.py ../tts/s01 out   → out_3.0.png …
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

def dur(name):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", os.path.join(TTS, name)])
    return float(out)


LINES, scenes, cues, SUBS, TOTAL = {}, [], [], [], 0.0


def setup(lines, plan):
    """строит таймлайн сцен, реплик и субтитров"""
    global TOTAL
    LINES.clear(); LINES.update(lines)
    scenes.clear(); cues.clear(); SUBS.clear()
    T = 0.0
    for name, clips, tail in plan:
        local, sc = 0.0, []
        for clip, delay in clips:
            d = dur(clip + ".mp3")
            start = (local + 0.4) if delay is None else delay
            sc.append((start, clip, d))
            local = start + d
        length = max(local + tail, tail)
        scenes.append((name, T, length, sc))
        cues.extend((T + s, c, d) for s, c, d in sc)
        T += length
    TOTAL = T
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
            SUBS.append((t, t + dd, c, clip.endswith("r")))
            t += dd


def span(name):
    for n, s, l, _ in scenes:
        if n == name:
            return s, l
    raise KeyError(name)


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



# ---------- коридор, дверь, лужа, пар ----------
WALL, WALL_D, FLOOR, CEIL = (156, 160, 164), (132, 136, 142), (96, 100, 106), (118, 122, 128)
DOOR = (186, 176, 150)


# ---------- коридор в перспективе ----------
VX, VY, F = W / 2, 560, 400


def pj(X, Y, Z):
    return (VX + X * F / Z, VY + Y * F / Z)


def corridor(img, cam=0.0, zmax=6.0, prints=True, doors=21, t=0.0):
    d = ImageDraw.Draw(img)
    ze = zmax - cam
    # стены, пол, потолок
    d.polygon([pj(-1, -1.4, .2), pj(1, -1.4, .2), pj(1, -1.4, ze), pj(-1, -1.4, ze)], fill=CEIL)
    d.polygon([pj(-1, 1.8, .2), pj(1, 1.8, .2), pj(1, 1.8, ze), pj(-1, 1.8, ze)], fill=FLOOR)
    d.polygon([pj(-1, -1.4, .2), pj(-1, 1.8, .2), pj(-1, 1.8, ze), pj(-1, -1.4, ze)], fill=WALL)
    d.polygon([pj(1, -1.4, .2), pj(1, 1.8, .2), pj(1, 1.8, ze), pj(1, -1.4, ze)], fill=WALL_D)
    d.rectangle([*pj(-1, -1.4, ze), *pj(1, 1.8, ze)], fill=(170, 174, 178), outline=INK, width=4)
    for a, b in [((-1, -1.4), (-1, 1.8)), ((1, -1.4), (1, 1.8))]:
        pass
    for X, Y in [(-1, -1.4), (1, -1.4), (-1, 1.8), (1, 1.8)]:
        d.line([pj(X, Y, .2), pj(X, Y, ze)], fill=INK, width=5)
    # плинтус
    for X in (-1, 1):
        d.polygon([pj(X, 1.6, .3), pj(X, 1.8, .3), pj(X, 1.8, ze), pj(X, 1.6, ze)], fill=(80, 84, 92))
    # двери (по очереди слева/справа), дальние рисуем первыми
    items = []
    for i in range(doors):
        side = -1 if i % 2 == 0 else 1
        z0 = 1.1 + (i // 2) * 0.48 - cam
        if z0 < .35 or z0 + .3 > ze:
            continue
        items.append((z0, side, i))
    for z0, side, i in sorted(items, reverse=True):
        z1 = z0 + .3
        q = [pj(side, -.5, z0), pj(side, -.5, z1), pj(side, 1.8, z1), pj(side, 1.8, z0)]
        d.polygon(q, fill=DOOR, outline=INK, width=max(2, int(6 / z0)))
        hx, hy = pj(side, .7, z0 + .25)
        r = max(2, 9 / z0)
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(120, 120, 126), outline=INK)
    # лампы на потолке
    for k in range(6):
        z = 1.3 + k * .9 - cam
        if z < .4 or z > ze:
            continue
        a, b = pj(-.25, -1.4, z), pj(.25, -1.4, z + .25)
        d.rectangle([a[0], a[1], b[0], b[1] + 3], fill=(250, 248, 224), outline=INK, width=2)
        glow(img, ((a[0] + b[0]) / 2, a[1] + 10), max(10, 70 / z), (70, 66, 46), .8)
    # мокрые следы по полу
    if prints:
        d = ImageDraw.Draw(img)
        for k in range(14):
            z = 1.0 + k * .34 - cam
            if z < .5 or z > ze - .1:
                continue
            x, y = pj(.16 if k % 2 else -.16, 1.8, z)
            boot_print(d, x, y, 1.1 / z, 0, k % 2 == 0)


def big_number(img, txt, y, size=150, col=YELLOW, pop=1.0):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, int(size * (0.8 + 0.2 * pop)))
    x = (W - f.getlength(txt)) / 2
    d.text((x, y), txt, font=f, fill=col, stroke_width=6, stroke_fill=(58, 50, 14))


def door_close(img, t, knock=0.0, dx=0, weld=0.0, hot=False, ajar=0.0, frost=True):
    d = ImageDraw.Draw(img)
    jx = knock * 6 * math.sin(t * 80)
    x0, y0, x1, y1 = 150 + jx + dx, 120, 570 + jx + dx, 1060
    d.rectangle([x0 - 26, y0 - 26, x1 + 26, y1], fill=(120, 124, 130), outline=INK, width=6)
    if ajar > 0:  # тёмная щель со стороны ручки
        gap = 70 * ajar
        d.rectangle([x1 - gap, y0, x1, y1], fill=(8, 10, 14))
        x1 = x1 - gap
    d.rectangle([x0, y0, x1, y1], fill=(170, 176, 184), outline=INK, width=7)
    # пустая табличка
    d.rectangle([x0 + 130, y0 + 90, x1 - 130, y0 + 170], fill=(150, 156, 164), outline=INK, width=5)
    for sx in (x0 + 146, x1 - 146):
        d.ellipse([sx - 6, y0 + 124, sx + 6, y0 + 136], fill=INK)
    d.ellipse([x1 - 80, 590, x1 - 40, 630], fill=(120, 120, 126), outline=INK, width=5)
    d.rectangle([x1 - 120, 600, x1 - 60, 620], fill=(120, 120, 126), outline=INK, width=4)
    # сварной шов по правому краю
    if weld > 0:
        yb = y0 + (y1 - y0) * weld
        for yy in np.arange(y0 + 6, yb, 12):
            col = (255, 170, 60) if hot and yy > yb - 120 else (110, 104, 96)
            d.ellipse([x1 - 12, yy - 8, x1 + 12, yy + 8], fill=col, outline=INK, width=2)
    if not frost:
        return (x0, x1, y1)
    # иней
    rnd = random.Random(4)
    for k in range(40):
        side = rnd.choice([0, 1, 2])
        if side == 0:
            x, y = x0 + rnd.uniform(0, 30), rnd.uniform(y0, y1)
        elif side == 1:
            x, y = x1 - rnd.uniform(0, 30), rnd.uniform(y0, y1)
        else:
            x, y = rnd.uniform(x0, x1), y0 + rnd.uniform(0, 30)
        a = rnd.uniform(0, 6.3); l = rnd.uniform(10, 26)
        d.line([x, y, x + l * math.cos(a), y + l * math.sin(a)], fill=(236, 246, 255), width=3)
    return (x0, x1, y1)


def floor_strip(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1060, W, H], fill=FLOOR); d.line([0, 1060, W, 1060], fill=INK, width=6)


def vapor(img, t, x0, x1, y1, k=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    rnd = random.Random(8)
    for i in range(16):
        ph = rnd.random()
        life = (t * .35 + ph) % 1
        x = rnd.uniform(x0, x1) + 40 * math.sin(t + i)
        y = y1 - 10 - life * 260
        r = 30 + 70 * life
        a = int(110 * (1 - life) * k)
        ld.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(230, 240, 250, a))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(10))).convert("RGB")


def puddle(img, t, x0, x1, y1, grow):
    d = ImageDraw.Draw(img)
    w = (x1 - x0) * (.45 + .6 * grow)
    cx = (x0 + x1) / 2
    d.ellipse([cx - w / 2, y1 - 14, cx + w / 2, y1 + 60 + 90 * grow], fill=WET, outline=INK, width=4)
    d.arc([cx - w / 3, y1 + 10, cx + w / 4, y1 + 40 + 50 * grow], 190, 300, fill=(150, 196, 226), width=6)
    # свет из-под двери
    d.rectangle([x0 + 4, y1 - 8, x1 - 4, y1], fill=(150, 210, 240))



def title(t, L, n):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    rnd = random.Random(1)
    for i in range(70):
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
    txt = f"серия {n}"
    d.text(((W - f2.getlength(txt)) / 2, 340), txt, font=f2, fill=(int(255 * a),) * 3, stroke_width=4, stroke_fill=INK)
    return img



def frame(t, funcs, title_scene="s01"):
    for name, start, length, sc in scenes:
        if start <= t < start + length:
            lt = t - start
            fn = funcs[name]
            if fn.__code__.co_argcount >= 3:
                img = fn(lt, length, {c: s for s, c, d in sc})
            else:
                img = fn(lt, length)
            img = grade(img)
            k = min(lt / .15, (length - lt) / .15, 1)
            if name != title_scene and k < 1:
                img = Image.blend(Image.new("RGB", (W, H)), img, max(0, k) * .6 + .4)
            draw_subs(img, t)
            return img
    return Image.new("RGB", (W, H))


def build_audio(path, static=(), hits=(), knocks=()):
    """озвучка + ветер + гул; static — интервалы помех рации, hits — низкие удары, knocks — стук"""
    inputs, filters, mix = [], [], []
    for i, (start, clip, d) in enumerate(cues):
        inputs += ["-i", os.path.join(TTS, clip + ".mp3")]
        ms = int(start * 1000)
        if clip.endswith("r"):
            filters.append(f"[{i}:a]highpass=f=450,lowpass=f=2600,acrusher=bits=6:mix=0.35,volume=1.6,aecho=0.8:0.5:40:0.25,adelay={ms}|{ms}[v{i}]")
        else:
            filters.append(f"[{i}:a]volume=1.35,adelay={ms}|{ms}[v{i}]")
        mix.append(f"[v{i}]")
    n, D = len(inputs) // 2, f"{TOTAL:.2f}"
    inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.6:d={D}:seed=4"]
    filters.append(f"[{n}:a]lowpass=f=500,volume='0.32+0.16*sin(t*0.7)+0.1*sin(t*1.9)':eval=frame[wind]"); mix.append("[wind]")
    inputs += ["-f", "lavfi", "-i", f"aevalsrc='0.08*sin(2*PI*55*t)+0.06*sin(2*PI*82.4*t)+0.03*sin(2*PI*110.3*t)':d={D}"]
    filters.append(f"[{n+1}:a]volume=0.8[drone]"); mix.append("[drone]")
    k = n + 2
    if static:
        cond = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in static)
        inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=white:amplitude=0.25:d={D}:seed=7"]
        filters.append(f"[{k}:a]highpass=f=1500,lowpass=f=6000,volume='if({cond},0.3,0)':eval=frame[stat]"); mix.append("[stat]"); k += 1
    for j, ht in enumerate(hits):
        inputs += ["-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(42+30*exp(-t*6))*t)*exp(-t*1.6)':d=3"]
        ms = int(ht * 1000)
        filters.append(f"[{k}:a]adelay={ms}|{ms}[hit{j}]"); mix.append(f"[hit{j}]"); k += 1
    for j, kt in enumerate(knocks):
        inputs += ["-f", "lavfi", "-i", "aevalsrc='1.0*sin(2*PI*95*t)*exp(-t*28)+0.5*sin(2*PI*210*t)*exp(-t*45)+0.25*(random(0)-0.5)*exp(-t*80)':d=0.5"]
        ms = int(kt * 1000)
        filters.append(f"[{k}:a]lowpass=f=1800,aecho=0.6:0.4:60:0.3,volume=1.4,adelay={ms}|{ms}[kn{j}]"); mix.append(f"[kn{j}]"); k += 1
    filters.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0,alimiter=limit=0.95,afade=t=out:st={TOTAL-1.5:.2f}:d=1.5[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filters), "-map", "[out]",
                                                                     "-ac", "2", "-ar", "44100", "-t", D, path])


def run(funcs, **audio_kw):
    print(f"длительность {TOTAL:.1f} c", flush=True)
    only = os.environ.get("PREVIEW")
    if only:
        for ts in only.split(","):
            frame(float(ts), funcs).save(f"{OUT}_{ts}.png")
        return
    audio = OUT + ".wav"
    build_audio(audio, **audio_kw)
    nframes = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "3500k", "-bufsize", "7000k",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    for i in range(nframes):
        ff.stdin.write(frame(i / FPS, funcs).tobytes())
        if i % 480 == 0:
            print(f"{i}/{nframes}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(audio)
    print("готово:", OUT)
