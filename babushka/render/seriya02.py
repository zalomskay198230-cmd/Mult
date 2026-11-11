"""«БАБУШКУ УКУСИЛИ». Серия 2 (по выбору зрителей: «Да — выдать патрулю»).
Гибрид: те же 3D-фоны (babushka/frames_bg) + 2D-персонажи, хелперы — из первой серии.
Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, os.path.join(ROOT, "million", "render"))
import toonlib

# хелперы первой серии (фон, Саша, бабушка, патруль, радио, окно, плашки)
_argv = sys.argv[:]
sys.argv[1:2] = [os.path.join(HERE, "..", "tts", "s01")]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("babushka_s01", os.path.join(HERE, "seriya01.py"))
B1 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(B1)
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import denis_rig as DR

LINES = {
    "01": "Я открыл дверь. И сказал патрулю: она в комнате.",
    "02": "Я думал, она будет кричать. А она надела пальто. И взяла банку вишнёвого варенья.",
    "03b": "Сашенька, блины на плите. Не забудь выключить.",
    "04": "Её посадили в фургон с красным крестом. Номер на борту — сорок семь. Я запомнил.",
    "05": "Дома стало тихо. Впервые за неделю никто не пел и не путал слова.",
    "06": "Утром я по привычке пошёл на кухню. Сковородка была холодная.",
    "07": "Под тарелкой лежала записка. Её почерк. Написана три дня назад.",
    "08b": "Если меня заберут — не ищи. Я ещё помню, как тебя зовут. Пусть так и останется.",
    "09": "Я позвонил на горячую линию. Укушенных не возвращают. Где они — не говорят.",
    "10": "А вечером по радио объявили: найдено лекарство.",
    "11r": "Препарат действует только в первые десять суток после укуса.",
    "12": "Бабушку укусили девять дней назад. Где она — не знает никто. Есть только номер фургона: сорок семь.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.3) for k in LINES]
PLAN[0] = ("s01", [("01", 0.3)], 0.3)
PLAN[-1] = ("s12", [("12", 0.1)], 3.6)
setup(LINES, PLAN)

F, GY, INK_ = B1.F, B1.GY, INK
bg, char, sasha, patrol, plate, steam, radio, window = B1.bg, B1.char, B1.sasha, B1.patrol, B1.plate, B1.steam, B1.radio, B1.window
FONT_HAND = "/usr/share/fonts/opentype/inter/Inter-MediumItalic.otf"


def babushka(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, coat=False, jar=False):
    """бабушка; coat — в пальто (без фартука), jar — банка варенья в руке"""
    if not coat:
        return B1.babushka(img, x, s, t, arms, expr, look, ground)
    DR.use("babushka", top=(112, 84, 64), hoodie=False)
    img = char(img, DR.front((W, H), x, ground, s, t, arms, "idle", expr, look))
    d = ImageDraw.Draw(img)
    P = lambda lx, ly: B1.L2S(x, ground, s, lx, ly)
    for k in range(4):   # пуговицы пальто
        d.ellipse([*P(-6, 250 + k * 60), *P(6, 262 + k * 60)], fill=(60, 44, 34))
    d.polygon([P(-58, 214), P(0, 250), P(58, 214), P(40, 200), P(0, 228), P(-40, 200)], fill=(90, 66, 50))   # воротник
    if jar:
        el, wr = DR.ARM[arms[1]] if isinstance(arms[1], str) else arms[1]
        hx, hy = P(wr[0], wr[1] + 12)
        d.rounded_rectangle([hx - 34 * s, hy - 90 * s, hx + 34 * s, hy], radius=int(10 * s), fill=(150, 20, 40), outline=INK, width=3)
        d.rectangle([hx - 36 * s, hy - 104 * s, hx + 36 * s, hy - 84 * s], fill=(240, 240, 236), outline=INK, width=3)
        d.rectangle([hx - 22 * s, hy - 70 * s, hx + 22 * s, hy - 36 * s], fill=(250, 246, 230))
    return img


def van(d, x0, y0, num="47", s=1.0):
    w, h = 400 * s, 300 * s
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(30 * s), fill=(236, 236, 232), outline=INK, width=5)
    d.rectangle([x0 + w * .62, y0 + 30 * s, x0 + w - 24 * s, y0 + 120 * s], fill=(150, 190, 214), outline=INK, width=3)   # окно кабины
    cx, cy = x0 + w * .3, y0 + 110 * s
    d.rectangle([cx - 20 * s, cy - 60 * s, cx + 20 * s, cy + 60 * s], fill=(210, 40, 40))
    d.rectangle([cx - 60 * s, cy - 20 * s, cx + 60 * s, cy + 20 * s], fill=(210, 40, 40))
    f = F(int(80 * s), FONT_SUB)
    d.text((x0 + w * .58, y0 + 150 * s), num, font=f, fill=INK)
    for wx in (x0 + 80 * s, x0 + w - 80 * s):
        d.ellipse([wx - 44 * s, y0 + h - 40 * s, wx + 44 * s, y0 + h + 48 * s], fill=(30, 30, 34), outline=(70, 70, 76), width=6)


def pan(d, cx=330, cy=860, cold=True):
    d.ellipse([cx - 280, cy - 150, cx + 280, cy + 150], fill=(32, 32, 36), outline=INK, width=6)
    d.ellipse([cx - 250, cy - 128, cx + 250, cy + 128], fill=(40, 40, 44) if cold else (44, 44, 48))
    d.line([cx + 270, cy, 640, cy - 30], fill=(26, 26, 30), width=40)


def note(img, lines, shown, y=330, k=1.0):
    """записка от руки; shown — сколько строк уже видно"""
    d = ImageDraw.Draw(img)
    x0, x1 = 90, W - 90
    paper = Image.new("RGB", (x1 - x0, 560), (246, 240, 222))
    pd = ImageDraw.Draw(paper)
    for yy in range(70, 560, 56):
        pd.line([20, yy, x1 - x0 - 20, yy], fill=(200, 210, 230), width=2)
    pd.line([60, 0, 60, 560], fill=(230, 160, 160), width=2)
    f = ImageFont.truetype(FONT_HAND, 40)
    for i, ln in enumerate(lines[:shown]):
        pd.text((80, 26 + i * 56), ln, font=f, fill=(40, 52, 120))
    paper = paper.rotate(-2.5, expand=True, fillcolor=(0, 0, 0))
    m = paper.convert("L").point(lambda v: 255 if v > 8 else 0)
    img.paste(paper, (x0 - 10, y), m)


def calendar(img, crossed, total=10, y=360):
    d = ImageDraw.Draw(img)
    cols, sz, gap = 5, 104, 14
    x0 = (W - (cols * sz + (cols - 1) * gap)) / 2
    f = F(44, FONT_SUB)
    for i in range(total):
        r, c = divmod(i, cols)
        x, yy = x0 + c * (sz + gap), y + r * (sz + gap)
        last = i == total - 1
        d.rounded_rectangle([x, yy, x + sz, yy + sz], radius=14, fill=(250, 250, 246) if not last else (255, 226, 120), outline=INK, width=4)
        txt = str(i + 1)
        d.text((x + sz / 2 - f.getlength(txt) / 2, yy + 26), txt, font=f, fill=INK)
        if i < crossed:
            d.line([x + 14, yy + 14, x + sz - 14, yy + sz - 14], fill=(210, 40, 40), width=10)
            d.line([x + sz - 14, yy + 14, x + 14, yy + sz - 14], fill=(210, 40, 40), width=10)


def fade_in(t, t0, dd=.3):
    return max(0.0, min(1.0, (t - t0) / dd))


# ---------- сцены ----------
def s01(t, L, cue):   # дверь открыта, патруль на пороге
    img = bg("b1_door", 1.0)
    d = ImageDraw.Draw(img)
    d.rectangle([380, 330, 640, 1250], fill=(20, 22, 26))   # проём открытой двери
    img = patrol(img, 450, .74, t)
    img = patrol(img, 580, .7, t + .4)
    p = (t - cue["01"]) / dur("01.mp3")
    img = sasha(img, 190, .9, t, ("down", "out") if p > .5 else ("down", "down"), "tense", (.8, 0))
    return zoom(img, 1.0 + .05 * t / L, .4, .5)


def s02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    img = bg("b1_kitchen", 1.05)
    coat = p > .35
    img = babushka(img, 300, .86, t, ("down", "phone") if p > .6 else ("down", "down"), "neutral", (.6, 0), coat=coat, jar=p > .6)
    img = patrol(img, 590, .76, t)
    return img


def s03b(t, L, cue):
    img = bg("b1_kitchen", .95, 4)
    img = babushka(img, W / 2, 1.5, t, ("down", "down"), "smile", (0, 0), ground=1900, coat=True)
    return zoom(img, 1.0 + .06 * t / L, .5, .35)


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = bg("b1_street", 1.25)
    img = B1.sirens(img, t, .1)
    d = ImageDraw.Draw(img)
    van(d, 300, 760)
    if p < .4:
        img = babushka(img, 230, .62, t, ("down", "phone"), "neutral", (1, 0), coat=True, jar=True)
        img = patrol(img, 120, .64, t)
    if p > .45:   # номер крупно
        d = ImageDraw.Draw(img)
        d.ellipse([520, 880, 700, 1000], outline=(250, 210, 90), width=8)
        plate(img, "ФУРГОН № 47", col=(160, 30, 30))
    return img


def s05(t, L, cue):
    img = bg("b1_kitchen", .55)
    img = Image.blend(img, Image.new("RGB", (W, H), (10, 14, 30)), .35)
    d = ImageDraw.Draw(img)
    window(d, 60, 300, 280, 360, tape_x=True)
    img = sasha(img, 450, .86, t, ("down", "down"), "sad", (-.6, .2))
    plate(img, "ночь · тишина", col=(20, 24, 40))
    return img


def s06(t, L, cue):
    img = bg("b1_kitchen_close", 1.0, 4)
    d = ImageDraw.Draw(img)
    pan(d, cold=True)
    plate(img, "утро · холодная")
    return zoom(img, 1.0 + .05 * t / L, .5, .6)


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    img = bg("b1_kitchen_close", .95, 5)
    d = ImageDraw.Draw(img)
    lift = min(1, max(0, (p - .1) / .3)) * 120
    d.polygon([(170, 940), (520, 900), (560, 1010), (200, 1060)], fill=(246, 240, 222), outline=INK)   # записка под тарелкой
    for k in range(4):
        d.line([220, 960 + k * 22, 500, 930 + k * 22], fill=(60, 72, 140), width=3)
    d.ellipse([140, 860 - lift, 560, 1000 - lift], fill=(240, 240, 236), outline=INK, width=5)   # тарелка
    d.ellipse([200, 890 - lift, 500, 970 - lift], fill=(226, 226, 222))
    if p > .55:
        plate(img, "написана 3 дня назад")
    return img


NOTE = ["Если меня заберут —", "не ищи.", "Я ещё помню,", "как тебя зовут.", "Пусть так", "и останется.", "         Бабушка"]


def s08b(t, L, cue):
    p = (t - cue["08b"]) / dur("08b.mp3")
    img = bg("b1_kitchen_close", .7, 8)
    shown = 1 + int(min(1, max(0, p)) * (len(NOTE) - 1) + .3)
    note(img, NOTE, shown)
    return zoom(img, 1.0 + .04 * t / L, .5, .45)


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = bg("b1_door", .95)
    img = sasha(img, 220, .9, t, ("ear", "down"), "worried", (.6, 0))
    if p > .35:
        B1.bubble(img, "не возвращают", 300, 170)
    if p > .7:
        B1.bubble(img, "где — не говорим", 260, 290)
    plate(img, "горячая линия", y=1120)
    return img


def s10(t, L, cue):
    img = bg("b1_kitchen", .8)
    img = Image.blend(img, Image.new("RGB", (W, H), (40, 24, 10)), .25)
    img = sasha(img, 470, .86, t, ("down", "down"), "tense", (-.8, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, 900, 330, 1080], radius=24, fill=(130, 84, 50), outline=INK, width=5)   # радио на столе
    d.rounded_rectangle([80, 920, 200, 1060], radius=12, fill=(210, 190, 150), outline=INK, width=3)
    d.ellipse([230, 940, 300, 1010], fill=(70, 50, 34), outline=INK, width=3)
    plate(img, "вечер")
    return img


def s11r(t, L, cue):
    img = bg("b1_kitchen", 1.0, 6)
    radio(img, t, 1.0 if t >= cue["11r"] and t < cue["11r"] + dur("11r.mp3") else .1)
    p = (t - cue["11r"]) / dur("11r.mp3")
    if p > .45:
        plate(img, "ТОЛЬКО ПЕРВЫЕ 10 СУТОК", col=(160, 30, 30))
    return img


def s12(t, L, cue):
    vo_end = cue["12"] + dur("12.mp3")
    p = (t - cue["12"]) / dur("12.mp3")
    img = bg("b1_kitchen", .6, 8)
    crossed = min(9, int(min(1, p / .3) * 9))
    calendar(img, crossed)
    d = ImageDraw.Draw(img)
    if p > .35:
        f = F(56, FONT_SUB)
        txt = "осталось: 1 день"
        d.text(((W - f.getlength(txt)) / 2, 640), txt, font=f, fill=(255, 226, 120), stroke_width=5, stroke_fill=INK)
    if p > .72:
        f = F(120, FONT_SUB)
        d.text(((W - f.getlength("№ 47")) / 2, 760), "№ 47", font=f, fill=(240, 70, 80), stroke_width=7, stroke_fill=INK)
    if t > vo_end + .9:
        a = min(1, (t - vo_end - .9) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2 = F(50, FONT_SUB), F(36, FONT_SUB)
            dd.text(((W - f1.getlength("ЧАСТЬ 3")) / 2, 500), "ЧАСТЬ 3", font=f1, fill=(240, 240, 244))
            dd.text(((W - f2.getlength("финал")) / 2, 576), "финал", font=f2, fill=(240, 70, 80))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(span("s11r")[0], span("s11r")[0] + span("s11r")[1])],
        hits=[span("s01")[0] + .3, span("s04")[0] + span("s04")[1] * .5, span("s12")[0] + span("s12")[1] * .7])
