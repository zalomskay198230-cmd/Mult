"""Рендер серии 1 «Вахта» — 2D-анимация кодом (PIL + ffmpeg).

Запуск:  python3 render.py <папка_с_озвучкой> <выходной.mp4>
В папке озвучки ожидаются 02.mp3 … 12.mp3 и 09r.mp3 (голос рации).
"""
import math, random, subprocess, sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 720, 1280, 24
TTS = sys.argv[1] if len(sys.argv) > 1 else "tts"
OUT = sys.argv[2] if len(sys.argv) > 2 else "vakhta_s01.mp4"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_I = "/usr/share/fonts/opentype/inter/Inter-BoldItalic.otf"

# ---------- палитра ----------
NAVY = (14, 22, 40)
NAVY2 = (28, 40, 66)
SEA = (6, 10, 18)
STEEL = (34, 40, 52)
STEEL2 = (52, 60, 76)
ORANGE = (255, 138, 36)
FLAME = (255, 196, 90)
COVER = (226, 98, 26)
SKIN = (214, 160, 128)
YELLOW = (240, 196, 40)


def dur(name):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", os.path.join(TTS, name)])
    return float(out)


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
# каждая сцена: (имя функции, [(клип, задержка от начала сцены)], хвост)
PLAN = [
    ("s01", [], 3.6),
    ("s02", [("02", 0.3)], 0.6),
    ("s03", [("03", 0.2)], 0.6),
    ("s04", [("04", 0.7)], 1.2),
    ("s05", [("05", 0.3)], 0.6),
    ("s06", [("06", 0.3)], 0.8),
    ("s07", [("07", 0.3)], 0.8),
    ("s08", [("08", 0.3)], 1.0),
    ("s09", [("09", 0.2), ("09r", None)], 0.8),
    ("s10", [("10", 0.3)], 0.6),
    ("s11", [("11", 0.5)], 0.8),
    ("s12", [("12", 0.3)], 2.2),
]

scenes, cues = [], []  # cues: (abs_start, clip, dur)
T = 0.0
for name, clips, tail in PLAN:
    local = 0.0
    sc_cues = []
    for clip, delay in clips:
        d = dur(clip + ".mp3")
        start = (local + 0.5) if delay is None else delay
        sc_cues.append((start, clip, d))
        local = start + d
    length = max(local + tail, tail)
    scenes.append((name, T, length, sc_cues))
    for s, c, d in sc_cues:
        cues.append((T + s, c, d))
    T += length
TOTAL = T


# ---------- субтитры ----------
def split_sentences(text):
    parts, cur = [], ""
    for ch in text:
        cur += ch
        if ch in ".!?" and len(cur.strip()) > 1:
            parts.append(cur.strip()); cur = ""
    if cur.strip():
        if parts and len(cur.strip()) <= 2:
            parts[-1] += cur.strip()
        else:
            parts.append(cur.strip())
    return parts


SUBS = []  # (start, end, text, radio)
for start, clip, d in cues:
    parts = split_sentences(LINES[clip])
    total = sum(len(p) for p in parts)
    t = start
    for p in parts:
        pd = d * len(p) / total
        SUBS.append((t, t + pd, p, clip == "09r"))
        t += pd

font_sub = ImageFont.truetype(FONT_B, 40)
font_rad = ImageFont.truetype(FONT_I, 40)


def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.getlength(test) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def draw_subs(img, t):
    for s, e, text, radio in SUBS:
        if s <= t < e:
            font = font_rad if radio else font_sub
            d = ImageDraw.Draw(img)
            lines = wrap(text, font, W - 110)
            y = int(H * 0.70)
            for ln in lines:
                lw = font.getlength(ln)
                x = (W - lw) / 2
                fill = (150, 255, 170) if radio else (255, 255, 255)
                d.text((x, y), ln, font=font, fill=fill, stroke_width=4, stroke_fill=(0, 0, 0))
                y += 52
            return


# ---------- утилиты рисования ----------
def vgrad(w, h, top, bottom):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - a) + np.array(bottom)[None, None, :] * a)
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def glow(img, xy, radius, color, strength=1.0):
    """мягкое свечение: аддитивно накладываем размытый круг"""
    x, y = xy
    r = int(radius)
    size = r * 4
    layer = Image.new("RGB", (size, size), (0, 0, 0))
    ImageDraw.Draw(layer).ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r],
                                  fill=tuple(int(c * strength) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.6))
    box = (int(x - size / 2), int(y - size / 2))
    region = img.crop((box[0], box[1], box[0] + size, box[1] + size))
    img.paste(ImageChops.add(region, layer), box)


class Snow:
    def __init__(self, n, seed, size=(1, 3.5), speed=(80, 200), wind=120):
        rnd = random.Random(seed)
        self.p = [(rnd.random() * W, rnd.random() * H, rnd.uniform(*size), rnd.uniform(*speed),
                   rnd.uniform(0.6, 1.4), rnd.random() * 6.28) for _ in range(n)]
        self.wind = wind

    def draw(self, img, t, alpha=1.0, wind=None):
        wind = self.wind if wind is None else wind
        d = ImageDraw.Draw(img)
        for x0, y0, s, sp, wf, ph in self.p:
            x = (x0 + wind * wf * t + 14 * math.sin(t * 1.7 + ph)) % (W + 40) - 20
            y = (y0 + sp * t) % (H + 40) - 20
            c = int(200 * alpha * min(1, s / 3) + 40)
            if wind > 400:  # штормовые росчерки
                d.line([x, y, x - wind * 0.025 * wf, y - sp * 0.025], fill=(c, c, c + 10), width=max(1, int(s * 0.6)))
            else:
                d.ellipse([x - s, y - s, x + s, y + s], fill=(c, c, min(255, c + 15)))


def waves(d, t, y0, amp, color, phase=0.0, speed=1.0, layers=1):
    pts = [(0, H)]
    for x in range(0, W + 9, 8):
        y = y0 + amp * (math.sin(x * 0.012 + t * 1.3 * speed + phase) * 0.6
                        + math.sin(x * 0.031 - t * 2.1 * speed + phase * 2) * 0.3
                        + math.sin(x * 0.07 + t * 3.3 * speed) * 0.1)
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=color)


def zoom(img, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-3:
        return img
    w, h = W / z, H / z
    x0 = (W - w) * cx
    y0 = (H - h) * cy
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def shake(img, t, amt):
    dx = amt * math.sin(t * 37) * math.cos(t * 13)
    dy = amt * math.sin(t * 29 + 1)
    return ImageChops.offset(img, int(dx), int(dy))


def vignette_mask():
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    v = np.clip(1.15 - 0.55 * r ** 2, 0.25, 1.0)
    return v[:, :, None]


VIG = vignette_mask()


def grade(img):
    arr = np.asarray(img).astype(np.float32) * VIG
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------- платформа ----------
def flame(img, x, y, t, s=1.0):
    d = ImageDraw.Draw(img)
    f = 1 + 0.18 * math.sin(t * 11) + 0.1 * math.sin(t * 23)
    glow(img, (x, y - 20 * s), 120 * s * f, (120, 50, 10), 0.9)
    for i, (r, c) in enumerate([(26, ORANGE), (17, FLAME), (8, (255, 245, 210))]):
        rr = r * s * f
        sway = 6 * s * math.sin(t * 7 + i)
        d.polygon([(x - rr, y), (x + rr, y), (x + sway * 2, y - rr * 3.2)], fill=c)
        d.ellipse([x - rr, y - rr, x + rr, y + rr * 0.4], fill=c)


def platform(img, cx, base, s, t, lights=True):
    d = ImageDraw.Draw(img)
    deck = base - 170 * s
    # опоры
    for lx in (-150, -60, 60, 150):
        x = cx + lx * s
        d.polygon([(x - 13 * s, deck), (x + 13 * s, deck), (x + 19 * s, base + 40 * s), (x - 19 * s, base + 40 * s)], fill=STEEL)
        for k in range(3):
            yy = deck + (k + 1) * 45 * s
            d.line([x - 15 * s, yy, x + 15 * s, yy], fill=STEEL2, width=max(1, int(3 * s)))
    d.line([cx - 150 * s, deck + 60 * s, cx + 150 * s, deck + 60 * s], fill=STEEL, width=int(6 * s))
    # палуба
    d.rectangle([cx - 200 * s, deck - 22 * s, cx + 200 * s, deck + 10 * s], fill=STEEL2)
    # жилой блок
    d.rectangle([cx - 190 * s, deck - 120 * s, cx - 40 * s, deck - 22 * s], fill=(44, 50, 64))
    d.rectangle([cx - 190 * s, deck - 128 * s, cx - 40 * s, deck - 120 * s], fill=(70, 78, 94))
    if lights:
        rnd = random.Random(3)
        for row in range(3):
            for col in range(6):
                if rnd.random() < 0.65:
                    wx = cx + (-180 + col * 24) * s
                    wy = deck + (-110 + row * 28) * s
                    d.rectangle([wx, wy, wx + 12 * s, wy + 9 * s], fill=(255, 214, 140))
    # вертолётная площадка (козырёк)
    d.polygon([(cx - 200 * s, deck - 128 * s), (cx - 320 * s, deck - 128 * s), (cx - 300 * s, deck - 116 * s), (cx - 200 * s, deck - 116 * s)], fill=(60, 66, 80))
    d.line([cx - 300 * s, deck - 116 * s, cx - 190 * s, deck - 60 * s], fill=STEEL, width=int(4 * s))
    # буровая вышка
    bx = cx + 60 * s
    top = deck - 380 * s
    d.line([bx - 40 * s, deck - 22 * s, bx, top], fill=STEEL2, width=int(5 * s))
    d.line([bx + 40 * s, deck - 22 * s, bx, top], fill=STEEL2, width=int(5 * s))
    for k in range(1, 8):
        yy = deck - 22 * s - k * (358 * s / 8)
        half = 40 * s * (1 - k / 8)
        d.line([bx - half, yy, bx + half, yy], fill=STEEL2, width=max(1, int(2 * s)))
        if k < 7:
            yy2 = yy - 358 * s / 8
            h2 = 40 * s * (1 - (k + 1) / 8)
            d.line([bx - half, yy, bx + h2, yy2], fill=STEEL, width=max(1, int(2 * s)))
    if int(t * 1.2) % 2 == 0:
        d.ellipse([bx - 5 * s, top - 5 * s, bx + 5 * s, top + 5 * s], fill=(255, 40, 40))
        glow(img, (bx, top), 18 * s, (160, 0, 0), 0.8)
    # факельная стрела
    fx, fy = cx + 330 * s, deck - 250 * s
    d.line([cx + 190 * s, deck - 20 * s, fx, fy], fill=STEEL2, width=int(7 * s))
    flame(img, fx, fy - 6 * s, t, s)


def sky(t, top=NAVY, bottom=NAVY2):
    return vgrad(W, H, top, bottom)


SNOW_A = Snow(260, 1)
SNOW_B = Snow(160, 2, size=(2, 5), speed=(160, 320), wind=220)
SNOW_STORM = Snow(320, 3, size=(1, 4), speed=(300, 600), wind=900)


# ---------- персонажи ----------
def ilya_close(img, t, cx, cy, s=1.0, lit=1.0, blink=True):
    d = ImageDraw.Draw(img)
    sway = 4 * math.sin(t * 1.3)
    cx += sway
    # плечи в комбинезоне
    d.ellipse([cx - 260 * s, cy + 150 * s, cx + 260 * s, cy + 560 * s], fill=(160, 64, 18))
    d.ellipse([cx - 245 * s, cy + 160 * s, cx + 200 * s, cy + 540 * s], fill=COVER)
    # нашивка
    d.rectangle([cx + 40 * s, cy + 290 * s, cx + 170 * s, cy + 330 * s], fill=(30, 36, 50))
    d.text((cx + 50 * s, cy + 298 * s), "СЕВЕРНАЯ-7", font=ImageFont.truetype(FONT_B, int(17 * s)), fill=(230, 230, 230))
    # капюшон
    d.ellipse([cx - 190 * s, cy - 200 * s, cx + 190 * s, cy + 240 * s], fill=(28, 30, 38))
    # шея и лицо
    d.rectangle([cx - 55 * s, cy + 90 * s, cx + 55 * s, cy + 190 * s], fill=(150, 104, 84))
    d.ellipse([cx - 115 * s, cy - 120 * s, cx + 115 * s, cy + 150 * s], fill=(150, 104, 84))
    # освещённая сторона (факел справа)
    lc = tuple(int(a * (1 - lit) + b * lit) for a, b in zip((150, 104, 84), (196, 136, 100)))
    d.chord([cx - 115 * s, cy - 120 * s, cx + 115 * s, cy + 150 * s], -80, 80, fill=lc)
    # щетина
    rnd = random.Random(7)
    for _ in range(170):
        a = rnd.uniform(0.15, 2.95)
        rr = rnd.uniform(0.62, 0.97)
        x = cx + math.cos(a) * 110 * s * rr
        y = cy + 20 * s + math.sin(a) * 125 * s * rr
        d.ellipse([x - 1.6 * s, y - 1.6 * s, x + 1.6 * s, y + 1.6 * s], fill=(176, 84, 40))
    # шапка
    d.chord([cx - 125 * s, cy - 175 * s, cx + 125 * s, cy + 10 * s], 180, 360, fill=(18, 18, 22))
    d.rectangle([cx - 125 * s, cy - 92 * s, cx + 125 * s, cy - 58 * s], fill=(26, 26, 32))
    for k in range(-120, 125, 14):
        d.line([cx + k * s, cy - 92 * s, cx + k * s, cy - 58 * s], fill=(14, 14, 18), width=2)
    # глаза
    closed = blink and (t % 3.7) < 0.12
    for ex in (-48, 48):
        x, y = cx + ex * s, cy - 10 * s
        if closed:
            d.line([x - 18 * s, y, x + 18 * s, y], fill=(40, 26, 20), width=int(3 * s))
        else:
            d.ellipse([x - 17 * s, y - 8 * s, x + 17 * s, y + 8 * s], fill=(222, 214, 200))
            d.ellipse([x - 8 * s, y - 8 * s, x + 8 * s, y + 8 * s], fill=(70, 86, 96))
            d.ellipse([x - 4 * s, y - 4 * s, x + 4 * s, y + 4 * s], fill=(10, 10, 12))
        # тяжёлые веки / брови
        d.line([x - 22 * s, y - 22 * s, x + 20 * s, y - 26 * s + (4 * s if ex > 0 else 0)], fill=(120, 60, 30), width=int(7 * s))
        d.arc([x - 20 * s, y + 2 * s, x + 20 * s, y + 18 * s], 20, 160, fill=(110, 72, 58), width=2)
    # нос и рот
    d.line([cx, cy, cx + 8 * s, cy + 48 * s, cx - 6 * s, cy + 54 * s], fill=(112, 74, 60), width=int(4 * s))
    d.line([cx - 30 * s, cy + 92 * s, cx + 28 * s, cy + 90 * s], fill=(90, 50, 40), width=int(4 * s))


def worker(d, x, y, s, seed, color=COVER, head=SKIN, hat=(20, 20, 26)):
    """сидящий рабочий: силуэт"""
    d.rounded_rectangle([x - 40 * s, y - 120 * s, x + 40 * s, y], radius=int(26 * s), fill=color)
    d.ellipse([x - 26 * s, y - 175 * s, x + 26 * s, y - 115 * s], fill=head)
    d.chord([x - 28 * s, y - 182 * s, x + 28 * s, y - 135 * s], 180, 360, fill=hat)
    d.rectangle([x - 40 * s, y - 10 * s, x + 60 * s, y + 20 * s], fill=tuple(int(c * 0.7) for c in color))


def runner(d, x, y, s, t, ph):
    """бегущий силуэт в куртке"""
    k = math.sin(t * 9 + ph)
    d.line([x, y - 60 * s, x + 30 * s * k, y], fill=(20, 20, 26), width=int(14 * s))
    d.line([x, y - 60 * s, x - 30 * s * k, y], fill=(20, 20, 26), width=int(14 * s))
    d.rounded_rectangle([x - 26 * s, y - 150 * s, x + 26 * s, y - 55 * s], radius=int(14 * s), fill=COVER)
    d.line([x, y - 130 * s, x + 40 * s, y - 100 * s - 10 * s * k], fill=COVER, width=int(12 * s))
    d.ellipse([x - 20 * s, y - 192 * s, x + 20 * s, y - 150 * s], fill=(24, 24, 30))
    return (x + 44 * s, y - 100 * s - 10 * s * k)


def beam(img, src, angle, length, spread, strength=0.55):
    layer = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(layer)
    a1, a2 = angle - spread, angle + spread
    pts = [src, (src[0] + length * math.cos(a1), src[1] + length * math.sin(a1)),
           (src[0] + length * math.cos(a2), src[1] + length * math.sin(a2))]
    ld.polygon(pts, fill=int(255 * strength))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    light = Image.new("RGB", (W, H), (255, 240, 200))
    return Image.composite(light, img, layer)


# ---------- сцены ----------
def s01(t, L):
    img = sky(t, (8, 12, 24), (24, 34, 56))
    d = ImageDraw.Draw(img)
    platform(img, W / 2 - 40, 940, 0.72, t)
    waves(d, t, 890, 26, (12, 18, 30), 0.0)
    waves(d, t, 925, 34, SEA, 1.7, 1.2)
    SNOW_A.draw(img, t)
    img = zoom(img, 1.15 - 0.15 * (t / L), 0.5, 0.6)
    d = ImageDraw.Draw(img)
    a = min(1, max(0, (t - 0.5) / 0.8))
    f = ImageFont.truetype(FONT_B, 130)
    txt = "ВАХТА"
    tw = f.getlength(txt)
    col = tuple(int(255 * a) for _ in range(3))
    d.text(((W - tw) / 2, 230), txt, font=f, fill=col, stroke_width=3, stroke_fill=(0, 0, 0))
    f2 = ImageFont.truetype(FONT_B, 40)
    t2 = "СЕРИЯ 1"
    d.text(((W - f2.getlength(t2)) / 2, 380), t2, font=f2, fill=(int(255 * a), int(150 * a), int(50 * a)))
    return img


def s02(t, L):
    img = vgrad(W, H, (12, 14, 24), (40, 26, 22))
    glow(img, (W + 60, 420), 380, (130, 60, 16), 0.9)
    ilya_close(img, t, W / 2 - 20, 470, 1.25, lit=0.9 + 0.1 * math.sin(t * 11))
    SNOW_B.draw(img, t)
    return zoom(img, 1.0 + 0.06 * t / L, 0.5, 0.4)


def s03(t, L):
    flick = 0.82 if (int(t * 24) % 53 in (0, 1, 7)) else 1.0
    img = vgrad(W, H, tuple(int(c * flick) for c in (70, 84, 76)), tuple(int(c * flick) for c in (36, 42, 40)))
    d = ImageDraw.Draw(img)
    # лампа
    d.rectangle([160, 60, 560, 80], fill=tuple(int(c * flick) for c in (230, 245, 230)))
    # иллюминатор
    d.ellipse([90, 200, 250, 360], fill=(40, 46, 50)); d.ellipse([104, 214, 236, 346], fill=(4, 6, 12))
    # часы
    d.ellipse([480, 200, 600, 320], fill=(230, 230, 220)); d.ellipse([480, 200, 600, 320], outline=(40, 40, 40), width=6)
    a = -math.pi / 2 + t * 0.9
    d.line([540, 260, 540 + 45 * math.cos(a), 260 + 45 * math.sin(a)], fill=(200, 30, 30), width=3)
    d.line([540, 260, 540 + 30 * math.cos(-1.2), 260 + 30 * math.sin(-1.2)], fill=(20, 20, 20), width=6)
    # пол
    d.rectangle([0, 820, W, H], fill=(30, 34, 34))
    # сумки и люди
    for i, (x, y, s, c) in enumerate([(130, 900, 1.1, COVER), (330, 880, 1.0, (200, 84, 22)), (540, 905, 1.15, COVER), (240, 1060, 1.3, (190, 80, 20)), (500, 1080, 1.35, COVER)]):
        d.rounded_rectangle([x - 70 * s, y - 20 * s, x + 80 * s, y + 50 * s], radius=int(20 * s), fill=(26, 40, 70))
        breathe = 2 * math.sin(t * 1.5 + i)
        worker(d, x, y - 20 * s + breathe, s, i, color=c)
    # стол
    d.rectangle([0, 1180, W, 1200], fill=(120, 110, 96))
    return zoom(img, 1.0 + 0.07 * t / L, 0.5, 0.45)


def s04(t, L):
    img = Image.new("RGB", (W, H), (10, 14, 22))
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, H / 2 - 40, 330
    oct_pts = [(cx + R * math.cos(math.pi / 8 + k * math.pi / 4), cy + R * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    d.polygon(oct_pts, fill=(44, 52, 46))
    for k in range(-R, R, 26):
        d.line([cx - R, cy + k, cx + R, cy + k], fill=(38, 46, 40), width=2)
    d.ellipse([cx - 230, cy - 230, cx + 230, cy + 230], outline=YELLOW, width=12)
    f = ImageFont.truetype(FONT_B, 300)
    d.text((cx - f.getlength("H") / 2, cy - 190), "H", font=f, fill=YELLOW)
    for i, (x, y) in enumerate(oct_pts):
        on = int(t * 2 + i) % 2 == 0
        col = (60, 255, 120) if on else (20, 60, 30)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=col)
        if on:
            glow(img, (x, y), 18, (20, 120, 50), 0.8)
    SNOW_STORM.draw(img, t, 0.8, wind=650)
    return zoom(img, 1.02 + 0.03 * t / L)


def s05(t, L):
    img = vgrad(W, H, (22, 26, 34), (16, 18, 24))
    d = ImageDraw.Draw(img)
    # окно
    win = vgrad(520, 640, (6, 8, 16), (14, 18, 30))
    img.paste(win, (100, 220))
    glow(img, (560, 520), 90, (110, 50, 12), 0.7)
    sn = Image.new("RGB", (W, H), (0, 0, 0))
    SNOW_A.draw(sn, t, 0.7)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle([100, 220, 620, 860], fill=255)
    img.paste(ImageChops.lighter(img, sn), (0, 0), mask)
    d.rectangle([92, 212, 628, 868], outline=(70, 76, 86), width=16)
    d.line([360, 212, 360, 868], fill=(70, 76, 86), width=12)
    # Михалыч со спины
    x, y = W / 2 + 10, 720
    d.ellipse([x - 230, y + 120, x + 230, y + 700], fill=(40, 46, 60))  # плечи в тёмной куртке
    d.rectangle([x - 50, y + 60, x + 50, y + 160], fill=(120, 90, 76))  # шея
    d.ellipse([x - 92, y - 110, x + 92, y + 120], fill=(110, 84, 72))
    d.ellipse([x - 96, y - 116, x + 96, y + 100], fill=(160, 160, 166))  # седина
    for k in range(-80, 85, 12):
        d.line([x + k, y - 100, x + k * 0.9, y + 90], fill=(140, 140, 148), width=2)
    d.ellipse([x - 104, y - 10, x - 78, y + 40], fill=(110, 84, 72))  # ухо
    d.ellipse([x + 78, y - 10, x + 104, y + 40], fill=(110, 84, 72))
    # отражение в стекле: седые усы и глаза-точки
    d.line([470, 470, 490, 466], fill=(70, 70, 80), width=4)
    return zoom(img, 1.0 + 0.08 * t / L, 0.5, 0.55)


def s06(t, L):
    img = vgrad(W, H, (8, 18, 14), (4, 8, 8))
    d = ImageDraw.Draw(img)
    # пульт
    d.rectangle([0, 760, W, H], fill=(30, 36, 34))
    d.rectangle([0, 740, W, 770], fill=(52, 60, 56))
    # экраны с шумом
    rng = np.random.default_rng(int(t * 24))
    for (x, y, w, h) in [(60, 300, 280, 200), (380, 300, 280, 200), (60, 530, 180, 150)]:
        d.rectangle([x - 10, y - 10, x + w + 10, y + h + 10], fill=(20, 24, 22))
        noise = rng.integers(0, 120, (h // 3, w // 3), dtype=np.uint8)
        n = Image.fromarray(noise, "L").resize((w, h), Image.NEAREST)
        scr = Image.merge("RGB", (n.point(lambda v: v * 0.3), n, n.point(lambda v: v * 0.45)))
        img.paste(scr, (x, y))
        glow(img, (x + w / 2, y + h / 2), w * 0.45, (0, 50, 25), 0.6)
    # шкала частот
    d.rectangle([280, 560, 660, 620], fill=(10, 30, 16))
    px = 290 + (math.sin(t * 0.8) * 0.5 + 0.5) * 360
    d.line([px, 562, px, 618], fill=(255, 70, 50), width=3)
    for k in range(290, 660, 18):
        d.line([k, 600, k, 618], fill=(60, 200, 110), width=2)
    # Даша в профиль
    x, y = 470, 930
    d.ellipse([x - 200, y + 40, x + 200, y + 500], fill=(40, 50, 62))
    d.ellipse([x - 80, y - 150, x + 80, y + 60], fill=(190, 150, 126))
    d.chord([x - 90, y - 170, x + 90, y + 20], 150, 390, fill=(14, 12, 16))
    d.rectangle([x + 40, y - 150, x + 92, y - 10], fill=(14, 12, 16))
    d.arc([x - 100, y - 180, x + 100, y + 20], 190, 350, fill=(30, 30, 34), width=14)  # дужка наушников
    d.ellipse([x - 112, y - 80, x - 62, y + 10], fill=(30, 30, 34))
    d.ellipse([x - 70, y - 30, x - 56, y - 18], fill=(10, 10, 14))  # глаз
    # рука на ручке настройки
    kx, ky = 200, 830
    d.ellipse([kx - 50, ky - 50, kx + 50, ky + 50], fill=(70, 74, 72))
    a = t * 2.2
    d.line([kx, ky, kx + 40 * math.cos(a), ky + 40 * math.sin(a)], fill=(220, 220, 210), width=6)
    d.line([kx + 20, ky + 40, x - 140, y + 170], fill=(40, 50, 62), width=60)
    d.ellipse([kx - 10, ky + 10, kx + 60, ky + 70], fill=(190, 150, 126))
    return zoom(img, 1.0 + 0.05 * t / L, 0.4, 0.6)


def horizon_bg(t, d_img=None):
    img = vgrad(W, H, (6, 10, 20), (18, 26, 44))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 640, W, H], fill=SEA)
    waves(d, t, 650, 6, (10, 15, 26), 0.3, 0.5)
    waves(d, t, 720, 12, (8, 12, 22), 1.0, 0.7)
    waves(d, t, 860, 22, SEA, 2.0, 0.9)
    return img


def s07(t, L):
    img = horizon_bg(t)
    d = ImageDraw.Draw(img)
    SNOW_A.draw(img, t, 0.6)
    # перила
    d.rectangle([0, 980, W, 996], fill=(70, 66, 50))
    d.rectangle([0, 1080, W, 1092], fill=(60, 56, 44))
    for x in range(30, W, 140):
        d.rectangle([x, 980, x + 12, H], fill=(60, 56, 44))
    # Илья из-за плеча (левая часть кадра)
    x, y = 170, 800
    d.ellipse([x - 280, y + 120, x + 220, y + 700], fill=(150, 60, 18))
    d.ellipse([x - 150, y - 150, x + 130, y + 170], fill=(26, 26, 32))  # капюшон
    d.ellipse([x + 30, y - 40, x + 125, y + 120], fill=(120, 84, 70))  # щека
    # зажигалка
    lt = t - 0.9
    if lt > 0:
        fx, fy = x + 150, y + 70
        if lt < 1.4:
            fl = 1 + 0.3 * math.sin(lt * 30)
            glow(img, (fx, fy - 10), 70 * fl, (140, 80, 20), 0.9)
            d.polygon([(fx - 7, fy), (fx + 7, fy), (fx, fy - 26 * fl)], fill=FLAME)
            d.chord([x + 30, y - 40, x + 125, y + 120], -90, 90, fill=(210, 140, 96))
        cig = 0.6 + 0.4 * math.sin(t * 2.5)
        glow(img, (fx - 6, fy - 4), 14, (int(200 * cig), int(60 * cig), 10), 1)
        d.ellipse([fx - 10, fy - 8, fx - 2, fy], fill=(255, int(120 * cig), 40))
    return zoom(img, 1.0 + 0.05 * t / L, 0.6, 0.5)


LIGHTS = [(70, 640), (130, 643), (148, 641), (300, 636), (318, 637), (336, 638), (470, 642), (560, 639), (578, 640), (660, 641)]


def s08(t, L):
    img = horizon_bg(t)
    d = ImageDraw.Draw(img)
    gone_start, step = 3.5, 0.55
    for i, (x, y) in enumerate(LIGHTS):
        k = 1 - min(1, max(0, (t - gone_start - i * step) / 0.35))
        if k <= 0:
            continue
        tw = 0.8 + 0.2 * math.sin(t * 5 + i)
        col = (255, 220, 150) if i % 3 else (255, 90, 70)
        glow(img, (x, y), 16, tuple(int(c * 0.5) for c in col), k * tw)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=tuple(int(c * k) for c in col))
    SNOW_A.draw(img, t, 0.5)
    return zoom(img, 1.08 - 0.06 * t / L, 0.5, 0.5)


def s09(t, L, radio_t):
    img = vgrad(W, H, (4, 8, 8), (2, 4, 4))
    d = ImageDraw.Draw(img)
    on = t > radio_t - 0.3
    # рация
    d.rounded_rectangle([110, 360, 610, 760], radius=24, fill=(36, 40, 38))
    d.rounded_rectangle([130, 380, 590, 470], radius=10, fill=(8, 22, 12))
    for gx in range(160, 560, 22):
        for gy in range(500, 730, 22):
            d.ellipse([gx, gy, gx + 10, gy + 10], fill=(18, 20, 20))
    led_on = on and int(t * 8) % 2 == 0 or (not on and int(t * 1.5) % 4 == 0)
    led = (80, 255, 120) if led_on else (14, 50, 26)
    d.ellipse([540, 520, 580, 560], fill=led)
    if led_on:
        glow(img, (560, 540), 70 if on else 30, (20, 140, 60), 1)
    # индикатор уровня
    if on:
        rnd = random.Random(int(t * 20))
        for k in range(20):
            h = rnd.uniform(5, 70) * (1 if t > radio_t else 0.2)
            d.rectangle([150 + k * 21, 450 - h, 162 + k * 21, 450], fill=(80, 255, 130))
        glow(img, (360, 420), 220, (0, 50, 22), 0.8)
    # Даша вскакивает
    rise = min(1, max(0, (t - radio_t + 0.2) / 0.4)) if on else 0
    x, y = 360, 1120 - 160 * rise
    d.ellipse([x - 220, y + 60, x + 220, y + 560], fill=(30, 38, 46))
    d.ellipse([x - 80, y - 140, x + 80, y + 70], fill=(30, 36, 40) if not on else (60, 90, 70))
    d.chord([x - 90, y - 160, x + 90, y + 20], 180, 360, fill=(8, 8, 10))
    img = zoom(img, 1.0 + (0.25 * min(1, (t - radio_t + 0.3) / 0.35) if on else 0.03 * t), 0.5, 0.4)
    if on:
        img = shake(img, t, 7 * max(0, 1 - (t - radio_t) / 1.5))
    return img


def s10(t, L):
    img = vgrad(W, H, (10, 14, 26), (30, 38, 52))
    d = ImageDraw.Draw(img)
    # площадка в перспективе
    d.polygon([(-200, 1280), (920, 1280), (600, 760), (120, 760)], fill=(44, 50, 46))
    d.polygon([(250, 1280), (470, 1280), (400, 760), (320, 760)], fill=(40, 46, 42))
    d.line([120, 760, -200, 1280], fill=YELLOW, width=8)
    d.line([600, 760, 920, 1280], fill=YELLOW, width=8)
    # бегущие
    beams = []
    for i, (bx, by, s, ph) in enumerate([(160, 1180, 1.25, 0.0), (330, 1080, 1.0, 1.6), (500, 1150, 1.15, 3.1), (600, 1010, 0.85, 4.4)]):
        x = bx + 20 * math.sin(t * 0.6 + i) - 16 * t
        y = by - 50 * t
        beams.append(runner(d, x, y, s, t, ph))
    for i, b in enumerate(beams):
        ang = -1.35 + 0.25 * math.sin(t * 1.4 + i * 1.7)
        img = beam(img, b, ang, 900, 0.12, 0.35)
    SNOW_STORM.draw(img, t, 0.9, wind=900)
    img = shake(img, t, 6)
    return zoom(img, 1.06, 0.5, 0.6)


# следы: от края площадки (низ кадра) к двери (верх)
STEPS = []
for k in range(14):
    yy = 1220 - k * 62
    xx = 300 + 45 * math.sin(k * 0.5) + (28 if k % 2 else -28)
    STEPS.append((xx, yy, k % 2))


def s11(t, L):
    base = Image.new("RGB", (W, H), (16, 18, 22))
    d = ImageDraw.Draw(base)
    for y in range(0, H, 40):
        d.line([0, y, W, y], fill=(22, 26, 30), width=2)
    rnd = random.Random(5)
    for _ in range(500):
        x, y = rnd.random() * W, rnd.random() * H
        d.line([x, y, x + 8, y + 3], fill=(26, 30, 34), width=2)
    # дверь
    d.rectangle([240, 120, 480, 420], fill=(40, 46, 52))
    d.rectangle([250, 130, 470, 420], fill=(30, 34, 40))
    gap = 18 + 6 * math.sin(t * 2)
    d.rectangle([360 - gap / 2, 135, 360 + gap / 2, 420], fill=(255, 200, 120))
    # следы
    for (x, y, side) in STEPS:
        s = 0.55 + 0.45 * (y / H)
        d.ellipse([x - 20 * s, y - 34 * s, x + 20 * s, y + 20 * s], fill=(8, 12, 16))
        d.ellipse([x - 16 * s, y + 24 * s, x + 16 * s, y + 46 * s], fill=(8, 12, 16))
        d.ellipse([x - 6 * s, y - 28 * s, x + 2 * s, y - 18 * s], fill=(90, 120, 140))  # блик воды
    # тьма + луч
    dark = ImageChops.multiply(base, Image.new("RGB", (W, H), (60, 60, 70)))
    p = min(1, t / (L * 0.8))
    ty = 1230 - p * 1000
    tx = 300 + 45 * math.sin((1230 - ty) / 62 * 0.5)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(W / 2 - 40, H + 40), (W / 2 + 40, H + 40), (tx + 170, ty - 110), (tx - 170, ty - 110)], fill=255)
    ImageDraw.Draw(mask).ellipse([tx - 180, ty - 190, tx + 180, ty + 130], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(30))
    lit = ImageChops.multiply(base, Image.new("RGB", (W, H), (255, 245, 220)))
    lit = Image.eval(lit, lambda v: min(255, int(v * 2.4)))
    img = Image.composite(lit, dark, mask)
    # свет из двери всегда виден
    glow(img, (360, 280), 70, (90, 60, 20), 0.6)
    SNOW_A.draw(img, t, 0.4, wind=300)
    return zoom(img, 1.05, 0.5, 0.5)


def s12(t, L):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    # море далеко внизу с пеной
    rnd = random.Random(9)
    for i in range(140):
        x0, y0 = rnd.random() * W, 500 + rnd.random() * 780
        r = rnd.uniform(8, 40)
        ph = rnd.random() * 6.28
        a = 0.5 + 0.5 * math.sin(t * 1.6 + ph)
        c = int(30 + 90 * a)
        x = x0 + 20 * math.sin(t * 0.7 + ph)
        d.ellipse([x - r, y0 - r * 0.4, x + r, y0 + r * 0.4], fill=(c - 10, c, c + 10))
    img = img.filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(img)
    # опоры уходят вниз в перспективе
    for x1, x2 in [(80, 250), (640, 470)]:
        d.polygon([(x1 - 40, 420), (x1 + 40, 420), (x2 + 12, 1280), (x2 - 12, 1280)], fill=(26, 30, 38))
    # край площадки сверху
    d.rectangle([0, 0, W, 420], fill=(44, 50, 46))
    for k in range(0, W + 60, 60):
        d.polygon([(k, 380), (k + 30, 380), (k + 10, 420), (k - 20, 420)], fill=YELLOW)
    d.polygon([(300, 360), (340, 360), (330, 300), (310, 300)], fill=(8, 12, 16))
    beam_img = beam(img, (W / 2, 120), math.pi / 2 + 0.1 * math.sin(t), 1300, 0.10, 0.3)
    img = beam_img
    SNOW_B.draw(img, t, 0.6)
    img = zoom(img, 1.0 + 0.12 * t / L, 0.5, 0.7)
    fade = max(0, (t - (L - 1.6)) / 1.2)
    if fade > 0:
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), min(1, fade))
    return img


FUNCS = {n: globals()[n] for n, *_ in PLAN}


def frame(t):
    for name, start, length, sc_cues in scenes:
        if start <= t < start + length:
            lt = t - start
            if name == "s09":
                radio_t = [s for s, c, d in sc_cues if c == "09r"][0]
                img = s09(lt, length, radio_t)
            else:
                img = FUNCS[name](lt, length)
            img = grade(img)
            # короткая склейка через чёрное
            k = min(lt / 0.25, (length - lt) / 0.25, 1)
            if name != "s01" and k < 1:
                img = Image.blend(Image.new("RGB", (W, H)), img, max(0, k))
            draw_subs(img, t)
            return img
    return Image.new("RGB", (W, H))


def build_audio(path):
    """озвучка + ветер + гул + помехи рации, всё синтезом ffmpeg"""
    inputs, filters, mix = [], [], []
    for i, (start, clip, d) in enumerate(cues):
        inputs += ["-i", os.path.join(TTS, clip + ".mp3")]
        ms = int(start * 1000)
        if clip == "09r":
            filters.append(f"[{i}:a]highpass=f=450,lowpass=f=2600,acrusher=bits=6:mix=0.35,volume=1.6,aecho=0.8:0.5:40:0.25,adelay={ms}|{ms}[v{i}]")
        else:
            filters.append(f"[{i}:a]volume=1.35,adelay={ms}|{ms}[v{i}]")
        mix.append(f"[v{i}]")
    n = len(cues)
    dur_s = f"{TOTAL:.2f}"
    inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.6:d={dur_s}:seed=4"]
    filters.append(f"[{n}:a]lowpass=f=500,volume='0.35+0.18*sin(t*0.7)+0.1*sin(t*1.9)':eval=frame[wind]")
    inputs += ["-f", "lavfi", "-i", f"aevalsrc='0.10*sin(2*PI*55*t)+0.07*sin(2*PI*82.4*t)+0.04*sin(2*PI*110.3*t)':d={dur_s}"]
    filters.append(f"[{n+1}:a]volume=0.8[drone]")
    # помехи — только в радиорубке (сцены 6 и 9)
    st = {name: (s, l) for name, s, l, _ in scenes}
    s6, l6 = st["s06"]; s9, l9 = st["s09"]
    inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=white:amplitude=0.25:d={dur_s}:seed=7"]
    filters.append(f"[{n+2}:a]highpass=f=1500,lowpass=f=6000,volume='if(between(t,{s6:.2f},{s6+l6:.2f})+between(t,{s9:.2f},{s9+l9:.2f}),0.35,0)':eval=frame[stat]")
    # удар на следах
    s11, _ = st["s11"]
    hit = int((s11 + 0.4) * 1000)
    inputs += ["-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(42+30*exp(-t*6))*t)*exp(-t*1.6)':d=3"]
    filters.append(f"[{n+3}:a]adelay={hit}|{hit}[hit]")
    filters.append("".join(mix) + f"[wind][drone][stat][hit]amix=inputs={n+4}:normalize=0,alimiter=limit=0.95,afade=t=out:st={TOTAL-1.5:.2f}:d=1.5[out]")
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filters), "-map", "[out]",
                                                     "-ac", "2", "-ar", "44100", "-t", dur_s, path]
    subprocess.check_call(cmd)


if __name__ == "__main__":
    audio = OUT + ".wav"
    build_audio(audio)
    nframes = int(TOTAL * FPS)
    print(f"длительность {TOTAL:.1f} c, кадров {nframes}", flush=True)
    only = os.environ.get("PREVIEW")  # PREVIEW=12.5,40 → только png-кадры
    if only:
        for ts in only.split(","):
            frame(float(ts)).save(f"{OUT}_{ts}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    for i in range(nframes):
        ff.stdin.write(frame(i / FPS).tobytes())
        if i % 240 == 0:
            print(f"{i}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()
    os.remove(audio)
    print("готово:", OUT)
