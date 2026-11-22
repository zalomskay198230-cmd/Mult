"""«НОЧНАЯ СМЕНА». Серия 1. Плоский 2D-хоррор от первого лица (механика: таймер, короткие фразы, выбор в конце).
Кадр рисуется в 2× и сглаживается. Субтитры — капсом с цветными словами (из den365).
Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
D365 = os.path.join(ROOT, "den365", "render")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, D365)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(ROOT, "den365", "tts", "s01_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s01", os.path.join(D365, "seriya01.py"))
E1 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E1)          # субтитры капсом с цветными словами
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import flatworld as FW
from flatworld import SD, chibi, OUT, dk, mix

W, H = toonlib.W, toonlib.H
F = E1.F
YEL, RED, WHITE = (255, 206, 40), (255, 72, 60), (255, 255, 255)
GREENL = (150, 230, 190)
K = 2   # суперсэмплинг кадра

FW.CHAR["intern"] = dict(skin=(238, 196, 166), hair=(52, 40, 34), top=(236, 240, 240), pants=(70, 140, 130), shoes=(230, 230, 232), style="short")
FW.CHAR["guard"] = dict(skin=(226, 186, 156), hair=(170, 170, 176), top=(40, 52, 80), pants=(40, 44, 56), shoes=(30, 30, 34), style="bald", beard=(180, 180, 186))

LINES = {
    "01": "Первая ночь в *морге*. Я стажёр. ^Один^.",
    "02": "Сторож сказал: «Каталки не трогай. И в *третий* *бокс* не заходи».",
    "03": "Два четырнадцать. Обход. *Шесть* каталок. Шесть простыней.",
    "04": "Считаю. Раз, два, три, четыре… *Пятая* — ^пустая^.",
    "05": "Простыня на полу. ^Мокрая^.",
    "06": "Под ней следы. ^Босые^. Ведут к *третьему* боксу.",
    "07": "Дверь приоткрыта. Оттуда тянет ^холодом^.",
    "08": "И тихий голос. Кто-то ^считает^. Раз. Два. Три.",
    "09": "Голос замолкает на ^пяти^.",
    "10": "Свет ^гаснет^.",
    "11": "В темноте скрипят колёса. Каталка ^едет^ ко мне.",
    "12": "Бежать к *выходу* через весь коридор? Или запереться в *третьем* боксе? ^Решай^.",
}
PLAN = [(f"m{k}", [(k, 0.05)], 0.15) for k in LINES]
PLAN[0] = ("m01", [("01", 0.0)], 0.15)
PLAN[8] = ("m09", [("09", 0.05)], 0.6)
PLAN[9] = ("m10", [("10", 0.1)], 0.5)
PLAN[-1] = ("m12", [("12", 0.05)], 1.2)
setup(LINES, PLAN)

# ---------- коридор в перспективе ----------
VX, VY = 360, 560            # точка схода
BX0, BY0, BX1, BY1 = 290, 500, 430, 640   # дальняя стена
TILE = (176, 196, 188)


def P(x, y):
    """точка экрана в координатах кадра (720×1280) → рисуем через SD с k=2"""
    return (x, y)


def lerp(a, b, k):
    return a + (b - a) * k


def corridor(light=1.0, door_open=0.0):
    img = Image.new("RGB", (W * K, H * K))
    d = SD(img, 0, 0, K)
    L = light
    col = lambda c, k=1.0: tuple(int(v * L * k) for v in c)
    # потолок, пол, стены
    d.polygon([(0, 0), (W, 0), (BX1, BY0), (BX0, BY0)], fill=col((70, 84, 80)))
    d.polygon([(0, H), (W, H), (BX1, BY1), (BX0, BY1)], fill=col((96, 104, 100)))
    d.polygon([(0, 0), (BX0, BY0), (BX0, BY1), (0, H)], fill=col(TILE, .82))
    d.polygon([(W, 0), (BX1, BY0), (BX1, BY1), (W, H)], fill=col(TILE, .9))
    d.rectangle([BX0, BY0, BX1, BY1], fill=col((40, 46, 46)))
    d.rectangle([BX0 + 40, BY0 + 30, BX1 - 40, BY1], fill=col((20, 24, 24)))   # дальний проём — темнота
    # плитка: линии на стенах и полу
    for i in range(1, 14):
        k = (i / 14) ** 1.6
        for side in (0, 1):
            x0 = 0 if side == 0 else W
            xb = BX0 if side == 0 else BX1
            x = lerp(x0, xb, k)
            y0, y1 = lerp(0, BY0, k), lerp(H, BY1, k)
            d.line([(x, y0), (x, y1)], fill=col(TILE, .7), width=2)
        y = lerp(H, BY1, k)
        d.line([(lerp(0, BX0, k), y), (lerp(W, BX1, k), y)], fill=col((84, 92, 88)), width=2)
    for j in range(1, 6):
        for side in (0, 1):
            xa = 0 if side == 0 else W
            xb = BX0 if side == 0 else BX1
            ya, yb = H * j / 6, lerp(BY0, BY1, j / 6)
            d.line([(xa, ya), (xb, yb)], fill=col(TILE, .7), width=2)
    for j in range(1, 7):
        x = W * j / 7
        d.line([(x, H), (lerp(BX0, BX1, j / 7), BY1)], fill=col((84, 92, 88)), width=2)
    # двери на правой стене, номер 3 — ближе всех к середине
    for n, k in ((1, .25), (2, .5), (3, .72)):
        xa, xb = lerp(W, BX1, k - .08), lerp(W, BX1, k + .04)
        ya0, ya1 = lerp(0, BY0, k - .08) + 120 * (1 - k), lerp(H, BY1, k - .08)
        yb0, yb1 = lerp(0, BY0, k + .04) + 120 * (1 - k - .04), lerp(H, BY1, k + .04)
        door_col = col((60, 70, 76))
        d.polygon([(xa, ya0), (xb, yb0), (xb, yb1), (xa, ya1)], fill=door_col, outline=col((30, 34, 36)))
        if n == 3 and door_open > 0:   # щель — тьма и холод
            gx = lerp(xa, xb, .2 + .5 * door_open)
            d.polygon([(xa, ya0), (gx, lerp(ya0, yb0, .3)), (gx, lerp(ya1, yb1, .3)), (xa, ya1)], fill=(6, 10, 14))
        cx, cy = (xa + xb) / 2, (ya0 + yb0) / 2 + 40 * (1 - k)
        d.rectangle([cx - 16 * (1 - k * .6), cy - 18 * (1 - k * .6), cx + 16 * (1 - k * .6), cy + 18 * (1 - k * .6)], fill=col((220, 220, 210)))
        f = F(int(26 * (1 - k * .6)), FONT_SUB)
        d.text((cx - f.getlength(str(n)) / 2, cy - 15 * (1 - k * .6)), str(n), font=f, fill=(150, 20, 20) if n == 3 else (30, 30, 30))
    # лампы дневного света
    for k in (.15, .45, .7, .88):
        y = lerp(0, BY0, k) + 6
        x0, x1 = lerp(120, BX0 + 30, k), lerp(600, BX1 - 30, k)
        d.rectangle([x0, y, x1, y + 14 * (1 - k) + 3], fill=col((230, 255, 236)) if L > .5 else (30, 34, 32))
    return img, d


def gurney(d, x, y, s=1.0, empty=False, light=1.0):
    """каталка (вид сбоку-сверху), y — уровень пола"""
    L = light
    c = lambda v: tuple(int(q * L) for q in v)
    d.rectangle([x - 110 * s, y - 92 * s, x + 110 * s, y - 80 * s], fill=c((170, 176, 182)), outline=c((60, 64, 70)), width=max(1, int(2 * s)))
    for lx in (-92, 92):
        d.line([(x + lx * s, y - 80 * s), (x + lx * s, y - 14 * s)], fill=c((140, 146, 152)), width=max(1, int(5 * s)))
        d.ellipse([x + lx * s - 10 * s, y - 16 * s, x + lx * s + 10 * s, y + 4 * s], fill=c((40, 40, 44)))
    if not empty:
        d.polygon([(x - 116 * s, y - 92 * s), (x - 100 * s, y - 128 * s), (x + 60 * s, y - 136 * s), (x + 100 * s, y - 120 * s),
                   (x + 116 * s, y - 92 * s), (x + 118 * s, y - 64 * s), (x - 118 * s, y - 64 * s)], fill=c((232, 236, 236)), outline=c((150, 160, 160)))
        d.ellipse([x + 52 * s, y - 150 * s, x + 104 * s, y - 116 * s], fill=c((226, 232, 232)), outline=c((150, 160, 160)))   # голова под простынёй


# каталки вдоль левой стены, глубина k
GURNEYS = [(.08, 170), (.3, 200), (.48, 230), (.62, 250), (.74, 268), (.84, 282)]


def gurney_pos(i):
    k, _ = GURNEYS[i]
    y = lerp(H - 40, BY1, k)
    x = lerp(160, BX0 + 30, k)
    s = lerp(1.15, .2, k)
    return x, y, s


def draw_gurneys(d, light=1.0, empty5=True, skip=None):
    for i in range(len(GURNEYS) - 1, -1, -1):
        if skip is not None and i == skip:
            continue
        x, y, s = gurney_pos(i)
        gurney(d, x, y, s, empty=(i == 4 and empty5), light=light)


def flashlight(img, x0, y0, x1, y1, spread=170, a=90):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([(x0 * K, y0 * K), ((x1 - spread) * K, y1 * K), ((x1 + spread) * K, y1 * K)], fill=a)
    img.paste(Image.new("RGB", img.size, (255, 246, 214)), (0, 0), m.filter(ImageFilter.GaussianBlur(24)))


def done(img):
    return img.resize((W, H), Image.LANCZOS)


def timer(img, t, base=(2, 14, 0)):
    h, m, s = base
    tot = h * 3600 + m * 60 + s + int(t)
    txt = f"{tot // 3600:02d}:{tot // 60 % 60:02d}:{tot % 60:02d}"
    d = ImageDraw.Draw(img)
    f = F(24, FONT_SUB)
    w = f.getlength(txt) + 28
    d.rounded_rectangle([W / 2 - w / 2, 40, W / 2 + w / 2, 80], radius=10, fill=(10, 12, 14))
    d.text((W / 2 - f.getlength(txt) / 2, 48), txt, font=f, fill=(230, 236, 232))


def tag(img, txt, y=100, col=(10, 12, 14), fg=WHITE, size=26):
    d = ImageDraw.Draw(img)
    f = F(size, FONT_SUB)
    w = f.getlength(txt) + 36
    d.rounded_rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + size + 20], radius=12, fill=col)
    d.text((W / 2 - f.getlength(txt) / 2, y + 9), txt, font=f, fill=fg)


def big(img, txt, y, col=RED, size=96):
    f = F(size, FONT_SUB)
    while f.getlength(txt) > W - 60:
        size -= 6; f = F(size, FONT_SUB)
    ImageDraw.Draw(img).text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col, stroke_width=7, stroke_fill=(8, 8, 10))


def bubble(img, txt, x, y):
    d = ImageDraw.Draw(img)
    f = F(26, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([x - w / 2 - 18, y - 56, x + w / 2 + 18, y - 8], radius=18, fill=WHITE)
    d.polygon([(x - 10, y - 10), (x + 10, y - 10), (x, y + 8)], fill=WHITE)
    d.text((x - w / 2, y - 48), txt, font=f, fill=(20, 20, 24))


# ---------- сцены ----------
def m01(t, L, cue):
    img, d = corridor()
    draw_gurneys(d, empty5=False)
    chibi(d, "intern", 470, 1180, 2.1, t, "neutral", -1, arm="phone")
    img = done(img)
    flashlight(img, 450, 760, 300, 560, 120, 70)
    timer(img, t)
    tag(img, "МОРГ · НОЧЬ 1", 100)
    return img


def m02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    img, d = corridor(door_open=0)
    draw_gurneys(d, empty5=False)
    chibi(d, "guard", 470, 1100, 1.9, t, "neutral", -1)
    img = done(img)
    if p > .1:
        bubble(img, "каталки не трогай", 470, 690)
    if p > .55:
        bubble(img, "в БОКС 3 не заходи", 470, 590)
    timer(img, t, (2, 10, 0))
    return img


def m03(t, L, cue):
    img, d = corridor()
    draw_gurneys(d, empty5=False)
    img = done(img)
    flashlight(img, 600, 1280, 260, 900, 160, 80)
    timer(img, t, (2, 14, 0))
    tag(img, "ОБХОД", 100)
    return img


def m04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img, d = corridor()
    n = min(5, 1 + int(p * 5.2))
    draw_gurneys(d, empty5=n >= 5)
    img = done(img)
    dd = ImageDraw.Draw(img)
    for i in range(n):
        x, y, s = gurney_pos(i)
        f = F(max(26, int(70 * s)), FONT_SUB)
        num = str(i + 1)
        dd.text((x - f.getlength(num) / 2, y - 200 * s - 40), num, font=f, fill=RED if i == 4 else YEL, stroke_width=4, stroke_fill=(8, 8, 10))
    flashlight(img, 600, 1280, 260, 900, 160, 70)
    timer(img, t, (2, 14, 6))
    return shake(img, t, 4 if p > .85 else 0)


def m05(t, L, cue):
    img = Image.new("RGB", (W * K, H * K), (90, 98, 96))
    d = SD(img, 0, 0, K)
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=(78, 86, 84), width=3)
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=(78, 86, 84), width=3)
    d.polygon([(120, 520), (420, 470), (610, 600), (560, 820), (300, 860), (140, 760)], fill=(230, 234, 234), outline=(150, 160, 160))
    for i in range(6):   # складки и мокрые пятна
        d.line([(200 + i * 60, 560), (260 + i * 50, 800)], fill=(200, 208, 210), width=6)
    for i in range(10):
        yy = 880 + ((t * 120 + i * 40) % 300)
        d.ellipse([300 + (i * 37) % 200, yy, 312 + (i * 37) % 200, yy + 16], fill=(120, 150, 170))
    d.ellipse([200, 860, 560, 960], fill=(70, 96, 110))   # лужа
    img = done(img)
    flashlight(img, 360, 1280, 360, 600, 260, 70)
    timer(img, t, (2, 14, 20))
    tag(img, "МОКРАЯ", 100, (150, 30, 30))
    return img


def footprint(d, x, y, s=1.0, left=True):
    m = -1 if left else 1
    d.ellipse([x - 16 * s, y - 34 * s, x + 16 * s, y + 6 * s], fill=(40, 52, 58))
    d.ellipse([x - 12 * s, y + 4 * s, x + 12 * s, y + 26 * s], fill=(40, 52, 58))
    for i in range(5):
        tx = x + m * (-12 + i * 6) * s
        d.ellipse([tx - 4 * s, y - 48 * s - (i % 3) * 3 * s, tx + 4 * s, y - 40 * s - (i % 3) * 3 * s], fill=(40, 52, 58))


def m06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    img, d = corridor(door_open=.15)
    draw_gurneys(d)
    n = int(min(1, p * 1.2) * 9)
    for i in range(n):   # следы к двери 3
        k = i / 9
        x = lerp(330, 520, k) + (14 if i % 2 else -14) * (1 - k)
        y = lerp(1180, 700, k)
        footprint(d, x, y, lerp(1.5, .5, k), i % 2 == 0)
    img = done(img)
    flashlight(img, 360, 1280, 470, 800, 200, 70)
    timer(img, t, (2, 14, 31))
    if p > .6:
        tag(img, "БОСЫЕ", 100, (150, 30, 30))
    return img


def mist(img, t, x, y, k=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i in range(7):
        life = (t * .35 + i / 7) % 1
        r = 40 + 90 * life
        ld.ellipse([x - 30 - r + 140 * life, y - r * .5 + 40 * math.sin(i), x - 30 + r + 140 * life, y + r * .5], fill=(210, 230, 240, int(90 * (1 - life) * k)))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(14))).convert("RGB")


def door3_close(t, dark=0.0):
    """крупно дверь бокса 3, щель с туманом"""
    img = Image.new("RGB", (W * K, H * K), (150, 168, 162))
    d = SD(img, 0, 0, K)
    for y in range(0, H, 70):
        d.line([(0, y), (W, y)], fill=(132, 150, 144), width=3)
    for x in range(0, W, 70):
        d.line([(x, 0), (x, H)], fill=(132, 150, 144), width=3)
    d.rectangle([140, 200, 600, 1180], fill=(62, 72, 78), outline=(26, 30, 32), width=8)
    d.polygon([(560, 200), (600, 200), (600, 1180), (560, 1180)], fill=(6, 10, 14))   # щель
    d.rectangle([300, 320, 440, 470], fill=(226, 226, 216), outline=(40, 40, 40), width=4)
    f = F(120, FONT_SUB)
    d.text((370 - f.getlength("3") / 2, 322), "3", font=f, fill=(150, 20, 20))
    d.ellipse([520, 680, 556, 716], fill=(170, 176, 182), outline=(40, 40, 40), width=3)
    img = done(img)
    img = mist(img, t, 600, 700, 1.0)
    if dark:
        img = Image.blend(img, Image.new("RGB", (W, H)), dark)
    return img


def m07(t, L, cue):
    img = toonlib.zoom(door3_close(t), 1 + .06 * t / L, .7, .5)
    timer(img, t, (2, 14, 40))
    tag(img, "ХОЛОД", 100, (40, 70, 110))
    return img


def m08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    img = toonlib.zoom(door3_close(t, .2), 1.06 + .05 * t / L, .7, .5)
    words = ["РАЗ…", "ДВА…", "ТРИ…"]
    n = 0 if p < .55 else min(3, 1 + int((p - .55) / .14))
    for i in range(n):
        big(img, words[i], 300 + i * 110, (220, 230, 236), 84)
    timer(img, t, (2, 14, 47))
    return img


def m09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = door3_close(t, .35)
    for i, w in enumerate(["РАЗ…", "ДВА…", "ТРИ…", "ЧЕТЫРЕ…"]):
        big(img, w, 240 + i * 100, (150, 160, 166), 70)
    if p > .3:
        big(img, "ПЯТЬ.", 660, RED, 130)
    timer(img, t, (2, 14, 53))
    return shake(img, t, 6 if .3 < p < .4 else 0)


def m10(t, L, cue):
    p = (t - cue["10"]) / dur("10.mp3")
    img, d = corridor(light=1.0 if p < .3 or (.4 < p < .5) else .12)
    draw_gurneys(d, light=1.0 if p < .3 else .12)
    img = done(img)
    if p >= .3:
        flashlight(img, 360, 1280, 360, 620, 150, 60)
    timer(img, t, (2, 15, 0))
    return img


def m11(t, L, cue):
    p = (t - cue["11"]) / dur("11.mp3")
    img = Image.new("RGB", (W * K, H * K), (4, 5, 6))
    d = SD(img, 0, 0, K)
    k = ease(min(1, p * 1.1))
    s = .25 + 1.2 * k   # каталка едет из темноты
    gurney(d, 360, 640 + 520 * k, s, empty=False, light=.55 + .4 * k)
    img = done(img)
    flashlight(img, 360, 1280, 360, 560, 170, 70)
    timer(img, t, (2, 15, 4))
    if p > .3:
        tag(img, "СКРИП…", 100, (20, 22, 24), (220, 220, 220))
    return shake(img, t, 3 + 6 * k if p > .4 else 0)


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def choice_card(img, x0, title, kind, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    w, h = 300, 400
    y0 = 360
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=20, fill=(16, 20, 24), outline=(200, 210, 210), width=4)
    mini = Image.new("RGB", (w - 24, h - 110), (20, 26, 28))
    md = ImageDraw.Draw(mini)
    if kind == "run":   # коридор и стрелка к выходу
        md.polygon([(0, mini.height), (mini.width, mini.height), (mini.width * .6, mini.height * .4), (mini.width * .4, mini.height * .4)], fill=(70, 80, 78))
        md.rectangle([mini.width * .4, mini.height * .2, mini.width * .6, mini.height * .4], fill=(40, 200, 90))
        md.text((mini.width * .41, mini.height * .23), "ВЫХОД", font=F(18, FONT_SUB), fill=WHITE)
        md.polygon([(mini.width * .5, mini.height * .5), (mini.width * .42, mini.height * .7), (mini.width * .58, mini.height * .7)], fill=YEL)
    else:               # дверь 3
        md.rectangle([mini.width * .25, mini.height * .1, mini.width * .75, mini.height * .95], fill=(62, 72, 78), outline=(10, 10, 10), width=4)
        md.text((mini.width * .43, mini.height * .2), "3", font=F(70, FONT_SUB), fill=(170, 30, 30))
    lay.paste(mini, (x0 + 12, y0 + 12))
    f = F(24, FONT_SUB)
    for i, ln in enumerate(title.split("\n")):
        d.text((x0 + w / 2 - f.getlength(ln) / 2, y0 + h - 88 + i * 32), ln, font=f, fill=WHITE)
    return Image.blend(img, lay, a)


def m12(t, L, cue):
    img = Image.new("RGB", (W, H), (10, 14, 18))
    d = ImageDraw.Draw(img)
    f = F(34, FONT_SUB)
    d.text(((W - f.getlength("ЧТО ДЕЛАТЬ?")) / 2, 250), "ЧТО ДЕЛАТЬ?", font=f, fill=WHITE)
    img = choice_card(img, 40, "Бежать к выходу\nчерез коридор", "run", min(1, t / .3))
    img = choice_card(img, 380, "Запереться\nв боксе №3", "door", min(1, max(0, t - .3) / .3))
    p = (t - cue["12"]) / dur("12.mp3")
    if p > .85:
        big(img, "РЕШАЙ", 800, RED, 80)
    d = ImageDraw.Draw(img)
    fp = F(30, FONT_SUB)
    txt = "ПОДПИШИСЬ — УЗНАЕШЬ, ЧТО ДАЛЬШЕ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 22, 940, W / 2 + fp.getlength(txt) / 2 + 22, 998], radius=28, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 951), txt, font=fp, fill=(20, 20, 24))
    timer(img, t, (2, 15, 9))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=[span("m11")[0] + .3 + i * .45 for i in range(5)],
        hits=[span("m04")[0] + span("m04")[1] * .85, span("m09")[0] + span("m09")[1] * .35, span("m10")[0] + span("m10")[1] * .3])
