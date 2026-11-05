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
    "10": "Той же ночью Михалыч всё решил. Оно боится огня. А в скважине — газ.",
    "11m": "Спускайте шлюпку. Все. Я открою скважину и подожгу. Без меня огонь не удержать.",
    "12": "Мы спорили. Он не слушал. Даша плакала. Я тащил её к шлюпке.",
    "13": "Когда мы отошли от платформы, над ней поднялся столб огня. Море вокруг светилось.",
    "14": "Из воды выходили тени. И уходили вниз. В глубину. Одна за другой.",
    "15": "Утром нас подобрал вертолёт. С берега. Настоящий.",
    "16": "Михалыча так и не нашли. Но в двадцать первую больше никто не стучит.",
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
    ("s11", [("11m", 0.2)], 0.5),
    ("s12", [("12", 0.2)], 0.5),
    ("s13", [("13", 0.2)], 0.6),
    ("s14", [("14", 0.2)], 0.6),
    ("s15", [("15", 0.2)], 0.6),
    ("s16", [("16", 0.2)], 4.8),
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
    img = bg_room("canteen", (90, 96, 92), (60, 64, 62)).copy()
    img = Image.eval(img, lambda v: int(v * .7))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=(86, 88, 92))
    glow(img, (360, 700), 300, (150, 80, 20), .6 + .3 * math.sin(t * 6))
    toon(img, W / 2, 1330, 1.5, "misha", "serious", ("down", "down"), (.6, -.3), t, blink=False)
    if t > L * .6:   # схема: скважина → факел
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(FONT_SUB, 46)
        d.text((60, 140), "газ", font=f, fill=(240, 240, 240), stroke_width=4, stroke_fill=INK)
        d.line([170, 170, 470, 170], fill=(240, 240, 240), width=8)
        d.polygon([(470, 150), (510, 170), (470, 190)], fill=(240, 240, 240))
        flame(img, 580, 190, t, .8)
    return zoom(img, 1 + .06 * t / L, .5, .42)


def s11(t, L):
    img = bg_room("canteen", (90, 96, 92), (60, 64, 62)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=(86, 88, 92)); d.line([0, 1040, W, 1040], fill=INK, width=6)
    toon(img, 400, 1240, 1.05, "misha", "serious", ("point", "front"), (-.6, 0), t, talk=True)
    toon(img, 90, 1440, .85, "ilya", "worried", ("down", "down"), (1, -.4), t, legs=False)
    toon(img, 660, 1460, .85, "dasha", "sad", ("down", "down"), (-1, -.4), t, legs=False)
    return zoom(img, 1 + .05 * t / L, .5, .45)


def lifeboat(d, x, y, s, t, open_hatch=True):
    o = max(2, int(5 * s))
    d.rounded_rectangle([x - 200 * s, y - 70 * s, x + 200 * s, y + 70 * s], radius=int(70 * s), fill=(240, 110, 40), outline=INK, width=o)
    d.chord([x - 180 * s, y - 130 * s, x + 180 * s, y + 10 * s], 180, 360, fill=(236, 236, 232), outline=INK, width=o)
    for k in range(-2, 3):
        d.ellipse([x + k * 62 * s - 18 * s, y - 70 * s, x + k * 62 * s + 18 * s, y - 34 * s], fill=(60, 100, 140), outline=INK, width=max(2, o - 1))
    d.line([x - 190 * s, y + 20 * s, x + 190 * s, y + 20 * s], fill=INK, width=max(2, o - 1))


def s12(t, L):
    img = vgrad(W, H, (30, 34, 46), (20, 24, 34))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=DECK); d.line([0, 1040, W, 1040], fill=INK, width=6)
    railing(d, 900)
    # шлюпбалка со шлюпкой справа
    d.line([620, 1040, 620, 340, 470, 300], fill=(120, 124, 132), width=16)
    d.line([470, 300, 470, 520], fill=INK, width=4)
    lifeboat(d, 470, 600, .7, t)
    p = t / L
    # Илья тащит Дашу к шлюпке, Михалыч остаётся слева
    toon(img, 110, 1340, .82, "misha", "serious", ("down", "down"), (1, 0), t)
    for who, x0, face in (("ilya", 260, "worried"), ("dasha", 380, "sad")):
        x = x0 + 150 * p
        toon(img, x, 1350, .78, who, face, ("out", "down") if who == "ilya" else ("down", "out"), (1, 0), t, walk=t, bob=4 * abs(math.sin(t * 9)))
        if who == "dasha":   # слёзы
            d = ImageDraw.Draw(img)
            for k in range(2):
                ph = (t * 1.5 + k * .5) % 1
                for side in (-1, 1):
                    ex, ey = x + side * 28, 1350 - 505 * .78 + 10 + ph * 50
                    d.ellipse([ex - 5, ey - 8, ex + 5, ey + 8], fill=(150, 200, 236), outline=INK, width=2)
    STORM.draw(img, t, streak=True)
    return img


def burning(img, t, fire_k, base=900):
    """платформа вдали и столб огня над ней"""
    paste_platform(img, 360, base + 4, .75, lit=False)
    if fire_k > 0:
        cx, top = 420, base - 470 * .75
        h = 520 * fire_k
        glow(img, (cx, top - h * .4), 240 * fire_k + 40, (200, 90, 20), 1)
        d = ImageDraw.Draw(img)
        for k, (w, col) in enumerate(((90, (230, 90, 30)), (60, (250, 150, 40)), (30, (255, 230, 140)))):
            pts = []
            for j in range(12):
                f = j / 11
                y = top - h * f
                ww = w * fire_k * (1 - f * .8) * (1 + .2 * math.sin(t * 9 + j + k))
                pts.append((cx - ww + 10 * math.sin(t * 5 + j), y))
            pts += [(cx + (w * fire_k) * (1 - (j / 11) * .8) * (1 + .2 * math.sin(t * 7 + j)), top - h * j / 11) for j in range(11, -1, -1)]
            d.polygon(pts, fill=col, outline=INK if k == 0 else None)


def sea_glow(img, t, k, horizon=900):
    d = ImageDraw.Draw(img)
    d.rectangle([0, horizon, W, H], fill=SEA)
    for i in range(18):   # отражение огня
        y = horizon + 20 + i * 22
        w = (200 - i * 6) * k
        x = 420 + 20 * math.sin(t * 3 + i)
        d.line([x - w, y, x + w, y], fill=(230, 130, 50), width=6)


def s13(t, L):
    img = vgrad(W, H, (40, 30, 40), (90, 50, 40))
    fire_k = min(1, max(0, (t - 1.6) / 1.4))
    sea_glow(img, t, fire_k)
    burning(img, t, fire_k)
    d = ImageDraw.Draw(img)
    lifeboat(d, 330, 1190 + 8 * math.sin(t * 2), 1.05, t)
    SNOW.draw(img, t, wind=200)
    return shake(img, t, 6 if 1.6 < t < 2.4 else 0)


def s14(t, L):
    img = vgrad(W, H, (40, 30, 40), (90, 50, 40))
    sea_glow(img, t, 1)
    burning(img, t, 1)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    rnd = random.Random(4)
    for i in range(9):   # тени поднимаются из воды и уходят вниз
        x = rnd.uniform(40, 680)
        ph = (t / L * 1.4 + i * .13) % 1
        rise = math.sin(ph * math.pi)
        y = 1000 + i % 3 * 70 - 110 * rise
        ld.rounded_rectangle([x - 34, y - 40, x + 34, y + 160], radius=30, fill=(14, 16, 22, int(230 * rise)))
        ld.ellipse([x - 30, y - 100, x + 30, y - 30], fill=(14, 16, 22, int(230 * rise)))
        for ex in (x - 12, x + 12):
            ld.ellipse([ex - 4, y - 72, ex + 4, y - 64], fill=(230, 236, 240, int(255 * rise)))
    img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
    d = ImageDraw.Draw(img)   # вода закрывает тени снизу
    d.rectangle([0, 1120, W, H], fill=SEA)
    lifeboat(d, 160, 1250 + 8 * math.sin(t * 2), .8, t)
    return zoom(img, 1 + .06 * t / L)


def s15(t, L):
    img = dawn_sky()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 860, W, H], fill=(56, 70, 96))
    for x in range(0, W, 26):
        d.line([x, 880 + (x * 7) % 60, x + 18, 880 + (x * 7) % 60], fill=(230, 170, 140), width=4)
    hx, hy = 400, 360 + 10 * math.sin(t * 2)
    heli(d, hx, hy, .9, t)
    k = min(1, t / (L * .6))
    d.line([hx - 10, hy + 60, hx - 10, hy + 60 + 380 * k], fill=INK, width=4)   # трос лебёдки
    lifeboat(d, 360, 900 + 8 * math.sin(t * 2), 1.0, t)
    toon(img, 300, 960, .55, "ilya", "smile", ("down", "up"), (0, -1), t, legs=False)
    toon(img, 440, 965, .55, "dasha", "smile", ("up", "down"), (0, -1), t, legs=False)
    return img


def s16(t, L, cue):
    vo_end = cue["16"] + dur("16.mp3")
    half = 3.4
    if t < half:   # догорающая платформа на рассвете
        img = dawn_sky()
        d = ImageDraw.Draw(img)
        d.rectangle([0, 820, W, H], fill=(56, 70, 96))
        paste_platform(img, 380, 824, .55, lit=False, alpha=.85)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for i in range(8):
            life = (t * .3 + i / 8) % 1
            r = 30 + 90 * life
            ld.ellipse([430 + 120 * life - r, 560 - 420 * life - r, 430 + 120 * life + r, 560 - 420 * life + r], fill=(70, 70, 76, int(150 * (1 - life))))
        img = Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(8))).convert("RGB")
        return zoom(img, 1.08 - .06 * t / half)
    img = bg_room(*CORR).copy()   # тихая дверь 21
    floor_strip(img)
    door_close(img, t, weld=1.0, frost=False)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 90)
    d.text(((W - f.getlength("21")) / 2, 140), "21", font=f, fill=(190, 190, 196), stroke_width=5, stroke_fill=INK)
    img = Image.eval(img, lambda v: int(v * .8))
    img = zoom(img, 1.02 + .08 * (t - half) / (L - half), .5, .45)
    if t > vo_end + 1.2:
        a = min(1, (t - vo_end - 1.2) / .6)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1 = ImageFont.truetype(FONT_SUB, 140)
            tw = f1.getlength("ВАХТА")
            dd.text(((W - tw) / 2, 470), "ВАХТА", font=f1, fill=YELLOW, stroke_width=5, stroke_fill=(58, 50, 14))
            f2 = ImageFont.truetype(FONT_SUB, 50)
            dd.text(((W - f2.getlength("конец")) / 2, 650), "конец", font=f2, fill=(240, 240, 240), stroke_width=4, stroke_fill=INK)
    return img


if __name__ == "__main__":
    s13s, _ = span("s13"); s15s, l15 = span("s15")
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s02")[0] + 3.4, span("s03")[0] + span("s03")[1] * .55, span("s06")[0] + span("s06")[1] * .5, s13s + 1.6],
        rotor=[(s15s, s15s + l15)])
