"""«365 ДНЕЙ». Серия 2 (зрители выбрали «бежать наверх»). Тот же плоский мир в разрезе + участок соседа.
Озвучка — пользователя (tts/s02_golos). Запуск: python3 seriya02.py ../tts/s02_golos ../seriya02.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s01", os.path.join(HERE, "seriya01.py"))
E1 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E1)          # хелперы первой серии: камера, HUD, плашки, карточки, субтитры капсом
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02_golos"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter
from flatworld import world, chibi, GR, PIT_X0, PIT_X1, OUT, dk

W, H = toonlib.W, toonlib.H
V, hud, pill, bubble, dark_card, fade_in, ease, F = E1.V, E1.hud, E1.pill, E1.bubble, E1.dark_card, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE

LINES = {
    "01": "Вы выбрали — ^бежать^.",
    "02": "Я вылез из ямы за *четыре* *секунды*. Лопату оставил внизу.",
    "03": "^Стук^ продолжался. Ровно. Как будто кто-то знал, что торопиться *некуда*.",
    "04": "Я спрятался за *гаражом* и просидел там до рассвета. В *пять* *утра* стук прекратился.",
    "05": "Правило второе: если не знаешь, кто рядом, — сначала *смотри*. Потом копай.",
    "06": "Утром я пошёл вдоль забора. И у соседнего гаража увидел кучу *земли*. Свежую. Кубов на *двадцать*.",
    "07": "Тот самый ^сосед^. Который дал мне лопату. И спросил — *зачем*.",
    "08": "Его машина стояла с открытым багажником. В багажнике — мешки с *цементом*. *Двенадцать* штук.",
    "09": "Когда сосед уехал, я перелез через забор. Под брезентом была ^яма^. Глубже моей.",
    "10": "А на стене, прямо в глине, было выцарапано число. ^Триста^ ^шестьдесят^ ^пять^.",
    "11": "Сообщение пришло не только *мне*.",
    "12": "Третья серия — *завтра*.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.3) for k in LINES]
PLAN[0] = ("s01", [("01", 0.15)], 0.2)
PLAN[-2] = ("s11", [("11", 0.05)], 0.6)
PLAN[-1] = ("s12", [("12", 0.1)], 1.0)
setup(LINES, PLAN)

PIT_FLOOR = GR + 340
NB_PIT_WALL = 1380


def car(d, x, trunk=False, bags=0):
    y = GR - 4
    col = (70, 76, 90)
    d.rounded_rectangle([x - 110, y - 70, x + 110, y - 20], radius=14, fill=col, outline=OUT, width=4)
    d.polygon([(x - 70, y - 70), (x - 40, y - 112), (x + 50, y - 112), (x + 80, y - 70)], fill=dk(col, .9), outline=OUT)
    d.polygon([(x - 56, y - 72), (x - 34, y - 104), (x + 4, y - 104), (x + 4, y - 72)], fill=(150, 190, 214))
    d.polygon([(x + 12, y - 72), (x + 12, y - 104), (x + 44, y - 104), (x + 66, y - 72)], fill=(150, 190, 214))
    for wx in (x - 64, x + 64):
        d.ellipse([wx - 22, y - 44, wx + 22, y], fill=(28, 28, 32), outline=(70, 70, 76), width=4)
    if trunk:   # открытая крышка багажника и мешки
        d.polygon([(x - 110, y - 70), (x - 150, y - 128), (x - 136, y - 134), (x - 98, y - 74)], fill=dk(col, .8), outline=OUT)
        for i in range(bags):
            bx, by = x - 104 + (i % 4) * 20, y - 66 - (i // 4) * 14
            d.rounded_rectangle([bx, by - 12, bx + 18, by], radius=3, fill=(214, 206, 186), outline=OUT, width=1)


def choice_banner(img, t, txt="БЕЖАТЬ НАВЕРХ", full=2.0):
    if t >= full:
        pill(img, "ВЫБОР ЗРИТЕЛЕЙ: бежать", W / 2, 160, (20, 22, 30), YEL, 24)
        return img
    a = min(1, t / .2, (full - t) / .3)
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 420, W, 760], fill=(10, 12, 18))
    d.rectangle([0, 420, W, 428], fill=YEL); d.rectangle([0, 752, W, 760], fill=YEL)
    f1, f2, f3 = F(40, FONT_SUB), F(66, FONT_SUB), F(26)
    for s_, f, y, col in (("ВЫ ВЫБРАЛИ", f1, 460, (200, 200, 206)), (txt, f2, 530, YEL), ("вариант №3 из комментариев", f3, 660, (170, 170, 176))):
        d.text(((W - f.getlength(s_)) / 2, y), s_, font=f, fill=col)
    return Image.blend(img, lay, a)


# ---------- сцены ----------
def s01(t, L, cue):
    v = V(world(lights=False, dug=1.0, cont=True), (1060, GR + 230, 1.6))
    chibi(v.d, "me", 1130, PIT_FLOOR - 40 * ease(t / L), 1.0, t, "shock", 1, arm="up")
    img = v.out()
    hud(img, 325)
    return choice_banner(img, t, full=L + .6)


def s02(t, L, cue):
    k = ease(t / (L * .55))
    v = V(world(lights=False, dug=1.0, cont=True), (1060, GR + 200, 1.6), (1060, GR - 40, 1.6), t / (L * .7))
    y = PIT_FLOOR - (PIT_FLOOR - GR + 4) * k
    x = 1138 if k < 1 else 1138 + 80 * ease((t - L * .55) / (L * .3))
    chibi(v.d, "me", x, y, 1.0, t, "shock", 1, arm="up" if k < 1 else None, walk=k >= 1)
    from flatworld import shovel
    shovel(v.d, 900, PIT_FLOOR)   # лопата осталась внизу
    img = v.out()
    if t > L * .5:
        pill(img, "4 секунды", W / 2, 260, (140, 30, 30), WHITE, 32)
    hud(img, 325)
    return choice_banner(img, t + 10)


def knock_marks(v, t, n_hits, wx=PIT_X1, wy=GR + 250):
    d = v.d
    rnd = random.Random(3)
    for i in range(n_hits):
        a = rnd.uniform(-1.2, 1.2)
        d.line([wx, wy, wx + 60 * math.cos(a) * (1 + i * .2), wy + 60 * math.sin(a) * (1 + i * .2)], fill=(14, 12, 12), width=4)


def s03(t, L, cue):
    beats = [cue["03"] + k * .8 for k in range(int(dur("03.mp3") / .8) + 1)]
    hit = any(0 <= t - b < .12 for b in beats)
    v = V(world(lights=False, dug=1.0, cont=True), (1120, GR + 120, 1.5))
    knock_marks(v, t, 4)
    chibi(v.d, "me", 1230, GR - 4, 1.0, t, "shock", -1)
    img = v.out()
    if hit:
        pill(img, "ТУК", W / 2 + 120, 640, (20, 22, 30), YEL, 40)
    hud(img, 325)
    return shake(img, t, 4 if hit else 0)


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    dawn = p > .6
    v = V(world(day=dawn, lights=False, dug=1.0, cont=True, nb="hidden"), (1180, 820, 1.7))
    chibi(v.d, "me", 1165, GR - 4, .9, t, "neutral" if not dawn else "sad", 1)
    img = v.out()
    pill(img, "05:00" if dawn else "02:40", W / 2, 200, (20, 22, 30), WHITE, 36)
    if dawn:
        pill(img, "стук прекратился", W / 2, 280, (30, 60, 110), WHITE, 24)
    hud(img, 325 if not dawn else 324)
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = V(world(day=True, lights=False, dug=1.0, cont=True, nb="hidden"), (1180, 860, 1.5)).out()
    rows = []
    if p > .45:
        rows.append(("1. СМОТРИ", "👁" if False else "", 1.0, BLUE))
    if p > .8:
        rows.append(("2. ПОТОМ КОПАЙ", "", 1.0, YEL))
    dark_card(img, "ПРАВИЛО №2", rows, 200, fade_in(t, .05))
    hud(img, 324)
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="hidden"), (1120, 830, 1.6), (1300, 830, 1.6), t / (L * .7))
    x = 1150 + 60 * ease(t / (L * .6))
    chibi(v.d, "me", x, GR - 4, 1.0, t, "shock" if p > .5 else "neutral", 1, walk=t < L * .6)
    img = v.out()
    if p > .45:
        sx, sy = v.screen(1296, GR - 96)
        pill(img, "≈ 20 м³", sx, sy - 90, (140, 30, 30), WHITE, 30, anchor=(sx, sy))
    hud(img, 324)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="hidden"), (1380, 840, 1.7))
    chibi(v.d, "neigh", 1340, GR - 4, 1.0, t, "neutral", -1)
    chibi(v.d, "me", 1180, GR - 4, .95, t, "neutral", 1)
    img = v.out()
    sx, sy = v.screen(1340, GR - 150)
    pill(img, "СОСЕД", sx, sy - 60, (20, 22, 30), YEL, 28)
    if p > .7:
        bubble(img, "зачем?", sx, sy - 80 if False else sy + 20)
    hud(img, 324)
    return img


def s08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="hidden"), (1460, 830, 1.9))
    bags = min(12, int(max(0, p - .45) / .4 * 12) + (1 if p > .45 else 0))
    car(v.d, 1480, trunk=True, bags=12 if p > .45 else 0)
    img = v.out()
    if p > .62:
        pill(img, f"цемент × {min(12, bags)}", W / 2, 260, (20, 22, 30), YEL, 32)
    hud(img, 324)
    return img


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    reveal = p > .55
    if p < .3:   # машина уезжает
        v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="hidden"), (1400, 840, 1.6))
        car(v.d, 1480 + 500 * ease(p / .3))
    else:
        v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="open" if reveal else "hidden"),
              (1400, 840, 1.6), (1480, GR + 200, 1.5), (p - .5) / .5)
        x = 1200 + 140 * ease((p - .3) / .25)
        chibi(v.d, "me", x, GR - 4 - (40 * math.sin(min(1, (p - .3) / .25) * math.pi) if p < .55 else 0), 1.0, t, "shock" if reveal else "tense", 1)
    img = v.out()
    if reveal:
        pill(img, "глубже моей", W / 2, 240, (140, 30, 30), WHITE, 30)
    hud(img, 324)
    return img


def scratched(v, t, k=1.0):
    """число 365, выцарапанное на глиняной стене ямы соседа"""
    d = v.d
    x0, y0 = NB_PIT_WALL + 26, GR + 160
    segs = {"3": [((0, 0), (30, 0)), ((30, 0), (10, 26)), ((10, 26), (32, 44)), ((32, 44), (0, 60))],
            "6": [((30, 0), (4, 24)), ((4, 24), (4, 58)), ((4, 58), (30, 58)), ((30, 58), (30, 34)), ((30, 34), (4, 34))],
            "5": [((32, 0), (2, 0)), ((2, 0), (2, 26)), ((2, 26), (30, 30)), ((30, 30), (30, 56)), ((30, 56), (0, 60))]}
    n = 0
    total = sum(len(segs[c]) for c in "365")
    for i, c in enumerate("365"):
        for (a, b) in segs[c]:
            n += 1
            if n / total > k:
                return
            d.line([(x0 + i * 46 + a[0], y0 + a[1]), (x0 + i * 46 + b[0], y0 + b[1])], fill=(18, 14, 12), width=6)
            d.line([(x0 + i * 46 + a[0] + 2, y0 + a[1] + 3), (x0 + i * 46 + b[0] + 2, y0 + b[1] + 3)], fill=(120, 96, 80), width=2)


def s10(t, L, cue):
    p = (t - cue["10"]) / dur("10.mp3")
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="open"), (1470, GR + 220, 1.6), (1450, GR + 200, 2.0), t / L)
    chibi(v.d, "me", 1500, GR + 476, 1.0, t, "shock", -1)
    v.beam([(1480, GR + 360), (NB_PIT_WALL + 10, GR + 120), (NB_PIT_WALL + 10, GR + 260)], (255, 236, 190), 90, 8)
    scratched(v, t, min(1, max(0, (p - .5) / .35)))
    img = v.out()
    hud(img, 324)
    return img


def s11(t, L, cue):
    v = V(world(day=True, lights=False, dug=1.0, cont=True, nb="open"), (1450, GR + 200, 2.0))
    scratched(v, t, 1.0)
    img = v.out()
    E1.sms_card(img, ["Через 365 дней — конец."], 180, fade_in(t, .1), "у соседа тоже?")
    hud(img, 324)
    return img


def s12(t, L, cue):
    img = Image.new("RGB", (W, H), (8, 8, 12))
    d = ImageDraw.Draw(img)
    f1, f2 = F(44, FONT_SUB), F(76, FONT_SUB)
    pop = 1 + .05 * math.sin(t * 8)
    f2 = F(int(76 * pop), FONT_SUB)
    d.text(((W - f1.getlength("365 ДНЕЙ")) / 2, 470), "365 ДНЕЙ", font=f1, fill=RED)
    f3 = F(int(54 * pop), FONT_SUB)
    d.text(((W - f3.getlength("3 СЕРИЯ — ЗАВТРА")) / 2, 540), "3 СЕРИЯ — ЗАВТРА", font=f3, fill=WHITE)
    return img


if __name__ == "__main__":
    s3 = span("s03")[0] + .05
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=[s3 + k * .8 for k in range(int(dur("03.mp3") / .8) + 1)],
        hits=[span("s01")[0] + .1, span("s09")[0] + span("s09")[1] * .55, span("s10")[0] + span("s10")[1] * .8])
