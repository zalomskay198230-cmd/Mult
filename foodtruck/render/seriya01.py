"""«ФУДТРАК С НУЛЯ». Серия 1. Интерактивный формат: интерфейс стрима, «лайк = 10 ₽», вопросы зрителям в конце.
Плоский мир (движок den365/render/flatworld.py): улица, фургон в разрезе с кухней. Озвучка — пользователя.
Реклама klassvpn ставится после рендера: den365/render/add_popup.py (стоп-кадр после фразы 5).
Запуск: python3 seriya01.py ../tts/s01_golos ../seriya01.mp4"""
import os, sys, math, random
import importlib.util
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
_sp.loader.exec_module(E1)          # субтитры капсом, плашки, облачка, карточки
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01_golos"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import flatworld as FW
from flatworld import SD, K, OUT, dk, mix, vgrad, soft, beam, chibi, View

W, H = toonlib.W, toonlib.H
pill, bubble, dark_card, fade_in, ease, F = E1.pill, E1.bubble, E1.dark_card, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE

FW.CHAR["timur"] = dict(skin=(224, 176, 140), hair=(30, 24, 22), top=(46, 120, 96), pants=(40, 44, 56), shoes=(34, 34, 38),
                        style="short", beard=(52, 40, 34))
FW.CHAR["ded"] = dict(skin=(232, 190, 162), hair=(214, 214, 218), top=(126, 94, 70), pants=(64, 62, 70), shoes=(70, 50, 40),
                      style="short", beard=(220, 220, 224))

LINES = {
    "01": "Слушай, меня ^уволили^ из кафе в понедельник. А во вторник я купил *фургон*. На все деньги, брат.",
    "02": "*Сорок* *тысяч* рублей. Девяносто восьмого года. Без одной ^фары^. Вах, *красавец*.",
    "03": "В кассе — ^ноль^. На холодильник денег нет. На вывеску — тоже нет.",
    "04": "Поэтому теперь всё решаете *вы*, дорогие.",
    "05": "Каждый ваш *лайк* — *десять* *рублей* в кассу. Лайкнул — помог. Клянусь, всё на кухню пойдёт.",
    "06": "Первый покупатель пришёл, когда я ещё плиту отмывал. *Дед* с *собакой*. Чай спросил.",
    "07": "Чая не было. Я отдал ему свой *термос* — гость же. Дед сказал: «Приду завтра. С *друзьями*».",
    "08": "А потом я полез под прилавок. И нашёл ^ящик^. Железный. С замком.",
    "09": "На крышке наклейка: «Рецепт номер *семь*. Не готовить после ^полуночи^». Слушай, что за рецепт такой?",
    "10": "Что готовим первым — *шаурму*, *бургеры* или *пельмени*? И ящик открывать или нет?",
    "11": "Пишите в *комментариях*, дорогие. Как скажете — так и сделаю.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.2) for k in LINES]
PLAN[0] = ("s01", [("01", 0.1)], 0.15)
PLAN[-1] = ("s11", [("11", 0.05)], 1.2)
setup(LINES, PLAN)

WW, WH, GR = 1600, 1700, 1000          # мир фудтрака
VX0, VX1 = 520, 1180                   # фургон по X
VFLOOR = GR - 70                       # пол фургона
VTOP = GR - 420                        # крыша фургона
WIN_X0, WIN_X1 = 760, 1040             # окно выдачи
CHAT_NICKS = ["ashot_77", "lena.k", "vova_grill", "nastya", "dimon", "kot_v_sapogah", "marat05", "olya_m"]
CHAT = ["вах фургон", "лайк брат", "шаурму давай", "дед красавчик", "открывай ящик!!", "пельмени топ", "где фара?", "бургеры!!!",
        "рецепт 7 жуть", "держи лайк", "термос отдал респект", "не открывай"]


# ---------- мир ----------
def van(img, d, lit):
    body, body_d = (236, 232, 222), (206, 200, 188)
    stripe = (220, 70, 50)
    # кабина
    d.polygon([(VX1, VFLOOR - 300), (VX1 + 110, VFLOOR - 240), (VX1 + 150, VFLOOR - 120), (VX1 + 150, VFLOOR), (VX1, VFLOOR)], fill=body, outline=OUT)
    d.polygon([(VX1 + 14, VFLOOR - 280), (VX1 + 100, VFLOOR - 228), (VX1 + 128, VFLOOR - 150), (VX1 + 14, VFLOOR - 150)], fill=(150, 190, 214), outline=OUT)
    d.ellipse([VX1 + 132, VFLOOR - 100, VX1 + 152, VFLOOR - 74], fill=(60, 60, 66), outline=OUT, width=2)     # фары нет
    # кузов в разрезе
    d.rectangle([VX0, VTOP, VX1, VFLOOR], fill=(250, 244, 230) if lit else (60, 58, 66))
    for x in range(VX0 + 20, VX1, 40):   # кафель
        d.line([x, VTOP + 10, x, VFLOOR - 6], fill=dk((250, 244, 230) if lit else (60, 58, 66), .96), width=2)
    for y in range(VTOP + 30, VFLOOR, 40):
        d.line([VX0 + 6, y, VX1 - 6, y], fill=dk((250, 244, 230) if lit else (60, 58, 66), .96), width=2)
    d.rectangle([VX0 - 8, VTOP - 8, VX1 + 8, VFLOOR + 8], outline=FW.SECT, width=16)
    d.rectangle([VX0 - 8, VFLOOR + 8, VX1 + 8, VFLOOR + 40], fill=body_d, outline=OUT)
    d.rectangle([VX0 - 8, VFLOOR + 18, VX1 + 150, VFLOOR + 30], fill=stripe)
    for k_ in range(6):   # ржавчина
        rx = VX0 + 40 + k_ * 110
        d.ellipse([rx, VFLOOR + 20, rx + 34, VFLOOR + 36], fill=(150, 90, 50))
    # окно выдачи и прилавок
    d.rectangle([WIN_X0, VTOP + 70, WIN_X1, VTOP + 220], fill=(150, 190, 214) if lit else (30, 40, 60), outline=FW.SECT, width=8)
    d.rectangle([WIN_X0 - 20, VTOP + 214, WIN_X1 + 20, VTOP + 232], fill=(170, 130, 90), outline=OUT, width=2)
    d.rectangle([WIN_X0, VTOP + 232, WIN_X1, VFLOOR], fill=(210, 206, 196), outline=OUT, width=3)     # прилавок
    # плита, мойка, пустое место под холодильник
    d.rectangle([VX0 + 30, VFLOOR - 150, VX0 + 200, VFLOOR], fill=(120, 124, 132), outline=OUT, width=3)
    for bx in (VX0 + 70, VX0 + 160):
        d.ellipse([bx - 26, VFLOOR - 162, bx + 26, VFLOOR - 146], fill=(40, 40, 44))
    d.rectangle([VX0 + 230, VFLOOR - 120, VX0 + 330, VFLOOR], fill=(180, 186, 196), outline=OUT, width=3)
    for x0 in (VX0 + 380,):
        for y in range(int(VFLOOR - 200), int(VFLOOR), 22):
            d.line([x0, y, x0 + 90, y + 22], fill=(200, 60, 60), width=3)   # штриховка «пусто»
    for wx in (VX0 + 120, VX1 + 30):   # колёса
        d.ellipse([wx - 56, VFLOOR + 6, wx + 56, VFLOOR + 118], fill=(28, 28, 32), outline=(70, 70, 76), width=8)
        d.ellipse([wx - 20, VFLOOR + 42, wx + 20, VFLOOR + 82], fill=(150, 150, 156))
    if lit:
        d.line([(VX0 + VX1) / 2, VTOP + 4, (VX0 + VX1) / 2, VTOP + 30], fill=(40, 40, 44), width=3)
        d.ellipse([(VX0 + VX1) / 2 - 10, VTOP + 28, (VX0 + VX1) / 2 + 10, VTOP + 46], fill=(255, 236, 170))
        soft(img, (VX0 + VX1) / 2, VTOP + 40, 40, (255, 220, 150), .6)


_cache = {}


def world(day=True, lit=True):
    key = (day, lit)
    if key in _cache:
        return _cache[key]
    top, bot = ((130, 180, 228), (214, 230, 244)) if day else ((14, 18, 36), (44, 48, 80))
    img = vgrad(WW * K, WH * K, top, bot)
    d = SD(img)
    rnd = random.Random(4)
    for layer, (col, hmin, hmax) in enumerate((((176, 186, 206) if day else (34, 40, 66), 260, 520), ((150, 160, 182) if day else (26, 30, 52), 180, 380))):
        x = -20
        while x < WW:
            w, h = rnd.randint(90, 180), rnd.randint(hmin, hmax)
            d.rectangle([x, GR - h, x + w, GR], fill=col)
            for wy in range(GR - h + 20, GR - 30, 34):
                for wx in range(x + 12, x + w - 16, 26):
                    if rnd.random() < .35:
                        d.rectangle([wx, wy, wx + 12, wy + 16], fill=(250, 206, 120) if not day else mix(col, (255, 255, 255), .3))
            x += w + rnd.randint(4, 30)
    d.rectangle([0, GR, WW, WH], fill=(70, 72, 80))                 # асфальт
    d.rectangle([0, GR, WW, GR + 30], fill=(150, 150, 156))          # бордюр
    for x in range(0, WW, 120):
        d.rectangle([x, GR + 300, x + 60, GR + 312], fill=(230, 230, 220))
    d.line([300, GR, 300, GR - 330], fill=(60, 64, 72), width=8)     # фонарь
    d.line([300, GR - 330, 350, GR - 330], fill=(60, 64, 72), width=6)
    if not day:
        beam(img, [(330, GR - 322), (366, GR - 322), (430, GR), (250, GR)], (255, 220, 150), 50, 16)
    van(img, d, lit)
    _cache[key] = img
    return img


def V(c0, c1=None, k=0.0, day=True, lit=True):
    if c1:
        e = ease(k)
        c0 = tuple(a + (b - a) * e for a, b in zip(c0, c1))
    cx, cy, z = c0
    w, h = W / z, H / z
    cx = min(max(cx, w / 2), WW - w / 2)
    cy = min(max(cy, h / 2), WH - h / 2)
    return View(world(day, lit), (cx, cy, z), W, H)


# ---------- интерфейс стрима ----------
def stream_ui(img, t, cash, viewers=None, chat_k=1.0):
    d = ImageDraw.Draw(img)
    f = F(22, FONT_SUB)
    on = int(t * 2) % 2 == 0
    d.rounded_rectangle([30, 44, 186, 84], radius=10, fill=(200, 30, 36))
    d.ellipse([44, 56, 60, 72], fill=(255, 255, 255) if on else (255, 160, 160))
    d.text((70, 52), "В ЭФИРЕ", font=f, fill=WHITE)
    v = viewers if viewers is not None else 1200 + int(t * 37) % 400
    d.rounded_rectangle([30, 92, 186, 124], radius=10, fill=(14, 16, 24))
    d.text((44, 98), f"зрители {v}", font=F(18), fill=(200, 200, 210))
    # касса — справа, в стиле шкал (под ней встанет значок рекламы)
    x0 = W - 30 - 300
    lay = img.crop((x0, 40, x0 + 300, 124)).point(lambda q: q * .45)
    img.paste(lay, (x0, 40))
    d.rounded_rectangle([x0, 40, x0 + 300, 124], radius=14, outline=(110, 150, 210), width=3)
    d.text((x0 + 150 - F(20).getlength("КАССА") / 2, 48), "КАССА", font=F(20), fill=(190, 210, 240))
    txt = f"{cash:,} ₽".replace(",", " ")
    fv = F(42, FONT_SUB)
    d.text((x0 + 150 - fv.getlength(txt) / 2, 70), txt, font=fv, fill=YEL if cash >= 0 else RED)
    if chat_k > 0:   # лента комментариев слева внизу
        n = 4
        base = int(t * 1.3)
        for i in range(n):
            j = base + i
            nick, msg = CHAT_NICKS[j % len(CHAT_NICKS)], CHAT[(j * 5) % len(CHAT)]
            y = 1110 + i * 36
            fn, fm = F(19, FONT_SUB), F(19)
            w = fn.getlength(nick + ": ") + fm.getlength(msg) + 24
            lay = img.crop((24, y - 4, int(24 + w), y + 28)).point(lambda q: q * .5)
            img.paste(lay, (24, y - 4))
            d.text((36, y), nick + ":", font=fn, fill=(160, 200, 255))
            d.text((36 + fn.getlength(nick + ": "), y), msg, font=fm, fill=(235, 235, 240))


def money_pop(img, t, t0, txt, col=RED):
    if 0 <= t - t0 < 1.4:
        k = (t - t0) / 1.4
        f = F(int(54 + 10 * (1 - k)), FONT_SUB)
        ImageDraw.Draw(img).text((W - 30 - 150 - f.getlength(txt) / 2, 140 + 60 * k), txt, font=f, fill=col, stroke_width=4, stroke_fill=(10, 10, 14))


def dog(d, x, y, s=1.0, t=0.0):
    wag = 6 * math.sin(t * 12)
    d.ellipse([x - 34 * s, y - 40 * s, x + 30 * s, y - 10 * s], fill=(200, 150, 90), outline=OUT, width=2.4 * s)
    d.ellipse([x + 18 * s, y - 62 * s, x + 50 * s, y - 32 * s], fill=(200, 150, 90), outline=OUT, width=2.4 * s)
    d.polygon([(x + 22 * s, y - 58 * s), (x + 18 * s, y - 76 * s), (x + 32 * s, y - 62 * s)], fill=(150, 100, 60))
    d.ellipse([x + 40 * s, y - 52 * s, x + 46 * s, y - 46 * s], fill=OUT)
    for lx in (-24, -8, 10, 22):
        d.line([x + lx * s, y - 14 * s, x + lx * s, y], fill=OUT, width=5 * s)
    d.line([x - 32 * s, y - 30 * s, x - 50 * s, y - 46 * s + wag * s], fill=(200, 150, 90), width=6 * s)


def box(d, x, y, s=1.0, t=0.0, sticker=True):
    d.rounded_rectangle([x - 70 * s, y - 70 * s, x + 70 * s, y], radius=6 * s, fill=(110, 116, 124), outline=OUT, width=3 * s)
    d.rectangle([x - 70 * s, y - 70 * s, x + 70 * s, y - 52 * s], fill=(90, 96, 104), outline=OUT, width=2 * s)
    d.rounded_rectangle([x - 12 * s, y - 50 * s, x + 12 * s, y - 24 * s], radius=4 * s, fill=(200, 170, 60), outline=OUT, width=2 * s)
    if sticker:
        d.rectangle([x - 50 * s, y - 68 * s, x + 30 * s, y - 54 * s], fill=(250, 240, 200))


# ---------- сцены ----------
def s01(t, L, cue):
    p = (t - cue["01"]) / dur("01.mp3")
    v = V((850, 760, 1.1), (900, 800, 1.35), t / L)
    chibi(v.d, "timur", 380 + 120 * ease(p / .6), GR - 4, 1.0, t, "smile" if p > .5 else "sad", 1, walk=p < .6)
    img = v.out()
    pill(img, "ПН: УВОЛЕН" if p < .45 else "ВТ: КУПИЛ ФУРГОН", W / 2, 220, (140, 30, 30) if p < .45 else (30, 80, 50), WHITE, 32)
    stream_ui(img, t, 0)
    return img


def s02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    v = V((1150, 820, 1.7))
    chibi(v.d, "timur", 1000, GR - 4, 1.0, t, "smile", 1, arm="up" if p > .7 else None)
    img = v.out()
    if p > .05:
        pill(img, "−40 000 ₽", W / 2, 220, (140, 30, 30), WHITE, 36)
    if p > .35:
        pill(img, "1998 г.", W / 2 - 140, 300, (20, 22, 30), WHITE, 26)
    if p > .55:
        sx, sy = v.screen(VX1 + 142, VFLOOR - 87)
        pill(img, "без фары", sx - 60, sy - 150, (20, 22, 30), YEL, 26, anchor=(sx, sy))
    stream_ui(img, t, 0)
    money_pop(img, t, cue["02"] + .1, "−40 000 ₽")
    return img


def s03(t, L, cue):
    p = (t - cue["03"]) / dur("03.mp3")
    v = V((850, 760, 1.2))
    chibi(v.d, "timur", 700, VFLOOR, 1.0, t, "sad", 1)
    img = v.out()
    if p > .3:
        pill(img, "холодильник — НЕТ", W / 2, 250, (140, 30, 30), WHITE, 26)
    if p > .65:
        pill(img, "вывеска — НЕТ", W / 2, 320, (140, 30, 30), WHITE, 26)
    stream_ui(img, t, 0)
    return shake(img, t, 3 if p < .2 else 0)


def s04(t, L, cue):
    v = V((720, VFLOOR - 120, 2.6))
    chibi(v.d, "timur", 720, VFLOOR, 1.0, t, "smile", 0, arm="up")
    img = v.out()
    pill(img, "РЕШАЕТЕ ВЫ", W / 2, 230, (20, 22, 30), YEL, 44)
    stream_ui(img, t, 0)
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    v = V((720, VFLOOR - 120, 2.2))
    chibi(v.d, "timur", 720, VFLOOR, 1.0, t, "smile", 0, arm="up")
    img = v.out()
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 330
    beat = 1 + .08 * abs(math.sin(t * 6))
    r = 70 * beat
    d.ellipse([cx - r, cy - r * .7, cx, cy + r * .3], fill=(240, 50, 70))   # сердечко
    d.ellipse([cx, cy - r * .7, cx + r, cy + r * .3], fill=(240, 50, 70))
    d.polygon([(cx - r * .97, cy - r * .05), (cx + r * .97, cy - r * .05), (cx, cy + r * .95)], fill=(240, 50, 70))
    f = F(46, FONT_SUB)
    d.text((cx - f.getlength("1 ЛАЙК = 10 ₽") / 2, 430), "1 ЛАЙК = 10 ₽", font=f, fill=WHITE, stroke_width=4, stroke_fill=(10, 10, 14))
    for i in range(6):   # сердечки летят в кассу
        k = ((t * .9) + i / 6) % 1
        x = cx + (W - 180 - cx) * k + 30 * math.sin(i * 2 + t * 3)
        y = cy - (cy - 90) * k
        d.text((x, y), "+10 ₽", font=F(24, FONT_SUB), fill=GREEN, stroke_width=3, stroke_fill=(10, 10, 14))
    if p > .45:
        pill(img, "ЛАЙКНУЛ — ПОМОГ", W / 2, 520, (200, 30, 36), WHITE, 30)
    stream_ui(img, t, int(min(1, p) * 0))
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    v = V((850, 800, 1.35), day=True)
    chibi(v.d, "timur", 610, VFLOOR, 1.0, t, "neutral", -1, arm="shovel")   # трёт плиту
    for i in range(4):   # пена
        v.d.ellipse([560 + i * 18, VFLOOR - 170 - (t * 30 + i * 9) % 30, 574 + i * 18, VFLOOR - 156 - (t * 30 + i * 9) % 30], fill=(240, 248, 255))
    if p > .35:
        dx = 1260 - 160 * ease((p - .35) / .3)
        chibi(v.d, "ded", dx, GR - 4, 1.0, t, "neutral", -1, walk=p < .65)
        dog(v.d, dx + 70, GR - 4, 1.0, t)
    img = v.out()
    if p > .75:
        sx, sy = v.screen(1100, GR - 150)
        bubble(img, "чай есть?", sx, sy)
    stream_ui(img, t, 0)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    v = V((950, 820, 1.7))
    chibi(v.d, "timur", 900, VFLOOR, 1.0, t, "smile", 1, arm="up" if .2 < p < .5 else None)
    chibi(v.d, "ded", 1100, GR - 4, 1.0, t, "smile" if p > .5 else "neutral", -1)
    dog(v.d, 1170, GR - 4, 1.0, t)
    if .2 < p < .55:   # термос
        v.d.rounded_rectangle([1000, VTOP + 170, 1024, VTOP + 214], radius=6, fill=(200, 40, 40), outline=OUT, width=2)
    img = v.out()
    if p > .3:
        pill(img, "ТЕРМОС — ДЕДУ", W / 2, 230, (30, 80, 50), WHITE, 28)
    if p > .65:
        sx, sy = v.screen(1100, GR - 150)
        bubble(img, "приду завтра. с друзьями", sx - 40, sy)
    stream_ui(img, t, 0)
    return img


def s08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    v = V((900, VFLOOR - 100, 2.2), day=True)
    chibi(v.d, "timur", 860, VFLOOR + (40 if p > .2 else 0), 1.0, t, "shock" if p > .4 else "neutral", 1, shadow=False)
    v.d.rectangle([WIN_X0, VTOP + 232, WIN_X1, VFLOOR], fill=(210, 206, 196), outline=OUT, width=3)   # прилавок перед ним
    if p > .35:
        v.d.rectangle([WIN_X0 + 20, VFLOOR - 110, WIN_X1 - 20, VFLOOR - 4], fill=(40, 38, 40))   # под прилавком темно
        box(v.d, 960, VFLOOR - 8, 1.0, t, sticker=True)
        v.glow(960, VFLOOR - 40, 30, (255, 220, 150), .4)
    img = v.out()
    if p > .6:
        pill(img, "железный · с замком", W / 2, 240, (20, 22, 30), YEL, 28)
    stream_ui(img, t, 0)
    return img


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = Image.new("RGB", (W, H), (24, 22, 26))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 640
    d.rounded_rectangle([cx - 260, cy - 200, cx + 260, cy + 200], radius=18, fill=(110, 116, 124), outline=OUT, width=6)
    d.rectangle([cx - 260, cy - 200, cx + 260, cy - 140], fill=(90, 96, 104), outline=OUT, width=4)
    d.rounded_rectangle([cx - 40, cy - 40, cx + 40, cy + 50], radius=10, fill=(200, 170, 60), outline=OUT, width=4)
    d.rectangle([cx - 8, cy - 4, cx + 8, cy + 24], fill=(40, 30, 10))
    rot = Image.new("RGBA", (440, 150), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rot)
    rd.rectangle([0, 0, 439, 149], fill=(250, 240, 200, 255), outline=(120, 100, 60, 255), width=3)
    rd.text((22, 16), "РЕЦЕПТ №7", font=F(46, FONT_SUB), fill=(40, 30, 20))
    if p > .3:
        rd.text((22, 82), "НЕ ГОТОВИТЬ ПОСЛЕ", font=F(26, FONT_SUB), fill=(170, 30, 30))
        rd.text((22, 112), "ПОЛУНОЧИ", font=F(26, FONT_SUB), fill=(170, 30, 30))
    rot = rot.rotate(-4, expand=True)
    img.paste(rot, (int(cx - rot.width / 2), int(cy - 190)), rot)
    if p > .75:
        for i, (qx, qy) in enumerate(((cx - 300, cy - 260), (cx + 230, cy - 290), (cx + 270, cy + 160))):
            if int(t * 3 + i) % 3:
                d.text((qx, qy), "?", font=F(90, FONT_SUB), fill=YEL, stroke_width=5, stroke_fill=(10, 10, 14))
    stream_ui(img, t, 0)
    return img


def vote_cards(img, t, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([60, 200, W - 60, 560], radius=22, fill=(14, 16, 24), outline=(110, 150, 210), width=4)
    f0 = F(34, FONT_SUB)
    d.text(((W - f0.getlength("ЧТО ГОТОВИМ?")) / 2, 222), "ЧТО ГОТОВИМ?", font=f0, fill=WHITE)
    for i, (txt, col) in enumerate((("ШАУРМА", (230, 140, 50)), ("БУРГЕРЫ", (210, 60, 60)), ("ПЕЛЬМЕНИ", (90, 150, 220)))):
        y = 290 + i * 86
        d.ellipse([100, y, 160, y + 60], fill=col)
        d.text((130 - F(34, FONT_SUB).getlength(str(i + 1)) / 2, y + 8), str(i + 1), font=F(34, FONT_SUB), fill=WHITE)
        d.text((186, y + 8), txt, font=F(40, FONT_SUB), fill=WHITE)
    d.rounded_rectangle([60, 590, W - 60, 760], radius=22, fill=(14, 16, 24), outline=(110, 150, 210), width=4)
    d.text(((W - f0.getlength("ЯЩИК ОТКРЫВАТЬ?")) / 2, 612), "ЯЩИК ОТКРЫВАТЬ?", font=f0, fill=WHITE)
    for i, (txt, col) in enumerate((("ДА", (60, 170, 90)), ("НЕТ", (200, 50, 50)))):
        x0 = 150 + i * 240
        d.rounded_rectangle([x0, 670, x0 + 180, 734], radius=14, fill=col)
        d.text((x0 + 90 - F(36, FONT_SUB).getlength(txt) / 2, 680), txt, font=F(36, FONT_SUB), fill=WHITE)
    return Image.blend(img, lay, a)


def s10(t, L, cue):
    img = V((850, 800, 1.2), day=False).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .3)
    img = vote_cards(img, t, fade_in(t, .05))
    stream_ui(img, t, 0)
    return img


def s11(t, L, cue):
    img = V((850, 800, 1.2), day=False).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .3)
    img = vote_cards(img, t)
    d = ImageDraw.Draw(img)
    pop = 1 + .05 * math.sin(t * 8)
    fp = F(int(32 * pop), FONT_SUB)
    txt = "ПИШИ В КОММЕНТАРИЯХ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 24, 800, W / 2 + fp.getlength(txt) / 2 + 24, 864], radius=30, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 812), txt, font=fp, fill=(20, 20, 24))
    stream_ui(img, t, 0)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s02")[0] + .1, span("s08")[0] + span("s08")[1] * .4])
