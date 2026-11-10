"""«365 ДНЕЙ». Серия 1. Плоская 2D-инфографика: один мир в разрезе (дом, двор, гараж, яма под ним, свалка),
камера ездит по нему; сверху счётчики, внизу крупные субтитры капсом с цветными словами, карточки, выбор в конце.
Слова в *звёздочках* — жёлтые, в ^галочках^ — красные (в озвучку не идут).
Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
import toonlib
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont

LINES = {
    "01": "Мне пришло *сообщение*. С моего же ^номера^. «Через триста шестьдесят пять дней — ^конец^. Строй *бункер*».",
    "02": "Я бы посмеялся. Но там было написано, что завтра в два часа дня во всём районе погаснет *свет*. ^Погас^. Минута в минуту.",
    "03": "Нас четверо: я, *жена*, *сын* и *тёща*. Тёща сказала, что я ^сошёл^ ^с^ ^ума^. Жена промолчала. Это ^хуже^.",
    "04": "Готовый бункер на четверых стоит от *пяти* *миллионов*. У меня на карте — ^ноль^. И старый *гараж*.",
    "05": "Правило первое: бункер — это не стены. Это *воздух*, *вода* и *еда* на год. Стены — потом.",
    "06": "Человек с лопатой выкапывает около *кубометра* земли в день. Мне нужно *шестьдесят*. Два ^месяца^ без выходных.",
    "07": "День первый. *Лопату* я одолжил у соседа. Он спросил — ^зачем^. Я сказал — *погреб*.",
    "08": "Бетон — дорого. Но на *свалке* за городом лежат списанные морские *контейнеры*. Сталь. Бесплатно — если вывезти до ^утра^.",
    "09": "День *сороковой*. Яма готова. Контейнер на месте. Я впервые поверил, что *успею*.",
    "10": "А ночью из стены ямы раздался ^стук^. Кто-то *копал*. С той ^стороны^.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.25) for k in LINES]
PLAN[0] = ("s01", [("01", 0.35)], 0.3)
PLAN[-1] = ("s10", [("10", 0.1)], 5.6)
setup(LINES, PLAN)

F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
YEL, RED, WHITE, GREEN, BLUE = (255, 206, 40), (255, 72, 60), (255, 255, 255), (90, 220, 120), (90, 150, 220)
SKY_N, SKY_D = ((10, 14, 30), (26, 34, 58)), ((120, 170, 220), (196, 220, 240))
EARTH = ((34, 30, 32), (18, 17, 20))
WW, WH, GR = 1600, 2000, 900          # размер мира и уровень земли
PIT_X0, PIT_X1 = 760, 1180


# ---------- субтитры: капс, белые, ключевые слова цветом ----------
F_CAP = ImageFont.truetype(FONT_SUB, 54)


def _tokens(text):
    out = []
    for w in text.split():
        col = WHITE
        if "*" in w:
            col = YEL
        elif "^" in w:
            col = RED
        out.append((w.replace("*", "").replace("^", "").upper(), col))
    return out


def draw_caps(img, t):
    if os.environ.get("NOSUBS"):
        return
    for s, e, text, _ in toonlib.SUBS:
        if not (s <= t < e):
            continue
        toks = _tokens(text)
        lines, cur = [], []
        for tok in toks:
            test = " ".join(w for w, _ in cur + [tok])
            if F_CAP.getlength(test) > W - 90 and cur:
                lines.append(cur); cur = [tok]
            else:
                cur.append(tok)
        lines.append(cur)
        pop = min(1, (t - s) / .07)
        d = ImageDraw.Draw(img)
        y0 = int(H * .70) - len(lines) * 33
        for i, ln in enumerate(lines):
            full = " ".join(w for w, _ in ln)
            x = (W - F_CAP.getlength(full)) / 2
            y = y0 + i * 66 + (1 - pop) * 8
            for w, col in ln:
                d.text((x, y), w, font=F_CAP, fill=col, stroke_width=6, stroke_fill=(8, 8, 10))
                x += F_CAP.getlength(w + " ")
        return


toonlib.draw_subs = draw_caps


# ---------- мир ----------
def city(d, lights_on=True, seed=3):
    rnd = random.Random(seed)
    x = -20
    while x < WW:
        w, h = rnd.randint(70, 150), rnd.randint(180, 420)
        d.rectangle([x, GR - h, x + w, GR], fill=(22, 26, 40))
        for wy in range(GR - h + 16, GR - 20, 30):
            for wx in range(x + 10, x + w - 14, 22):
                if rnd.random() < .3:
                    d.rectangle([wx, wy, wx + 10, wy + 14], fill=(230, 190, 100) if lights_on else (30, 34, 46))
        x += w + rnd.randint(0, 20)


def house(d, lights_on=True):
    x0, x1, y0 = 60, 640, GR - 300
    d.polygon([(x0 - 30, y0), ((x0 + x1) / 2, y0 - 150), (x1 + 30, y0)], fill=(70, 50, 52))
    wall_in = (64, 58, 66) if lights_on else (30, 28, 34)
    d.rectangle([x0, y0, x1, GR], fill=wall_in)
    d.rectangle([x0, y0, x1, GR], outline=(150, 110, 100), width=14)            # стены в разрезе
    d.line([360, y0, 360, GR - 150], fill=(150, 110, 100), width=12)             # перегородка
    if lights_on:
        for lx in (210, 500):
            d.polygon([(lx - 14, y0 + 14), (lx + 14, y0 + 14), (lx + 110, GR), (lx - 110, GR)], fill=(84, 76, 80))
            d.ellipse([lx - 12, y0 + 10, lx + 12, y0 + 30], fill=(255, 230, 160))
    # кухня: стол, холодильник
    d.rectangle([90, GR - 140, 140, GR], fill=(200, 200, 206))
    d.rectangle([180, GR - 60, 320, GR - 50], fill=(140, 100, 70))
    d.line([190, GR - 50, 190, GR], fill=(140, 100, 70), width=6); d.line([310, GR - 50, 310, GR], fill=(140, 100, 70), width=6)
    # спальня: кровать, окно
    d.rectangle([420, GR - 50, 600, GR], fill=(90, 110, 160)); d.rectangle([420, GR - 70, 460, GR - 50], fill=(230, 230, 236))
    d.rectangle([480, y0 + 60, 580, y0 + 140], fill=(16, 20, 36) if lights_on else (10, 12, 20), outline=(150, 110, 100), width=6)


def garage(d):
    x0, x1, y0 = 800, 1140, GR - 210
    d.rectangle([x0, y0, x1, GR], fill=(52, 54, 60))
    d.rectangle([x0, y0, x1, GR], outline=(120, 124, 132), width=12)
    d.polygon([(x0 - 20, y0), (x1 + 20, y0), (x1 + 20, y0 - 26), (x0 - 20, y0 - 26)], fill=(90, 94, 102))
    d.rectangle([840, GR - 150, 980, GR], fill=(40, 42, 48), outline=(120, 124, 132), width=4)


def earth(img):
    d = ImageDraw.Draw(img)
    img.paste(vgrad(WW, WH - GR, *EARTH), (0, GR))
    rnd = random.Random(5)
    for _ in range(400):
        x, y, r = rnd.uniform(0, WW), rnd.uniform(GR + 20, WH), rnd.uniform(4, 14)
        d.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(40, 36, 38))
    d.rectangle([0, GR - 6, WW, GR + 8], fill=(70, 90, 60))   # трава / поверхность


def container(d, x0, y0, x1, y1, col=(176, 72, 52), door=True):
    d.rectangle([x0, y0, x1, y1], fill=col)
    for x in range(int(x0) + 14, int(x1) - 6, 20):
        d.line([x, y0 + 8, x, y1 - 8], fill=tuple(int(c * .78) for c in col), width=6)
    d.rectangle([x0, y0, x1, y1], outline=tuple(int(c * .6) for c in col), width=5)
    if door:
        d.rectangle([(x0 + x1) / 2 - 30, y1 - 120, (x0 + x1) / 2 + 30, y1 - 4], fill=(30, 30, 34))


def scrapyard(d):
    for x in range(1240, WW, 30):
        d.line([x, GR - 110, x, GR], fill=(70, 74, 80), width=4)
    d.line([1240, GR - 100, WW, GR - 100], fill=(70, 74, 80), width=4)
    container(d, 1270, GR - 110, 1520, GR, (60, 96, 130), False)
    container(d, 1300, GR - 220, 1560, GR - 110, (176, 72, 52), False)
    container(d, 1330, GR - 330, 1580, GR - 220, (70, 120, 80), False)


_world = {}


def world(day=False, lights=True, dug=0.0, cont=False):
    """статичный слой мира; dug — сколько ямы выкопано (0..1)"""
    key = (day, lights, round(dug, 2), cont)
    if key in _world:
        return _world[key].copy()
    img = vgrad(WW, WH, *(SKY_D if day else SKY_N))
    d = ImageDraw.Draw(img)
    if not day:
        rnd = random.Random(1)
        for _ in range(220):
            x, y = rnd.uniform(0, WW), rnd.uniform(0, GR - 300)
            d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(200, 200, 220))
    city(d, lights and not day)
    earth(img)
    d = ImageDraw.Draw(img)
    house(d, lights)
    d.ellipse([660, GR - 230, 780, GR - 110], fill=(40, 80, 50)); d.rectangle([714, GR - 120, 726, GR], fill=(70, 50, 40))   # дерево
    garage(d)
    scrapyard(d)
    if dug > 0:   # яма под гаражом, растёт вниз
        depth = 340 * dug
        d.rectangle([PIT_X0, GR + 8, PIT_X1, GR + 8 + depth], fill=(62, 50, 44))
        d.rectangle([PIT_X0, GR + 8, PIT_X1, GR + 8 + depth], outline=(110, 90, 76), width=6)
        for k in range(int(depth // 34)):   # лестница
            d.line([PIT_X1 - 60, GR + 20 + k * 34, PIT_X1 - 20, GR + 20 + k * 34], fill=(150, 104, 60), width=5)
        d.line([PIT_X1 - 60, GR, PIT_X1 - 60, GR + depth], fill=(150, 104, 60), width=6)
        d.line([PIT_X1 - 20, GR, PIT_X1 - 20, GR + depth], fill=(150, 104, 60), width=6)
    if cont:
        container(d, PIT_X0 + 20, GR + 120, PIT_X1 - 80, GR + 340)
    if len(_world) > 12:
        _world.clear()
    _world[key] = img
    return img.copy()


# ---------- персонажи: плоские чиби ----------
CHAR = {
    "me": dict(skin=(232, 186, 150), hair=(40, 32, 30), top=(60, 120, 200), pants=(40, 50, 70), style="short"),
    "wife": dict(skin=(238, 196, 164), hair=(230, 190, 90), top=(70, 160, 120), pants=(50, 50, 60), style="long"),
    "son": dict(skin=(236, 192, 160), hair=(120, 80, 50), top=(220, 70, 60), pants=(40, 60, 90), style="short"),
    "mil": dict(skin=(230, 190, 166), hair=(200, 200, 206), top=(140, 90, 150), pants=(70, 60, 80), style="bun"),
    "neigh": dict(skin=(214, 168, 132), hair=(214, 168, 132), top=(240, 140, 40), pants=(50, 54, 60), style="bald"),
}


def chibi(d, who, x, y, s=1.0, t=0.0, face="neutral", look=0, walk=False, arm=None):
    """x, y — точка на полу; рост ~110*s"""
    c = CHAR[who]
    bob = 2 * math.sin(t * 3 + x) * s
    lg = 8 * math.sin(t * 10) * s if walk else 0
    for sx, off in ((-1, lg), (1, -lg)):   # ноги
        d.rounded_rectangle([x + sx * 10 * s - 7 * s + off, y - 34 * s, x + sx * 10 * s + 7 * s + off, y], radius=int(5 * s), fill=c["pants"])
    by = y - 30 * s + bob
    d.rounded_rectangle([x - 22 * s, by - 46 * s, x + 22 * s, by], radius=int(12 * s), fill=c["top"])   # тело
    for sx in (-1, 1):   # руки
        if arm == "up" and sx == 1:
            d.line([x + 20 * s, by - 40 * s, x + 34 * s, by - 76 * s], fill=c["top"], width=int(11 * s))
            d.ellipse([x + 28 * s, by - 86 * s, x + 40 * s, by - 74 * s], fill=c["skin"])
        elif arm == "phone" and sx == -1:
            d.line([x - 20 * s, by - 40 * s, x - 6 * s, by - 52 * s], fill=c["top"], width=int(11 * s))
            d.rounded_rectangle([x - 12 * s, by - 66 * s, x + 2 * s, by - 46 * s], radius=3, fill=(180, 220, 255))
        else:
            d.line([x + sx * 22 * s, by - 40 * s, x + sx * 28 * s, by - 12 * s], fill=c["top"], width=int(11 * s))
            d.ellipse([x + sx * 28 * s - 6 * s, by - 16 * s, x + sx * 28 * s + 6 * s, by - 4 * s], fill=c["skin"])
    hy = by - 46 * s - 26 * s   # голова
    R = 27 * s
    if c["style"] == "long":
        d.rounded_rectangle([x - R - 4 * s, hy - R, x + R + 4 * s, hy + R + 18 * s], radius=int(14 * s), fill=c["hair"])
    d.ellipse([x - R, hy - R, x + R, hy + R], fill=c["skin"])
    if c["style"] in ("short", "long"):
        d.chord([x - R, hy - R - 2 * s, x + R, hy + R * .4], 180, 360, fill=c["hair"])
    elif c["style"] == "bun":
        d.chord([x - R, hy - R, x + R, hy + R * .3], 180, 360, fill=c["hair"])
        d.ellipse([x - 10 * s, hy - R - 16 * s, x + 10 * s, hy - R + 4 * s], fill=c["hair"])
    elif c["style"] == "bald":
        d.chord([x - R + 4 * s, hy - 6 * s, x + R - 4 * s, hy + R + 6 * s], 0, 180, fill=(120, 90, 70))   # борода
    ex = look * 4 * s
    blink = (t + x * .01) % 3.3 < .1
    for sx in (-1, 1):
        if blink:
            d.line([x + sx * 9 * s + ex - 3 * s, hy, x + sx * 9 * s + ex + 3 * s, hy], fill=(20, 20, 24), width=max(1, int(2 * s)))
        else:
            d.ellipse([x + sx * 9 * s + ex - 3 * s, hy - 3 * s, x + sx * 9 * s + ex + 3 * s, hy + 3 * s], fill=(20, 20, 24))
    if face == "shock":
        d.ellipse([x - 5 * s + ex, hy + 9 * s, x + 5 * s + ex, hy + 19 * s], fill=(80, 30, 30))
    elif face == "smile":
        d.arc([x - 9 * s + ex, hy + 4 * s, x + 9 * s + ex, hy + 16 * s], 20, 160, fill=(20, 20, 24), width=max(1, int(2 * s)))
    elif face == "sad":
        d.arc([x - 8 * s + ex, hy + 12 * s, x + 8 * s + ex, hy + 22 * s], 200, 340, fill=(20, 20, 24), width=max(1, int(2 * s)))
    else:
        d.line([x - 6 * s + ex, hy + 13 * s, x + 6 * s + ex, hy + 13 * s], fill=(20, 20, 24), width=max(1, int(2 * s)))


def shovel(d, x, y, s=1.0):
    d.line([x, y - 120 * s, x, y - 20 * s], fill=(150, 104, 60), width=int(7 * s))
    d.polygon([(x - 14 * s, y - 24 * s), (x + 14 * s, y - 24 * s), (x + 10 * s, y + 6 * s), (x, y + 12 * s), (x - 10 * s, y + 6 * s)], fill=(160, 166, 174))


# ---------- камера и экранные элементы ----------
def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def cam(img, c0, c1=None, k=0.0):
    """c = (cx, cy, zoom) в координатах мира"""
    if c1:
        e = ease(k)
        c0 = tuple(a + (b - a) * e for a, b in zip(c0, c1))
    cx, cy, z = c0
    w, h = W / z, H / z
    cx = min(max(cx, w / 2), WW - w / 2)
    cy = min(max(cy, h / 2), WH - h / 2)
    return img.resize((W, H), Image.BICUBIC, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


def hud(img, days, money="0 ₽"):
    d = ImageDraw.Draw(img)
    for i, (lab, val, col) in enumerate((("ДО КОНЦА", f"{days} дн", RED), ("БЮДЖЕТ", money, YEL))):
        x0 = 40 + i * 340
        lay = img.crop((x0, 40, x0 + 300, 132)).point(lambda v: v * .45)
        img.paste(lay, (x0, 40))
        d.rounded_rectangle([x0, 40, x0 + 300, 132], radius=14, outline=(110, 150, 210), width=3)
        f1, f2 = F(20), F(46, FONT_SUB)
        d.text((x0 + 150 - f1.getlength(lab) / 2, 50), lab, font=f1, fill=(190, 210, 240))
        d.text((x0 + 150 - f2.getlength(val) / 2, 72), val, font=f2, fill=col)


def pill(img, txt, x, y, col=(20, 22, 30), fg=WHITE, size=26, anchor=None):
    """подпись-плашка; anchor — точка, к которой тянется линия"""
    d = ImageDraw.Draw(img)
    f = F(size, FONT_SUB)
    w = f.getlength(txt)
    if anchor:
        d.line([x, y + size, anchor[0], anchor[1]], fill=WHITE, width=3)
        d.ellipse([anchor[0] - 5, anchor[1] - 5, anchor[0] + 5, anchor[1] + 5], fill=WHITE)
    d.rounded_rectangle([x - w / 2 - 14, y, x + w / 2 + 14, y + size + 18], radius=10, fill=col, outline=(240, 240, 240), width=2)
    d.text((x - w / 2, y + 7), txt, font=f, fill=fg)


def bubble(img, txt, x, y):
    d = ImageDraw.Draw(img)
    f = F(28, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([x - w / 2 - 18, y - 60, x + w / 2 + 18, y - 8], radius=18, fill=WHITE)
    d.polygon([(x - 10, y - 10), (x + 10, y - 10), (x, y + 8)], fill=WHITE)
    d.text((x - w / 2, y - 52), txt, font=f, fill=(20, 20, 24))


def sms_card(img, lines, y=170, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    x0, x1 = 60, W - 60
    f = F(30)
    h = 96 + 42 * len(lines)
    d.rounded_rectangle([x0, y, x1, y + h], radius=22, fill=(246, 246, 248))
    d.ellipse([x0 + 22, y + 20, x0 + 70, y + 68], fill=(60, 120, 200))
    d.text((x0 + 86, y + 20), "МОЙ НОМЕР", font=F(26, FONT_SUB), fill=RED)
    d.text((x0 + 86, y + 52), "сообщение · 02:13", font=F(18), fill=(140, 140, 146))
    for i, ln in enumerate(lines):
        d.text((x0 + 30, y + 88 + i * 42), ln, font=f, fill=(20, 20, 24))
    img.paste(Image.blend(img, lay, a))


def dark_card(img, title, rows, y=170, a=1.0):
    """тёмная карточка с полосками: rows = [(подпись, значение, доля 0..1, цвет)]"""
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    x0, x1 = 70, W - 70
    h = 90 + 92 * len(rows)
    d.rounded_rectangle([x0, y, x1, y + h], radius=20, fill=(14, 16, 24), outline=(110, 150, 210), width=3)
    f0 = F(28, FONT_SUB)
    d.text(((W - f0.getlength(title)) / 2, y + 22), title, font=f0, fill=WHITE)
    for i, (lab, val, k, col) in enumerate(rows):
        yy = y + 80 + i * 92
        d.text((x0 + 26, yy), lab, font=F(26, FONT_SUB), fill=(220, 220, 226))
        fv = F(30, FONT_SUB)
        d.text((x1 - 26 - fv.getlength(val), yy - 2), val, font=fv, fill=col)
        d.rounded_rectangle([x0 + 26, yy + 44, x1 - 26, yy + 60], radius=8, fill=(40, 44, 56))
        if k > 0:
            d.rounded_rectangle([x0 + 26, yy + 44, x0 + 26 + (x1 - x0 - 52) * k, yy + 60], radius=8, fill=col)
    img.paste(Image.blend(img, lay, a))


def fade_in(t, t0, d=.25):
    return max(0.0, min(1.0, (t - t0) / d))


# ---------- сцены ----------
HOUSE_BED = (500, 800, 1.7)
KITCHEN = (230, 800, 1.6)
WIDE = (760, 720, .9)
GARAGE = (970, 860, 1.6)
UNDER = (970, 1020, 1.5)


def s01(t, L, cue):
    p = (t - cue["01"]) / dur("01.mp3")
    img = world(lights=True)
    d = ImageDraw.Draw(img)
    chibi(d, "me", 500, GR - 4, 1.0, t, "shock" if p > .45 else "neutral", 0, arm="phone")
    glow(img, (494, GR - 116), 50, (150, 200, 255), .7)
    img = cam(img, (500, 810, 2.0), HOUSE_BED, t / 1.2)
    if p > .05:
        msgs = ["Через 365 дней — конец."] + (["Строй бункер."] if p > .72 else [])
        sms_card(img, msgs, 180, fade_in(t, cue["01"] + .2))
    hud(img, 365)
    return shake(img, t, 5 if t < .4 else 0)


def s02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    off = p > .76
    img = world(lights=not off)
    d = ImageDraw.Draw(img)
    chibi(d, "me", 720, GR - 4, 1.0, t, "shock" if off else "neutral", 0, arm="phone")
    img = cam(img, (600, 800, 1.6), WIDE, t / 3)
    if not off:
        sms_card(img, ["Завтра в 14:00 в районе", "погаснет свет."], 180, fade_in(t, .1))
    pill(img, "14:00" if off else "13:59", W / 2, 400, (140, 30, 30) if off else (20, 22, 30), size=34)
    hud(img, 364)
    return shake(img, t, 7 if .76 < p < .82 else 0)


def s03(t, L, cue):
    p = (t - cue["03"]) / dur("03.mp3")
    img = world()
    d = ImageDraw.Draw(img)
    fam = (("mil", 120, "shock" if p > .45 else "neutral", 1), ("wife", 205, "sad" if p > .72 else "neutral", 1),
           ("son", 280, "neutral", 1), ("me", 335, "neutral", -1))
    for who, x, face, lk in fam:
        chibi(d, who, x, GR - 4, .8 if who == "son" else 1.0, t, face, lk)
    img = cam(img, KITCHEN, (230, 800, 1.75), t / L)
    for (who, x, *_), name in zip(fam, ("ТЁЩА", "ЖЕНА", "СЫН", "Я")):
        sx = (x - 230) * 1.75 + W / 2
        pill(img, name, sx, 380, size=22)
    if p > .45:
        bubble(img, "сошёл с ума!", 170, 560)
    if p > .72:
        bubble(img, "…", 300, 540)
    hud(img, 364)
    return img


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = cam(world(), GARAGE)
    rows = [("БУНКЕР НА 4", "5 000 000 ₽", 1.0, BLUE)]
    if p > .5:
        rows.append(("У МЕНЯ", "0 ₽", 0.0, RED))
    dark_card(img, "ЦЕНА СПАСЕНИЯ", rows, 180, fade_in(t, .05))
    if p > .8:
        pill(img, "старый гараж", W / 2, 760, anchor=(W / 2 + 40, 900))
    hud(img, 364)
    return img


def dashed_rect(d, box, col=(255, 206, 40), w=5, dash=22):
    x0, y0, x1, y1 = box
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(L_ // dash)
        for i in range(0, n, 2):
            k0, k1 = i / n, min(1, (i + 1) / n)
            d.line([a[0] + (b[0] - a[0]) * k0, a[1] + (b[1] - a[1]) * k0, a[0] + (b[0] - a[0]) * k1, a[1] + (b[1] - a[1]) * k1], fill=col, width=w)


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = world()
    dashed_rect(ImageDraw.Draw(img), (PIT_X0, GR + 10, PIT_X1, GR + 350))
    img = cam(img, GARAGE, UNDER, t / L)
    rows = []
    for lab, show, col in (("ВОЗДУХ", .32, (120, 210, 255)), ("ВОДА", .45, BLUE), ("ЕДА НА ГОД", .58, GREEN)):
        if p > show:
            rows.append((lab, "✓", 1.0, col))
    dark_card(img, "ПРАВИЛО №1", rows, 180, fade_in(t, .05))
    if p > .85:
        pill(img, "стены — потом", W / 2, 180 + 90 + 92 * 3 + 20, (40, 40, 48), size=24)
    hud(img, 364)
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    k = min(1, max(0, (t - .3) / (L - .6)))
    img = world(dug=.05 + .25 * k)
    dashed_rect(ImageDraw.Draw(img), (PIT_X0, GR + 10, PIT_X1, GR + 350))
    img = cam(img, UNDER)
    pill(img, "1 м³ / день", W / 2 - 150, 250, size=30)
    if p > .45:
        pill(img, "нужно 60 м³", W / 2 + 140, 250, (30, 60, 110), size=30)
    if p > .72:
        pill(img, "≈ 60 дней", W / 2, 340, (140, 30, 30), size=34)
    hud(img, 364)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    img = world(day=True, lights=False, dug=.06)
    d = ImageDraw.Draw(img)
    shovel(d, 1040, GR - 4)
    chibi(d, "me", 990, GR - 4, 1.0, t, "smile" if p > .75 else "neutral", 1)
    chibi(d, "neigh", 1110, GR - 4, 1.0, t, "neutral", -1)
    img = cam(img, (1050, 820, 1.7))
    pill(img, "ДЕНЬ 1", W / 2, 180, (20, 22, 30), YEL, 34)
    if .4 < p:
        bubble(img, "зачем?", W / 2 + 130, 520)
    if p > .72:
        bubble(img, "погреб", W / 2 - 110, 500)
    hud(img, 364)
    return img


def s08(t, L, cue):
    img = world(dug=.3)
    d = ImageDraw.Draw(img)
    x = 1180 + 60 * min(1, t / 2)
    chibi(d, "me", x, GR - 4, 1.0, t, "neutral", 1, walk=t < 2)
    lay = Image.new("L", (WW, WH), 0)
    ImageDraw.Draw(lay).polygon([(x + 20, GR - 70), (1560, GR - 300), (1600, GR - 10)], fill=70)
    img.paste(Image.new("RGB", (WW, WH), (255, 240, 200)), (0, 0), lay.filter(ImageFilter.GaussianBlur(14)))
    img = cam(img, GARAGE, (1400, 800, 1.5), t / 2.5)
    pill(img, "свалка · 03:40", W / 2, 180, size=30)
    pill(img, "бесплатно — до утра", W / 2, 250, (30, 80, 50), size=24)
    hud(img, 345)
    return img


def s09(t, L, cue):
    img = world(day=True, lights=False, dug=1.0, cont=True)
    d = ImageDraw.Draw(img)
    chibi(d, "me", 1060, GR - 4, 1.0, t, "smile", 0, arm="up")
    img = cam(img, (970, 950, 1.7), UNDER, t / L)
    pill(img, "ДЕНЬ 40", W / 2, 180, (20, 22, 30), GREEN, 34)
    pill(img, "яма 60 м³ · контейнер", W / 2, 250, size=24)
    hud(img, 325)
    return img


def s10(t, L, cue):
    vo_end = cue["10"] + dur("10.mp3")
    knocks = [cue["10"] + dur("10.mp3") * .32 + k * .55 for k in range(3)] + [vo_end + .3 + k * .5 for k in range(3)]
    n = sum(t > k for k in knocks)
    hit = any(0 <= t - k < .15 for k in knocks)
    img = world(lights=False, dug=1.0, cont=True)
    d = ImageDraw.Draw(img)
    chibi(d, "me", 1020, GR + 336, 1.0, t, "shock" if n else "neutral", 1)
    lay = Image.new("L", (WW, WH), 0)   # фонарик
    ImageDraw.Draw(lay).polygon([(1040, GR + 250), (1190, GR + 160), (1190, GR + 340)], fill=90)
    img.paste(Image.new("RGB", (WW, WH), (255, 236, 190)), (0, 0), lay.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(img)
    wx, wy = PIT_X1, GR + 250
    rnd = random.Random(3)
    for i in range(n):   # трещины в стене
        a = rnd.uniform(-1.2, 1.2)
        d.line([wx, wy, wx + 70 * math.cos(a) * (1 + i * .3), wy + 70 * math.sin(a) * (1 + i * .3)], fill=(14, 12, 12), width=5)
    if n:
        r = 6 + n * 4
        d.ellipse([wx - r * .6, wy - r, wx + r * .6, wy + r], fill=(8, 6, 6))
        for i in range(n * 5):   # осыпь
            y = wy + r + ((t * 220 + i * 37) % 90)
            d.ellipse([wx - 18 + i % 5 * 7, y, wx - 10 + i % 5 * 7, y + 6], fill=(90, 76, 64))
    # тоннель «с той стороны» — виден только зрителю
    k = min(1, max(0, (t - cue["10"]) / (L - cue["10"] - 2.0)))
    tx = WW - (WW - wx - 40) * k
    d.rectangle([tx, wy - 30, WW, wy + 30], fill=(10, 8, 8))
    img = cam(img, UNDER, (1080, GR + 230, 1.8), (t - cue["10"]) / 3)
    hud(img, 325)
    img = shake(img, t, 10 if hit else 0)
    if t > vo_end + 2.0:   # выбор — пиши в комментариях
        a = fade_in(t, vo_end + 2.0, .4)
        lay = img.copy()
        dd = ImageDraw.Draw(lay)
        for i, (title, sub, col) in enumerate((("ЗАСЫПАТЬ", "сделать вид, что не слышал", (90, 150, 220)),
                                               ("КОПАТЬ", "навстречу. а если там тот,\nкто прислал сообщение?", RED))):
            x0 = 40 + i * 330
            dd.rounded_rectangle([x0, 200, x0 + 310, 470], radius=22, fill=(14, 16, 24), outline=col, width=4)
            ft = F(34, FONT_SUB)
            dd.text((x0 + 155 - ft.getlength(title) / 2, 330), title, font=ft, fill=WHITE)
            fs = F(18)
            for j, sl in enumerate(sub.split("\n")):
                dd.text((x0 + 155 - fs.getlength(sl) / 2, 390 + j * 26), sl, font=fs, fill=(190, 190, 200))
            dd.ellipse([x0 + 125, 225, x0 + 185, 285], fill=col)
            dd.text((x0 + 155 - F(36, FONT_SUB).getlength(str(i + 1)) / 2, 232), str(i + 1), font=F(36, FONT_SUB), fill=WHITE)
        dd.ellipse([W / 2 - 34, 300, W / 2 + 34, 368], fill=YEL)
        dd.text((W / 2 - F(22, FONT_SUB).getlength("ИЛИ") / 2, 320), "ИЛИ", font=F(22, FONT_SUB), fill=(20, 20, 24))
        fp = F(28, FONT_SUB)
        txt = "ПИШИ В КОММЕНТАРИЯХ 1 ИЛИ 2"
        dd.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 22, 500, W / 2 + fp.getlength(txt) / 2 + 22, 556], radius=28, fill=YEL)
        dd.text((W / 2 - fp.getlength(txt) / 2, 510), txt, font=fp, fill=(20, 20, 24))
        img = Image.blend(img, lay, a)
    return img


if __name__ == "__main__":
    s0 = span("s10")[0] + .1
    d10 = dur("10.mp3")
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=[s0 + d10 * .32 + k * .55 for k in range(3)] + [s0 + d10 + .3 + k * .5 for k in range(3)],
        hits=[span("s02")[0] + .05 + dur("02.mp3") * .76, span("s01")[0] + .05])
