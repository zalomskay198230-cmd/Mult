"""ГЛУБИНА 40. Серия 2. Гибрид: те же 3D-фоны станции (g1_*) + 2D-герои. Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
TTS2 = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib
toonlib.TTS = os.path.join(HERE, "..", "tts", "s01")
import seriya01 as G          # хелперы первой серии: фоны, часы, чертёж, рация, плашки
toonlib.TTS = TTS2
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter
import denis_rig as DR

LINES = {
    "01": "Люк открылся. В шлюз ввалился человек в гидрокостюме. Это был Костя. Мой напарник.",
    "02": "Он ушёл наверх десять часов назад. А вернулся без баллонов. На глубину сорок метров. Без воздуха.",
    "03": "А вот и подвох: костюм весь в ожогах. И он молчит.",
    "04k": "«Не открывай люк. Никому. Наверху больше нет кораблей».",
    "05": "Правило третье: под водой не верь глазам. Верь приборам.",
    "06": "На сорока метрах давление — пять атмосфер. Без баллона человек здесь продержится минуту. Две — если повезёт.",
    "07": "Я подключил его к монитору. Пульс — двадцать ударов в минуту. Температура тела — восемь градусов. Как у воды.",
    "08": "Он сел у иллюминатора и смотрел в темноту. Всю ночь. Ни разу не моргнул.",
    "09": "Воздуха осталось на четыре часа. На подъём нужно сорок минут.",
    "10": "А потом выяснилось вот что: на полу шлюза — две пары мокрых следов от ласт. А вошёл он один.",
    "11": "И тут ожила рация. Канал поверхности. Сквозь шипение — голос. Мой голос.",
    "12r": "«Олег, не открывай люк. Это не Костя».",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[-1] = ("s12r", [("12r", 0.4)], 3.8)
setup(LINES, PLAN)

GY, F, ORANGE, CYAN = G.GY, G.F, G.ORANGE, G.CYAN
RED_T = G.RED_T


def kostya(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, blink=True, tint=RED_T):
    DR.use("kostya", hoodie=False, suit=False)
    fig = DR.front((W, H), x, ground, s, t if blink else 1.0, arms, "idle", expr, look)
    img = G.char(img, fig, tint)
    d = ImageDraw.Draw(img)
    P = lambda lx, ly: G.L2S(x, ground, s, lx, ly) if hasattr(G, "L2S") else (x + lx * s, ground - 962 * s + ly * s)
    # синие вставки гидрокостюма, маска на лбу, ожоги, капли
    for sx in (-1, 1):
        d.polygon([P(sx * 100, 210), P(sx * 108, 300), P(sx * 92, 420), P(sx * 80, 420), P(sx * 92, 300), P(sx * 86, 214)], fill=(40, 90, 150))
    d.rounded_rectangle([*P(-62, 10), *P(62, 52)], radius=int(16 * s), fill=(30, 30, 34), outline=INK, width=2)
    d.rounded_rectangle([*P(-52, 16), *P(52, 46)], radius=int(12 * s), fill=(90, 140, 170))
    rnd = random.Random(4)
    for _ in range(7):
        bx, by = rnd.uniform(-80, 80), rnd.uniform(240, 500)
        r = rnd.uniform(12, 26)
        d.ellipse([*P(bx - r, by - r * .7), *P(bx + r, by + r * .7)], fill=(90, 40, 30))
        d.ellipse([*P(bx - r * .5, by - r * .3), *P(bx + r * .5, by + r * .3)], fill=(160, 70, 40))
    for i in range(6):
        ph = (t * .8 + i / 6) % 1
        dx = -70 + i * 28
        yy = 540 + ph * 400
        d.ellipse([*P(dx - 4, yy - 6), *P(dx + 4, yy + 6)], fill=(140, 190, 220))
    return img


def oleg(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, tint=RED_T):
    DR.use("oleg", hoodie=False, suit=True)
    return G.char(img, DR.front((W, H), x, ground, s, t, arms, "idle", expr, look), tint)


def hatch_open(img, t, k=1.0):
    """поверх шлюза: люк откинут, за ним тёмная вода"""
    d = ImageDraw.Draw(img)
    cx, cy, R = 368, 613, 205
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(4, 18, 34))
    for i in range(10):   # пузыри
        ph = (t * .6 + i / 10) % 1
        bx = cx - 80 + i * 18
        by = cy + R - ph * 2 * R
        d.ellipse([bx - 6, by - 6, bx + 6, by + 6], outline=(120, 180, 220), width=2)
    d.ellipse([cx + R - 40, cy - R + 10, cx + R + 140, cy + R - 10], fill=(150, 154, 160), outline=INK, width=6)   # откинутая крышка


def plate(img, txt, y=150):
    G.tag(img, txt, "", y)


def medscreen(img, t, k=1.0):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 120, 300, 600, 820
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(10, 16, 14), outline=(120, 130, 126), width=8)
    pts, x = [], x0 + 20
    while x < x1 - 20:
        ph = ((x - x0) / 420 + t * .35) % 1
        y = y0 + 170 - (90 if .48 < ph < .52 else 0) + (40 if .52 < ph < .55 else 0)
        pts.append((x, y))
        x += 6
    d.line(pts, fill=(80, 255, 140), width=4)
    f, f2 = F(80, FONT_SUB), F(26)
    d.text((x0 + 30, y0 + 270), "ПУЛЬС", font=f2, fill=(150, 200, 170))
    d.text((x0 + 30, y0 + 300), str(int(20 * k) if k < 1 else 20), font=f, fill=(80, 255, 140))
    d.text((x0 + 250, y0 + 270), "ТЕМП.", font=f2, fill=(150, 200, 170))
    if k >= 1:
        d.text((x0 + 250, y0 + 300), "8°", font=f, fill=(255, 110, 100))


def flipper(d, x, y, s=1.0, left=False):
    m = -1 if left else 1
    pts = [(-14, 30), (-18, -10), (-30, -80), (0, -96), (30, -80), (18, -10), (14, 30)]
    d.polygon([(x + px * s * m, y + py * s) for px, py in pts], fill=(30, 50, 70), outline=INK)
    d.line([(x - 6 * s, y - 70 * s), (x + 6 * s, y - 70 * s)], fill=(140, 190, 220), width=3)


# ---------- сцены ----------
def s01(t, L, cue):
    img = G.bg("s13", t, 1.25)
    hatch_open(img, t)
    img = kostya(img, 360, .86, t, ("out", "down"), "neutral", (0, .3), blink=False)
    G.clock(img, "23:41")
    G.depth_plate(img, "4:20")
    return shake(img, t, 6 if t < .6 else 0)


def s02(t, L, cue):
    img = G.bg("s03", t, 1.4)
    img = oleg(img, 170, .84, t, ("down", "down"), "shock", (.8, 0))
    img = kostya(img, 470, .84, t, ("down", "down"), "neutral", (-.4, .2), blink=False)
    p = (t - cue["02"]) / dur("02.mp3")
    if p > .45:
        G.tag(img, "баллонов", "0 из 2", 1080)
    G.depth_plate(img, "4:15")
    return img


def s03(t, L, cue):
    img = G.bg("s03", t, 1.3)
    img = kostya(img, W / 2, 1.5, t, ("down", "down"), "neutral", (0, 0), ground=1900, blink=False)
    return zoom(img, 1.0 + .08 * t / L, .5, .45)


def s04k(t, L, cue):
    img = G.bg("s03", t, 1.2)
    img = kostya(img, W / 2, 1.6, t, ("down", "down"), "tense", (0, 0), ground=1980, blink=False)
    d = ImageDraw.Draw(img)
    G.tag(img, "КОСТЯ", "говорит впервые", 150)
    return zoom(img, 1.0 + .1 * t / L, .5, .35)


def s05(t, L, cue):
    img = G.blueprint("ПРАВИЛО №3", min(1, t / .4))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 560
    d.ellipse([cx - 180, cy - 90, cx + 180, cy + 90], outline=CYAN, width=8)   # глаз
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], outline=CYAN, width=8)
    if t > 1.0:
        d.line([cx - 220, cy + 130, cx + 220, cy - 130], fill=(255, 110, 100), width=16)
    if t > 1.6:   # прибор
        d.ellipse([cx - 110, 760, cx + 110, 980], outline=ORANGE, width=8)
        d.line([cx, 870, cx + 70, 820], fill=ORANGE, width=8)
        f = F(52, FONT_SUB)
        d.text((cx - f.getlength("ВЕРЬ ПРИБОРАМ") / 2, 1020), "ВЕРЬ ПРИБОРАМ", font=f, fill=CYAN)
    return img


def s06(t, L, cue):
    img = G.blueprint("40 МЕТРОВ")
    d = ImageDraw.Draw(img)
    f = F(120, FONT_SUB)
    k = min(1, t / 1.2)
    d.text((W / 2 - f.getlength("5 атм") / 2, 340), "5 атм", font=f, fill=ORANGE)
    # лёгкие сжимаются
    cx, cy = W / 2, 760
    sc = 1 - .45 * k
    for sx in (-1, 1):
        d.ellipse([cx + sx * 20 - (sx < 0) * 140 * sc, cy - 150 * sc, cx + sx * 20 + (sx > 0) * 140 * sc, cy + 150 * sc], outline=CYAN, width=6)
    p = (t - cue["06"]) / dur("06.mp3")
    if p > .45:
        d.text((W / 2 - F(52, FONT_SUB).getlength("1–2 минуты") / 2, 1000), "1–2 минуты", font=F(52, FONT_SUB), fill=(255, 110, 100))
    return img


def s07(t, L, cue):
    img = G.bg("s03", t, 1.0).filter(ImageFilter.GaussianBlur(6))
    p = (t - cue["07"]) / dur("07.mp3")
    medscreen(img, t, 1.0 if p > .7 else min(.99, p / .7))
    G.depth_plate(img, "3:50")
    return img


def s08(t, L, cue):
    img = G.bg("s03", t, 1.2)
    d = ImageDraw.Draw(img)
    cx, cy, R = 470, 470, 150   # иллюминатор
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(4, 16, 30), outline=(140, 146, 152), width=26)
    img = kostya(img, 300, .86, t, ("down", "down"), "neutral", (1, -.4), blink=False)
    hh = 1 + int(4 * min(1, t / L))
    G.clock(img, f"0{hh}:{int((t * 37) % 60):02d}")
    G.depth_plate(img, "3:10")
    return img


def s09(t, L, cue):
    img = G.bg("s03", t, 1.3)
    img = oleg(img, W / 2, 1.5, t, ("down", "down"), "worried", (0, -.2), ground=1900)
    G.depth_plate(img, "4:00" if t < .5 else "3:59")
    G.tag(img, "воздух", "4 часа · подъём 40 мин", 1080)
    return img


def s10(t, L, cue):
    img = Image.new("RGB", (W, H), (70, 74, 80))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 40):
        d.line([0, y, W, y], fill=(80, 84, 90), width=4)
    for x in range(0, W, 40):
        d.line([x, 0, x, H], fill=(80, 84, 90), width=4)
    p = (t - cue["10"]) / dur("10.mp3")
    for trail, (bx, show) in enumerate(((240, .0), (480, .45))):   # вторая цепочка следов появляется на «две пары»
        if p < show:
            continue
        for k in range(5):
            y = 1150 - k * 210
            flipper(d, bx + (-36 if k % 2 else 36), y, 1.6, k % 2 == 0)
            for j in range(3):   # мокрые капли
                d.ellipse([bx - 50 + j * 40, y + 50, bx - 42 + j * 40, y + 58], fill=(120, 170, 210))
    img = zoom(img, 1.0 + .1 * t / L, .5, .5)
    G.tag(img, "следов", "2 пары · вошёл 1", 150)
    return img


def s11(t, L, cue):
    img = G.bg("s03", t, 1.1).filter(ImageFilter.GaussianBlur(6))
    G.radio(img, t, .15 + .6 * min(1, max(0, t - 1.5)))
    G.depth_plate(img, "2:40")
    return img


def s12r(t, L, cue):
    vo_end = cue["12r"] + dur("12r.mp3")
    img = G.bg("s03", t, 1.1).filter(ImageFilter.GaussianBlur(6))
    G.radio(img, t, 1.0 if t < vo_end else 0.0, "ПОВЕРХНОСТЬ · ГОЛОС ОЛЕГА")
    img = shake(img, t, 5 if vo_end - .4 < t < vo_end + .2 else 0)
    if t > vo_end + .6:
        a = min(1, (t - vo_end - .6) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(40, FONT_SUB), F(70, FONT_SUB), F(30, FONT_SUB)
            dd.text(((W - f1.getlength("ГЛУБИНА 40")) / 2, 470), "ГЛУБИНА 40", font=f1, fill=(240, 240, 244))
            dd.text(((W - f2.getlength("ДЕНЬ 2")) / 2, 530), "ДЕНЬ 2", font=f2, fill=ORANGE)
            dd.text(((W - f3.getlength("ПРОДОЛЖЕНИЕ СЛЕДУЕТ")) / 2, 630), "ПРОДОЛЖЕНИЕ СЛЕДУЕТ", font=f3, fill=(200, 200, 206))
            if t > vo_end + 1.6:
                dd.text(((W - F(28).getlength("кто вошёл в шлюз?")) / 2, 700), "кто вошёл в шлюз?", font=F(28), fill=(150, 150, 156))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(span("s11")[0], span("s12r")[0] + span("s12r")[1] - 3.0)],
        hits=[span("s01")[0] + .05, span("s04k")[0] + .2, span("s07")[0] + 4.0, span("s10")[0] + 3.0, span("s12r")[0] + .4])
