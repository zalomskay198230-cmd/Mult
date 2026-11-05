"""ВАХТА. Серия 6. Запуск: python3 seriya06.py ../tts/s06 ../seriya06.mp4"""
from toonlib import *

LINES = {
    "02": "На видео — служебная площадка. Тимур снимал воду. И говорил шёпотом.",
    "03r": "«Тут кто-то есть. Под водой. Он смотрит на меня».",
    "04": "Под решёткой что-то двигалось. Тёмное. Оно взялось за опору и полезло вверх.",
    "05r": "«Оно лезет. Илья, если найдёшь телефон — не верь ему. Не верь мне».",
    "06": "Тимур отступил. Камера дрожала. Над краем решётки показалась голова.",
    "07": "Мокрые волосы. Белая кожа. И лицо. Лицо Тимура.",
    "08": "Телефон упал. Дальше только небо и снег. Сорок секунд закончились.",
    "09": "Я стоял на решётке и не мог пошевелиться. А сзади кто-то сказал:",
    "10t": "Илюха, ты чего тут делаешь?",
    "11": "Это был Тимур. Живой. В сухой одежде.",
}

PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2), ("03r", None)], 0.5),
    ("s03", [("04", 0.2)], 0.4),
    ("s04", [("05r", 0.2)], 0.4),
    ("s05", [("06", 0.2)], 0.4),
    ("s06", [("07", 0.3)], 0.8),
    ("s07", [("08", 0.2)], 0.6),
    ("s08", [("09", 0.2), ("10t", None)], 0.5),
    ("s09", [("11", 0.2)], 3.6),
]
setup(LINES, PLAN)

PALE = (204, 216, 220)
DARK_BODY = (26, 30, 40)
VID_LEN = 40.0


def end_card(img, t, start, n):
    if t <= start:
        return img
    a = min(1, (t - start) / .4)
    img = Image.blend(img, Image.new("RGB", (W, H)), a)
    if a >= 1:
        dd = ImageDraw.Draw(img)
        f2 = ImageFont.truetype(FONT_SUB, 64)
        for j, line in enumerate((f"серия {n}", "скоро")):
            dd.text(((W - f2.getlength(line)) / 2, 520 + j * 84), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


# ---------- «видео с телефона» ----------
def video_t(t):
    """секунда внутри 40-секундного ролика Тимура по общему времени"""
    s2 = span("s02")[0]
    s7, l7 = span("s07")
    return min(VID_LEN, (t - s2) / (s7 + 3.0 - s2) * VID_LEN)


def cam_filter(img, t, shake_amt=4):
    img = shake(img, t, shake_amt)
    a = np.asarray(img).astype(np.float32)
    g = a.mean(-1, keepdims=True)
    a = a * .55 + g * .45
    a = a * np.array([.92, .98, 1.08]) + np.random.default_rng(int(t * 24)).normal(0, 9, a.shape[:2])[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(FONT_B, 28)
    vt = video_t(GLOBAL_T[0])
    d.line([40, H - 60, W - 40, H - 60], fill=(150, 150, 160), width=6)
    d.line([40, H - 60, 40 + (W - 80) * vt / VID_LEN, H - 60], fill=(240, 60, 60), width=6)
    d.ellipse([40 + (W - 80) * vt / VID_LEN - 10, H - 70, 40 + (W - 80) * vt / VID_LEN + 10, H - 50], fill=(240, 240, 240))
    d.text((40, H - 110), f"0:{int(vt):02d} / 0:40", font=f, fill=(240, 240, 240), stroke_width=2, stroke_fill=INK)
    d.text((40, 40), "12:40", font=f, fill=(240, 240, 240), stroke_width=2, stroke_fill=INK)
    return out


GLOBAL_T = [0.0]


def view_down(t, creature_y=None, hands=False, body=False):
    """вид вниз с края решётки: опора уходит в воду"""
    img = vgrad(W, H, (70, 76, 88), (40, 46, 58))
    d = ImageDraw.Draw(img)
    water = 1060
    # опора
    d.rectangle([430, 240, 600, H], fill=(196, 198, 206), outline=INK, width=6)
    d.rectangle([430, 880, 600, 910], fill=(232, 96, 60), outline=INK, width=4)
    d.rectangle([430, 910, 600, H], fill=(40, 42, 48), outline=INK, width=5)
    # существо
    if creature_y is not None:
        cx = 400
        if body:   # тёмный силуэт на опоре, белые руки
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([cx - 80, creature_y - 40, cx + 40, creature_y + 260], radius=40, fill=DARK_BODY + (235,))
            ld.ellipse([cx - 70, creature_y - 130, cx + 30, creature_y - 20], fill=DARK_BODY + (245,))
            img.paste(Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(2))).convert("RGB"))
            d = ImageDraw.Draw(img)
            k = math.sin(t * 5)
            for hx, hy in ((450, creature_y - 60 + 30 * k), (452, creature_y + 60 - 30 * k)):
                d.ellipse([hx - 24, hy - 18, hx + 24, hy + 18], fill=PALE, outline=INK, width=4)
                for f_ in range(3):
                    d.line([hx + 4, hy - 12 + f_ * 12, hx + 34, hy - 10 + f_ * 12], fill=PALE, width=9)
    # вода
    pts = [(0, H)] + [(x, water + 18 * math.sin(x * .02 + t * 2.4)) for x in range(0, W + 10, 10)] + [(W, H)]
    sea = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sea).polygon(pts, fill=SEA + (230,))
    img = Image.alpha_composite(img.convert("RGBA"), sea).convert("RGB")
    d = ImageDraw.Draw(img)
    d.line(pts[1:-1], fill=(200, 220, 236), width=6)
    if creature_y is not None and not body:   # тень под водой с двумя белыми точками
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.ellipse([300, creature_y - 60, 480, creature_y + 120], fill=(10, 12, 18, 200))
        img = Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(14))).convert("RGB")
        d = ImageDraw.Draw(img)
        for ex in (365, 415):
            d.ellipse([ex - 7, creature_y - 7, ex + 7, creature_y + 7], fill=(230, 236, 240))
        if hands:
            d.ellipse([430, creature_y - 70, 470, creature_y - 40], fill=PALE, outline=INK, width=4)
    # край решётки сверху
    d.rectangle([0, 0, W, 240], fill=(44, 50, 62))
    for x in range(-40, W + 40, 34):
        d.line([x, 0, x + 20, 240], fill=STEEL, width=8)
    for y in range(0, 240, 34):
        d.line([0, y, W, y], fill=STEEL, width=8)
    d.line([0, 240, W, 240], fill=INK, width=8)
    for x in range(10, W, 44):
        l = 24 + (x * 7) % 40
        d.polygon([(x - 8, 242), (x + 8, 242), (x, 242 + l)], fill=ICE, outline=INK)
    SNOW.draw(img, t, wind=300)
    return img


def drowned_head(d, x, y, s, t, look=(0, 0)):
    """голова с лицом Тимура: белая кожа, мокрые волосы, неподвижный взгляд"""
    o = int(5 * s)
    R = 92 * s
    for side in (-1, 1):
        d.ellipse([x + side * R - 16 * s, y - 6 * s, x + side * R + 16 * s, y + 34 * s], fill=PALE, outline=INK, width=o)
    d.ellipse([x - R, y - R * 1.05, x + R, y + R * 1.05], fill=PALE, outline=INK, width=o)
    # тени под глазами
    for side in (-1, 1):
        d.arc([x + side * 36 * s - 30 * s, y - 4 * s, x + side * 36 * s + 30 * s, y + 40 * s], 20, 160, fill=(150, 160, 170), width=int(6 * s))
    for side in (-1, 1):
        ex, ey = x + side * 36 * s, y - 14 * s
        d.ellipse([ex - 28 * s, ey - 32 * s, ex + 28 * s, ey + 32 * s], fill=(246, 248, 250), outline=INK, width=o)
        pr = 7 * s
        px, py = ex + look[0] * 6 * s, ey + look[1] * 6 * s
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=INK)
    d.arc([x - 10 * s, y + 14 * s, x + 12 * s, y + 36 * s], 270, 120, fill=INK, width=max(2, o - 1))
    d.line([x - 16 * s, y + 62 * s, x + 16 * s, y + 62 * s], fill=INK, width=o)
    # мокрые волосы: чёлка прядями до бровей
    d.chord([x - R - 4 * s, y - R * 1.12, x + R + 4 * s, y - 30 * s], 180, 360, fill=(22, 22, 26), outline=INK, width=o)
    rnd = random.Random(3)
    for k in range(9):
        hx = x - R * .8 + k * R * .2
        L_ = rnd.uniform(6, 20) * s
        d.line([hx, y - 70 * s, hx + rnd.uniform(-6, 6) * s, y - 62 * s + L_], fill=(22, 22, 26), width=int(12 * s))
    # каска Тимура — тусклая, мокрая
    hc = (184, 146, 70)
    d.chord([x - R, y - R * 1.3, x + R, y + 6 * s], 180, 360, fill=hc, outline=INK, width=o)
    d.rounded_rectangle([x - R - 22 * s, y - 60 * s, x + R + 22 * s, y - 44 * s], radius=int(6 * s), fill=hc, outline=INK, width=o)
    for k in range(3):
        d.line([x - 40 * s + k * 34 * s, y - 60 * s, x - 42 * s + k * 34 * s, y - 34 * s], fill=(120, 160, 196), width=int(5 * s))
    # капли
    for k in range(4):
        ph = (t * .8 + k * .27) % 1
        dx = x + (-60 + k * 40) * s
        dy = y + R * .9 + ph * 200 * s
        d.ellipse([dx - 6 * s, dy - 9 * s, dx + 6 * s, dy + 9 * s], fill=(120, 160, 196), outline=INK, width=2)


def view_back(t, rise, face=False, look=(0, 0)):
    """Тимур отошёл: решётка в перспективе, за краем — пустота; над краем поднимается голова"""
    img = vgrad(W, H, (60, 66, 78), (34, 40, 52))
    d = ImageDraw.Draw(img)
    edge = 720
    if rise > 0:
        hy = edge + 140 - 230 * rise
        drowned_head(d, 360, hy, 1.25, t, look)
        d = ImageDraw.Draw(img)
    # решётка (перед головой — закрывает подбородок)
    d.polygon([(0, edge), (W, edge), (W, H), (0, H)], fill=(44, 50, 62))
    for k in range(-12, 13):
        d.line([360 + k * 40, edge, 360 + k * 130, H], fill=STEEL, width=8)
    for j in range(12):
        y = edge + (H - edge) * (j / 12) ** 1.5
        d.line([0, y, W, y], fill=STEEL, width=8)
    d.line([0, edge, W, edge], fill=INK, width=8)
    if rise > .2:   # белые руки вцепились в край
        for hx in (200, 520):
            d.ellipse([hx - 34, edge - 16, hx + 34, edge + 22], fill=PALE, outline=INK, width=5)
            for f_ in range(4):
                d.line([hx - 24 + f_ * 16, edge + 10, hx - 26 + f_ * 16, edge + 44], fill=PALE, width=10)
    SNOW.draw(img, t, wind=350)
    return img


# ---------- сцены ----------
def s01(t, L):
    return title(t, L, 6)


def s02(t, L):
    GLOBAL_T[0] = span("s02")[0] + t
    return cam_filter(view_down(t), t, 3)


def s03(t, L):
    GLOBAL_T[0] = span("s03")[0] + t
    p = t / L
    if p < .55:
        img = view_down(t, creature_y=1200 - 160 * p / .55, hands=p > .4)
    else:
        img = view_down(t, creature_y=1000 - 320 * (p - .55) / .45, body=True)
    return cam_filter(img, t, 4)


def s04(t, L):
    GLOBAL_T[0] = span("s04")[0] + t
    p = t / L
    img = view_down(t, creature_y=680 - 300 * p, body=True)
    return cam_filter(zoom(img, 1 + .15 * p, .55, .4), t, 7)


def s05(t, L):
    GLOBAL_T[0] = span("s05")[0] + t
    p = t / L
    if p < .35:   # отступает: решётка, край
        img = view_back(t, 0)
        img = zoom(img, 1.25 - .25 * p / .35, .5, .7)
    else:
        img = view_back(t, .45 * (p - .35) / .65)
    return cam_filter(img, t, 8)


def s06(t, L):
    GLOBAL_T[0] = span("s06")[0] + t
    p = t / L
    img = view_back(t, .45 + .55 * min(1, p * 2), look=(0, 0))
    img = zoom(img, 1 + .55 * p, .5, .42)
    return cam_filter(img, t, 3 + 4 * p)


def s07(t, L):
    GLOBAL_T[0] = span("s07")[0] + t
    if t < 3.0:   # телефон падает и крутится
        img = vgrad(W, H, (90, 96, 110), (60, 66, 80))
        SNOW_BIG.draw(img, t)
        ang = min(1, t / .8) * 200 + 10 * math.sin(t * 4)
        img = img.rotate(ang, resample=Image.BICUBIC, expand=False, fillcolor=(44, 50, 62))
        if t > .8:   # лежит: только небо и снег
            img = vgrad(W, H, (86, 92, 106), (70, 76, 90))
            SNOW_BIG.draw(img, t, wind=60)
        return cam_filter(img, t, 0 if t > .8 else 14)
    img = Image.new("RGB", (W, H), (8, 8, 10))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_B, 40)
    d.text(((W - f.getlength("0:40 / 0:40")) / 2, 560), "0:40 / 0:40", font=f, fill=(200, 200, 206))
    cx, cy = W / 2, 720
    d.arc([cx - 50, cy - 50, cx + 50, cy + 50], 40, 330, fill=(200, 200, 206), width=10)   # «повтор»
    d.polygon([(cx + 40, cy - 52), (cx + 66, cy - 22), (cx + 28, cy - 18)], fill=(200, 200, 206))
    return img


def s08(t, L, cue):
    img = vgrad(W, H, (78, 82, 94), (50, 54, 64))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 700, W, 760], fill=SEA)
    d.rectangle([520, -10, 700, 860], fill=(214, 216, 222), outline=INK, width=6)
    d.rectangle([520, 600, 700, 640], fill=(232, 96, 60), outline=INK, width=5)
    d.rectangle([520, 640, 700, 860], fill=(40, 42, 48), outline=INK, width=5)
    grating(img, 860, t, waves=False)
    tt = cue["10t"]
    turned = t > tt + .6
    toon(img, 440, 1180, .95, "ilya", "scared", ("down", "front"), (-1, 0) if turned else (0, .4), t)
    if t > tt - .8:   # Тимур выходит слева
        k = min(1, (t - (tt - .8)) / 1.2)
        toon(img, -150 + 330 * k, 1190, .9, "timur", "smile", ("down", "down"), (1, 0), t,
             walk=t if k < 1 else None, talk=tt <= t < tt + dur("10t.mp3"))
    grating(img, 860, t, base=False)
    SNOW.draw(img, t, wind=400)
    return zoom(img, 1.02, .4, .5)


def s09(t, L):
    img = vgrad(W, H, (78, 82, 94), (50, 54, 64))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 700, W, 760], fill=SEA)
    grating(img, 900, t, waves=False)
    hands = toon(img, W / 2, 1330, 1.5, "timur", "smile", ("down", "down"), (0, 0), t, blink=False)
    d = ImageDraw.Draw(img)
    # одна капля с пальцев — единственная мокрая деталь
    drop0 = L - 4.6
    if t > drop0:
        hx, hy = hands[0]
        dy = min(260, (t - drop0) ** 2 * 400)
        d.ellipse([hx - 9, hy + 24 + dy, hx + 9, hy + 50 + dy], fill=(120, 160, 196), outline=INK, width=3)
    SNOW.draw(img, t, wind=300)
    img = zoom(img, 1 + .25 * min(1, t / (L - 2.2)), .5, .38)
    return end_card(img, t, L - 1.6, 7)


if __name__ == "__main__":
    s2, _ = span("s02"); s7, l7 = span("s07")
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(s2, s7 + 3.0)],
        hits=[span("s06")[0] + .2, s7 + .3, span("s08")[0] + dict((c, s) for s, c, d in [(s, c, d) for n, st, l, sc in scenes if n == "s08" for s, c, d in sc])["10t"]])
