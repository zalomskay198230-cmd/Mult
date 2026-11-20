"""«365 ДНЕЙ». Серия 6 — ФИНАЛ (~40 с, без рекламы). Жена признаётся, улица строит общий бункер, люк закрыт, небо белеет.
Озвучка — голос Дмитрия (tts/s06). Запуск: python3 seriya06.py ../tts/s06 ../seriya06.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s05_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s05", os.path.join(HERE, "seriya05.py"))
E5 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E5)
sys.argv[:] = _argv
E1 = E5.E1
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s06"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya06.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter
import flatworld as FW
from flatworld import world, chibi, GR, OUT, PIT_X0, PIT_X1

W, H = toonlib.W, toonlib.H
V, hud, pill, dark_card, fade_in, ease, F = E1.V, E1.hud, E1.pill, E1.dark_card, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE
big_top, stamp, phone_back = E5.big_top, E5.stamp, E5.phone_back
WRLD = dict(day=False, lights=True, dug=1.0, cont=True, nb="open")
KITCHEN = (215, 800, 2.1)

# соседи — разные куртки и причёски
for i, (top, hair, style) in enumerate((((60, 140, 200), (90, 60, 40), "short"), ((200, 90, 60), (30, 30, 30), "spiky"),
                                        ((120, 170, 80), (220, 200, 120), "long"), ((150, 110, 190), (60, 40, 30), "short"),
                                        ((230, 190, 60), (40, 30, 30), "bald"), ((90, 90, 100), (150, 150, 150), "short"))):
    FW.CHAR[f"nb{i}"] = dict(skin=(232, 190, 156), hair=hair, top=top, pants=(50, 56, 72), shoes=(40, 40, 44), style=style)

LINES = {
    "01": "«Да. Это я *писала*», — сказала ^жена^. И положила на стол *пропуск*.",
    "02": "Она работает в *обсерватории*. Год назад их телескоп засёк то, о чём им ^запретили^ говорить.",
    "03": "Сказать прямо она не могла. Поэтому писала каждому — с его же *номера*. Чтобы ^поверили^.",
    "04": "«Выживут ^трое^» — это был *расчёт*. Воздуха в одном контейнере хватит на троих. Не на четверых.",
    "05": "Ей нужно было, чтобы мы *объединились*. Всей *улицей*.",
    "06": "Мы соединили ямы. Цемент *Михалыча*, мой *контейнер*, руки *двенадцати* соседей. Тёща таскала мешки. И ^ворчала^.",
    "07": "Через триста девятнадцать дней мы закрыли *люк*. Все. Даже *тёща*.",
    "08": "А потом небо стало ^белым^.",
    "09": "*Подпишись* — скоро новая история.",
}
PLAN = [(f"f{k}", [(k, 0.05)], 0.15) for k in LINES]
PLAN[0] = ("f01", [("01", 0.0)], 0.15)
PLAN[7] = ("f08", [("08", 0.1)], 1.6)
PLAN[8] = ("f09", [("09", 0.05)], 0.6)
setup(LINES, PLAN)


def pass_card(img, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    x0, y0 = 150, 560
    d.rounded_rectangle([x0, y0, x0 + 420, y0 + 250], radius=18, fill=(240, 244, 250), outline=(30, 40, 70), width=5)
    d.rectangle([x0, y0, x0 + 420, y0 + 60], fill=(40, 70, 140))
    d.text((x0 + 24, y0 + 12), "ОБСЕРВАТОРИЯ", font=F(32, FONT_SUB), fill=WHITE)
    d.rounded_rectangle([x0 + 24, y0 + 84, x0 + 134, y0 + 214], radius=10, fill=(246, 210, 180), outline=(30, 40, 70), width=3)
    d.chord([x0 + 30, y0 + 84, x0 + 128, y0 + 170], 180, 360, fill=(232, 186, 86))
    for i, ln in enumerate(("ПРОПУСК № 0365", "сотрудник", "доступ: секретно")):
        d.text((x0 + 156, y0 + 96 + i * 38), ln, font=F(24 if i == 0 else 20, FONT_SUB if i == 0 else FONT_B), fill=(30, 40, 70) if i < 2 else RED)
    return Image.blend(img, lay, a)


# ---------- сцены ----------
def f01(t, L, cue):   # холодный старт: признание на кухне
    v = V(world(**WRLD), KITCHEN, (215, 800, 2.3), t / L)
    chibi(v.d, "wife", 150, GR - 4, 1.0, t, "sad", 1)
    chibi(v.d, "me", 300, GR - 4, 1.0, t, "shock", -1)
    img = v.out()
    big_top(img, "«ЭТО Я ПИСАЛА»", 190, YEL, 64)
    p = (t - cue["01"]) / dur("01.mp3")
    if p > .6:
        img = pass_card(img, fade_in(t, cue["01"] + dur("01.mp3") * .6, .25))
    hud(img, 319)
    return shake(img, t, 4 if t < .3 else 0)


def f02(t, L, cue):   # обсерватория, вспышка в небе
    p = (t - cue["02"]) / dur("02.mp3")
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(8 + 20 * k), int(10 + 24 * k), int(30 + 40 * k)))
    rnd = random.Random(4)
    for _ in range(180):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 760), rnd.choice((1, 1, 1.5, 2))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 220, 236))
    if p > .3:   # то, что засекли: яркая точка с хвостом
        k = min(1, (p - .3) / .5)
        cx, cy = 520 - 60 * k, 300 + 40 * k
        for i in range(30):
            d.line([cx + i * 6, cy - i * 3, cx + i * 6 + 6, cy - i * 3 - 3], fill=(255, 240 - i * 4, 200 - i * 5), width=max(1, 8 - i // 4))
        E1.glow(img, (cx, cy), 40 + 20 * k, (255, 250, 220), 1.0) if hasattr(E1, "glow") else None
        d = ImageDraw.Draw(img)
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(255, 255, 255))
    d.chord([170, 820, 550, 1200], 180, 360, fill=(170, 176, 188), outline=OUT, width=5)   # купол
    d.rectangle([150, 1010, 570, H], fill=(140, 146, 158), outline=OUT, width=5)
    d.polygon([(340, 830), (380, 830), (470, 700), (446, 690)], fill=(60, 64, 74), outline=OUT)   # телескоп в щели
    pill(img, "ОБСЕРВАТОРИЯ · ГОД НАЗАД", W / 2, 180, (20, 22, 30), WHITE, 28)
    if p > .7:
        stamp(img, "ЗАСЕКРЕЧЕНО", t, cue["02"] + dur("02.mp3") * .7, RED, 420, -10, 60)
    hud(img, 319 + 46)
    return img


def f03(t, L, cue):   # рассылка с номеров соседей
    p = (t - cue["03"]) / dur("03.mp3")
    img = V(world(**WRLD), (900, 760, 1.0)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .5)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 640
    n = min(14, int(max(0, p - .2) / .6 * 14) + 1)
    for i in range(14):
        a = -math.pi / 2 + i * 2 * math.pi / 14
        x, y = cx + 270 * math.cos(a), cy + 300 * math.sin(a)
        on = i < n
        d.line([cx, cy, x, y], fill=(255, 206, 40) if on else (60, 60, 70), width=3)
        d.polygon([(x - 26, y), (x, y - 26), (x + 26, y), (x + 20, y), (x + 20, y + 22), (x - 20, y + 22), (x - 20, y)],
                  fill=(240, 240, 236) if on else (80, 80, 90), outline=OUT)
    img = phone_back(img, cx, cy, .38)
    if p > .55:
        pill(img, "КАЖДОМУ — С ЕГО НОМЕРА", W / 2, 200, (20, 22, 30), YEL, 30)
    hud(img, 319)
    return img


def f04(t, L, cue):   # расчёт воздуха
    p = (t - cue["04"]) / dur("04.mp3")
    img = V(world(**WRLD), (970, GR + 230, 1.6)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .45)
    rows = [("ВОЗДУХ В КОНТЕЙНЕРЕ", "на 3", 0.75, BLUE)]
    if p > .55:
        rows.append(("НАС В СЕМЬЕ", "4", 1.0, RED))
    dark_card(img, "«ВЫЖИВУТ ТРОЕ» = РАСЧЁТ", rows, 230, fade_in(t, .05))
    if p > .75:
        stamp(img, "3 < 4", t, cue["04"] + dur("04.mp3") * .75, RED, 560, 0, 96)
    hud(img, 319)
    return img


NEIGHBORS = ["nb0", "nb1", "nb2", "nb3", "nb4", "nb5"]


def f05(t, L, cue):   # вся улица
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="open"), (800, 820, 1.0))
    people = [("wife", 380), ("me", 450), ("son", 520), ("mil", 590), ("neigh", 1290)] + [(n, 700 + i * 90) for i, n in enumerate(NEIGHBORS)]
    for i, (who, x) in enumerate(people):
        k = min(1, max(0, t * 1.5 - i * .12))
        chibi(v.d, who, x, GR - 4, .85 if who == "son" else 1.0, t, "smile", 0, arm="up" if k >= 1 and i % 2 else None)
    img = v.out()
    if t > .4:
        stamp(img, "ВСЕЙ УЛИЦЕЙ", t, .4, YEL, 220, -4, 66)
    hud(img, 300)
    return img


def f06(t, L, cue):   # соединяем ямы, тёща таскает мешки
    p = (t - cue["06"]) / dur("06.mp3")
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="open"), (1220, GR + 180, 1.15))
    d = v.d
    k = min(1, p / .4)
    d.rectangle([PIT_X1, GR + 270, PIT_X1 + (1380 - PIT_X1) * k, GR + 340], fill=(54, 42, 38), outline=(96, 76, 64), width=4)   # тоннель
    for i, n in enumerate(NEIGHBORS[:4]):
        chibi(v.d, n, 860 + i * 140 + 20 * math.sin(t * 2 + i), GR - 4, .9, t, "smile", 1, walk=True)
    chibi(v.d, "neigh", 1470, GR + 476, 1.0, t, "smile", -1, arm="up")
    mx = 900 + (t * 60) % 400
    chibi(v.d, "mil", mx, GR - 4, .95, t, "angry", 1, walk=True)
    d.rounded_rectangle([mx + 20, GR - 80, mx + 66, GR - 34], radius=6, fill=(214, 206, 186), outline=OUT, width=2)   # мешок
    img = v.out()
    if p > .78:
        sx, sy = v.screen(mx, GR - 150)
        E1.bubble(img, "ворчу, но несу", sx, sy)
    money = int(min(1, p * 1.3) * 1240000)
    hud(img, 160 - int(100 * p), f"{money:,} ₽".replace(",", " "))
    return img


def f07(t, L, cue):   # 319 → 0, люк закрыт
    p = (t - cue["07"]) / dur("07.mp3")
    days = max(0, int(319 * (1 - min(1, p / .5))))
    v = V(world(day=False, lights=True, dug=1.0, cont=True, nb="open"), (1000, GR + 120, 1.5))
    d = v.d
    ang = min(1, max(0, (p - .5) / .3))
    hx, hy = PIT_X0 + 90, GR - 30   # люк над вентиляцией
    d.line([hx, hy, hx + 90 * math.cos(ang * math.pi / 2), hy - 90 * math.sin((1 - ang) * math.pi / 2)], fill=(110, 116, 126), width=14)
    for i, who in enumerate(("wife", "me", "son", "mil")):
        chibi(v.d, who, PIT_X0 + 110 + i * 80, GR + 344, .8, t, "smile", 0, shadow=False)
    if p > .8:
        v.glow((PIT_X0 + PIT_X1) / 2, GR + 240, 120, (255, 220, 150), .5)
    img = v.out()
    if p > .8:
        stamp(img, "ЛЮК ЗАКРЫТ", t, cue["07"] + dur("07.mp3") * .8, GREEN, 230, -4, 64)
    hud(img, days, "1 240 000 ₽")
    return img


def f08(t, L, cue):   # небо белеет
    vo_end = cue["08"] + dur("08.mp3")
    img = V(world(day=False, lights=False, dug=1.0, cont=True, nb="open"), (800, 760, 1.0)).out()
    k = min(1, max(0, (t - cue["08"] * .5) / (vo_end + .6)))
    img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), k ** 1.5)
    hud(img, 0, "1 240 000 ₽") if k < .9 else None
    return img


def f09(t, L, cue):
    img = Image.new("RGB", (W, H), (250, 250, 250))
    a = min(1, t / .5)
    img = Image.blend(img, Image.new("RGB", (W, H), (8, 8, 12)), a)
    d = ImageDraw.Draw(img)
    f1, f2, f3 = F(44, FONT_SUB), F(96, FONT_SUB), F(40, FONT_SUB)
    d.text(((W - f1.getlength("365 ДНЕЙ")) / 2, 440), "365 ДНЕЙ", font=f1, fill=RED)
    d.text(((W - f2.getlength("КОНЕЦ")) / 2, 500), "КОНЕЦ", font=f2, fill=WHITE)
    pop = 1 + .05 * math.sin(t * 8)
    fp = F(int(36 * pop), FONT_SUB)
    d.rounded_rectangle([W / 2 - fp.getlength("ПОДПИШИСЬ") / 2 - 26, 650, W / 2 + fp.getlength("ПОДПИШИСЬ") / 2 + 26, 718], radius=32, fill=YEL)
    d.text((W / 2 - fp.getlength("ПОДПИШИСЬ") / 2, 662), "ПОДПИШИСЬ", font=fp, fill=(20, 20, 24))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("f01")[0] + .05, span("f07")[0] + span("f07")[1] * .8, span("f08")[0] + span("f08")[1] * .7])
