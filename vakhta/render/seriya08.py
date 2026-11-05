"""ВАХТА. Серия 8 (финал сезона). Запуск: python3 seriya08.py ../tts/s08 ../seriya08.mp4"""
from toonlib import *

LINES = {
    "02": "Я не успел отступить. Снизу ударила вспышка — Михалыч поджёг факел из ракетницы.",
    "03": "Тимур закрыл лицо руками. Огонь ему не нравился. Он попятился к краю стрелы — и упал в море.",
    "04": "Всплеска не было.",
    "05": "Ночью Михалыч рассказал всё.",
    "05m": "Неделю назад мы пробурили что-то не то. Из скважины пошла вода. Не нефть — вода. Ледяная.",
    "06m": "Оно выходит из моря и становится тем, кого забрало. Первым был пилот. Я запер его в старом отсеке. В двадцать первой.",
    "07m": "Берег всё знает. Поэтому вертолётов не будет. Пока мы здесь — оно здесь.",
    "08": "Я спросил про рацию. Михалыч долго молчал.",
    "09m": "Я говорил не с берегом. С тем, кто за дверью. Оно отвечает моим голосом.",
    "10": "Утром на горизонте показался вертолёт. Мы выбежали на площадку.",
    "11": "Только летел он не с берега. Он летел из открытого моря.",
    "12": "Вертолёт сел. Дверь открылась. На палубу вышел пилот. Мокрый с головы до ног.",
    "13": "А в двадцать первой каюте снова постучали. Три раза.",
}

PLAN = [
    ("s01", [], 3.2),
    ("s02", [("02", 0.4)], 0.6),
    ("s03", [("03", 0.2)], 0.6),
    ("s04", [("04", 0.4)], 1.4),
    ("s05", [("05", 0.2), ("05m", None)], 0.5),
    ("s06", [("06m", 0.2)], 0.5),
    ("s07", [("07m", 0.2)], 0.5),
    ("s08", [("08", 0.2)], 1.2),
    ("s09", [("09m", 0.2)], 0.8),
    ("s10", [("10", 0.2)], 0.4),
    ("s11", [("11", 0.2)], 0.4),
    ("s12", [("12", 0.2)], 0.6),
    ("s13", [("13", 0.2)], 5.6),
]
setup(LINES, PLAN)

SHIRT, SHIRT_D = (176, 178, 186), (90, 94, 104)
CORR = ("corr_bg", (140, 144, 150), (100, 104, 110))
PALE = (204, 216, 220)


def end_card(img, t, start, lines, sub=None):
    if t <= start:
        return img
    a = min(1, (t - start) / .5)
    img = Image.blend(img, Image.new("RGB", (W, H)), a)
    if a >= 1:
        dd = ImageDraw.Draw(img)
        f2 = ImageFont.truetype(FONT_SUB, 62)
        for j, line in enumerate(lines):
            dd.text(((W - f2.getlength(line)) / 2, 470 + j * 82), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
        if sub and t > start + 1.2:
            f3 = ImageFont.truetype(FONT_SUB, 40)
            dd.text(((W - f3.getlength(sub)) / 2, 470 + len(lines) * 82 + 40), sub, font=f3, fill=(240, 240, 240), stroke_width=3, stroke_fill=INK)
    return img


def toon_layer(x, y, s, who, face, arms, look, t, **kw):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    toon(lay, x, y, s, who, face, arms, look, t, **kw)
    return lay


def heli(d, x, y, s, t, landed=False):
    """вертолёт сбоку"""
    o = max(2, int(5 * s))
    body = (226, 228, 232)
    d.line([x + 60 * s, y, x + 260 * s, y - 20 * s], fill=body, width=int(26 * s))      # хвост
    d.line([x + 60 * s, y, x + 260 * s, y - 20 * s], fill=INK, width=max(1, o // 2))
    d.polygon([(x + 240 * s, y - 20 * s), (x + 280 * s, y - 70 * s), (x + 290 * s, y - 20 * s)], fill=(200, 60, 50), outline=INK)
    d.ellipse([x - 130 * s, y - 70 * s, x + 90 * s, y + 60 * s], fill=body, outline=INK, width=o)
    d.chord([x - 128 * s, y - 64 * s, x - 10 * s, y + 30 * s], 120, 250, fill=(70, 120, 160), outline=INK, width=o)  # стекло
    d.rectangle([x - 40 * s, y - 20 * s, x + 30 * s, y + 30 * s], fill=(196, 198, 204), outline=INK, width=max(1, o // 2))  # дверь
    d.line([x - 20 * s, y - 70 * s, x - 20 * s, y - 92 * s], fill=INK, width=o)
    span_ = 230 * s * (.35 + .65 * abs(math.sin(t * 25))) if not landed else 230 * s
    d.line([x - 20 * s - span_, y - 94 * s, x - 20 * s + span_, y - 94 * s], fill=(40, 40, 46), width=max(2, int(8 * s)))
    d.line([x - 100 * s, y + 70 * s, x + 60 * s, y + 70 * s], fill=INK, width=o)         # полозья
    d.line([x - 70 * s, y + 50 * s, x - 70 * s, y + 70 * s], fill=INK, width=o)
    d.line([x + 30 * s, y + 50 * s, x + 30 * s, y + 70 * s], fill=INK, width=o)
    if int(t * 2) % 2 == 0:
        d.ellipse([x + 280 * s, y - 80 * s, x + 296 * s, y - 64 * s], fill=(255, 60, 60))


# ---------- сцены ----------
def s01(t, L):
    img = title(t, L, 8)
    d = ImageDraw.Draw(img)
    a = min(1, max(0, (t - .8) / .5))
    f = ImageFont.truetype(FONT_SUB, 58)
    d.text(((W - f.getlength("ФИНАЛ")) / 2, 410), "ФИНАЛ", font=f, fill=(int(240 * a), int(80 * a), int(70 * a)), stroke_width=4, stroke_fill=INK)
    return img


def s02(t, L):
    img = vgrad(W, H, (34, 38, 50), (20, 24, 34))
    d = ImageDraw.Draw(img)
    d.rectangle([420, 300, 520, 620], fill=(70, 72, 80), outline=INK, width=6)
    d.ellipse([400, 270, 540, 330], fill=(40, 40, 46), outline=INK, width=6)
    flash = 3.4
    if t > flash - .5:   # ракета снизу
        k = min(1, (t - (flash - .5)) / .5)
        rx, ry = 470, H - (H - 300) * k
        d.line([rx, ry, rx, min(H, ry + 260)], fill=(255, 200, 120), width=8)
        glow(img, (rx, ry), 40, (200, 120, 40), 1)
    if t > flash:
        flame(img, 470, 290, t, 2.2)
    toon(img, W / 2, 1330, 1.55, "timur", "neutral", ("down", "down"), (0, 0), t, outfit_c=SHIRT, pants_c=SHIRT_D, blink=False,
         pupil=1.0 if t < flash else max(.2, 1 - (t - flash)))
    if flash <= t < flash + .25:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 244, 220)), 1 - (t - flash) / .25)
    STORM.draw(img, t, streak=True)
    return shake(img, t, 10 if flash < t < flash + .6 else 2)


def s03(t, L):
    img = vgrad(W, H, (50, 46, 52), (26, 30, 40))
    glow(img, (640, 120), 300, (140, 80, 20), 1)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1000, W, H], fill=SEA)
    for x in range(0, W, 30):
        d.line([x, 1000 + 8 * math.sin(x * .05 + t * 2), x + 20, 1000 + 8 * math.sin(x * .05 + t * 2)], fill=(90, 110, 130), width=4)
    # стрела сверху-справа
    d.line([W + 40, 140, 160, 520], fill=(120, 124, 132), width=18)
    d.line([W + 40, 80, 160, 460], fill=(226, 110, 40), width=6)
    fall0 = L * .55
    if t < fall0:   # пятится, закрываясь
        x = 380 - 120 * t / fall0
        lay = toon_layer(x, 500, .55, "timur", "scared", ("ear", "ear"), (0, 0), t, outfit_c=SHIRT, pants_c=SHIRT_D)
        img.paste(lay, (0, 0), lay)
    else:
        k = (t - fall0) / (L - fall0)
        x, y = 260 - 60 * k, 500 + 600 * k * k
        if y < 1020:
            lay = toon_layer(W / 2, H / 2 + 150, .55, "timur", "scared", ("up", "up"), (0, -1), t, outfit_c=SHIRT, pants_c=SHIRT_D)
            lay = lay.rotate(160 * k, center=(W / 2, H / 2), resample=Image.BICUBIC)
            img.paste(lay, (int(x - W / 2), int(y - H / 2)), lay)
    SNOW.draw(img, t, wind=500)
    return img


def s04(t, L):
    img = vgrad(W, H, (40, 46, 58), (24, 28, 38))
    d = ImageDraw.Draw(img)
    pts = [(0, H)] + [(x, 640 + 6 * math.sin(x * .02 + t)) for x in range(0, W + 10, 10)] + [(W, H)]
    d.polygon(pts, fill=SEA)
    d.line(pts[1:-1], fill=(110, 130, 150), width=4)
    # ровная тёмная вода, тихо расходится один круг
    r = 40 + 160 * min(1, t / L)
    d.ellipse([360 - r, 760 - r * .2, 360 + r, 760 + r * .2], outline=(80, 96, 116), width=3)
    SNOW.draw(img, t, wind=60)
    return zoom(img, 1 + .06 * t / L)


def night_talk(img, t, talk_m=True, ilya_face="worried"):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=(86, 88, 92)); d.line([0, 1040, W, 1040], fill=INK, width=6)
    glow(img, (360, 760), 260, (90, 76, 36), .9)
    toon(img, 360, 1150, 1.0, "misha", "sad", ("front", "front"), (0, .3), t, legs=False, talk=talk_m)
    toon(img, 80, 1420, .85, "ilya", ilya_face, ("down", "down"), (1, -.4), t, legs=False)
    toon(img, 650, 1430, .85, "dasha", "worried", ("down", "down"), (-1, -.4), t, legs=False)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, 1080], fill=(150, 112, 80), outline=INK, width=5)
    d.rectangle([330, 990, 390, 1050], fill=(240, 240, 236), outline=INK, width=4)   # кружка
    img = breath(img, 370, 980, t, .6)
    return img


def breath(img, x, y, t, k=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i in range(3):
        life = (t * .7 + i / 3) % 1
        r = 10 + 30 * life
        ld.ellipse([x - 10 * life - r, y - 70 * life - r * .6, x - 10 * life + r, y - 70 * life + r * .6], fill=(235, 240, 250, int(140 * (1 - life) * k)))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(5))).convert("RGB")


def drill_insert(img, t, p):
    """скважина: из трубы бьёт ледяная вода"""
    d = ImageDraw.Draw(img)
    d.rectangle([300, 300, 420, 1100], fill=(90, 94, 104), outline=INK, width=6)
    d.rectangle([250, 280, 470, 330], fill=(110, 114, 124), outline=INK, width=6)
    if p > .25:
        rnd = random.Random(int(t * 24))
        for _ in range(60):
            a = rnd.uniform(-2.6, -.5); r = rnd.uniform(20, 280)
            x, y = 360 + r * math.cos(a), 280 + r * math.sin(a) + r * r * .004
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(150, 200, 236), outline=INK, width=2)
        d.polygon([(330, 280), (390, 280), (420, 120), (300, 120)], fill=(150, 200, 236), outline=INK)
    f = ImageFont.truetype(FONT_SUB, 50)
    if p > .6:
        d.text(((W - f.getlength("НЕ НЕФТЬ")) / 2, 1140), "НЕ НЕФТЬ", font=f, fill=(250, 120, 110), stroke_width=4, stroke_fill=INK)


def s05(t, L, cue):
    if t < cue["05m"] + 1.0:
        img = bg_room("canteen", (90, 96, 92), (60, 64, 62)).copy()
        img = night_talk(img, t, talk_m=False)
        return zoom(img, 1.02, .5, .5)
    img = vgrad(W, H, (60, 66, 78), (34, 40, 52))
    drill_insert(img, t, (t - cue["05m"]) / dur("05m.mp3"))
    return zoom(img, 1.02 + .05 * t / L)


def s06(t, L):
    p = t / L
    img = bg_room(*CORR).copy()
    img = Image.eval(img, lambda v: int(v * .35))
    d = ImageDraw.Draw(img)
    if p < .5:   # пилот выходит из воды → идёт к старому отсеку
        d.rectangle([0, 900, W, H], fill=SEA)
        y = 1100 - 200 * p / .5
        toon(img, 360, y + 200, .8, "timur", "neutral", ("down", "down"), (0, 0), t, outfit_c=(84, 98, 72), pants_c=(70, 80, 60), pupil=1.0)
        hx, hy = 360, y + 200 - 505 * .8
        d = ImageDraw.Draw(img)
        d.ellipse([hx - 84, hy - 92, hx + 84, hy + 40], fill=(236, 236, 232), outline=INK, width=5)   # шлем пилота
        d.rectangle([hx - 70, hy - 30, hx + 70, hy + 6], fill=(40, 60, 90), outline=INK, width=4)
    else:   # отсек 21: за решёткой окошка стоит пилот
        x0, x1, y1 = door_close(img, t, weld=1.0)
        d = ImageDraw.Draw(img)
        d.rectangle([280, 300, 440, 420], fill=(6, 8, 12), outline=INK, width=6)
        for gx in range(296, 440, 24):
            d.line([gx, 300, gx, 420], fill=(90, 94, 104), width=5)
        for ex in (340, 384):
            d.ellipse([ex - 8, 352, ex + 8, 368], fill=(230, 236, 240))
        f = ImageFont.truetype(FONT_SUB, 90)
        d.text(((W - f.getlength("21")) / 2, 140), "21", font=f, fill=(240, 80, 70), stroke_width=5, stroke_fill=INK)
    return zoom(img, 1.02 + .06 * t / L)


def s07(t, L):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    # берег слева сверху, платформа в море
    d.polygon([(0, 0), (W, 0), (W, 120), (420, 210), (160, 330), (0, 380)], fill=(120, 128, 110), outline=INK)
    f = ImageFont.truetype(FONT_SUB, 38)
    d.text((40, 60), "БЕРЕГ", font=f, fill=(240, 240, 240), stroke_width=3, stroke_fill=INK)
    px, py = 450, 600
    d.rectangle([px - 30, py - 30, px + 30, py + 30], fill=DECK, outline=INK, width=5)
    k = min(1, t / 1.5)
    r = 200 * k
    d.ellipse([px - r, py - r, px + r, py + r], outline=(240, 70, 60), width=8)
    # маршрут вертолёта — перечёркнут
    if t > 1.5:
        d.line([200, 300, px - 40, py - 40], fill=(240, 240, 240), width=6)
        hx, hy = 290, 400
        heli(d, hx, hy, .35, t, landed=True)
        if t > 2.6:
            d.line([hx - 70, hy - 70, hx + 90, hy + 70], fill=(240, 70, 60), width=14)
            d.line([hx - 70, hy + 70, hx + 90, hy - 70], fill=(240, 70, 60), width=14)
    d.text((px - f.getlength("СЕВЕРНАЯ-7") / 2, py - 260), "СЕВЕРНАЯ-7", font=f, fill=(240, 240, 240), stroke_width=3, stroke_fill=INK)
    SNOW.draw(img, t)
    return img


def s08(t, L):
    img = bg_room("canteen", (90, 96, 92), (60, 64, 62)).copy()
    img = night_talk(img, t, talk_m=False, ilya_face="serious")
    return zoom(img, 1 + .1 * t / L, .5, .45)


def s09(t, L):
    img = bg_room("canteen", (90, 96, 92), (60, 64, 62)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=(86, 88, 92))
    glow(img, (360, 700), 260, (90, 76, 36), .9)
    toon(img, W / 2, 1330, 1.55, "misha", "sad", ("down", "down"), (0, .4), t, talk=True)
    return zoom(img, 1 + .08 * t / L, .5, .42)


def dawn_sky():
    img = vgrad(W, H, (70, 84, 120), (238, 160, 120))
    return img


def s10(t, L):
    img = dawn_sky()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 760, W, H], fill=(56, 70, 96))
    for x in range(0, W, 26):
        d.line([x, 770 + (x * 7) % 60, x + 18, 770 + (x * 7) % 60], fill=(230, 170, 140), width=4)
    hx = 600 - 140 * t / L
    heli(d, hx, 560 + 6 * math.sin(t * 3), .22 + .1 * t / L, t)
    # бегут на площадку
    d.polygon([(-200, H), (W + 200, H), (W - 120, 1000), (120, 1000)], fill=(70, 84, 72), outline=INK)
    for who, x, ph in (("ilya", 220, 0), ("dasha", 420, 1.1), ("misha", 560, 2.2)):
        toon(img, x, 1240 - 60 * t / L, .5, who, "worried", ("down", "down"), (0, -1), t + ph, walk=t + ph, bob=6 * abs(math.sin((t + ph) * 9)))
    return img


def s11(t, L):
    img = dawn_sky()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 700, W, H], fill=(56, 70, 96))
    # вертолёт поднимается из-за горизонта со стороны моря, с полозьев капает вода
    hx, hy = 360, 600 - 120 * min(1, t / L)
    heli(d, hx, hy, .9, t)
    rnd = random.Random(int(t * 12))
    for _ in range(14):
        x = hx + rnd.uniform(-90, 60); y = hy + 80 + rnd.uniform(0, 200)
        d.ellipse([x - 5, y - 8, x + 5, y + 8], fill=(120, 160, 196), outline=INK, width=2)
    f = ImageFont.truetype(FONT_SUB, 40)
    d.text((40, 1100), "← берег", font=f, fill=(240, 240, 240), stroke_width=3, stroke_fill=INK)
    d.text((W - 40 - f.getlength("море →"), 1100), "море →", font=f, fill=(250, 120, 110), stroke_width=3, stroke_fill=INK)
    return shake(img, t, 2)


def s12(t, L):
    img = dawn_sky()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 900, W, H], fill=(70, 84, 72)); d.line([0, 900, W, 900], fill=INK, width=6)
    d.ellipse([60, 940, 660, 1120], outline=YELLOW, width=10)
    heli(d, 380, 820, 1.3, t, landed=t > L * .3)
    p = (t - L * .45) / (L * .45)
    if p > 0:   # из двери выходит мокрый пилот
        k = min(1, p)
        px = 330 - 40 * k
        toon(img, px, 1080 + 60 * k, .7, "timur", "neutral", ("down", "down"), (0, 0), t, outfit_c=(84, 98, 72), pants_c=(70, 80, 60), blink=False)
        hx, hy = px, 1080 + 60 * k - 505 * .7
        d = ImageDraw.Draw(img)
        d.ellipse([hx - 74, hy - 82, hx + 74, hy + 34], fill=(236, 236, 232), outline=INK, width=5)
        d.rectangle([hx - 60, hy - 26, hx + 60, hy + 4], fill=(40, 60, 90), outline=INK, width=4)
        rnd = random.Random(int(t * 10))
        for _ in range(10):   # течёт вода
            x = px + rnd.uniform(-60, 60); y = hy + rnd.uniform(60, 520)
            d.ellipse([x - 5, y - 8, x + 5, y + 8], fill=(120, 160, 196), outline=INK, width=2)
        d.ellipse([px - 90, 1120 + 60 * k, px + 90, 1150 + 60 * k], fill=(60, 90, 120), outline=INK, width=3)
    return zoom(img, 1 + .2 * max(0, p), .45, .7)


def s13(t, L, cue):
    vo_end = cue["13"] + dur("13.mp3")
    ks = [vo_end + .2, vo_end + .75, vo_end + 1.3]
    k = max([max(0, 1 - (t - kt) / .25) for kt in ks if t >= kt] + [0])
    img = bg_room(*CORR).copy()
    floor_strip(img)
    door_close(img, t, knock=k, weld=1.0)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 90)
    for i, kt in enumerate(ks):
        if kt <= t < kt + .6:
            a = 1 - (t - kt) / .6
            x, y = [(120, 330), (430, 470), (180, 620)][i]
            d.text((x, y - 30 * (1 - a)), "ТУК", font=f, fill=tuple(int(c * (.4 + .6 * a)) for c in YELLOW), stroke_width=6, stroke_fill=INK)
    img = zoom(img, 1.05 + .2 * min(1, t / 4), .5, .45)
    img = shake(img, t, 14 * k)
    return end_card(img, t, ks[-1] + 1.0, ("конец", "первого сезона"), "ждёте второй сезон?")


if __name__ == "__main__":
    s13s, _ = span("s13")
    c13 = {c: s for n, st, l, sc in scenes if n == "s13" for s, c, d in sc}
    vo_end = s13s + c13["13"] + dur("13.mp3")
    s10s, _ = span("s10"); s12s, l12 = span("s12")
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s02")[0] + 3.4, span("s03")[0] + span("s03")[1] * .55, span("s06")[0] + span("s06")[1] * .5],
        knocks=[vo_end + .2, vo_end + .75, vo_end + 1.3],
        rotor=[(s10s, s12s + l12 * .5)])
