"""«НОЧНАЯ СМЕНА». Серия 2: бокс №3 — холодильные камеры, ручка, стук из пятой, бирка с фамилией.
Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4"""
import os, sys, math, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("morg_s01", os.path.join(HERE, "seriya01.py"))
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter
from flatworld import SD, chibi

W, H, K, F = M.W, M.H, M.K, M.F
RED, YEL, WHITE = M.RED, M.YEL, M.WHITE
SURNAME = "КОВАЛЁВ Д."

LINES = {
    "01": "Почти все вы выбрали — *запереться*.",
    "02": "Влетаю в третий бокс. Захлопываю дверь. Щёлкаю ^замком^.",
    "03": "Внутри ^холодно^. Пар изо рта.",
    "04": "Вдоль стены — холодильные камеры. *Девять* дверец.",
    "05": "Одна ^приоткрыта^. Номер *пять*.",
    "06": "Каталка снаружи ^останавливается^. У самой двери.",
    "07": "Ручка медленно опускается. Вниз. ^Вверх^.",
    "08": "А потом — ^стук^. Но не в дверь.",
    "09": "Изнутри *пятой* камеры.",
    "10": "Дверца открывается шире. ^Сама^.",
    "11": "Оттуда торчит нога. С *биркой*. А на бирке — ^моя^ ^фамилия^.",
    "12": "Открыть дверь и *бежать*? Или *заглянуть* в камеру? ^Решай^.",
}
PLAN = [(f"b{k}", [(k, 0.05)], 0.15) for k in LINES]
PLAN[0] = ("b01", [("01", 0.0)], 0.1)
PLAN[8] = ("b09", [("09", 0.05)], 0.5)
PLAN[-1] = ("b12", [("12", 0.05)], 1.2)
setup(LINES, PLAN)

T0 = (2, 15, 10)


def vote_bar(img, t, label="ЗАПЕРЕТЬСЯ В БОКСЕ №3", pct=0.81):
    d = ImageDraw.Draw(img)
    k = min(1, t / 1.2)
    v = .27 + (pct - .27) * k
    x0, y0, x1 = 40, 110, W - 40
    d.rounded_rectangle([x0, y0, x1, y0 + 44], radius=10, fill=(20, 24, 28), outline=(200, 210, 210), width=2)
    d.rounded_rectangle([x0 + 4, y0 + 4, x0 + 4 + (x1 - x0 - 8) * v, y0 + 40], radius=8, fill=(214, 90, 60))
    d.text((x0 + 16, y0 + 10), label, font=F(20, FONT_SUB), fill=WHITE)
    d.text((x1 - 70, y0 + 10), f"{int(v * 100)}%", font=F(22, FONT_SUB), fill=WHITE)


def cold_room(t, open5=0.0, light=1.0, breath=True):
    """бокс изнутри: дверь слева, стена с 3×3 камерами"""
    img = Image.new("RGB", (W * K, H * K))
    d = SD(img, 0, 0, K)
    c = lambda v: tuple(int(q * light) for q in v)
    d.rectangle([0, 0, W, H], fill=c((120, 150, 156)))
    for y in range(0, H, 64):
        d.line([(0, y), (W, y)], fill=c((104, 132, 138)), width=2)
    d.rectangle([0, 1000, W, H], fill=c((80, 96, 100)))
    # 3×3 холодильных камер
    for r in range(3):
        for col in range(3):
            n = r * 3 + col + 1
            x0, y0 = 90 + col * 190, 300 + r * 220
            d.rectangle([x0, y0, x0 + 170, y0 + 190], fill=c((176, 186, 192)), outline=c((60, 70, 76)), width=4)
            d.rectangle([x0 + 66, y0 + 80, x0 + 104, y0 + 96], fill=c((90, 100, 106)))
            f = F(28, FONT_SUB)
            d.text((x0 + 14, y0 + 10), str(n), font=f, fill=(170, 30, 30) if n == 5 else c((40, 40, 44)))
            if n == 5 and open5 > 0:   # дверца приоткрыта: тёмная щель
                gap = 12 + 150 * open5
                d.polygon([(x0, y0), (x0 + gap, y0 + 10), (x0 + gap, y0 + 180), (x0, y0 + 190)], fill=(6, 10, 14))
    # иней
    rnd = random.Random(2)
    for _ in range(60):
        x, y = rnd.uniform(80, 660), rnd.uniform(290, 970)
        d.line([(x, y), (x + rnd.uniform(-8, 8), y + rnd.uniform(4, 10))], fill=(230, 244, 250), width=2)
    img = M.done(img)
    if breath:
        img = M.mist(img, t, 160, 1100, .5)
    return img


def timer(img, t, off=0):
    M.timer(img, t, (T0[0], T0[1], T0[2] + off))


# ---------- сцены ----------
def b01(t, L, cue):   # голосование + он вбегает
    img, d = M.corridor(light=.25, door_open=.6)
    M.gurney(d, 360, 1240, 1.2, light=.4)
    chibi(d, "intern", 520, 1050, 1.6, t, "shock", 1, walk=True)
    img = M.done(img)
    M.flashlight(img, 360, 1280, 520, 700, 140, 60)
    M.timer(img, t, T0)
    vote_bar(img, t)
    return img


def b02(t, L, cue):   # дверь изнутри, замок щёлкает
    p = (t - cue["02"]) / dur("02.mp3")
    img = Image.new("RGB", (W * K, H * K), (100, 124, 128))
    d = SD(img, 0, 0, K)
    d.rectangle([140, 200, 600, 1180], fill=(70, 80, 86), outline=(26, 30, 32), width=8)
    d.rectangle([470, 640, 560, 680], fill=(170, 176, 182), outline=(30, 30, 30), width=3)   # ручка
    lock_x = 300 if p < .7 else 360
    d.rectangle([280, 600, 420, 640], fill=(150, 156, 162), outline=(30, 30, 30), width=3)
    d.rectangle([lock_x, 604, lock_x + 50, 636], fill=(60, 60, 66))   # засов
    chibi(d, "intern", 330, 1270, 2.4, t, "shock", 1)
    img = M.done(img)
    if p > .7:
        M.tag(img, "ЩЁЛК", 120, (20, 22, 24), YEL, 40)
    timer(img, t, 4)
    return shake(img, t, 6 if p < .25 else 0)


def b03(t, L, cue):
    img = cold_room(t)
    M.tag(img, "−18°", 120, (40, 70, 110), WHITE, 40)
    timer(img, t, 9)
    return img


def b04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = cold_room(t)
    if p > .5:
        M.tag(img, "9 КАМЕР", 120, (20, 22, 24), WHITE, 32)
    timer(img, t, 13)
    return toonlib.zoom(img, 1 + .05 * t / L, .5, .5)


def b05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = cold_room(t, open5=.1)
    img = toonlib.zoom(img, 1.0 + .5 * M.ease(t / L), .5, .45)
    if p > .5:
        M.big(img, "№5", 140, RED, 110)
    timer(img, t, 18)
    return img


def b06(t, L, cue):   # каталка за дверью: тень в щели снизу
    p = (t - cue["06"]) / dur("06.mp3")
    img = Image.new("RGB", (W * K, H * K), (90, 112, 116))
    d = SD(img, 0, 0, K)
    d.rectangle([140, 200, 600, 1180], fill=(70, 80, 86), outline=(26, 30, 32), width=8)
    d.rectangle([470, 640, 560, 680], fill=(170, 176, 182), outline=(30, 30, 30), width=3)
    d.rectangle([140, 1172, 600, 1190], fill=(250, 240, 200))   # полоска света под дверью
    k = min(1, p / .6)
    for wx in (220 + 200 * (1 - k), 420 + 200 * (1 - k)):   # тени колёс
        d.rectangle([wx, 1172, wx + 40, 1190], fill=(10, 10, 12))
    img = M.done(img)
    if p > .65:
        M.tag(img, "СТОП", 120, (150, 30, 30), WHITE, 34)
    timer(img, t, 21)
    return img


def b07(t, L, cue):   # ручка вниз-вверх
    p = (t - cue["07"]) / dur("07.mp3")
    img = Image.new("RGB", (W * K, H * K), (90, 112, 116))
    d = SD(img, 0, 0, K)
    d.rectangle([60, 0, 660, H], fill=(70, 80, 86))
    ang = 0
    if .2 < p < .55:
        ang = 35 * min(1, (p - .2) / .2)
    elif .55 <= p < .85:
        ang = 35 * (1 - min(1, (p - .55) / .15))
    a = math.radians(ang)
    cx, cy = 300, 640
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(150, 156, 162), outline=(30, 30, 30), width=4)
    d.polygon([(cx, cy - 18), (cx + 300 * math.cos(a), cy - 18 + 300 * math.sin(a)), (cx + 300 * math.cos(a), cy + 18 + 300 * math.sin(a)), (cx, cy + 18)],
              fill=(176, 182, 188), outline=(30, 30, 30))
    img = M.done(img)
    if .2 < p < .85:
        M.big(img, "ВНИЗ" if p < .55 else "ВВЕРХ", 300, YEL, 90)
    timer(img, t, 25)
    return shake(img, t, 2 if .2 < p < .85 else 0)


def b08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    img = cold_room(t, open5=.1, light=.8)
    if p > .25:
        M.big(img, "ТУК", 360 + 40 * math.sin(t * 20), WHITE, 120)
    timer(img, t, 30)
    return shake(img, t, 8 if .25 < p < .4 else 0)


def b09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = cold_room(t, open5=.15, light=.75)
    img = toonlib.zoom(img, 1.8, .5, .52)
    if int(t * 3) % 2:
        M.big(img, "ТУК", 220, RED, 110)
    timer(img, t, 34)
    return shake(img, t, 6)


def b10(t, L, cue):
    p = (t - cue["10"]) / dur("10.mp3")
    img = cold_room(t, open5=.15 + .7 * M.ease(p), light=.7)
    img = toonlib.zoom(img, 1.6, .5, .52)
    img = M.mist(img, t, 380, 640, 1.0)
    timer(img, t, 37)
    return img


def toe_tag(img, t, p):
    d = ImageDraw.Draw(img)
    # стопа из темноты камеры
    d.rectangle([0, 0, W, H], fill=(4, 6, 8))
    d.polygon([(0, 560), (330, 520), (430, 470), (520, 480), (540, 560), (500, 640), (330, 680), (0, 720)], fill=(206, 214, 210), outline=(30, 30, 30))
    for i in range(5):
        d.ellipse([500 - i * 6, 470 + i * 30, 540 - i * 6, 500 + i * 30], fill=(196, 204, 200), outline=(30, 30, 30))
    # бирка на верёвке
    sw = 6 * math.sin(t * 2)
    d.line([(470, 560), (420 + sw, 720)], fill=(180, 170, 140), width=4)
    tag = Image.new("RGBA", (300, 170), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([0, 0, 299, 169], radius=14, fill=(236, 228, 196, 255), outline=(120, 100, 70, 255), width=4)
    td.ellipse([16, 70, 40, 94], fill=(4, 6, 8, 255))
    td.text((56, 20), "№ 5", font=F(30, FONT_SUB), fill=(60, 50, 40))
    if p > .6:
        td.text((56, 70), SURNAME, font=F(36, FONT_SUB), fill=(170, 30, 30))
        td.text((56, 120), "стажёр", font=F(24), fill=(80, 70, 60))
    tag = tag.rotate(-8 + sw, expand=True)
    img.paste(tag, (int(250 + sw), 700), tag)


def b11(t, L, cue):
    p = (t - cue["11"]) / dur("11.mp3")
    img = Image.new("RGB", (W, H))
    toe_tag(img, t, p)
    img = M.mist(img, t, 120, 600, .6)
    M.flashlight(img, 360, 1280, 360, 620, 220, 50)
    if p > .7:
        M.big(img, "ЭТО Я?!", 200, RED, 100)
    timer(img, t, 40)
    return shake(img, t, 5 if .6 < p < .7 else 0)


def b12(t, L, cue):
    img = Image.new("RGB", (W, H), (10, 14, 18))
    d = ImageDraw.Draw(img)
    f = F(34, FONT_SUB)
    d.text(((W - f.getlength("ЧТО ДЕЛАТЬ?")) / 2, 250), "ЧТО ДЕЛАТЬ?", font=f, fill=WHITE)
    img = M.choice_card(img, 40, "Открыть дверь\nи бежать", "run", min(1, t / .3))
    img = M.choice_card(img, 380, "Заглянуть\nв камеру №5", "door", min(1, max(0, t - .3) / .3))
    p = (t - cue["12"]) / dur("12.mp3")
    if p > .85:
        M.big(img, "РЕШАЙ", 800, RED, 80)
    d = ImageDraw.Draw(img)
    fp = F(30, FONT_SUB)
    txt = "ПОДПИШИСЬ — УЗНАЕШЬ, ЧТО ДАЛЬШЕ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 22, 940, W / 2 + fp.getlength(txt) / 2 + 22, 998], radius=28, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 951), txt, font=fp, fill=(20, 20, 24))
    timer(img, t, 46)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=[span("b08")[0] + span("b08")[1] * .3 + i * .5 for i in range(3)] + [span("b09")[0] + .2 + i * .45 for i in range(3)],
        hits=[span("b02")[0] + span("b02")[1] * .7, span("b11")[0] + span("b11")[1] * .65])
