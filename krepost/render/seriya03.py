"""«КРЕПОСТЬ». Серия 3 (зрители выбрали «спуститься глянуть», 100%): спуск в колодец → боковой ход → ползём на свет →
живой мужик из бункера под школой, там 20 человек. Выбор: пустить к себе или уйти к ним.
Запуск: python3 seriya03.py ../tts/s03 ../seriya03.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s02"), "x.mp4"]
import seriya02 as S2          # разрез колодца, HUD, плашка «вы выбрали»; тянет и хелперы 1-й серии
sys.argv[:] = _argv
import toonlib
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s03"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya03.mp4"
from toonlib import setup, run, dur, shake, glow, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter
import flatworld as FW
from flatworld import SD, chibi, OUT, world, GR

K = S2.K
W, H, F, B = K.W, K.H, K.F, K.B
YEL, RED, WHITE, GREEN = K.YEL, K.RED, K.WHITE, K.GREEN
pill, V = K.pill, K.V
FLOOR, PX_M, PX0, PX1 = S2.FLOOR, S2.PX_M, S2.PX0, S2.PX1
BOT = FLOOR + 6 * PX_M

FW.CHAR["dig"] = dict(skin=(214, 192, 172), hair=(120, 116, 110), top=(104, 96, 86), pants=(60, 58, 56), shoes=(50, 44, 40), style="long", beard=(130, 124, 116))
FW.CHAR["p1"] = dict(skin=(232, 190, 160), hair=(150, 90, 50), top=(150, 60, 60), pants=(50, 54, 70), shoes=(50, 44, 40), style="bun")
FW.CHAR["p2"] = dict(skin=(200, 150, 120), hair=(30, 30, 34), top=(60, 100, 150), pants=(46, 48, 60), shoes=(40, 40, 44), style="spiky")
FW.CHAR["p3"] = dict(skin=(236, 200, 170), hair=(210, 190, 140), top=(120, 140, 80), pants=(60, 56, 50), shoes=(50, 44, 40), style="long")

LINES = {
    "01": "Под моим гаражом кто-то роет ^ход^. *Шесть* метров подо мной… и оттуда ^стучат^.",
    "02": "Вы выбрали — *спуститься* глянуть.",
    "03": "Фонарик, монтировка, верёвка за пояс. Ну, погнали!",
    "04": "Вода по колено… ледяная. Сбоку — ^дыра^.",
    "05": "Ход. ^Свежий^, б§§§§. Ползу.",
    "06": "Метр… два… Впереди — *свет*. И голос: «Не бей. Я ^живой^».",
    "07": "Мужик. Худой как скелет. Говорит, *две недели* копает — из бункера под *школой*. И их там, с§§а, *двадцать* человек.",
    "08": "Короче… или пускаю их к себе в *гараж*… или сам ухожу к ним в *бункер*. ^Голосуй^ в опросе.",
}
PLAN = [(f"k{k}", [(k, 0.04)], 0.1) for k in LINES]
PLAN[0] = ("k01", [("01", 0.0)], 0.1)
PLAN[-1] = ("k08", [("08", 0.05)], 1.0)
setup(LINES, PLAN)
toonlib.draw_subs = K.draw_caps


def P(cue, key, t):
    return max(0.0, (t - cue[key]) / dur(key + ".mp3"))


def darkness(img, lights, amount=.88):
    """темнота с пятнами света: lights = [(x, y, r)]"""
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    for x, y, r in lights:
        md.ellipse([x - r, y - r, x + r, y + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(60))
    dark = img.point(lambda v: int(v * (1 - amount)))
    dark.paste(img, (0, 0), m)
    return dark


def beam(img, x, y, ang, length=420, spread=.35):
    lay = Image.new("RGB", (W, H))
    ImageDraw.Draw(lay).polygon([(x, y), (x + length * math.cos(ang - spread), y + length * math.sin(ang - spread)),
                                 (x + length * math.cos(ang + spread), y + length * math.sin(ang + spread))], fill=(120, 110, 70))
    from PIL import ImageChops
    return ImageChops.add(img, lay.filter(ImageFilter.GaussianBlur(24)))


# ---------- сцены ----------
def k01(t, L, cue):   # стоит над колодцем, снизу стучат
    p = P(cue, "01", t)
    img = S2.section(t, 6, water=1, face="shock" if p > .85 else "neutral", dig=False, hero_y=FLOOR, knock=.6 if p > .85 else 0)
    img = S2.cam(img, 640, 1.0)
    img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 12)), .25)
    if p > .85:
        K.B.M.big(img, "ТУК", 560, RED, 110)
    pill(img, "6 МЕТРОВ ПОДО МНОЙ", W / 2, 190, (20, 22, 30), YEL, 30)
    S2.hud(img, "есть", 6)
    return shake(img, t, 8 if .86 < p < .93 else 0)


def k02(t, L, cue):
    bg = S2.section(t, 6, water=1, face="angry", dig=False, hero_y=FLOOR, ladder=True)
    img = Image.blend(S2.cam(bg, 640), Image.new("RGB", (W, H)), .35)
    img = S2.choice_banner(img, t, "СПУСТИТЬСЯ", L - .05, sub="100% голосов в опросе")
    S2.hud(img, "есть", 6)
    return img


def k03(t, L, cue):   # снаряжение → спуск по лестнице
    p = P(cue, "03", t)
    if p < .62:
        img = Image.new("RGB", (W * 2, H * 2))
        d = SD(img, 0, 0, 2)
        d.rectangle([0, 0, W, H], fill=(54, 56, 64))
        chibi(d, "hero", 330, 1540, 6.0, t, "angry", 1, arm="phone")
        d.line([60, 1060, 260, 900], fill=(90, 90, 100), width=16)       # монтировка
        d.line([60, 1060, 40, 1030], fill=(90, 90, 100), width=16)
        d.arc([380, 1080, 700, 1260], 0, 360, fill=(190, 150, 90), width=10)   # верёвка
        img = img.resize((W, H), Image.LANCZOS)
        glow(img, (W / 2, 80), 200, (255, 220, 150), .35)
        items = ["ФОНАРИК", "МОНТИРОВКА", "ВЕРЁВКА"][: 1 + int(p / .2)]
        for i, it in enumerate(items):
            pill(img, "✓ " + it, W / 2, 190 + i * 64, (20, 22, 30), YEL, 30)
    else:
        k = (p - .62) / .38
        img = S2.section(t, 6, water=1, face="angry", dig=False, ladder=True, hero_y=FLOOR + 40 + k * (BOT - FLOOR - 60))
        img = S2.cam(img, FLOOR + 40 + k * (BOT - FLOOR - 60), 1.15)
        pill(img, "ПОГНАЛИ", W / 2, 190, (150, 30, 30), WHITE, 34)
    S2.hud(img, "есть", 6)
    return img


def k04(t, L, cue):   # на дне: вода по колено, дыра сбоку
    p = P(cue, "04", t)
    img = S2.section(t, 6, water=1, face="shock" if p > .6 else "neutral", dig=False, ladder=True, hole=p > .55)
    img = S2.cam(img, BOT - 120, 1.35)
    sx = W * .55
    img = beam(img, sx, 760, 0.0 if p > .55 else math.pi / 2, 380)
    img = darkness(img, [(sx, 760, 260), (W * .78, 840, 200 if p > .55 else 1)])
    pill(img, "ВОДА ПО КОЛЕНО" if p < .55 else "ДЫРА", W / 2, 190, (20, 22, 30) if p < .55 else (150, 30, 30), WHITE, 32)
    S2.hud(img, "есть", 6)
    return img


def tunnel(t, prog, light=0.0, man=0.0, hero_face="angry"):
    """горизонтальный ход: герой пригнувшись идёт вправо, в конце — тёплый свет и мужик"""
    img = Image.new("RGB", (W * 2, H * 2))
    d = SD(img, 0, 0, 2)
    d.rectangle([0, 0, W, H], fill=(70, 56, 50))
    rnd = random.Random(11)
    for _ in range(120):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(3, 10)
        d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(52, 42, 38))
    TY0, TY1 = 560, 860
    d.rounded_rectangle([-40, TY0, W + 40, TY1], radius=60, fill=(30, 24, 22))
    off = (prog * 400) % 240
    for x in range(-240, W + 240, 240):   # крепь
        xx = x - off
        d.rectangle([xx, TY0 - 6, xx + 18, TY1], fill=(120, 84, 56), outline=OUT, width=2)
        d.rectangle([xx - 20, TY0 - 10, xx + 38, TY0 + 8], fill=(120, 84, 56), outline=OUT, width=2)
    d.rectangle([0, TY1 - 30, W, TY1], fill=(40, 50, 64))   # вода на дне хода
    chibi(d, "hero", 230, TY1 - 26, 1.15, t * (1 if man == 0 else .2), hero_face, 1, walk=man == 0, arm="phone")
    if man > 0:
        chibi(d, "dig", 560, TY1 - 26, 1.15, t, "shock", -1, arm="up")
    img = img.resize((W, H), Image.LANCZOS)
    if light > 0:
        glow(img, (W + 140 - 160 * light, (TY0 + TY1) / 2), 240 * light, (255, 200, 120), (.9 if man == 0 else .5) * light)
    img = beam(img, 300, 690, 0.0, 400, .22)
    lights = [(300, 700, 230)]
    if light > 0:
        lights.append((W + 140 - 160 * light, 710, 320 * light))
    return darkness(img, lights, .9)


def k05(t, L, cue):   # ход свежий — ползу
    p = P(cue, "05", t)
    img = tunnel(t, t * .5)
    pill(img, "СВЕЖИЙ ХОД", W / 2, 190, (150, 30, 30), WHITE, 32)
    S2.hud(img, "есть", 6)
    return img


def k06(t, L, cue):   # метр, два, свет → «я живой»
    p = P(cue, "06", t)
    light = min(1, max(0, (p - .25) / .3))
    man = 1 if p > .6 else 0
    img = tunnel(t, t * .5 if not man else 0, light, man, "shock" if man else "angry")
    if p < .35:
        pill(img, f"{1 if p < .18 else 2} МЕТРА" if p >= .18 else "1 МЕТР", W / 2, 190, (20, 22, 30), YEL, 34)
    if p > .85:
        K.B.M.big(img, "Я ЖИВОЙ", 300, GREEN, 96)
    S2.hud(img, "есть", 6)
    return shake(img, t, 8 if .6 < p < .66 else 0)


def school_bunker(t, n=20, hero=False):
    img = Image.new("RGB", (W * 2, H * 2))
    d = SD(img, 0, 0, 2)
    for y in range(0, 520, 8):   # вечернее небо
        k = y / 520
        d.rectangle([0, y, W, y + 8], fill=(int(60 + 150 * k), int(50 + 60 * k), int(80 - 20 * k)))
    d.rectangle([110, 230, 610, 520], fill=(214, 190, 150), outline=OUT, width=5)          # школа
    d.rectangle([250, 180, 470, 230], fill=(214, 190, 150), outline=OUT, width=5)
    d.text((266, 184), "ШКОЛА", font=F(80, FONT_SUB), fill=(90, 60, 40))
    for r in range(3):
        for c in range(6):
            d.rectangle([140 + c * 78, 250 + r * 88, 190 + c * 78, 310 + r * 88], fill=(30, 34, 44), outline=OUT, width=3)
    d.rectangle([0, 520, W, H], fill=(96, 74, 56))                                          # земля
    d.rectangle([90, 720, 630, 1010], fill=(70, 72, 76), outline=OUT, width=6)               # бункер
    d.rectangle([110, 740, 610, 990], fill=(150, 140, 110))
    d.line([360, 520, 360, 720], fill=(60, 60, 64), width=14)                               # шахта-лаз
    d.ellipse([340, 750, 380, 790], fill=(255, 230, 160), outline=OUT, width=3)
    rnd = random.Random(4)
    who = ["p1", "p2", "p3", "dig"]
    for i in range(n):
        x = 140 + (i % 10) * 48 + rnd.uniform(-6, 6)
        y = 900 + (i // 10) * 82
        chibi(d, who[i % 4], x, y, .5, t + i, "neutral" if i % 3 else "sad", rnd.choice((-1, 1)))
    d.rectangle([630, 960, W + 10, 1000], fill=(30, 24, 22))                                 # ход к гаражу
    img = img.resize((W, H), Image.LANCZOS)
    glow(img, (360, 800), 260, (255, 210, 140), .45)
    return img


def k07(t, L, cue):   # мужик крупно → бункер под школой, 20 человек
    p = P(cue, "07", t)
    if p < .5:
        img = Image.new("RGB", (W * 2, H * 2))
        d = SD(img, 0, 0, 2)
        d.rectangle([0, 0, W, H], fill=(36, 30, 28))
        chibi(d, "dig", 360, 1540, 6.0, t, "sad", 0)
        img = img.resize((W, H), Image.LANCZOS)
        glow(img, (360, 760), 300, (255, 200, 120), .35)
        pill(img, "ХУДОЙ КАК СКЕЛЕТ" if p < .25 else "КОПАЕТ 2 НЕДЕЛИ", W / 2, 190, (20, 22, 30), YEL, 32)
    else:
        img = school_bunker(t, n=min(20, int(4 + (p - .5) / .4 * 20)))
        if p > .75:
            K.B.M.big(img, "20 ЧЕЛОВЕК", 1080, YEL, 92)
    S2.hud(img, "есть", 6)
    return img


def card_garage():
    v = V(world(day=True, lights=False), (980, GR - 110, 2.2))
    K.gate(v.d, "steel", dents=5)
    for i, w in enumerate(["p1", "dig", "p2", "p3", "hero"]):
        chibi(v.d, w, 900 + i * 48, GR - 4, .9, i, "smile" if w != "dig" else "neutral", 1 if i % 2 else -1)
    return v.out()


def k08(t, L, cue):   # выбор
    B._cards["garage"] = B._cards.get("garage") or card_garage()
    B._cards["bunker"] = B._cards.get("bunker") or S2.cam(school_bunker(0), 760, 1.0)
    bg = school_bunker(t).filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(bg, Image.new("RGB", (W, H)), .55)
    d = ImageDraw.Draw(img)
    f = F(44, FONT_SUB)
    d.text(((W - f.getlength("КУДА ДАЛЬШЕ?")) / 2, 170), "КУДА ДАЛЬШЕ?", font=f, fill=WHITE, stroke_width=4, stroke_fill=(8, 8, 10))
    pulse = .5 + .5 * math.sin(t * 4)
    img = B.pretty_card(img, 36, 300, 310, 470, "garage", "1", "Пустить их\nв гараж", (240, 170, 60), min(1, t / .3), pulse)
    img = B.pretty_card(img, 374, 300, 310, 470, "bunker", "2", "Уйти к ним\nв бункер", (90, 150, 230), min(1, max(0, t - .25) / .3), 1 - pulse)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 40, 495, W / 2 + 40, 575], fill=YEL, outline=(10, 10, 14), width=5)
    fi = F(24, FONT_SUB)
    d.text((W / 2 - fi.getlength("ИЛИ") / 2, 520), "ИЛИ", font=fi, fill=(20, 20, 24))
    p = P(cue, "08", t)
    S2.hud(img, "есть", 6)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN})
