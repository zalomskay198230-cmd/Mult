"""ГЛУБИНА 40. Серия 3 (финал). Гибрид: 3D-фоны станции (g1_*) + 2D-герои + рисованная поверхность.
Запуск: python3 seriya03.py ../tts/s03 ../seriya03.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
TTS3 = sys.argv[1] if len(sys.argv) > 1 else "../tts/s03"
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib
toonlib.TTS = os.path.join(HERE, "..", "tts", "s01")
import seriya01 as G
_argv = sys.argv[:]
sys.argv[1:2] = [os.path.join(HERE, "..", "tts", "s02")]
import importlib.util
_sp = importlib.util.spec_from_file_location("glubina_s02", os.path.join(HERE, "seriya02.py"))
G2 = importlib.util.module_from_spec(_sp)   # Костя, люк, монитор (по пути: в sys.path есть другой seriya02)
_sp.loader.exec_module(G2)
sys.argv[:] = _argv
toonlib.TTS = TTS3
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter
import denis_rig as DR

LINES = {
    "01": "Голос в рации был мой. Слово в слово. Но я молчал. Рация висела у меня на поясе.",
    "02": "Костя у иллюминатора встал. Впервые за ночь. Суставы щёлкали, как лёд.",
    "03m": "Олег. Открой люк.",
    "04": "Он говорил моим голосом. И улыбался. Не моргая.",
    "05": "Правило третье: верь приборам. Монитор показал: пульс — ноль. А он шёл ко мне.",
    "06": "Воздуха — на два часа. Подъём — сорок минут. Я прыгнул в шлюз и задраил дверь.",
    "07": "Удар. Второй. Третий. Металл прогнулся. Я открыл внешний люк и ушёл в воду.",
    "08": "Правило первое: не торопись наверх. Девять метров — стоп. Шесть — стоп. Три — стоп.",
    "09": "Снизу, из темноты, за мной поднимались пузыри. Я не обернулся. Ни разу.",
    "10": "Наверху был рассвет. И спасательный катер. Меня втащили на борт.",
    "11": "Капитан сказал: Костю нашли позавчера. На поверхности. Он утонул в первый же день.",
    "12": "Мне дали рацию: скажи вниз, вдруг там кто-то остался. Я нажал кнопку. И сказал:",
    "13": "Олег, не открывай люк. Это не Костя.",
    "14r": "Поздно. Я уже открыл.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[2] = ("s03m", [("03m", 0.3)], 0.6)
PLAN[-2] = ("s13", [("13", 0.1)], 1.0)
PLAN[-1] = ("s14r", [("14r", 0.3)], 4.4)
setup(LINES, PLAN)

GY, F, ORANGE, CYAN, RED_T = G.GY, G.F, G.ORANGE, G.CYAN, G.RED_T
kostya, oleg, medscreen, hatch_open = G2.kostya, G2.oleg, G2.medscreen, G2.hatch_open
DAWN_T = (1.05, .9, .82)


def dplate(img, depth, air):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([430, 26, 700, 104], radius=14, fill=(10, 16, 26), outline=(60, 90, 120), width=2)
    d.text((446, 32), "ГЛУБИНА", font=F(18), fill=(130, 160, 190))
    d.text((446, 54), depth, font=F(36, FONT_SUB), fill=CYAN)
    d.text((580, 32), "ВОЗДУХ", font=F(18), fill=(130, 160, 190))
    d.text((580, 54), air, font=F(36, FONT_SUB), fill=ORANGE)


def porthole(img, cx=470, cy=470, R=150):
    ImageDraw.Draw(img).ellipse([cx - R, cy - R, cx + R, cy + R], fill=(4, 16, 30), outline=(140, 146, 152), width=26)


def dawn(t):
    """рисованная поверхность моря на рассвете"""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    hz = 640
    for y in range(hz):
        k = y / hz
        d.line([0, y, W, y], fill=(int(70 + 180 * k), int(60 + 110 * k), int(110 + 20 * k)))
    glow(img, (W * .62, hz - 10), 260, (255, 170, 80), .9)
    d = ImageDraw.Draw(img)
    d.ellipse([W * .62 - 60, hz - 70, W * .62 + 60, hz + 50], fill=(255, 214, 140))
    for y in range(hz, H):
        k = (y - hz) / (H - hz)
        d.line([0, y, W, y], fill=(int(60 - 40 * k), int(70 - 40 * k), int(100 - 40 * k)))
    rnd = random.Random(3)
    for _ in range(70):   # блики на волнах
        y = rnd.uniform(hz + 8, H)
        x = (rnd.uniform(0, W) + 20 * math.sin(t * 1.3 + y * .02)) % W
        w = 10 + (y - hz) * .06
        d.line([x - w, y, x + w, y], fill=(250, 190, 120) if abs(x - W * .62) < 120 + (y - hz) * .2 else (90, 104, 140), width=3)
    return img


def boat(img, t, y=1080):
    d = ImageDraw.Draw(img)
    bob = 8 * math.sin(t * 1.4)
    y += bob
    d.polygon([(-20, y - 60), (W + 20, y - 60), (W - 40, y + 140), (40, y + 140)], fill=(214, 92, 40), outline=INK)
    d.rectangle([-20, y - 74, W + 20, y - 54], fill=(240, 240, 236), outline=INK)
    d.text((80, y + 10), "СПАСАТЕЛЬ-7", font=F(40, FONT_SUB), fill=(250, 240, 230))
    return img


# ---------- сцены ----------
def s01(t, L, cue):
    img = G.bg("s03", t, 1.3)
    img = oleg(img, W / 2, 1.5, t, ("down", "down"), "shock", (0, 0), ground=1900)
    p = (t - cue["01"]) / dur("01.mp3")
    if p > .55:
        G.tag(img, "рация", "на поясе · выключена", 1080)
    dplate(img, "40 м", "2:40")
    img = zoom(img, 1.0 + .06 * t / L, .5, .4)
    return choice_banner(img, t)


def choice_banner(img, t, full=2.8):
    """вставка: финал выбрали зрители — крупно в начале, потом маленькой плашкой"""
    if t >= full:
        G.tag(img, "ВЫБОР ЗРИТЕЛЕЙ", "слушать Олега", 130)
        return img
    a = min(1, t / .25, (full - t) / .3)
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 380, W, 780], fill=(8, 10, 14))
    d.rectangle([0, 380, W, 388], fill=ORANGE)
    d.rectangle([0, 772, W, 780], fill=ORANGE)
    f1, f2, f3 = F(40, FONT_SUB), F(76, FONT_SUB), F(30)
    for txt, f, y, col in (("ВЫ ВЫБРАЛИ", f1, 420, (200, 200, 206)), ("СЛУШАТЬ", f2, 490, ORANGE),
                           ("ОЛЕГА", f2, 580, ORANGE), ("финал по вашему голосованию", f3, 700, (170, 170, 176))):
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)
    return Image.blend(img, lay, a)


def s02(t, L, cue):
    img = G.bg("s03", t, 1.2)
    porthole(img)
    k = min(1, t / 2.5)
    rise = (1 - k) * 160
    img = kostya(img, 300 + 60 * k, .86, t, ("down", "down"), "neutral", (1 - 1.2 * k, -.4 + .4 * k), ground=GY + rise, blink=False)
    if int(t * 6) % 3 == 0 and t < 3:
        img = shake(img, t, 3)
    dplate(img, "40 м", "2:30")
    return img


def s03m(t, L, cue):
    img = G.bg("s03", t, 1.0)
    img = kostya(img, W / 2, 2.1, t, ("down", "down"), "smile", (0, 0), ground=2500, blink=False)
    G.tag(img, "голос", "мой", 150)
    return zoom(img, 1.0 + .12 * t / L, .5, .35)


def s04(t, L, cue):
    img = G.bg("s03", t, 1.0)
    img = kostya(img, W / 2, 1.6, t, ("down", "down"), "smile", (0, 0), ground=1980, blink=False)
    if int(t * 2) % 2:
        glow(img, (W / 2, 300), 300, (120, 0, 0), .5)
    return zoom(img, 1.0 + .08 * t / L, .5, .35)


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    if p < .62:
        img = G.bg("s03", t, 1.0).filter(ImageFilter.GaussianBlur(6))
        medscreen(img, t, 1.0)
        d = ImageDraw.Draw(img)
        if p > .3:   # линия падает в ноль
            d.rectangle([140, 320, 580, 560], fill=(10, 16, 14))
            d.line([140, 470, 580, 470], fill=(255, 90, 90), width=4)
            d.rectangle([140, 602, 340, 700], fill=(10, 16, 14))
            d.text((150, 600), "0", font=F(80, FONT_SUB), fill=(255, 90, 90))
    else:
        img = G.bg("s03", t, 1.1)
        k = min(1, (p - .62) / .38)
        img = kostya(img, W / 2, .8 + .9 * k, t, ("out", "out"), "smile", (0, 0), ground=GY + 700 * k, blink=False)
    dplate(img, "40 м", "2:10")
    return img


def s06(t, L, cue):
    img = G.bg("s13", t, 1.25)
    img = oleg(img, 360, .9, t, ("fist_up", "down"), "tense", (-.6, 0))
    p = (t - cue["06"]) / dur("06.mp3")
    dplate(img, "40 м", "2:00")
    if p > .8:
        G.tag(img, "дверь", "задраена", 1080)
        img = shake(img, t, 6 if p < .9 else 0)
    return img


def s07(t, L, cue):
    img = G.bg("s13", t, 1.15)
    d = ImageDraw.Draw(img)
    p = (t - cue["07"]) / dur("07.mp3")
    hits = sum(p > q for q in (.0, .12, .24))
    for k in range(hits):   # вмятины изнутри станции
        x, y = 200 + k * 150, 380 + (k % 2) * 120
        d.ellipse([x - 50, y - 40, x + 50, y + 40], fill=(70, 66, 64), outline=(30, 30, 30), width=4)
        d.line([x - 30, y, x + 30, y], fill=(20, 20, 20), width=3)
    if p > .62:
        hatch_open(img, t)
        img = G.water(img, t, min(1, (p - .62) * 4))
    img = oleg(img, 520, .8, t, ("out", "down"), "shock", (-.8, 0))
    dplate(img, "40 м", "1:55")
    sh = any(abs(p - q) < .04 for q in (.0, .12, .24))
    return shake(img, t, 10 if sh else 0)


def diver(img, x, y, s, t, tint=(.5, .7, .9)):
    DR.use("oleg", hoodie=False, suit=True)
    fig = DR.front((W, H), x, y, s, t, ("fist_up", "fist_up"), "idle", "tense", (0, -1))
    img = G.char(img, fig, tint)
    d = ImageDraw.Draw(img)
    for i in range(8):   # пузыри от регулятора
        ph = (t * .9 + i / 8) % 1
        bx, by = x + 20 + 14 * math.sin(i * 2 + t), y - 900 * s - ph * 500
        d.ellipse([bx - 6, by - 6, bx + 6, by + 6], outline=(190, 230, 250), width=2)
    return img


def s08(t, L, cue):
    k = min(1, t / L)
    img = G.bg("s01", max(0, 88 - k * 88) / 12, 1.0)   # спуск камеры задом наперёд = подъём
    img = G.water(img, t, .9)
    img = diver(img, W / 2, 1150, .55, t)
    p = (t - cue["08"]) / dur("08.mp3")
    depth = 40 if p < .3 else 9 if p < .55 else 6 if p < .8 else 3
    dplate(img, f"{depth} м", "1:20" if depth > 9 else "0:50")
    if p > .3:
        G.tag(img, "СТОП", f"{depth} метров · ждать", 1080)
    return img


def s09(t, L, cue):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(30 * (1 - k)), int(80 * (1 - k)), int(120 * (1 - k) + 6)))
    img = G.water(img, t, .5)
    d = ImageDraw.Draw(img)
    rnd = random.Random(9)
    for i in range(40):   # пузыри снизу
        ph = (t * .25 + rnd.random()) % 1
        x = 140 + rnd.uniform(-60, 380)
        y = H - ph * H * .9
        r = rnd.uniform(4, 12)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(150, 200, 230), width=2)
    p = (t - cue["09"]) / dur("09.mp3")
    if p > .2:   # что-то в глубине
        a = min(1, (p - .2) * 3)
        for ex in (-34, 34):
            glow(img, (W / 2 + ex, 1170), 40, (200, 240, 255), .5 * a)
            ImageDraw.Draw(img).ellipse([W / 2 + ex - 8, 1162, W / 2 + ex + 8, 1178], fill=(int(220 * a), int(240 * a), int(250 * a)))
    img = diver(img, W / 2, 620, .4, t)
    dplate(img, "3 м", "0:30")
    return img


def s10(t, L, cue):
    img = dawn(t)
    img = boat(img, t, 1120)
    DR.use("kapitan", hoodie=False, suit=False)
    img = G.char(img, DR.front((W, H), 520, 1060, .7, t, ("out", "down"), "idle", "neutral", (-.6, 0)), DAWN_T)
    DR.use("oleg", hoodie=False, suit=True)
    img = G.char(img, DR.front((W, H), 220, 1060, .7, t, ("down", "down"), "idle", "worried", (.5, -.3)), DAWN_T)
    G.tag(img, "05:52", "поверхность", 150)
    return img


def s11(t, L, cue):
    img = dawn(t)
    img = boat(img, t, 1500)
    DR.use("kapitan", hoodie=False, suit=False)
    img = G.char(img, DR.front((W, H), W / 2, 1900, 1.4, t, ("down", "down"), "idle", "sad", (0, 0)), DAWN_T)
    p = (t - cue["11"]) / dur("11.mp3")
    if p > .35:
        G.tag(img, "КОСТЯ", "найден позавчера · утонул в 1-й день", 1080)
    return img


def s12(t, L, cue):
    img = dawn(t)
    img = boat(img, t, 1500)
    DR.use("oleg", hoodie=False, suit=True)
    img = G.char(img, DR.front((W, H), W / 2, 1900, 1.4, t, ("phone", "down"), "idle", "worried", (0, .3)), DAWN_T)
    return zoom(img, 1.0 + .06 * t / L, .5, .5)


def s13(t, L, cue):
    img = dawn(t).filter(ImageFilter.GaussianBlur(6))
    vo = cue["13"] <= t <= cue["13"] + dur("13.mp3")
    G.radio(img, t, 1.0 if vo else .05, "ВНИЗ · СТАНЦИЯ «НЕРПА»")
    G.tag(img, "ПЕРЕДАЧА", "это я сказал той ночью", 1080)
    return img


def s14r(t, L, cue):
    vo_end = cue["14r"] + dur("14r.mp3")
    img = dawn(t).filter(ImageFilter.GaussianBlur(6))
    G.radio(img, t, 1.0 if cue["14r"] <= t < vo_end else (.15 if t < cue["14r"] else 0), "СТАНЦИЯ «НЕРПА» · 40 м")
    img = shake(img, t, 5 if vo_end - .4 < t < vo_end + .2 else 0)
    if t > vo_end + .7:
        a = min(1, (t - vo_end - .7) / .5)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(40, FONT_SUB), F(80, FONT_SUB), F(30, FONT_SUB)
            dd.text(((W - f1.getlength("ГЛУБИНА 40")) / 2, 460), "ГЛУБИНА 40", font=f1, fill=(240, 240, 244))
            dd.text(((W - f2.getlength("КОНЕЦ")) / 2, 520), "КОНЕЦ", font=f2, fill=ORANGE)
            if t > vo_end + 1.6:
                q = "а ты бы открыл люк?"
                dd.text(((W - f3.getlength(q)) / 2, 650), q, font=f3, fill=(200, 200, 206))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .05, span("s03m")[0] + .2, span("s06")[0] + span("s06")[1] * .8,
              span("s07")[0] + .05, span("s14r")[0] + .3])
