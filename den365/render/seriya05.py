"""«365 ДНЕЙ». Серия 5 (~25 с, без рекламы). Зрители выбрали «разбить». Холодный старт — чехол жены.
Озвучка — пользователя (tts/s05_golos). Запуск: python3 seriya05.py ../tts/s05_golos ../seriya05.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s04_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s04", os.path.join(HERE, "seriya04.py"))
E4 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E4)
sys.argv[:] = _argv
E3, E1 = E4.E3, E4.E1
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s05_golos"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya05.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter
from flatworld import world, chibi, GR, OUT

W, H = toonlib.W, toonlib.H
V, hud, pill, fade_in, ease, F = E1.V, E1.hud, E1.pill, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE
ROOF_Y, WRLD, black_box = E3.ROOF_Y, E4.WRLD, E4.black_box
DAYS = 319

LINES = {
    "01": "Этот *чехол* я дарил своей ^жене^…",
    "02": "Вы выбрали — *разбить*.",
    "03": "Михалыч ударил ^кувалдой^. Коробка треснула, как *орех*.",
    "04": "Внутри — старый *телефон*. Без пароля. А в нём все сообщения. Мне, Михалычу и ещё *двенадцати* соседям.",
    "05": "В черновиках — следующее, на завтра: «Михалыч ^врёт^».",
    "06": "А на телефоне — *розовый* чехол. С ^котом^.",
    "07": "Зачем ей это? Пишите *версии*. Шестая серия — *завтра*.",
}
PLAN = [(f"s{k}", [(k, 0.04)], 0.12) for k in LINES]
PLAN[0] = ("s01", [("01", 0.0)], 0.15)
PLAN[-1] = ("s07", [("07", 0.0)], 0.4)
setup(LINES, PLAN)


def big_top(img, txt, y=190, col=YEL, size=70):
    f = F(size, FONT_SUB)
    while f.getlength(txt) > W - 60:
        size -= 4; f = F(size, FONT_SUB)
    ImageDraw.Draw(img).text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col, stroke_width=7, stroke_fill=(14, 12, 16))


def stamp(img, txt, t, t0, col=RED, y=300, rot=-8, size=72):
    if t < t0:
        return
    k = min(1, (t - t0) / .15)
    f = F(int(size * (1.6 - .6 * k)), FONT_SUB)
    lay = Image.new("RGBA", (int(f.getlength(txt)) + 40, size * 2), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((20, 10), txt, font=f, fill=col + (255,), stroke_width=7, stroke_fill=(16, 14, 16, 255))
    lay = lay.rotate(rot, expand=True)
    img.paste(lay, (int(W / 2 - lay.width / 2), y), lay)


def phone_back(img, cx, cy, s=1.0, a=1.0):
    """телефон в розовом чехле с котом (вид сзади)"""
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    w, h = 300 * s, 560 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(46 * s), fill=(246, 150, 186), outline=(30, 24, 30), width=int(6 * s))
    d.rounded_rectangle([cx - w / 2 + 24 * s, cy - h / 2 + 24 * s, cx - w / 2 + 110 * s, cy - h / 2 + 110 * s], radius=int(20 * s), fill=(40, 36, 44))
    d.ellipse([cx - w / 2 + 42 * s, cy - h / 2 + 42 * s, cx - w / 2 + 92 * s, cy - h / 2 + 92 * s], fill=(90, 100, 120))
    # свой кот: рыжий, полосатый, круглый
    hx, hy, R = cx, cy + 40 * s, 92 * s
    ginger, stripe = (246, 160, 70), (210, 110, 40)
    d.polygon([(hx - R * .95, hy - R * .2), (hx - R * .85, hy - R * 1.1), (hx - R * .3, hy - R * .75)], fill=ginger, outline=(30, 24, 30))
    d.polygon([(hx + R * .95, hy - R * .2), (hx + R * .85, hy - R * 1.1), (hx + R * .3, hy - R * .75)], fill=ginger, outline=(30, 24, 30))
    d.ellipse([hx - R, hy - R * .85, hx + R, hy + R * .85], fill=ginger, outline=(30, 24, 30), width=int(5 * s))
    for k in (-1, 0, 1):   # полоски на лбу
        d.line([hx + k * 22 * s, hy - R * .8, hx + k * 16 * s, hy - R * .45], fill=stripe, width=int(8 * s))
    d.ellipse([hx - 40 * s, hy + 6 * s, hx + 40 * s, hy + 60 * s], fill=(255, 236, 214))   # мордочка
    for sx in (-1, 1):
        d.ellipse([hx + sx * 34 * s - 9 * s, hy - 16 * s, hx + sx * 34 * s + 9 * s, hy + 4 * s], fill=(30, 24, 30))
        for k in range(3):
            d.line([hx + sx * 50 * s, hy + 14 * s + k * 10 * s, hx + sx * 110 * s, hy + 4 * s + k * 16 * s], fill=(30, 24, 30), width=int(3 * s))
    d.polygon([(hx - 9 * s, hy + 18 * s), (hx + 9 * s, hy + 18 * s), (hx, hy + 28 * s)], fill=(240, 120, 150))
    return Image.blend(img, lay, a)


def phone_screen(img, title, rows, red_last=False, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 130, 330, 590, 990
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(20, 20, 24), outline=(70, 70, 76), width=6)
    d.rounded_rectangle([x0 + 18, y0 + 24, x1 - 18, y1 - 24], radius=24, fill=(240, 240, 244))
    d.text((x0 + 44, y0 + 46), title, font=F(26, FONT_SUB), fill=(60, 60, 66))
    for i, (who, txt) in enumerate(rows):
        y = y0 + 100 + i * 64
        last = red_last and i == len(rows) - 1
        d.rounded_rectangle([x0 + 36, y, x1 - 36, y + 54], radius=14, fill=(255, 220, 216) if last else (222, 224, 232))
        d.text((x0 + 52, y + 6), who, font=F(19, FONT_SUB), fill=RED if last else (40, 60, 120))
        d.text((x0 + 52, y + 28), txt, font=F(18), fill=(150, 20, 20) if last else (30, 30, 34))
    return Image.blend(img, lay, a)


ROWS = [("Мне", "Через 365 дней — конец…"), ("Михалычу", "Через 365 дней — конец…")] + \
       [(f"Соседу, дом {n}", "Через 365 дней — конец…") for n in (3, 5, 6, 8, 11, 12, 14)]


# ---------- сцены ----------
def s01(t, L, cue):   # холодный старт: чехол жены
    img = V(world(**WRLD), (1060, ROOF_Y + 40, 2.0)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .55)
    img = phone_back(img, W / 2, 700, 1.0 + .06 * t)
    big_top(img, "ЧЕХОЛ ЖЕНЫ?!", 200, YEL, 74)
    hud(img, DAYS)
    return shake(img, t, 5 if t < .3 else 0)


def s02(t, L, cue):
    img = V(world(**WRLD), (1100, ROOF_Y + 60, 1.7)).out()
    hud(img, DAYS)
    return E3.choice_banner(img, t, "РАЗБИТЬ", L + .5, "вариант №1 из комментариев")


def s03(t, L, cue):   # кувалда
    p = (t - cue["03"]) / dur("03.mp3")
    v = V(world(**WRLD), (1020, ROOF_Y - 30, 2.4))
    hit = p > .35
    chibi(v.d, "neigh", 1080, ROOF_Y, 1.0, t, "angry", -1, arm="up" if not hit else "shovel")
    d = v.d
    if not hit:   # кувалда над головой
        d.line([1110, ROOF_Y - 150, 1060, ROOF_Y - 230], fill=(140, 100, 60), width=8)
        d.rectangle([1040, ROOF_Y - 250, 1080, ROOF_Y - 214], fill=(70, 70, 76), outline=OUT, width=3)
        black_box(d, 1000, ROOF_Y, t, 1.0)
    else:         # коробка расколота
        d.line([1110, ROOF_Y - 90, 1010, ROOF_Y - 40], fill=(140, 100, 60), width=8)
        d.rectangle([990, ROOF_Y - 60, 1030, ROOF_Y - 24], fill=(70, 70, 76), outline=OUT, width=3)
        d.polygon([(966, ROOF_Y), (996, ROOF_Y - 40), (998, ROOF_Y)], fill=(20, 20, 24), outline=OUT)
        d.polygon([(1004, ROOF_Y), (1006, ROOF_Y - 38), (1036, ROOF_Y)], fill=(20, 20, 24), outline=OUT)
        rnd = random.Random(int(t * 10))
        for _ in range(10):
            x, y = 1000 + rnd.uniform(-60, 60), ROOF_Y - rnd.uniform(10, 80)
            d.polygon([(x, y), (x + 8, y + 3), (x + 2, y + 8)], fill=(30, 30, 34))
    img = v.out()
    if hit:
        stamp(img, "БАЦ!", t, cue["03"] + dur("03.mp3") * .35, RED, 300, -8)
    hud(img, DAYS)
    return shake(img, t, 10 if .35 < p < .45 else 0)


def s04(t, L, cue):   # телефон: все сообщения
    p = (t - cue["04"]) / dur("04.mp3")
    img = V(world(**WRLD), (1000, ROOF_Y - 40, 2.6)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .5)
    n = 1 if p < .15 else min(len(ROWS), 2 + int((p - .45) / .55 * 7)) if p > .45 else 2
    img = phone_screen(img, "ОТПРАВЛЕННЫЕ", ROWS[:n])
    if p > .75:
        pill(img, "14 ПОЛУЧАТЕЛЕЙ", W / 2, 230, (150, 30, 36), WHITE, 36)
    hud(img, DAYS)
    return img


def s05(t, L, cue):   # черновик на завтра
    p = (t - cue["05"]) / dur("05.mp3")
    img = V(world(**WRLD), (1000, ROOF_Y - 40, 2.6)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .5)
    rows = [("Черновик · на завтра", "…")]
    if p > .55:
        rows = [("Черновик · на завтра", "Михалыч врёт.")]
    img = phone_screen(img, "ЧЕРНОВИКИ", rows, red_last=p > .55)
    if p > .55:
        stamp(img, "МИХАЛЫЧ ВРЁТ?!", t, cue["05"] + dur("05.mp3") * .55, RED, 210, 5, 56)
    hud(img, DAYS)
    return shake(img, t, 5 if .55 < p < .62 else 0)


def s06(t, L, cue):   # телефон переворачивают — чехол
    p = (t - cue["06"]) / dur("06.mp3")
    v = V(world(**WRLD), (1040, 800, 2.2))
    chibi(v.d, "me", 1100, GR - 4, 1.0, t, "shock", -1)
    img = Image.blend(v.out(), Image.new("RGB", (W, H)), .3)
    k = min(1, p / .35)   # телефон «переворачивают» — растёт из ребра
    img = phone_back(img, 220, 640, .62 * max(.12, k))
    if p > .6:
        stamp(img, "С КОТОМ…", t, cue["06"] + dur("06.mp3") * .6, YEL, 170, -4, 60)
    hud(img, DAYS)
    return img


def s07(t, L, cue):
    img = V(world(**WRLD), (1100, 840, 2.0)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .55)
    img = phone_back(img, W / 2, 760, .7)
    big_top(img, "ЗАЧЕМ ЕЙ ЭТО?", 200, WHITE, 70)
    d = ImageDraw.Draw(img)
    fp = F(32, FONT_SUB)
    txt = "ПИШИ ВЕРСИИ В КОММЕНТАРИЯХ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 24, 300, W / 2 + fp.getlength(txt) / 2 + 24, 364], radius=30, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 312), txt, font=fp, fill=(20, 20, 24))
    p = (t - cue["07"]) / dur("07.mp3")
    if p > .6:
        f = F(44, FONT_SUB)
        d.text(((W - f.getlength("6 СЕРИЯ — ЗАВТРА")) / 2, 1080), "6 СЕРИЯ — ЗАВТРА", font=f, fill=RED, stroke_width=5, stroke_fill=(10, 10, 14))
    hud(img, DAYS)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .05, span("s03")[0] + span("s03")[1] * .35, span("s05")[0] + span("s05")[1] * .55])
