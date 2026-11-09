"""«БАБУШКУ УКУСИЛИ». Серия 1. Гибрид: 3D-фоны (babushka/frames_bg, сцены b1_*) + 2D-персонажи.
Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
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
import person

LINES = {
    "01": "Мою бабушку укусили. Я никому не сказал.",
    "02": "Город уже неделю на карантине. По радио каждый час одно и то же.",
    "03r": "«Внимание. Всех укушенных — немедленно передать санитарному патрулю. Укрывательство карается по закону».",
    "04": "Патрули ходят по квартирам. Укушенных увозят. Обратно не вернулся никто.",
    "05": "Бабушку укусили три дня назад, у магазина. Она сказала — собака. Но я видел, кто это был.",
    "06": "Я заклеил окна. Соседям сказал, что бабушка уехала к сестре.",
    "07": "Она начала забывать слова. Вчера назвала чайник «эта… горячая».",
    "08": "Но каждое утро она печёт блины. Как всегда. С вишнёвым вареньем. Это она помнит.",
    "09": "А это оказалось не так просто — прятать человека, который не понимает, что его надо прятать.",
    "10": "Сегодня утром она открыла окно. И запела. На весь двор.",
    "11": "А через час в дверь постучали.",
    "12r": "«Откройте. Санитарный патруль. У нас сигнал».",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[0] = ("s01", [("01", 0.6)], 0.6)            # первые полсекунды — молча, только рука и блин
PLAN[10] = ("s11", [("11", 0.05)], 1.9)          # пауза под стук
PLAN[-1] = ("s12r", [("12r", 0.3)], 4.2)
setup(LINES, PLAN)
# в первой сцене текст уже есть титром — субтитры не дублируем
_s2 = [x for x in toonlib.scenes if x[0] == "s02"][0][1]
toonlib.SUBS[:] = [x for x in toonlib.SUBS if x[0] >= _s2]

FR = os.path.join(ROOT, "babushka", "frames_bg")
F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
GY = 1250
_cache = {}
SKIN_B = person.CAST["babushka"]["skin"]


def bg(name, bright=1.0, blur=0):
    key = (name, bright, blur)
    if key not in _cache:
        im = Image.open(os.path.join(FR, f"{name}_0000.png")).convert("RGB").resize((W, H), Image.LANCZOS)
        im = ImageEnhance.Brightness(im).enhance(bright)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        _cache[key] = im
    return _cache[key].copy()


def L2S(ox, ground, s, x, y):
    return (ox + x * s, ground - 962 * s + y * s)


def char(img, fig, shadow=True):
    a = fig.getchannel("A")
    bb = a.getbbox()
    if bb and shadow:
        x0, y0, x1, y1 = bb
        sh = Image.new("L", (W, H), 0)
        cx, w = (x0 + x1) / 2, (x1 - x0) * .55
        ImageDraw.Draw(sh).ellipse([cx - w, y1 - 16, cx + w, y1 + 18], fill=140)
        img.paste(Image.new("RGB", (W, H)), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    img.paste(fig, (0, 0), fig)
    return img


def sasha(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), legs="idle", ground=GY):
    DR.use("vnuk", hoodie=True)
    return char(img, DR.front((W, H), x, ground, s, t, arms, legs, expr, look))


def babushka(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, prop=None):
    DR.use("babushka", hoodie=False)
    img = char(img, DR.front((W, H), x, ground, s, t, arms, "idle", expr, look))
    d = ImageDraw.Draw(img)
    P = lambda lx, ly: L2S(x, ground, s, lx, ly)
    # фартук
    d.polygon([P(-46, 226), P(46, 226), P(52, 300), P(-52, 300)], fill=(246, 240, 228), outline=INK)
    d.polygon([P(-74, 300), P(74, 300), P(84, 520), P(-84, 520)], fill=(246, 240, 228), outline=INK)
    for k in range(-60, 70, 30):
        d.ellipse([*P(k - 6, 380 - 6), *P(k + 6, 380 + 6)], fill=(214, 70, 70))
    # бинт на правом запястье
    el, wr = DR.ARM[arms[1]] if isinstance(arms[1], str) else arms[1]
    bx, by = (wr[0] * .75 + el[0] * .25), (wr[1] * .75 + el[1] * .25)
    cx, cy = P(bx, by)
    r = 30 * s
    d.rounded_rectangle([cx - r, cy - r * .7, cx + r, cy + r * .7], radius=int(10 * s), fill=(248, 248, 244), outline=INK, width=2)
    d.line([cx - r * .7, cy - r * .2, cx + r * .7, cy + r * .1], fill=(200, 200, 196), width=2)
    d.ellipse([cx + r * .2, cy - r * .3, cx + r * .5, cy], fill=(200, 120, 110))   # пятнышко
    hx, hy = P(wr[0], wr[1] + 12)
    if prop == "pan":
        d.line([hx, hy, hx + 90 * s, hy - 10 * s], fill=(30, 30, 34), width=int(14 * s))
        d.ellipse([hx + 70 * s, hy - 60 * s, hx + 250 * s, hy + 30 * s], fill=(40, 40, 44), outline=INK, width=3)
        d.ellipse([hx + 100 * s, hy - 45 * s, hx + 220 * s, hy + 15 * s], fill=(232, 176, 84))
    if prop == "kettle":
        d.ellipse([hx - 10 * s, hy - 20 * s, hx + 110 * s, hy + 90 * s], fill=(220, 60, 50), outline=INK, width=3)
        d.line([hx + 100 * s, hy + 20 * s, hx + 150 * s, hy - 10 * s], fill=(220, 60, 50), width=int(12 * s))
    return img


def patrol(img, x, s, t, legs="idle", arms=("down", "down")):
    DR.use("patrul", hoodie=False)
    img = char(img, DR.front((W, H), x, GY, s, t, arms, legs, "neutral", (0, 0)))
    d = ImageDraw.Draw(img)
    P = lambda lx, ly: L2S(x, GY, s, lx, ly)
    d.ellipse([*P(-78, -30), *P(78, 170)], fill=(222, 196, 46), outline=INK, width=3)    # капюшон
    d.rounded_rectangle([*P(-50, 30), *P(50, 140)], radius=int(30 * s), fill=(30, 30, 34), outline=INK, width=3)   # маска
    d.rounded_rectangle([*P(-40, 44), *P(40, 92)], radius=int(16 * s), fill=(120, 160, 180))   # визор
    for sx in (-1, 1):
        d.ellipse([*P(sx * 46 - 18, 110), *P(sx * 46 + 18, 150)], fill=(60, 60, 66), outline=INK, width=2)   # фильтры
    return img


def plate(img, txt, y=150, col=(20, 22, 30), fg=(240, 240, 244)):
    d = ImageDraw.Draw(img)
    f = F(36, FONT_SUB)
    d.rounded_rectangle([40, y, 64 + f.getlength(txt), y + 58], radius=12, fill=col)
    d.text((52, y + 8), txt, font=f, fill=fg)


def steam(img, t, x, y, n=4):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i in range(n):
        life = (t * .45 + i / n) % 1
        yy = y - 260 * life
        xx = x + 30 * math.sin(life * 6 + i)
        r = 30 + 40 * life
        ld.ellipse([xx - r, yy - r * .6, xx + r, yy + r * .6], fill=(255, 255, 255, int(110 * (1 - life))))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(10))).convert("RGB")


# ---------- сцены ----------
def s01(t, L, cue):   # крупно: забинтованная рука, сковородка, блин + титр
    img = bg("b1_kitchen_close", 1.0, 4)
    d = ImageDraw.Draw(img)
    cx, cy = 330, 860
    d.ellipse([cx - 280, cy - 150, cx + 280, cy + 150], fill=(32, 32, 36), outline=INK, width=6)   # сковородка
    d.ellipse([cx - 250, cy - 128, cx + 250, cy + 128], fill=(44, 44, 48))
    flip = max(0, min(1, (t - 1.6) / .6))   # блин подлетает
    py = cy - 160 * math.sin(flip * math.pi)
    pw = 210 * abs(math.cos(flip * math.pi)) + 20
    d.ellipse([cx - 200, py - pw * .55, cx + 200, py + pw * .55], fill=(232, 176, 84), outline=(160, 100, 40), width=4)
    for k in range(6):
        a = k * 1.05
        d.ellipse([cx + 120 * math.cos(a) - 12, py + 60 * math.sin(a) - 8, cx + 120 * math.cos(a) + 12, py + 60 * math.sin(a) + 8], fill=(200, 136, 60))
    # рука с ручкой сковородки
    d.line([cx + 270, cy, 560, cy - 30], fill=(26, 26, 30), width=40)
    d.rounded_rectangle([450, cy - 100, 610, cy + 50], radius=60, fill=SKIN_B, outline=INK, width=5)   # кисть
    for k in range(3):
        d.rounded_rectangle([440 + k * 22, cy - 120 + k * 4, 480 + k * 22, cy - 60], radius=16, fill=SKIN_B, outline=INK, width=3)
    d.rounded_rectangle([560, cy - 130, 800, cy + 70], radius=30, fill=(248, 248, 244), outline=INK, width=5)   # бинт
    for k in range(5):
        d.line([570 + k * 45, cy - 126, 600 + k * 45, cy + 66], fill=(210, 210, 206), width=3)
    d.ellipse([600, cy - 80, 640, cy - 44], fill=(200, 110, 100))
    img = steam(img, t, cx, cy - 140)
    d = ImageDraw.Draw(img)
    f = F(62, FONT_SUB)
    a = min(1, max(0, (t - .3) / .4))
    for j, line in enumerate(("МОЮ БАБУШКУ УКУСИЛИ.", "Я НИКОМУ НЕ СКАЗАЛ.")):
        if j == 1 and t < 1.2:
            continue
        ff = f
        while ff.getlength(line) > W - 60:
            ff = F(ff.size - 4, FONT_SUB)
        d.text(((W - ff.getlength(line)) / 2, 230 + j * 86), line, font=ff, fill=tuple(int(c * a) for c in (255, 255, 255)) if j == 0 else (250, 210, 90),
               stroke_width=6, stroke_fill=INK)
    return zoom(img, 1.0 + .06 * t / L, .5, .6)


def tape(d, y0, ang):
    a = math.radians(ang)
    L_ = 1100
    x0 = -100
    p = [(x0, y0), (x0 + L_ * math.cos(a), y0 - L_ * math.sin(a))]
    d.line(p, fill=(240, 210, 40), width=56)
    f = F(30, FONT_SUB)
    for k in range(5):
        tx = x0 + 60 + k * 230
        ty = y0 - (tx - x0) * math.tan(a) - 18
        d.text((tx, ty), "КАРАНТИН", font=f, fill=INK)


def sirens(img, t, k=.18):
    col = (40, 60, 255) if int(t * 5) % 2 else (255, 40, 50)
    return Image.blend(img, Image.new("RGB", (W, H), col), k)


def s02(t, L, cue):
    img = bg("b1_street", 1.3)
    img = sirens(img, t)
    d = ImageDraw.Draw(img)
    tape(d, 980, 14)
    tape(d, 760, -10)
    plate(img, "КАРАНТИН · ДЕНЬ 7", col=(160, 30, 30))
    return img


def radio(img, t, level=1.0):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 120, 420, 600, 820
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(130, 84, 50), outline=INK, width=6)
    d.rounded_rectangle([x0 + 30, y0 + 40, x0 + 260, y1 - 40], radius=20, fill=(210, 190, 150), outline=INK, width=4)
    for k in range(8):
        d.line([x0 + 50, y0 + 70 + k * 36, x0 + 240, y0 + 70 + k * 36], fill=(150, 120, 90), width=8)
    d.ellipse([x1 - 170, y0 + 60, x1 - 50, y0 + 180], fill=(70, 50, 34), outline=INK, width=4)
    d.ellipse([x1 - 170, y0 + 220, x1 - 50, y0 + 340], fill=(70, 50, 34), outline=INK, width=4)
    rnd = random.Random(int(t * 20))
    for k in range(16):
        h = rnd.uniform(6, 60) * level + 2
        x = x0 + 40 + k * 14
        d.rectangle([x, 900 - h, x + 8, 900 + h], fill=(250, 210, 90))


def s03r(t, L, cue):
    img = bg("b1_kitchen", 1.0, 6)
    radio(img, t, 1.0)
    return img


def s04(t, L, cue):
    img = bg("b1_street", 1.25)
    img = sirens(img, t, .12)
    d = ImageDraw.Draw(img)
    # фургон с красным крестом
    d.rounded_rectangle([420, 760, 760, 1060], radius=30, fill=(236, 236, 232), outline=INK, width=5)
    d.rectangle([560, 820, 600, 940], fill=(210, 40, 40)); d.rectangle([520, 860, 640, 900], fill=(210, 40, 40))
    for wx in (480, 700):
        d.ellipse([wx - 40, 1030, wx + 40, 1110], fill=(30, 30, 34))
    x = 140 + 60 * min(1, t / L)
    img = patrol(img, x, .66, t, "walk")
    fig, _ = person.figure((W, H), x + 120, GY - 962 * .62, .62, "host", "sad", (1, .4))
    img = char(img, fig)
    img = patrol(img, x + 240, .66, t + .3, "walk")
    return img


def s05(t, L, cue):
    img = bg("b1_door", 1.0)
    img = sasha(img, 300, .86, t, ("down", "down"), "tense", (.4, 0))
    plate(img, "3 ДНЯ НАЗАД")
    return img


def window(d, x0, y0, w, h, tape_x=True, opened=False):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(190, 220, 240), outline=(240, 240, 236), width=14)
    d.line([x0 + w / 2, y0, x0 + w / 2, y0 + h], fill=(240, 240, 236), width=10)
    if tape_x:
        for (a, b) in (((x0, y0), (x0 + w, y0 + h)), ((x0 + w, y0), (x0, y0 + h))):
            d.line([a, b], fill=(214, 190, 140), width=26)
    if opened:
        d.polygon([(x0 + w / 2, y0), (x0 + w / 2 + 120, y0 + 40), (x0 + w / 2 + 120, y0 + h + 40), (x0 + w / 2, y0 + h)], fill=(170, 200, 220), outline=(240, 240, 236))


def s06(t, L, cue):
    img = bg("b1_kitchen", 1.05)
    d = ImageDraw.Draw(img)
    window(d, 60, 300, 280, 360, tape_x=t > .8)
    img = sasha(img, 430, .86, t, ("down", "fist_up"), "tense", (-.8, -.6))
    return img


def bubble(img, txt, x, y):
    d = ImageDraw.Draw(img)
    f = F(40, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([x, y, x + w + 50, y + 80], radius=30, fill=(255, 255, 255), outline=INK, width=4)
    d.polygon([(x + 40, y + 78), (x + 80, y + 78), (x + 30, y + 120)], fill=(255, 255, 255), outline=INK)
    d.text((x + 25, y + 16), txt, font=f, fill=INK)


def s07(t, L, cue):
    img = bg("b1_kitchen", 1.05)
    p = (t - cue["07"]) / dur("07.mp3")
    img = babushka(img, 300, .86, t, ("down", "phone"), "worried" if p < .7 else "neutral", (.6, -.2), prop="kettle")
    if p > .55:
        bubble(img, "эта… горячая", 300, 230)
    return img


def s08(t, L, cue):
    img = bg("b1_kitchen", 1.05)
    img = babushka(img, 420, .86, t, ("down", "phone"), "smile", (-.4, .4), prop="pan")
    img = steam(img, t, 560, 720)
    d = ImageDraw.Draw(img)
    # стопка блинов на тарелке
    d.ellipse([60, 1090, 300, 1150], fill=(240, 240, 236), outline=INK, width=4)
    for k in range(6):
        d.ellipse([80, 1080 - k * 14, 280, 1120 - k * 14], fill=(232, 176, 84), outline=(160, 100, 40), width=2)
    d.ellipse([140, 1000, 220, 1030], fill=(150, 20, 40))   # варенье
    plate(img, "каждое утро")
    return img


def s09(t, L, cue):
    img = bg("b1_kitchen", .95, 3)
    img = sasha(img, W / 2, 1.5, t, ("down", "down"), "worried", (0, 0), ground=1900)
    return img


def s10(t, L, cue):
    img = bg("b1_kitchen", 1.05)
    d = ImageDraw.Draw(img)
    window(d, 60, 300, 280, 360, tape_x=False, opened=True)
    img = babushka(img, 300, .86, t, ("down", "out"), "smile", (-.6, -.4))
    d = ImageDraw.Draw(img)
    for i in range(5):   # ноты
        life = (t * .5 + i / 5) % 1
        x, y = 210 - 90 * life - i * 6, 470 - 260 * life
        d.ellipse([x, y + 30, x + 26, y + 50], fill=(70, 70, 150))   # нота рисуется вручную
        d.line([x + 24, y + 40, x + 24, y], fill=(70, 70, 150), width=5)
        d.line([x + 24, y, x + 40, y + 12], fill=(70, 70, 150), width=5)
    return img


def s11(t, L, cue):
    img = bg("b1_door", 1.0)
    vo_end = cue["11"] + dur("11.mp3")
    ks = [vo_end + .2, vo_end + .65, vo_end + 1.1]
    k = max([max(0, 1 - (t - kt) / .25) for kt in ks if t >= kt] + [0])
    img = sasha(img, 200, .86, t, ("down", "down"), "shock" if t > ks[0] else "tense", (.8, 0))
    d = ImageDraw.Draw(img)
    f = F(90, FONT_SUB)
    for i, kt in enumerate(ks):
        if kt <= t < kt + .6:
            x, y = [(330, 330), (430, 470), (360, 610)][i]
            d.text((x, y), "ТУК", font=f, fill=(250, 210, 90), stroke_width=6, stroke_fill=INK)
    return shake(img, t, 12 * k)


def s12r(t, L, cue):
    vo_end = cue["12r"] + dur("12r.mp3")
    img = Image.new("RGB", (W, H), (0, 0, 0))
    view = bg("b1_door", .7).resize((W, H))
    view = patrol(view, 260, .78, t)
    view = patrol(view, 470, .74, t + .4)
    # «рыбий глаз» глазка: круг с затемнением краёв
    R = 320
    cx, cy = W / 2, 620
    circ = view.crop((int(cx - R), int(cy - R), int(cx + R), int(cy + R))).resize((2 * R, 2 * R))
    m = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * R, 2 * R], fill=255)
    vig = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(vig).ellipse([40, 40, 2 * R - 40, 2 * R - 40], fill=255)
    circ = Image.composite(circ, Image.new("RGB", (2 * R, 2 * R)), vig.filter(ImageFilter.GaussianBlur(40)))
    img.paste(circ, (int(cx - R), int(cy - R)), m)
    if t > vo_end + .7:
        a = min(1, (t - vo_end - .7) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            d = ImageDraw.Draw(img)
            f1, f2, f3 = F(50, FONT_SUB), F(80, FONT_SUB), F(32, FONT_SUB)
            d.text(((W - f1.getlength("ЧАСТЬ 2")) / 2, 420), "ЧАСТЬ 2", font=f1, fill=(240, 240, 244))
            pop = 1 + .06 * math.sin((t - vo_end) * 8)
            f2 = F(int(80 * pop), FONT_SUB)
            d.text(((W - f2.getlength("после 100 ♥")) / 2, 500), "после 100 ♥", font=f2, fill=(240, 70, 80), stroke_width=5, stroke_fill=(58, 50, 14))
            if t > vo_end + 1.8:
                for j, line in enumerate(("Ты бы выдал бабушку патрулю?", "1 — да     2 — никогда")):
                    d.text(((W - f3.getlength(line)) / 2, 700 + j * 56), line, font=f3, fill=(220, 220, 226))
    return img


if __name__ == "__main__":
    s11s, _ = span("s11")
    c11 = {c: s for n, st, l, sc in scenes if n == "s11" for s, c, d in sc}
    vo_end = s11s + c11["11"] + dur("11.mp3")
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(span("s03r")[0], span("s03r")[0] + span("s03r")[1])],
        hits=[span("s01")[0] + .6, span("s05")[0] + 3.0],
        knocks=[vo_end + .2, vo_end + .65, vo_end + 1.1])
