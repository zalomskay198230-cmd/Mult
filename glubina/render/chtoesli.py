"""ГЛУБИНА 40. «Что если…» — альтернативный финал: Олег послушал Костю.
Запуск: python3 chtoesli.py ../tts/chtoesli ../chtoesli.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/chtoesli"
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib
toonlib.TTS = os.path.join(HERE, "..", "tts", "s01")
import seriya01 as G


def _load(name, file, tts):
    argv = sys.argv[:]
    sys.argv[1:2] = [os.path.join(HERE, "..", "tts", tts)]
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    sys.argv[:] = argv
    return m


G2 = _load("glubina_s02", "seriya02.py", "s02")   # Костя, люк, монитор
G3 = _load("glubina_s03", "seriya03.py", "s03")   # рассвет, плашка глубины, водолаз
toonlib.TTS = TTS
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter
import denis_rig as DR

LINES = {
    "01": "А что, если бы я послушал Костю? Я поверил ему. Люк остался закрытым. А рация не замолкала.",
    "02r": "Олег, поднимайся. Открой люк. Олег…",
    "03": "Правило третье: верь приборам. Пульс двадцать, восемь градусов — это не смерть. Это холод.",
    "04": "В ледяной воде сердце замедляется, чтобы выжить. Костя не умер. Он замёрз.",
    "05": "Я укутал его в одеяла. Через час пульс — шестьдесят. И он заговорил.",
    "06k": "Оно вошло со мной. Вторые следы — его. Оно повторяет голоса.",
    "07": "И тут погас свет. Из тёмного коридора позвал голос. Голос Кости.",
    "08m": "Олег, помоги. Я здесь.",
    "09": "А настоящий Костя сидел рядом. И держал меня за руку.",
    "10": "Монитор пищал: пульс шестьдесят — это он. Значит, в коридоре — оно.",
    "11": "Мы заманили голос в шлюз. Я задраил дверь и открыл внешний люк. Сорок метров воды ударили внутрь.",
    "12": "Через двое суток к станции пристыковался спасательный колокол. Мы поднялись. Оба.",
    "13": "Только теперь по ночам береговая рация ловит канал «Нерпы». И мой голос просит: открой люк.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[1] = ("s02r", [("02r", 0.2)], 0.4)
PLAN[7] = ("s08m", [("08m", 0.3)], 0.6)
PLAN[-1] = ("s13", [("13", 0.1)], 4.2)
setup(LINES, PLAN)

GY, F, ORANGE, CYAN, RED_T = G.GY, G.F, G.ORANGE, G.CYAN, G.RED_T
kostya, oleg, medscreen = G2.kostya, G2.oleg, G2.medscreen
dplate, porthole, dawn = G3.dplate, G3.porthole, G3.dawn
WARM_T = (1.0, .78, .66)


def blanket(img, x, s, ground=GY):
    d = ImageDraw.Draw(img)
    P = lambda lx, ly: (x + lx * s, ground - 962 * s + ly * s)
    d.polygon([P(-150, 200), P(-60, 170), P(60, 170), P(150, 200), P(170, 560), P(-170, 560)], fill=(150, 120, 90), outline=INK)
    for k in range(4):
        d.line([P(-150 + k * 10, 260 + k * 80), P(150 - k * 10, 260 + k * 80)], fill=(120, 92, 70), width=max(2, int(8 * s)))


def dark(img, k=.25, beam=None):
    img = Image.blend(img, Image.new("RGB", (W, H), (2, 4, 8)), 1 - k)
    if beam:
        m = Image.new("L", (W, H), 0)
        x0, y0, x1, y1 = beam
        ImageDraw.Draw(m).polygon([(x0, y0), (x1 - 160, y1), (x1 + 160, y1)], fill=90)
        img.paste(Image.new("RGB", (W, H), (240, 230, 190)), (0, 0), m.filter(ImageFilter.GaussianBlur(30)))
    return img


def what_if(img, t, full=3.2):
    """вставка «ЧТО ЕСЛИ…» в начале, потом маленькая метка"""
    if t >= full:
        G.tag(img, "ЧТО ЕСЛИ…", "Олег послушал Костю", 130)
        return img
    a = min(1, t / .25, (full - t) / .3)
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 380, W, 780], fill=(8, 10, 14))
    d.rectangle([0, 380, W, 388], fill=CYAN)
    d.rectangle([0, 772, W, 780], fill=CYAN)
    f1, f2, f3 = F(40, FONT_SUB), F(84, FONT_SUB), F(30)
    for txt, f, y, col in (("ГЛУБИНА 40", f1, 420, (200, 200, 206)), ("ЧТО ЕСЛИ…", f2, 490, CYAN),
                           ("Олег послушал Костю?", F(46, FONT_SUB), 600, ORANGE), ("другой финал", f3, 700, (170, 170, 176))):
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)
    return Image.blend(img, lay, a)


# ---------- сцены ----------
def s01(t, L, cue):
    img = G.bg("s03", t, 1.3)
    img = oleg(img, 200, .84, t, ("down", "down"), "tense", (.8, 0))
    img = kostya(img, 480, .84, t, ("down", "down"), "neutral", (-.4, .2), blink=False)
    dplate(img, "40 м", "2:40")
    return what_if(img, t)


def s02r(t, L, cue):
    img = G.bg("s03", t, 1.1).filter(ImageFilter.GaussianBlur(6))
    vo = cue["02r"] <= t <= cue["02r"] + dur("02r.mp3")
    G.radio(img, t, 1.0 if vo else .1, "ПОВЕРХНОСТЬ · ГОЛОС ОЛЕГА")
    return img


def s03(t, L, cue):
    img = G.blueprint("ПРАВИЛО №3")
    d = ImageDraw.Draw(img)
    p = (t - cue["03"]) / dur("03.mp3")
    f = F(110, FONT_SUB)
    d.text((W / 2 - f.getlength("20 уд/мин") / 2, 360), "20 уд/мин", font=f, fill=ORANGE)
    d.text((W / 2 - f.getlength("8°") / 2, 520), "8°", font=f, fill=CYAN)
    if p > .62:
        f2 = F(64, FONT_SUB)
        d.text((W / 2 - f2.getlength("≠ смерть") / 2, 740), "≠ смерть", font=f2, fill=(255, 110, 100))
    if p > .85:
        f2 = F(64, FONT_SUB)
        d.text((W / 2 - f2.getlength("= холод") / 2, 840), "= холод", font=f2, fill=CYAN)
    return img


def s04(t, L, cue):
    img = G.blueprint("ЛЕДЯНАЯ ВОДА")
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 620
    beat = 1 + .08 * max(0, math.sin(t * 2.2)) ** 8   # редкие удары
    r = 150 * beat
    d.polygon([(cx, cy + r), (cx - r, cy - r * .2), (cx - r * .5, cy - r * .8), (cx, cy - r * .4),
               (cx + r * .5, cy - r * .8), (cx + r, cy - r * .2)], outline=(255, 110, 100), width=8)
    for k in range(10):   # снежинки-кристаллы
        a = k * .63 + t * .2
        x, y = cx + 260 * math.cos(a), cy + 300 * math.sin(a)
        for j in range(3):
            b = j * math.pi / 3
            d.line([x - 14 * math.cos(b), y - 14 * math.sin(b), x + 14 * math.cos(b), y + 14 * math.sin(b)], fill=CYAN, width=3)
    p = (t - cue["04"]) / dur("04.mp3")
    if p > .55:
        f = F(54, FONT_SUB)
        d.text((W / 2 - f.getlength("ЖИВ") / 2, 1000), "ЖИВ", font=f, fill=CYAN)
    return img


def s05(t, L, cue):
    img = G.bg("s03", t, 1.4)
    img = kostya(img, W / 2, 1.1, t, ("down", "down"), "neutral", (0, .2), ground=1500, tint=WARM_T)
    blanket(img, W / 2, 1.1, 1500)
    p = (t - cue["05"]) / dur("05.mp3")
    G.tag(img, "пульс", "20" if p < .45 else "60", 1080)
    G.clock(img, "02:10" if p < .45 else "03:10")
    return img


def s06k(t, L, cue):
    img = G.bg("s03", t, 1.3)
    img = kostya(img, W / 2, 1.6, t, ("down", "down"), "worried", (0, 0), ground=1980, tint=WARM_T)
    blanket(img, W / 2, 1.6, 1980)
    G.tag(img, "КОСТЯ", "живой", 150)
    return zoom(img, 1.0 + .08 * t / L, .5, .35)


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    img = G.bg("s03", t, 1.2)
    img = oleg(img, 200, .84, t, ("down", "down"), "shock", (1, 0))
    img = kostya(img, 420, .84, t, ("down", "down"), "worried", (1, 0), tint=WARM_T)
    blanket(img, 420, .84)
    if p > .18:
        img = dark(img, .22, beam=(220, 640, 660, 900))
        img = shake(img, t, 4 if p < .25 else 0)
    return img


def s08m(t, L, cue):
    img = dark(G.bg("s03", t, 1.0), .12)
    d = ImageDraw.Draw(img)
    vo = cue["08m"] <= t <= cue["08m"] + dur("08m.mp3")
    for ex in (-26, 26):   # что-то в конце коридора
        if vo or int(t * 5) % 4:
            d.ellipse([W / 2 + ex - 7, 640, W / 2 + ex + 7, 654], fill=(210, 230, 240))
    G.tag(img, "голос из коридора", "как у Кости", 150)
    return zoom(img, 1.0 + .1 * t / L, .5, .45)


def s09(t, L, cue):
    img = dark(G.bg("s03", t, 1.3), .45)
    img = oleg(img, 250, 1.3, t, ("out", "down"), "worried", (1, 0), ground=1850)
    img = kostya(img, 520, 1.3, t, ("out", "down"), "worried", (-1, 0), ground=1850, tint=WARM_T)
    blanket(img, 520, 1.3, 1850)
    return img


def s10(t, L, cue):
    img = dark(G.bg("s03", t, 1.0), .35).filter(ImageFilter.GaussianBlur(5))
    medscreen(img, t * 3, 1.0)
    d = ImageDraw.Draw(img)
    d.rectangle([140, 602, 340, 700], fill=(10, 16, 14))
    d.text((150, 600), "60", font=F(80, FONT_SUB), fill=(80, 255, 140))
    d.rectangle([370, 602, 590, 700], fill=(10, 16, 14))
    d.text((380, 600), "34°", font=F(80, FONT_SUB), fill=(80, 255, 140))
    p = (t - cue["10"]) / dur("10.mp3")
    if p > .5:
        G.tag(img, "КОСТЯ — ЗДЕСЬ", "в коридоре — оно", 1080)
    return img


def s11(t, L, cue):
    p = (t - cue["11"]) / dur("11.mp3")
    img = G.bg("s13", t, 1.25)
    if p > .45:
        G2.hatch_open(img, t)
        img = G.water(img, t, min(1, (p - .45) * 3))
        d = ImageDraw.Draw(img)
        rnd = random.Random(int(t * 10))
        for _ in range(60):   # поток воды
            x, y = rnd.uniform(160, 580), rnd.uniform(400, 1300)
            d.line([x, y, x + rnd.uniform(-20, 20), y + 60], fill=(170, 210, 240), width=3)
    else:
        img = dark(img, .5)
        G.tag(img, "дверь", "задраена · внутри — оно", 1080)
    dplate(img, "40 м", "1:40")
    return shake(img, t, 9 if .45 < p < .62 else 0)


def s12(t, L, cue):
    k = min(1, t / L)
    img = G.bg("s01", max(0, 88 - k * 88) / 12, 1.0)
    img = G.water(img, t, .9)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 520 - 80 * k   # спасательный колокол
    d.ellipse([cx - 150, cy - 170, cx + 150, cy + 110], fill=(230, 200, 60), outline=INK, width=6)
    d.rectangle([cx - 150, cy - 10, cx + 150, cy + 110], fill=(230, 200, 60), outline=INK, width=6)
    for k2 in (-70, 70):
        d.ellipse([cx + k2 - 34, cy - 70, cx + k2 + 34, cy - 2], fill=(200, 240, 255), outline=INK, width=4)
    d.line([cx, cy - 170, cx, -10], fill=(40, 40, 40), width=6)
    G.tag(img, "+2 суток", "поднялись оба", 1080)
    return img


def s13(t, L, cue):
    vo_end = cue["13"] + dur("13.mp3")
    img = dark(dawn(t), .35).filter(ImageFilter.GaussianBlur(6))
    G.radio(img, t, 1.0 if t > cue["13"] + dur("13.mp3") * .6 and t < vo_end + .4 else .1, "КАНАЛ «НЕРПЫ» · 03:12")
    if t > vo_end + .9:
        a = min(1, (t - vo_end - .9) / .5)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(40, FONT_SUB), F(80, FONT_SUB), F(30, FONT_SUB)
            dd.text(((W - f1.getlength("ЧТО ЕСЛИ…")) / 2, 460), "ЧТО ЕСЛИ…", font=f1, fill=(240, 240, 244))
            dd.text(((W - f2.getlength("ВЫЖИЛИ ОБА")) / 2, 520), "ВЫЖИЛИ ОБА", font=f2, fill=ORANGE)
            if t > vo_end + 1.8:
                q = "какой финал лучше? 1 или 2"
                dd.text(((W - f3.getlength(q)) / 2, 650), q, font=f3, fill=(200, 200, 206))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(span("s02r")[0], span("s02r")[0] + span("s02r")[1])],
        hits=[span("s07")[0] + .9, span("s08m")[0] + .2, span("s11")[0] + span("s11")[1] * .45, span("s13")[0] + .2])
