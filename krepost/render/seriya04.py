"""«КРЕПОСТЬ». Финал (зрители выбрали «уйти в бункер», 62%): бункер под школой → карта с гаражом «вода» две недели назад →
половина людей пропала → назад по ходу → ворота открыты изнутри. «Крепость строил три дня, отдал за минуту».
Запуск: python3 seriya04.py ../tts/s04 ../seriya04.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s03"), "x.mp4"]
import seriya03 as S3          # ход, темнота, школа-бункер; тянет S2 и хелперы 1-й серии
sys.argv[:] = _argv
import toonlib
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s04"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya04.mp4"
from toonlib import setup, run, dur, shake, glow, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from flatworld import SD, chibi, OUT, world, GR

S2, K = S3.S2, S3.K
W, H, F, B = K.W, K.H, K.F, K.B
YEL, RED, WHITE, GREEN = K.YEL, K.RED, K.WHITE, K.GREEN
pill, V, big = K.pill, K.V, K.B.M.big
darkness, beam = S3.darkness, S3.beam

LINES = {
    "01": "Я три дня строил *крепость* от мёртвых. А надо было — от ^живых^.",
    "02": "Вы выбрали — уйти в *бункер*.",
    "03": "Ползём по ходу. Худой впереди, я за ним. *Двести* метров под землёй, б§§§§.",
    "04": "Бункер под школой. Лампы. Консервы. *Двадцать* человек. И все ^молчат^.",
    "05": "На стене — карта района. Мой гараж обведён ^красным^. И подпись: «*вода*».",
    "06": "А под ней — дата. *Две недели* назад. Я тогда ещё даже копать не начал.",
    "07": "Оборачиваюсь… Худого ^нет^. И половины людей ^нет^.",
    "08": "Назад по ходу, на карачках, бегом, с§§а, колени в кровь!",
    "09": "Вылезаю в гараж… Ворота. *Мои* ворота. Открыты. ^Изнутри^.",
    "10": "Короче. Крепость я строил *три дня*. А отдал — за ^одну минуту^.",
    "11": "Подпишись, братан. Завтра — *новая* история.",
}
PLAN = [(f"k{k}", [(k, 0.04)], 0.1) for k in LINES]
PLAN[0] = ("k01", [("01", 0.0)], 0.1)
PLAN[8] = ("k09", [("09", 0.04)], 0.5)
PLAN[-1] = ("k11", [("11", 0.05)], 0.8)
setup(LINES, PLAN)
toonlib.draw_subs = K.draw_caps


def P(cue, key, t):
    return max(0.0, (t - cue[key]) / dur(key + ".mp3"))


def hud(img, status, col=GREEN):
    d = ImageDraw.Draw(img)
    for i, (lab, val, c) in enumerate((("ДЕНЬ", "4 · ФИНАЛ", YEL), ("КРЕПОСТЬ", status, col))):
        x0 = 40 + i * 340
        lay = img.crop((x0, 40, x0 + 300, 124)).point(lambda v: v * .4)
        img.paste(lay, (x0, 40))
        d.rounded_rectangle([x0, 40, x0 + 300, 124], radius=14, outline=(110, 150, 210), width=3)
        d.text((x0 + 150 - F(20).getlength(lab) / 2, 48), lab, font=F(20), fill=(200, 216, 240))
        fv = F(38, FONT_SUB)
        d.text((x0 + 150 - fv.getlength(val) / 2, 72), val, font=fv, fill=c)


def gate_open(d):
    x0, y0, x1, y1 = K.GATE
    d.rectangle([x0, y0, x1, y1], fill=(14, 12, 14), outline=OUT, width=3)
    mid = (x0 + x1) / 2
    for sx, xe in ((x0, x0 - 70), (x1, x1 + 70)):   # створки распахнуты наружу
        d.polygon([(sx, y0), (xe, y0 + 14), (xe, y1 + 8), (sx, y1)], fill=(110, 116, 126), outline=OUT)
        d.line([(sx + xe) / 2, y0 + 7, (sx + xe) / 2, y1 + 4], fill=(220, 200, 150), width=3)


def tunnel_run(t, speed, man_ahead=False, face="angry", red=0.0):
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
    off = (t * speed) % 240
    for x in range(-240, W + 480, 240):
        xx = x - off if speed > 0 else x + off
        d.rectangle([xx, TY0 - 6, xx + 18, TY1], fill=(120, 84, 56), outline=OUT, width=2)
        d.rectangle([xx - 20, TY0 - 10, xx + 38, TY0 + 8], fill=(120, 84, 56), outline=OUT, width=2)
    d.rectangle([0, TY1 - 30, W, TY1], fill=(40, 50, 64))
    hx = 230 if speed > 0 else 480
    chibi(d, "hero", hx, TY1 - 26, 1.15, t * (1.6 if red else 1), face, 1 if speed > 0 else -1, walk=True, arm="phone")
    if man_ahead:
        chibi(d, "dig", 470, TY1 - 26, 1.1, t + 1, "neutral", 1, walk=True)
    img = img.resize((W, H), Image.LANCZOS)
    bx = hx + (70 if speed > 0 else -70)
    img = beam(img, bx, 690, 0.0 if speed > 0 else math.pi, 400, .22)
    img = darkness(img, [(bx, 700, 250)], .9)
    if red:
        img = Image.blend(img, Image.new("RGB", (W, H), (120, 0, 0)), .25 * red)
    return img


PEOPLE = ["p1", "p2", "p3", "dig"]


def bunker_room(t, n=20, gone=0.0, man=True, hero_face="neutral", hero=True):
    img = Image.new("RGB", (W * 2, H * 2))
    d = SD(img, 0, 0, 2)
    d.rectangle([0, 0, W, H], fill=(72, 76, 70))
    for x in range(0, W, 120):
        d.line([x, 0, x, H], fill=(62, 66, 60), width=4)
    d.rectangle([0, 840, W, H], fill=(56, 54, 50))
    for k, x in enumerate((140, 360, 580)):   # лампы
        d.line([x, 0, x, 70], fill=OUT, width=3)
        d.ellipse([x - 20, 66, x + 20, 100], fill=(255, 230, 160), outline=OUT, width=3)
    for sx in (30, 560):   # стеллажи с консервами
        d.rectangle([sx, 300, sx + 130, 620], fill=(110, 84, 60), outline=OUT, width=4)
        for r in range(3):
            d.line([sx, 400 + r * 100, sx + 130, 400 + r * 100], fill=OUT, width=4)
            for c in range(4):
                d.rounded_rectangle([sx + 10 + c * 30, 366 + r * 100, sx + 34 + c * 30, 398 + r * 100], radius=4, fill=(170, 170, 176), outline=OUT, width=2)
    rnd = random.Random(9)
    keep = int(round(n * (1 - gone)))
    for i in range(n):
        if i >= keep:
            continue
        x = 70 + (i % 10) * 64 + rnd.uniform(-6, 6)
        y = 700 + (i // 10) * 80
        chibi(d, PEOPLE[i % 4], x, y, .62, 0, "neutral", 0)    # стоят и смотрят, не двигаются
    if man and gone == 0:
        chibi(d, "dig", 520, 860, 1.1, 0, "neutral", -1)
    if hero:
        chibi(d, "hero", 230, 870, 1.2, t, hero_face, 1 if gone == 0 else -1)
    img = img.resize((W, H), Image.LANCZOS)
    for x in (140, 360, 580):
        glow(img, (x, 90), 140, (255, 220, 150), .3)
    return img


def wall_map(t, ring=1.0, date=0.0):
    img = Image.new("RGB", (W * 2, H * 2))
    d = SD(img, 0, 0, 2)
    d.rectangle([0, 0, W, H], fill=(72, 76, 70))
    d.rectangle([60, 260, 660, 980], fill=(226, 214, 180), outline=OUT, width=6)    # бумага
    for x in range(110, 660, 90):
        d.line([x, 260, x + 20, 980], fill=(190, 180, 150), width=8)
    for y in range(320, 980, 110):
        d.line([60, y, 660, y - 10], fill=(190, 180, 150), width=8)
    d.rectangle([140, 380, 300, 470], fill=(200, 160, 120), outline=OUT, width=3)
    d.text((152, 404), "ШКОЛА", font=F(56, FONT_SUB), fill=(90, 60, 40))
    for k in range(8):   # гаражный кооператив
        d.rectangle([380 + (k % 4) * 60, 640 + (k // 4) * 60, 430 + (k % 4) * 60, 690 + (k // 4) * 60], fill=(170, 170, 160), outline=OUT, width=2)
    gx, gy = 490, 665
    d.line([220, 470, 240, 600, 420, 650, gx, gy], fill=(90, 60, 40), width=4)   # пунктир хода
    if ring > 0:
        rr = 70
        a1 = 360 * min(1, ring)
        d.arc([gx - rr, gy - rr, gx + rr, gy + rr], -90, -90 + a1, fill=(220, 30, 30), width=12)
    if ring >= 1:
        d.text((gx - 90, gy + 80), "ВОДА", font=F(90, FONT_SUB), fill=(200, 30, 30))
    if date > 0:
        d.text((180, 860), "14.11", font=F(120, FONT_SUB), fill=(200, 30, 30))
    img = img.resize((W, H), Image.LANCZOS)
    glow(img, (360, 120), 260, (255, 220, 150), .3)
    return img


# ---------- сцены ----------
def k01(t, L, cue):   # «от мёртвых — от живых»
    p = P(cue, "01", t)
    if p < .58:
        v = V(world(day=False, lights=False), (980, GR - 120, 1.6), (1010, GR - 110, 1.9), p / .58)
        K.gate(v.d, "steel", dents=5)
        K.zombies(v.d, t, 6, x0=1150, spread=55, s=.8)
        chibi(v.d, "hero", 1050, GR - 4, 1.0, t, "angry", 1)
        img = v.out()
        img = Image.blend(img, Image.new("RGB", (W, H), (210, 90, 40)), .18)
        pill(img, "ОТ МЁРТВЫХ", W / 2, 190, (20, 22, 30), WHITE, 34)
        hud(img, "держит")
    else:
        img = bunker_room(t, hero=False)
        img = Image.blend(img, Image.new("RGB", (W, H), (110, 0, 0)), .3)
        big(img, "ОТ ЖИВЫХ", 230, RED, 110)
        hud(img, "держит")
    return img


def k02(t, L, cue):
    bg = tunnel_run(t, 160, man_ahead=True)
    img = Image.blend(bg, Image.new("RGB", (W, H)), .3)
    img = S2.choice_banner(img, t, "БУНКЕР", L - .05, sub="62% голосов в опросе")
    hud(img, "держит")
    return img


def k03(t, L, cue):
    img = tunnel_run(t, 160, man_ahead=True)
    pill(img, "200 М ПОД ЗЕМЛЁЙ", W / 2, 190, (20, 22, 30), YEL, 32)
    hud(img, "держит")
    return img


def k04(t, L, cue):   # бункер: молчат
    p = P(cue, "04", t)
    img = bunker_room(t, n=20)
    z = 1.0 + .08 * p
    img = img.resize((W, H), Image.LANCZOS, box=(W * (1 - 1 / z) / 2, H * (1 - 1 / z) / 2, W * (1 + 1 / z) / 2, H * (1 + 1 / z) / 2))
    pill(img, "20 ЧЕЛОВЕК" if p < .75 else "ВСЕ МОЛЧАТ", W / 2, 190, (20, 22, 30) if p < .75 else (150, 30, 30), WHITE, 34)
    hud(img, "держит")
    return img


def zoomed(img, z, cx, cy):
    w, h = W / z, H / z
    cx = min(W - w / 2, max(w / 2, cx)); cy = min(H - h / 2, max(h / 2, cy))
    return img.resize((W, H), Image.LANCZOS, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


def k05(t, L, cue):   # карта, гараж обведён, «вода»
    p = P(cue, "05", t)
    ring = min(1.0, max(0, (p - .3) / .25)) if p < .72 else 1.0
    img = wall_map(t, ring=ring if p < .72 else 1.0)
    img = zoomed(img, 1.0 + .5 * p, 360 + 130 * p, 620 + 60 * p)
    img = darkness(img, [(W / 2, H / 2, 420)], .55)
    hud(img, "держит")
    return img


def k06(t, L, cue):   # дата — две недели назад
    p = P(cue, "06", t)
    img = wall_map(t, 1.0, date=1.0 if p > .15 else 0.0)
    img = zoomed(img, 1.7, 300, 860)
    img = darkness(img, [(W / 2, H / 2, 420)], .55)
    if p > .3:
        pill(img, "2 НЕДЕЛИ НАЗАД", W / 2, 190, (150, 30, 30), WHITE, 34)
    hud(img, "держит")
    return img


def k07(t, L, cue):   # оборачиваюсь — худого нет, половины нет
    p = P(cue, "07", t)
    img = bunker_room(t, n=20, gone=.5 if p > .25 else 0, man=p <= .25, hero_face="shock" if p > .25 else "neutral")
    if p > .25:
        img = Image.blend(img, Image.new("RGB", (W, H), (20, 0, 0)), .3)
        pill(img, "ХУДОГО НЕТ" if p < .6 else "ПОЛОВИНЫ НЕТ", W / 2, 190, (150, 30, 30), WHITE, 34)
    hud(img, "держит")
    return shake(img, t, 6 if .25 < p < .32 else 0)


def k08(t, L, cue):   # назад бегом
    img = tunnel_run(t, -520, face="shock", red=1.0)
    pill(img, "НАЗАД!", W / 2, 190, (150, 30, 30), WHITE, 38)
    hud(img, "???", YEL)
    return shake(img, t, 4)


def k09(t, L, cue):   # ворота открыты изнутри
    p = P(cue, "09", t)
    if p < .3:   # вылезает из ямы внутри гаража
        img = S2.section(t, 6, water=1, face="shock", dig=False, ladder=True, hero_y=S2.FLOOR + 80 - 80 * p / .3)
        img = S2.cam(img, 420, 1.2)
        img = darkness(img, [(W / 2, 520, 320)], .6)
        hud(img, "???", YEL)
        return img
    k = min(1, (p - .3) / .5)
    v = V(world(day=False, lights=False), (920, GR - 90, 3.0), (930, GR - 100, 2.0), k)
    gate_open(v.d)
    chibi(v.d, "hero", 900, GR - 4, 1.0, t, "shock", 0)
    img = v.out()
    img = Image.blend(img, Image.new("RGB", (W, H), (30, 10, 10)), .35)
    if p > .55:
        pill(img, "ОТКРЫТЫ", W / 2, 190, (150, 30, 30), WHITE, 36)
    if p > .82:
        big(img, "ИЗНУТРИ", 330, RED, 120)
    hud(img, "ПАЛА", RED)
    return shake(img, t, 10 if .82 < p < .9 else 0)


def k10(t, L, cue):   # «три дня — одна минута»
    p = P(cue, "10", t)
    v = V(world(day=False, lights=False), (980, GR - 200, 1.0), (1000, GR - 160, 1.35), min(1, t / L))
    gate_open(v.d)
    chibi(v.d, "hero", 960, GR - 4, 1.0, t, "sad", 0)
    K.zombies(v.d, t, 7, x0=1250 - 80 * min(1, t / L), spread=60, s=.8)
    img = v.out()
    img = Image.blend(img, Image.new("RGB", (W, H), (200, 80, 40)), .15)
    if p > .2:
        big(img, "3 ДНЯ", 220, YEL, 100)
    if p > .6:
        big(img, "1 МИНУТА", 340, RED, 100)
    hud(img, "ПАЛА", RED)
    return img


def k11(t, L, cue):   # конец + подписка
    bg = V(world(day=False, lights=False), (1000, GR - 160, 1.35)).out().filter(ImageFilter.GaussianBlur(8))
    img = Image.blend(bg, Image.new("RGB", (W, H)), .6)
    d = ImageDraw.Draw(img)
    f1 = F(110, FONT_SUB)
    d.text(((W - f1.getlength("КРЕПОСТЬ")) / 2, 330), "КРЕПОСТЬ", font=f1, fill=(244, 238, 228), stroke_width=8, stroke_fill=(10, 10, 12))
    f2 = F(40, FONT_SUB)
    d.text(((W - f2.getlength("КОНЕЦ")) / 2, 470), "КОНЕЦ", font=f2, fill=RED)
    a = min(1, t / .4)
    pill(img, "ПОДПИШИСЬ · ЗАВТРА НОВАЯ ИСТОРИЯ", W / 2, 620, (150, 30, 30), WHITE, 28)
    return Image.blend(bg.point(lambda v: v * .4), img, a)


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN})
