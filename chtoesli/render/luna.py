"""ЧТО ЕСЛИ… Луна исчезнет? Рисованный 2D-ролик (рубрика «Что если»).
Запуск: python3 luna.py ../tts/luna ../luna.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, os.path.join(ROOT, "million", "render"))
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import denis_rig as DR

LINES = {
    "01": "Луна исчезла. Прямо сейчас. Но ещё секунду ты будешь её видеть.",
    "02": "Свет от Луны летит до нас чуть больше секунды. Всё это время ты смотришь на Луну, которой уже нет.",
    "03": "Потом — темно. Каждая ночь станет чёрной, как в новолуние. Навсегда.",
    "04": "Через шесть часов придёт прилив. Точнее, его тень. Приливы станут втрое слабее — останется только тяга Солнца.",
    "05": "Крабы, моллюски и птицы, которые кормятся на отливе, потеряют свой стол.",
    "06": "Кораллы Большого Барьерного рифа мечут икру раз в год — по сигналу полной Луны. Сигнала больше не будет.",
    "07": "Черепашата ночью ползут к самому светлому горизонту. Раньше это было море под Луной. Теперь — огни города.",
    "08": "Солнечных затмений больше не будет. Никогда.",
    "09": "Но самое страшное — медленное. Луна держит наклон земной оси, как руль.",
    "10": "Без неё за миллионы лет ось может раскачаться. А вместе с ней — климат. Лёд там, где сейчас пляжи.",
    "11": "А теперь представь, что исчезло Солнце. Его свет летит к нам восемь минут. Восемь минут ты не будешь знать.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[-1] = ("s11", [("11", 0.1)], 3.8)
setup(LINES, PLAN)

F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
ORANGE, CYAN, MOON = (250, 170, 60), (120, 210, 255), (236, 232, 214)
BLUEPR, GRID = (16, 28, 48), (34, 52, 80)
GY = 1250


# ---------- элементы ----------
def stars(img, seed=1, n=160, k=1.0, top=0, bottom=H):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(top, bottom), rnd.choice((1, 1, 1.5, 2))
        c = int(rnd.uniform(140, 255) * k)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, min(255, c + 10)))


def moon(img, cx, cy, R, a=1.0):
    if a <= 0:
        return
    glow(img, (cx, cy), R * 2.6, (90, 100, 130), .6 * a)
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=MOON)
    rnd = random.Random(7)
    for _ in range(9):
        a0, rr = rnd.uniform(0, 6.28), rnd.uniform(.1, .7) * R
        x, y, r = cx + rr * math.cos(a0), cy + rr * math.sin(a0), rnd.uniform(.08, .22) * R
        d.ellipse([x - r, y - r, x + r, y + r], fill=(206, 200, 184))
    img.paste(Image.blend(img, lay, a))


def night(t, moon_a=1.0, ground=True, dark=1.0):
    img = vgrad(W, H, (int(14 + 20 * moon_a), int(18 + 30 * moon_a), int(40 + 50 * moon_a)), (4, 6, 14))
    stars(img, k=.6 + .4 * (1 - moon_a) * dark)
    moon(img, 470, 300, 110, moon_a)
    if ground:
        d = ImageDraw.Draw(img)
        lit = int(40 * moon_a)
        for i, (x, w, h) in enumerate(((0, 160, 260), (150, 120, 340), (260, 180, 220), (430, 140, 300), (560, 180, 240))):
            d.rectangle([x, GY - h - 160, x + w, GY], fill=(18 + lit // 2, 20 + lit // 2, 30 + lit))
            rnd = random.Random(i)
            for wy in range(GY - h - 130, GY - 40, 50):
                for wx in range(x + 18, x + w - 20, 40):
                    if rnd.random() < .35:
                        d.rectangle([wx, wy, wx + 18, wy + 24], fill=(240, 200, 110))
        d.rectangle([0, GY, W, H], fill=(14 + lit // 3, 16 + lit // 3, 22 + lit // 2))
    return img


def denis(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, tint=None):
    DR.use("denis")
    fig = DR.front((W, H), x, ground, s, t, arms, "idle", expr, look)
    if tint:
        R, G_, B = fig.convert("RGB").split()
        fig = Image.merge("RGBA", (R.point(lambda v: int(v * tint[0])), G_.point(lambda v: int(v * tint[1])),
                                   B.point(lambda v: int(v * tint[2])), fig.getchannel("A")))
    img.paste(fig, (0, 0), fig)
    return img


def tag(img, title, sub, y=1090):
    d = ImageDraw.Draw(img)
    f1, f2 = F(30, FONT_SUB), F(18)
    w = max(f1.getlength(title), f2.getlength(sub)) + 40
    d.rounded_rectangle([30, y, 30 + w, y + 74], radius=8, fill=(14, 14, 16))
    d.rectangle([30, y, 36, y + 74], fill=CYAN)
    d.text((48, y + 6), title, font=f1, fill=(255, 255, 255))
    d.text((48, y + 44), sub, font=f2, fill=(160, 160, 166))


def corner(img):
    d = ImageDraw.Draw(img)
    f = F(26, FONT_SUB)
    txt = "ЧТО ЕСЛИ…"
    d.rounded_rectangle([30, 30, 56 + f.getlength(txt), 80], radius=10, fill=(10, 14, 24))
    d.text((43, 38), txt, font=f, fill=CYAN)


def timer(img, txt, y=130):
    d = ImageDraw.Draw(img)
    f = F(50, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([(W - w) / 2 - 24, y, (W + w) / 2 + 24, y + 78], radius=16, fill=(12, 12, 14), outline=(230, 230, 230), width=3)
    d.text(((W - w) / 2, y + 9), txt, font=f, fill=(255, 255, 255))


def blueprint(title=None):
    img = Image.new("RGB", (W, H), BLUEPR)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        d.line([x, 0, x, H], fill=GRID)
    for y in range(0, H, 40):
        d.line([0, y, W, y], fill=GRID)
    if title:
        f = F(54, FONT_SUB)
        d.text(((W - f.getlength(title)) / 2, 170), title, font=f, fill=ORANGE)
        d.line([(W - f.getlength(title)) / 2, 240, (W + f.getlength(title)) / 2, 240], fill=ORANGE, width=4)
    return img


def crab(d, x, y, s=1.0, col=(214, 90, 50)):
    d.ellipse([x - 26 * s, y - 16 * s, x + 26 * s, y + 14 * s], fill=col, outline=INK, width=2)
    for sx in (-1, 1):
        for k in range(3):
            d.line([x + sx * 18 * s, y + 4 * s, x + sx * (36 + k * 4) * s, y + (10 + k * 8) * s], fill=INK, width=3)
        d.ellipse([x + sx * 34 * s - 10 * s, y - 34 * s, x + sx * 34 * s + 10 * s, y - 16 * s], fill=col, outline=INK, width=2)
    for sx in (-8, 8):
        d.ellipse([x + sx * s - 4, y - 24 * s, x + sx * s + 4, y - 16 * s], fill=INK)


def turtle(d, x, y, ang, s=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    for u, v in ((14, 14), (14, -14), (-14, 14), (-14, -14)):
        d.ellipse([*P(u - 7, v - 5), *P(u + 7, v + 5)], fill=(70, 90, 60))
    d.ellipse([*P(20, -6), *P(32, 6)], fill=(70, 90, 60))
    d.ellipse([*P(-18, -14), *P(18, 14)], fill=(110, 90, 60), outline=INK)


# ---------- сцены ----------
def s01(t, L, cue):
    p = (t - cue["01"]) / dur("01.mp3")
    img = night(t, 1.0)
    img = denis(img, 230, .62, t, ("down", "down"), "shock" if p > .35 else "neutral", (.5, -1), tint=(.7, .75, .95))
    if p > .3:   # вспышка-«исчезновение»: Луна ещё видна, но обведена пунктиром
        d = ImageDraw.Draw(img)
        for k in range(24):
            a = k * math.pi / 12
            d.arc([470 - 140, 300 - 140, 470 + 140, 300 + 140], math.degrees(a), math.degrees(a) + 7, fill=(255, 110, 100), width=4)
        timer(img, "+0,0 с", 520)
    corner(img)
    return shake(img, t, 5 if .3 < p < .4 else 0)


def s02(t, L, cue):
    img = blueprint("384 000 км")
    d = ImageDraw.Draw(img)
    d.ellipse([60, 560, 220, 720], fill=(60, 130, 200), outline=CYAN, width=4)   # Земля
    d.ellipse([560, 600, 640, 680], outline=MOON, width=4)                       # Луна (уже нет)
    k = min(1, (t % 2.6) / 1.3)
    x = 560 - k * 340
    d.line([560, 640, x, 640], fill=(255, 230, 150), width=6)
    glow(img, (x, 640), 30, (255, 230, 150), 1)
    d = ImageDraw.Draw(img)
    f = F(110, FONT_SUB)
    d.text((W / 2 - f.getlength("1,3 с") / 2, 820), "1,3 с", font=f, fill=ORANGE)
    corner(img)
    return img


def s03(t, L, cue):
    k = min(1, t / 1.2)
    img = night(t, 1 - k)
    img = denis(img, 230, .62, t, ("down", "down"), "worried", (.5, -1), tint=(.5 + .2 * (1 - k), .55 + .2 * (1 - k), .8))
    timer(img, "+1,3 с", 520)
    corner(img)
    return img


def tides(img, t, k):
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 700
    a = 230 + 70 * k * (1 + .05 * math.sin(t * 2))
    d.ellipse([cx - a, cy - 230, cx + a, cy + 230], fill=(40, 110, 190), outline=CYAN, width=4)
    d.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(70, 140, 80), outline=INK, width=4)


def s04(t, L, cue):
    img = blueprint("ПРИЛИВЫ")
    p = (t - cue["04"]) / dur("04.mp3")
    k = 1.0 if p < .5 else max(.33, 1 - (p - .5) * 3)
    tides(img, t, k)
    d = ImageDraw.Draw(img)
    if p > .55:
        f = F(80, FONT_SUB)
        d.text((W / 2 - f.getlength("÷ 3") / 2, 990), "÷ 3", font=f, fill=ORANGE)
        glow(img, (W - 60, 700), 80, (255, 200, 80), 1)
        tag(img, "остаётся", "только Солнце", 1110)
    timer(img, "+6 ч", 300)
    corner(img)
    return img


def s05(t, L, cue):
    img = vgrad(W, H, (120, 150, 190), (200, 180, 140))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 560, W, H], fill=(210, 190, 140))   # песок
    wl = 760 - 60 * math.sin(t * .4)                       # вода почти не уходит
    d.rectangle([0, 560, W, wl], fill=(50, 110, 160))
    rnd = random.Random(3)
    for i in range(6):
        x, y = rnd.uniform(80, 640), rnd.uniform(860, 1180)
        crab(d, x + 6 * math.sin(t * 3 + i), y, 1.1)
    for i in range(3):   # птицы
        x, y = 140 + i * 200 + 30 * math.sin(t + i), 300 + 20 * math.cos(t * 1.3 + i)
        d.line([x - 30, y, x, y + 12, x + 30, y], fill=INK, width=5)
    tag(img, "отлив", "почти пропал", 1110)
    corner(img)
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    img = vgrad(W, H, (10, 40, 70), (4, 14, 26))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for i in range(14):   # кораллы
        x, h = 20 + i * 52, rnd.uniform(120, 260)
        col = rnd.choice(((230, 110, 120), (240, 170, 80), (180, 120, 220)))
        for j in range(4):
            d.line([x, H, x + rnd.uniform(-40, 40), H - h + j * 20], fill=col, width=14)
    if p < .6:   # икра поднимается под полной луной
        glow(img, (W / 2, 0), 300, (120, 140, 180), .8)
        d = ImageDraw.Draw(img)
        for i in range(160):
            ph = (t * .15 + rnd.random()) % 1
            x, y = rnd.uniform(0, W), H - 200 - ph * 900
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(250, 200, 210))
    else:
        tag(img, "сигнал", "нет полной Луны", 1110)
    tag(img, "Большой Барьерный риф", "1 раз в год · полнолуние", 130)
    corner(img)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    lunar = p < .55
    img = vgrad(W, H, (16, 20, 40), (4, 6, 14))
    stars(img, 3, 100, .8, 0, 500)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 500, W, 760], fill=(20, 40, 70) if lunar else (8, 14, 24))   # море
    if lunar:
        moon(img, 500, 200, 60)
        d = ImageDraw.Draw(img)
        for k in range(10):
            d.line([440 + k % 3 * 30, 520 + k * 22, 560 - k % 2 * 30, 520 + k * 22], fill=(200, 200, 190), width=3)
    else:   # огни города слева
        for i in range(30):
            glow(img, (10 + i * 8, 1150 + 30 * math.sin(i)), 26, (255, 180, 80), .6)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 760, W, H], fill=(70, 66, 60))   # пляж
    rnd = random.Random(8)
    for i in range(9):
        x0, y0 = rnd.uniform(120, 620), rnd.uniform(860, 1200)
        tgt = (x0, 600) if lunar else (0, 1150)
        ang = math.atan2(tgt[1] - y0, tgt[0] - x0)
        m = (t * 25) % 120
        turtle(d, x0 + math.cos(ang) * m, y0 + math.sin(ang) * m, ang, 1.2)
    corner(img)
    return img


def s08(t, L, cue):
    img = vgrad(W, H, (110, 160, 220), (190, 210, 240))
    cx, cy = W / 2, 560
    glow(img, (cx, cy), 260, (255, 220, 120), 1)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 130, cy - 130, cx + 130, cy + 130], fill=(255, 236, 160))
    k = min(1, t / 2.0)
    if t < 2.4:   # диск Луны наползает… и пропадает
        mx = cx - 300 + 300 * k
        d.ellipse([mx - 128, cy - 128, mx + 128, cy + 128], fill=(30, 30, 40))
    else:
        d.line([cx - 200, cy - 200, cx + 200, cy + 200], fill=(255, 90, 90), width=14)
        tag(img, "затмения", "больше никогда", 1110)
    corner(img)
    return img


def earth_axis(img, t, ang):
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, 660, 200
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(40, 110, 190), outline=CYAN, width=4)
    d.ellipse([cx - 120, cy - 90, cx + 20, cy + 40], fill=(70, 140, 80))
    d.ellipse([cx + 40, cy + 10, cx + 150, cy + 120], fill=(70, 140, 80))
    a = math.radians(ang)
    dx, dy = math.sin(a) * 320, math.cos(a) * 320
    d.line([cx - dx, cy + dy, cx + dx, cy - dy], fill=ORANGE, width=8)
    f = F(56, FONT_SUB)
    txt = f"{abs(ang):.0f}°"
    d.text((W / 2 - f.getlength(txt) / 2, 980), txt, font=f, fill=ORANGE)


def s09(t, L, cue):
    img = blueprint("НАКЛОН ОСИ")
    earth_axis(img, t, 23 + 1.5 * math.sin(t * 1.2))
    p = (t - cue["09"]) / dur("09.mp3")
    if p > .6:
        tag(img, "Луна", "держит ось, как руль", 1110)
    corner(img)
    return img


def s10(t, L, cue):
    p = (t - cue["10"]) / dur("10.mp3")
    img = blueprint("МИЛЛИОНЫ ЛЕТ")
    ang = 23 + min(1, p * 1.3) * 30 * math.sin(t * 2.4)
    earth_axis(img, t, ang)
    if p > .65:   # ледяная шапка ползёт к экватору
        d = ImageDraw.Draw(img)
        d.chord([W / 2 - 200, 460, W / 2 + 200, 860], 180, 360, fill=(230, 240, 250))
        tag(img, "лёд", "там, где пляжи", 1110)
    corner(img)
    return img


def s11(t, L, cue):
    vo_end = cue["11"] + dur("11.mp3")
    p = (t - cue["11"]) / dur("11.mp3")
    img = vgrad(W, H, (120, 170, 230), (200, 220, 240))
    glow(img, (W / 2, 380), 240, (255, 220, 120), 1)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 110, 270, W / 2 + 110, 490], fill=(255, 236, 160))
    img = denis(img, W / 2, .9, t, ("down", "down"), "smile" if p < .5 else "worried", (0, -.6), ground=1500)
    if p > .45:
        left = max(0, 8 * 60 - (t - cue["11"] - dur("11.mp3") * .45) * 40)
        timer(img, f"{int(left // 60)}:{int(left % 60):02d}", 140)
    corner(img)
    if t > vo_end + .6:
        a = min(1, (t - vo_end - .6) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(40, FONT_SUB), F(76, FONT_SUB), F(30, FONT_SUB)
            dd.text(((W - f1.getlength("ЧТО ЕСЛИ…")) / 2, 460), "ЧТО ЕСЛИ…", font=f1, fill=CYAN)
            dd.text(((W - f2.getlength("ИСЧЕЗНЕТ СОЛНЦЕ")) / 2, 520), "ИСЧЕЗНЕТ СОЛНЦЕ", font=F(60, FONT_SUB), fill=ORANGE)
            if t > vo_end + 1.4:
                q = "часть 2 после 100 ♥"
                dd.text(((W - f3.getlength(q)) / 2, 640), q, font=f3, fill=(200, 200, 206))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + dur("01.mp3") * .32, span("s08")[0] + 2.4])
