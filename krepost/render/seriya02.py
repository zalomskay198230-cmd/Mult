"""«КРЕПОСТЬ». Серия 2 (зрители выбрали «колодец»): вода кончилась → копаем колодец в смотровой яме → на 6 м вода → снизу стук.
Голос пользователя, мат в субтитрах звёздочками (§). Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01"), "x.mp4"]
import seriya01 as K          # хелперы первой серии (ворота, искры, HUD-стиль, карточки)
sys.argv[:] = _argv
import toonlib
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import setup, run, dur, shake, glow, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter
from flatworld import SD, chibi, OUT, world, GR

W, H, F, E1, B = K.W, K.H, K.F, K.E1, K.B
YEL, RED, WHITE, GREEN = K.YEL, K.RED, K.WHITE, K.GREEN
pill, V = K.pill, K.V

LINES = {
    "01": "Всё, приехали. ^Вода^ кончилась.",
    "02": "Последняя полторашка — на *два* глотка, ё§§а.",
    "03": "Вы выбрали — *колодец*.",
    "04": "Ну а чё, яма смотровая есть. Вот прямо в ней и копаю вниз.",
    "05": "*Три* метра — глина, с§§а. *Пять* метров — руки в мясо. Но копаю.",
    "06": "*Шесть* метров… ^Вода^! Ледяная, зараза. Пью… кайф.",
    "07": "И тут снизу — ^тук^. ^Тук^. Из-под земли, б§§§§. Кто-то копает мне ^навстречу^.",
    "08": "Короче, завтра: или н§§§й *замуровать* эту яму — или *спуститься* глянуть. ^Решай^, братан.",
}
PLAN = [(f"k{k}", [(k, 0.04)], 0.1) for k in LINES]
PLAN[0] = ("k01", [("01", 0.0)], 0.1)
PLAN[-1] = ("k08", [("08", 0.05)], 0.9)
setup(LINES, PLAN)
toonlib.draw_subs = K.draw_caps


# ---------- HUD: вода и глубина ----------
def hud(img, water, depth):
    d = ImageDraw.Draw(img)
    for i, (lab, val, col) in enumerate((("ВОДА", water, RED if water in ("0 л", "0,3 л") else GREEN),
                                         ("ГЛУБИНА", f"{depth:.0f} м" if depth else "—", YEL))):
        x0 = 40 + i * 340
        lay = img.crop((x0, 40, x0 + 300, 124)).point(lambda v: v * .4)
        img.paste(lay, (x0, 40))
        d.rounded_rectangle([x0, 40, x0 + 300, 124], radius=14, outline=(110, 150, 210), width=3)
        d.text((x0 + 150 - F(20).getlength(lab) / 2, 48), lab, font=F(20), fill=(200, 216, 240))
        fv = F(38, FONT_SUB)
        d.text((x0 + 150 - fv.getlength(val) / 2, 72), val, font=fv, fill=col)


def bottle(d, x, y, s, level):
    """полторашка: x,y — низ по центру"""
    w, h = 34 * s, 110 * s
    d.rounded_rectangle([x - w / 2, y - h, x + w / 2, y], radius=8 * s, fill=(200, 222, 236), outline=OUT, width=3)
    if level > 0:
        d.rounded_rectangle([x - w / 2 + 4 * s, y - 4 * s - (h - 30 * s) * level, x + w / 2 - 4 * s, y - 4 * s], radius=5 * s, fill=(90, 160, 220))
    d.rectangle([x - 8 * s, y - h - 16 * s, x + 8 * s, y - h], fill=(60, 140, 70), outline=OUT, width=2)   # крышка
    d.rectangle([x - w / 2, y - h * .6, x + w / 2, y - h * .42], fill=(220, 60, 50), outline=OUT, width=2)   # этикетка


# ---------- разрез: гараж + шахта колодца ----------
FLOOR, PX_M = 300, 110          # пол гаража (экранный y) и пикселей на метр
PX0, PX1 = 250, 470             # стенки ямы


def section(t, depth, water=0.0, hero=True, face="angry", dig=True, knock=0.0, slab=False, ladder=False, eyes=False):
    img = Image.new("RGB", (W * 2, H * 2))
    d = SD(img, 0, 0, 2)
    # гараж: стены, полка, лампа
    d.rectangle([0, 0, W, FLOOR], fill=(54, 56, 64))
    for x in range(0, W, 90):
        d.line([x, 0, x, FLOOR], fill=(48, 50, 58), width=3)
    d.rectangle([40, 150, 200, 166], fill=(120, 84, 56), outline=OUT, width=3)        # полка
    for i in range(4):
        bottle(d, 70 + i * 36, 150, .45, 0)                                             # пустые бутылки
    d.line([W / 2, 0, W / 2, 70], fill=OUT, width=3)
    d.ellipse([W / 2 - 18, 66, W / 2 + 18, 96], fill=(255, 230, 160), outline=OUT, width=3)
    d.rectangle([560, FLOOR - 120, 700, FLOOR], fill=(110, 116, 126), outline=OUT, width=4)   # ворота изнутри
    d.rectangle([548, FLOOR - 66, 712, FLOOR - 54], fill=(150, 90, 60), outline=OUT, width=2)
    # грунт слоями
    for y0, y1, col in ((FLOOR, FLOOR + 24, (90, 90, 96)), (FLOOR + 24, FLOOR + 2.5 * PX_M, (112, 82, 58)),
                        (FLOOR + 2.5 * PX_M, FLOOR + 5 * PX_M, (150, 96, 60)), (FLOOR + 5 * PX_M, H, (70, 56, 50))):
        d.rectangle([0, y0, W, y1], fill=col)
    rnd = random.Random(7)
    for _ in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(FLOOR + 30, H)
        r = rnd.uniform(3, 9)
        d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(60, 46, 40))
    # шахта
    bot = FLOOR + depth * PX_M
    d.rectangle([PX0, FLOOR, PX1, bot], fill=(34, 28, 26))
    d.line([PX0, FLOOR, PX0, bot], fill=OUT, width=4); d.line([PX1, FLOOR, PX1, bot], fill=OUT, width=4)
    if water > 0:
        d.rectangle([PX0 + 2, bot - water * 60, PX1 - 2, bot], fill=(60, 130, 200))
        for k in range(3):
            yy = bot - water * 60 + 6 + 4 * math.sin(t * 3 + k)
            d.line([PX0 + 20 + k * 60, yy, PX0 + 60 + k * 60, yy], fill=(170, 210, 240), width=3)
    if ladder:
        for x in (PX0 + 40, PX0 + 110):
            d.line([x, FLOOR - 40, x, bot], fill=(150, 110, 70), width=6)
        for y in range(int(FLOOR), int(bot), 40):
            d.line([PX0 + 40, y, PX0 + 110, y], fill=(150, 110, 70), width=5)
    if slab:
        d.rectangle([PX0 - 30, FLOOR - 26, PX1 + 30, FLOOR + 4], fill=(150, 150, 152), outline=OUT, width=4)
        for x in range(PX0, PX1, 50):
            d.line([x, FLOOR - 20, x + 30, FLOOR - 4], fill=(120, 120, 124), width=2)
    # мерная рейка справа
    for m in range(1, 7):
        y = FLOOR + m * PX_M
        d.line([PX1 + 30, y, PX1 + 70, y], fill=(240, 236, 220), width=3)
        d.text((PX1 + 80, y - 30), f"{m} м", font=F(52, FONT_SUB), fill=(240, 236, 220) if m <= depth + .01 else (150, 130, 110))
    if hero:
        hy = bot - (water * 60 * .6 if water else 0)
        arm = "shovel" if dig else "up"
        bob = 6 * abs(math.sin(t * 4)) if dig else 0
        chibi(d, "hero", (PX0 + PX1) / 2 + 20, hy - bob, 1.25, t, face, -1, arm=arm)
        if dig:
            rnd2 = random.Random(int(t * 8))
            for _ in range(5):   # комья земли из-под лопаты
                a = rnd2.uniform(-2.6, -.6)
                r = rnd2.uniform(20, 60)
                d.ellipse([(PX0 + PX1) / 2 - 30 + r * math.cos(a) - 6, hy - 20 + r * math.sin(a) - 5,
                           (PX0 + PX1) / 2 - 30 + r * math.cos(a) + 6, hy - 20 + r * math.sin(a) + 5], fill=(130, 90, 60), outline=OUT, width=1)
    # снизу: чужой ход
    if knock > 0 or eyes:
        cy = bot + 150
        d.ellipse([PX0 + 10, cy - 50 * max(knock, .6), PX1 - 10, cy + 70], fill=(22, 18, 18))
        if eyes:
            for ex in ((PX0 + PX1) / 2 - 30, (PX0 + PX1) / 2 + 30):
                d.ellipse([ex - 9, cy - 4, ex + 9, cy + 10], fill=(255, 60, 40))
        for k in range(int(6 * knock)):   # трещины в дне
            x = PX0 + 30 + k * 30
            d.line([x, bot, x + 14, bot + 40, x - 6, bot + 80], fill=(20, 14, 12), width=3)
    img = img.resize((W, H), Image.LANCZOS)
    glow(img, (W / 2, 80), 160, (255, 220, 150), .35)
    return img


def cam(img, cy, z=1.0):
    """камера по вертикали: показываем окно вокруг cy (экранные координаты разреза)"""
    h = H / z
    top = max(0, min(H - h, cy - h / 2))
    w = W / z
    left = (W - w) / 2
    return img.resize((W, H), Image.LANCZOS, box=(left, top, left + w, top + h))


# ---------- сцены ----------
def k01(t, L, cue):   # холодный старт: гараж, ворота во вмятинах, воды нет
    v = V(world(day=True, lights=False), (900, GR - 120, 1.9), (930, GR - 90, 2.4), t / L)
    K.gate(v.d, "steel", dents=5)
    chibi(v.d, "hero", 1040, GR - 4, 1.0, t, "sad", -1)
    bottle(v.d, 1080, GR - 4, .35, 0)
    img = v.out()
    B.M.big(img, "ВОДЫ НЕТ", 190, RED, 96)
    hud(img, "0,3 л", 0)
    return img


def k02(t, L, cue):   # полторашка крупно
    p = (t - cue["02"]) / dur("02.mp3")
    img = Image.new("RGB", (W * 2, H * 2))
    d = SD(img, 0, 0, 2)
    d.rectangle([0, 0, W, H], fill=(54, 56, 64))
    chibi(d, "hero", 300, 1560, 6.0, t, "sad", 1)
    bottle(d, 520, 1180, 3.0, .1 if p < .6 else .05)
    img = img.resize((W, H), Image.LANCZOS)
    glow(img, (W / 2, 80), 200, (255, 220, 150), .35)
    if p > .3:
        pill(img, "2 ГЛОТКА", W / 2, 200, (150, 30, 30), WHITE, 38)
    hud(img, "0,3 л", 0)
    return img


def k03(t, L, cue):   # «вы выбрали — колодец»
    bg = section(t, 1.2, hero=True, dig=False, face="neutral")
    img = Image.blend(bg, Image.new("RGB", (W, H)), .35)
    img = choice_banner(img, t, "КОЛОДЕЦ", L - .05)
    hud(img, "0,3 л", 1)
    return img


def choice_banner(img, t, txt, full, sub="вариант №2 · решили комментарии"):
    if t >= full:
        return img
    a = min(1, t / .15, (full - t) / .25)
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 420, W, 760], fill=(10, 12, 18))
    d.rectangle([0, 420, W, 428], fill=YEL); d.rectangle([0, 752, W, 760], fill=YEL)
    f1, f2, f3 = F(40, FONT_SUB), F(80, FONT_SUB), F(26)
    for s_, f, y, col in (("ВЫ ВЫБРАЛИ", f1, 460, (200, 200, 206)), (txt, f2, 525, YEL), (sub, f3, 660, (170, 170, 176))):
        d.text(((W - f.getlength(s_)) / 2, y), s_, font=f, fill=col)
    return Image.blend(img, lay, a)


def k04(t, L, cue):   # смотровая яма → копаем
    p = (t - cue["04"]) / dur("04.mp3")
    depth = 1.4 + 1.2 * max(0, p)
    img = section(t, depth, face="angry", dig=p > .35)
    img = cam(img, 520, 1.0)
    if p < .45:
        pill(img, "СМОТРОВАЯ ЯМА", W / 2, 190, (20, 22, 30), YEL, 32)
    hud(img, "0,3 л", depth)
    return img


def k05(t, L, cue):   # 3 м глина → 5 м руки в мясо
    p = max(0, (t - cue["05"]) / dur("05.mp3"))
    depth = 2.6 + 2.6 * min(1, p * 1.1)
    img = section(t, depth, face="angry" if p < .7 else "sad")
    img = cam(img, FLOOR + depth * PX_M - 250, 1.15)
    lab = "ГЛИНА" if p < .45 else "РУКИ В МЯСО"
    pill(img, lab, W / 2, 190, (150, 30, 30) if p >= .45 else (20, 22, 30), WHITE, 34)
    img = shake(img, t, 2)
    hud(img, "0,3 л", depth)
    return img


def k06(t, L, cue):   # 6 м — вода!
    p = max(0, (t - cue["06"]) / dur("06.mp3"))
    depth = min(6, 5.2 + p * 3)
    water = 0 if p < .18 else min(1, (p - .18) / .2)
    img = section(t, depth, water=water, face="smile" if water > .5 else "shock", dig=water == 0)
    img = cam(img, FLOOR + depth * PX_M - 260, 1.2)
    if water > .3:
        B.M.big(img, "ВОДА!", 230, (110, 190, 250), 110)
    hud(img, "есть" if water > .5 else "0 л", depth)
    return img


KNOCKS = (.16, .29)


def k07(t, L, cue):   # стук снизу
    p = max(0, (t - cue["07"]) / dur("07.mp3"))
    n = sum(p > q for q in KNOCKS)
    knock = min(1, n * .4 + max(0, p - .5) * 1.2)
    img = section(t, 6, water=1, face="shock", dig=False, knock=knock, eyes=p > .82)
    img = cam(img, FLOOR + 6 * PX_M + 40, 1.2)
    img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 10)), .35)
    if n and p < .45:
        B.M.big(img, "ТУК", 280 + 40 * n, RED, 120)
    if p > .7:
        pill(img, "КТО-ТО КОПАЕТ НАВСТРЕЧУ", W / 2, 190, (150, 30, 30), WHITE, 30)
    hud(img, "есть", 6)
    return shake(img, t, 14 if any(0 < p - q < .05 for q in KNOCKS) else 0)


def k08(t, L, cue):   # выбор
    B._cards["slab"] = B._cards.get("slab") or cam(section(0, 6, water=1, hero=False, slab=True), 520, 1.0)
    B._cards["down"] = B._cards.get("down") or cam(section(0, 6, water=1, hero=False, ladder=True, knock=1, eyes=True), 1000, 1.0)
    bg = section(t, 6, water=1, hero=False, knock=1).filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(bg, Image.new("RGB", (W, H)), .55)
    d = ImageDraw.Draw(img)
    f = F(44, FONT_SUB)
    d.text(((W - f.getlength("ЧТО ДЕЛАЕМ?")) / 2, 170), "ЧТО ДЕЛАЕМ?", font=f, fill=WHITE, stroke_width=4, stroke_fill=(8, 8, 10))
    pulse = .5 + .5 * math.sin(t * 4)
    img = B.pretty_card(img, 36, 300, 310, 470, "slab", "1", "Замуровать\nяму", (240, 170, 60), min(1, t / .3), pulse)
    img = B.pretty_card(img, 374, 300, 310, 470, "down", "2", "Спуститься\nглянуть", (220, 60, 50), min(1, max(0, t - .25) / .3), 1 - pulse)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 40, 495, W / 2 + 40, 575], fill=YEL, outline=(10, 10, 14), width=5)
    fi = F(24, FONT_SUB)
    d.text((W / 2 - fi.getlength("ИЛИ") / 2, 520), "ИЛИ", font=fi, fill=(20, 20, 24))
    p = (t - cue["08"]) / dur("08.mp3")
    if p > .8:
        B.M.big(img, "РЕШАЙ", 800, RED, 84)
    hud(img, "есть", 6)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN})
