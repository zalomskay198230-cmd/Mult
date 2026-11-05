"""ВАХТА. Серия 4. Запуск: python3 seriya04.py ../tts/s04 ../seriya04.mp4"""
from toonlib import *

LINES = {
    "02": "После той записи Даша перестала спать. Сидела в радиорубке и листала журнал связи.",
    "03": "Каждый день — запись. Погода, частоты, позывные. А одна страница вырвана.",
    "04": "Даша заштриховала карандашом следующий лист. Кто писал — давил сильно. Текст проступил.",
    "05": "Это была радиограмма с берега. За день до того, как пропала связь.",
    "06r": "«Северная-семь. Эвакуацию не проводить. Персонал на берег не возвращать. Ждать».",
    "07": "Внизу почерк Михалыча: «Принял. Экипажу не сообщать».",
    "08": "А ниже ещё одна строчка: «Двадцать первую не открывать».",
    "09": "Мы пошли к Михалычу. Каюта пустая. А на столе — его рация. Включённая.",
    "10": "Из неё шёл голос Михалыча. Он с кем-то говорил. Но берег молчит уже четыре дня.",
    "10r": "«Да. Понял. Они ещё ничего не знают».",
}

PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2)], 0.4),
    ("s03", [("03", 0.2)], 0.5),
    ("s04", [("04", 0.2)], 0.6),
    ("s05", [("05", 0.2)], 0.4),
    ("s06", [("06r", 0.3)], 0.6),
    ("s07", [("07", 0.2)], 0.6),
    ("s08", [("08", 0.2)], 1.2),
    ("s09", [("09", 0.2)], 0.5),
    ("s10", [("10", 0.2), ("10r", None)], 3.0),
]
setup(LINES, PLAN)

PAPER, PAPER_D, BLUE_INK = (240, 234, 214), (214, 206, 182), (52, 64, 120)
GRAPH = (92, 92, 100)
F_HAND = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBoldItalic.otf", 29)
F_HAND_B = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-BoldItalic.otf", 32)
RG_LINES = ["РАДИОГРАММА · 31.10", "", "СЕВЕРНАЯ-7.", "ЭВАКУАЦИЮ НЕ ПРОВОДИТЬ.", "ПЕРСОНАЛ НА БЕРЕГ", "НЕ ВОЗВРАЩАТЬ.", "ЖДАТЬ."]
NOTE1 = "Принял. Экипажу не сообщать."
NOTE2 = "21-ю НЕ ОТКРЫВАТЬ"


def scribble(d, x, y, w, seed, col=BLUE_INK, width=3):
    rnd = random.Random(seed)
    pts, cx = [], x
    while cx < x + w:
        pts.append((cx, y + rnd.uniform(-9, 9)))
        cx += rnd.uniform(6, 14)
    d.line(pts, fill=col, width=width, joint="curve")


def notebook(img, t, torn=True, box=(40, 120, 680, 1100)):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    xm = (x0 + x1) / 2
    d.rectangle([x0 + 12, y0 + 14, x1 + 12, y1 + 14], fill=(50, 50, 56))
    d.rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], fill=(70, 50, 40), outline=INK, width=6)   # обложка
    d.rectangle([x0, y0, xm, y1], fill=PAPER, outline=INK, width=4)
    # левая страница: записи
    for k, yy in enumerate(range(int(y0) + 60, int(y1) - 30, 46)):
        d.line([x0 + 20, yy + 14, xm - 20, yy + 14], fill=(190, 200, 220), width=2)
        if k % 4 == 0:
            d.text((x0 + 24, yy - 14), f"{20 + k // 4}.10", font=ImageFont.truetype(FONT_B, 20), fill=(170, 60, 60))
            scribble(d, x0 + 100, yy, xm - x0 - 130, k)
        else:
            scribble(d, x0 + 30, yy, xm - x0 - 60 - (k * 37) % 80, k)
    # правая: вырванная страница — рваный край у корешка
    rnd = random.Random(5)
    pts = [(xm, y0)]
    for yy in range(int(y0), int(y1), 18):
        pts.append((xm + rnd.uniform(10, 34), yy + 9))
    pts += [(xm, y1)]
    d.rectangle([xm, y0, x1, y1], fill=PAPER_D, outline=INK, width=4)   # следующий лист
    d.polygon(pts, fill=PAPER, outline=INK)
    d.line([xm, y0, xm, y1], fill=INK, width=6)
    return xm


def page(img, box=(70, 110, 650, 1150)):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle([x0 + 14, y0 + 16, x1 + 14, y1 + 16], fill=(50, 50, 56))
    d.rectangle(box, fill=PAPER_D, outline=INK, width=6)
    return d


def revealed_text(img, box, reveal, t, upto=len(RG_LINES), hl=-1, notes=0):
    """штриховка карандашом, сквозь неё проступают белые буквы"""
    x0, y0, x1, y1 = box
    hatch = Image.new("RGB", (W, H), PAPER_D)
    hd = ImageDraw.Draw(hatch)
    rnd = random.Random(2)
    for k in range(700):
        yy = y0 + 20 + k * (y1 - y0 - 40) / 700
        hd.line([x0 + 24, yy + rnd.uniform(-6, 6), x1 - 24, yy + rnd.uniform(-20, 20)], fill=GRAPH, width=3)
    td = ImageDraw.Draw(hatch)
    y = y0 + 50
    for i, ln in enumerate(RG_LINES[:upto]):
        if ln:
            f = F_HAND_B if i == 0 else F_HAND
            if i == hl:
                td.rectangle([x0 + 40, y - 6, x0 + 60 + f.getlength(ln), y + 48], fill=(220, 190, 60))
            td.text((x0 + 50, y), ln, font=f, fill=(246, 244, 236))
        y += 56
    if notes >= 1:
        y += 30
        td.text((x0 + 50, y), NOTE1, font=F_HAND, fill=(246, 244, 236))
        scribble(td, x0 + 330, y + 70, 160, 77, col=(246, 244, 236), width=5)   # подпись
        y += 120
    if notes >= 2:
        td.text((x0 + 50, y), NOTE2, font=ImageFont.truetype(FONT_SUB, 46), fill=(250, 120, 110))
    # маска штриховки растёт сверху вниз зигзагом
    m = Image.new("L", (W, H))
    md = ImageDraw.Draw(m)
    yb = y0 + (y1 - y0) * reveal
    md.rectangle([x0 + 20, y0 + 20, x1 - 20, max(y0 + 20, yb - 40)], fill=255)
    wav = [(x, yb - 40 + 30 * math.sin(x * .05 + t * 9)) for x in range(int(x0 + 20), int(x1 - 20), 10)]
    md.polygon([(x0 + 20, yb - 40)] + wav + [(x1 - 20, yb - 40)], fill=255)
    img.paste(hatch, (0, 0), m.filter(ImageFilter.GaussianBlur(3)))
    return yb


def pencil(img, x, y):
    d = ImageDraw.Draw(img)
    a = -0.9
    L_, w = 330, 34
    ca, sa = math.cos(a), math.sin(a)
    def P(u, v):
        return (x + u * ca - v * sa, y + u * sa + v * ca)
    d.polygon([P(0, 0), P(40, -w / 2), P(40, w / 2)], fill=(226, 196, 150), outline=INK)
    d.polygon([P(0, 0), P(14, -6), P(14, 6)], fill=(60, 60, 66))
    d.polygon([P(40, -w / 2), P(L_, -w / 2), P(L_, w / 2), P(40, w / 2)], fill=(240, 196, 50), outline=INK)
    d.line([P(40, 0), P(L_, 0)], fill=(210, 160, 30), width=4)
    d.polygon([P(L_, -w / 2), P(L_ + 40, -w / 2), P(L_ + 40, w / 2), P(L_, w / 2)], fill=(230, 130, 140), outline=INK)


# ---------- сцены ----------
def s01(t, L):
    return title(t, L, 4)


def desk_lamp(img, x, y):
    d = ImageDraw.Draw(img)
    glow(img, (x, y + 60), 200, (90, 76, 36), .9)
    d.polygon([(x - 70, y + 40), (x + 70, y + 40), (x + 30, y - 20), (x - 30, y - 20)], fill=(60, 120, 90), outline=INK)
    d.line([x, y - 20, x + 60, y - 160, x + 120, y + 300], fill=INK, width=10)


def s02(t, L):
    img = bg_room("radio", (70, 92, 88), (46, 58, 56)).copy()
    img = Image.eval(img, lambda v: int(v * .7))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1000, W, H], fill=(84, 88, 90), outline=INK, width=6)
    desk_lamp(img, 160, 700)
    toon(img, 420, 1210, 1.0, "dasha", "sad", ("front", "front"), (-.3, .8), t, legs=False, blink=True)
    d = ImageDraw.Draw(img)
    d.polygon([(230, 1020), (560, 1020), (600, 1100), (190, 1100)], fill=PAPER, outline=INK)   # журнал на столе
    d.line([395, 1020, 395, 1100], fill=INK, width=4)
    # часы «04:12»
    f = ImageFont.truetype(FONT_B, 44)
    d.rounded_rectangle([470, 140, 670, 220], radius=12, fill=(20, 26, 24), outline=INK, width=5)
    d.text((492, 152), "04:12", font=f, fill=(240, 80, 70))
    return zoom(img, 1 + .05 * t / L, .5, .55)


def s03(t, L):
    img = vgrad(W, H, (70, 60, 52), (50, 42, 36))
    xm = notebook(img, t)
    p = min(1, max(0, (t - L * .55) / .8))
    img = zoom(img, 1 + .5 * p, .5 + .25 * p, .5)   # наезд на рваный край
    return img


def s04(t, L):
    img = vgrad(W, H, (70, 60, 52), (50, 42, 36))
    box = (70, 110, 650, 1150)
    page(img, box)
    reveal = min(1, max(0, (t - .6) / (L - 1.4)))
    yb = revealed_text(img, box, reveal, t, notes=2)
    if reveal < 1:
        px = 360 + 230 * math.sin(t * 9)
        pencil(img, px, yb - 30)
    return zoom(img, 1.02)


def s05(t, L):
    img = bg_room("radio", (70, 92, 88), (46, 58, 56)).copy()
    img = Image.eval(img, lambda v: int(v * .75))
    desk_lamp(img, 120, 640)
    hands = toon(img, W / 2, 1300, 1.4, "dasha", "shock" if t > 1.2 else "worried", ("front", "front"), (0, .8), t)
    d = ImageDraw.Draw(img)
    cx, cy = (hands[0][0] + hands[1][0]) / 2, hands[0][1]
    d.rectangle([cx - 160, cy - 40, cx + 160, cy + 210], fill=PAPER_D, outline=INK, width=5)
    for k in range(6):
        d.line([cx - 130, cy - 10 + k * 34, cx + 130, cy - 10 + k * 34], fill=GRAPH, width=14)
    for hp in hands:
        hand(d, hp, 1.4)
    return zoom(img, 1 + .06 * t / L, .5, .45)


def s06(t, L, cue):
    img = vgrad(W, H, (70, 60, 52), (50, 42, 36))
    box = (70, 110, 650, 1150)
    page(img, box)
    p = (t - cue["06r"]) / dur("06r.mp3")
    hl = 2 if p < .2 else 3 if p < .5 else 4 if p < .72 else 5 if p < .86 else 6
    revealed_text(img, box, 1.0, t, notes=0, hl=hl if p > 0 else -1)
    return zoom(img, 1.15, .5, .1 + .3 * min(1, max(0, p)))


def s07(t, L):
    img = vgrad(W, H, (70, 60, 52), (50, 42, 36))
    box = (70, 110, 650, 1150)
    page(img, box)
    revealed_text(img, box, 1.0, t, notes=1)
    d = ImageDraw.Draw(img)
    if t > 1.0:  # красный круг вокруг подписи
        a = min(1, (t - 1.0) / .6)
        d.arc([80, 560, 640, 700], -90, -90 + 360 * a, fill=(230, 60, 50), width=8)
    return zoom(img, 1.3, .5, .5)


def s08(t, L):
    if t > L - 1.3:   # врезка: заваренная дверь
        img = bg_room("corr_bg", (140, 144, 150), (100, 104, 110)).copy()
        floor_strip(img)
        door_close(img, t, weld=1.0)
        return shake(zoom(img, 1.2, .8, .5), t, 6)
    img = vgrad(W, H, (70, 60, 52), (50, 42, 36))
    box = (70, 110, 650, 1150)
    page(img, box)
    revealed_text(img, box, 1.0, t, notes=2 if t > .9 else 1)
    img = zoom(img, 1.3 + .1 * t / L, .5, .5)
    return shake(img, t, 5 if .9 < t < 1.4 else 0)


def cabin(img, t, radio_k=1.0):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 940, W, H], fill=(96, 92, 88)); d.line([0, 940, W, 940], fill=INK, width=6)
    # койка
    d.rectangle([20, 700, 300, 900], fill=(60, 84, 140), outline=INK, width=6)
    d.rounded_rectangle([30, 670, 140, 720], radius=16, fill=(236, 236, 232), outline=INK, width=5)
    d.rectangle([20, 900, 300, 940], fill=(120, 120, 126), outline=INK, width=5)
    # иллюминатор
    d.ellipse([90, 230, 250, 390], fill=(150, 150, 156), outline=INK, width=6)
    d.ellipse([110, 250, 230, 370], fill=(30, 36, 52), outline=INK, width=5)
    # стол и рация
    d.rectangle([380, 760, 700, 790], fill=(150, 112, 80), outline=INK, width=5)
    d.rectangle([400, 790, 420, 940], fill=(120, 90, 64), outline=INK, width=4)
    d.rectangle([660, 790, 680, 940], fill=(120, 90, 64), outline=INK, width=4)
    d.rounded_rectangle([440, 640, 640, 760], radius=14, fill=(80, 86, 84), outline=INK, width=6)
    d.line([600, 640, 630, 540], fill=INK, width=8)
    on = (int(t * 3) % 2 == 0) or radio_k > 1
    d.ellipse([600, 660, 624, 684], fill=(90, 255, 140) if on else (30, 70, 40), outline=INK, width=3)
    if on:
        glow(img, (612, 672), 40, (20, 140, 60), 1)
    for gx in range(460, 580, 16):
        for gy in range(660, 740, 16):
            d.ellipse([gx, gy, gx + 8, gy + 8], fill=(50, 54, 52))
    # фуражка/кружка Михалыча
    d.rectangle([660, 710, 690, 760], fill=(236, 236, 232), outline=INK, width=4)


def s09(t, L):
    img = bg_room("cabin", (150, 140, 124), (110, 104, 94)).copy()
    cabin(img, t)
    toon(img, 220, 1450, .82, "dasha", "worried", ("down", "down"), (1, 0), t, legs=False)
    toon(img, 470, 1500, .9, "ilya", "worried" if t < L * .6 else "scared", ("down", "down"), (.6, -.3), t, legs=False)
    return zoom(img, 1 + .05 * t / L, .7, .5)


def s10(t, L, cue):
    rt = cue["10r"]
    img = bg_room("cabin", (150, 140, 124), (110, 104, 94)).copy()
    speaking = rt <= t < rt + dur("10r.mp3")
    cabin(img, t, radio_k=2 if speaking else 1)
    d = ImageDraw.Draw(img)
    if speaking or t < rt:
        rnd = random.Random(int(t * 20))
        for i in range(3):   # звуковые волны из динамика
            r = 40 + ((t * 120 + i * 50) % 150)
            a = 1 - (r - 40) / 150
            d.arc([510 - r, 700 - r, 510 + r, 700 + r], 200, 340, fill=tuple(int(90 + 160 * a) for _ in range(3)), width=5)
    z = 1.0 + .9 * min(1, t / max(1, rt))
    img = zoom(img, z, 1.0, .6)
    end = rt + dur("10r.mp3") + 1.2
    if t > end:
        a = min(1, (t - end) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f2 = ImageFont.truetype(FONT_SUB, 64)
            for j, line in enumerate(("серия 5", "скоро")):
                dd.text(((W - f2.getlength(line)) / 2, 520 + j * 84), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    s10s, l10 = span("s10")
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(span("s06")[0], span("s06")[0] + span("s06")[1]), (s10s, s10s + l10 - 2.0)],
        hits=[span("s08")[0] + 1.0, span("s10")[0] + l10 - 2.6])
