"""Полуреалистичный персонаж в стиле графического романа: Макс-курьер.

Рисуется кривыми Катмулла–Рома, с заливкой, светотенью (свет от огня справа),
тонким тёмным контуром. Рисуем с 2× сглаживанием (supersample).
Координаты фигуры — в «пикселях при s=1»: начало (0, 0) — макушка по центру,
рост ≈ 960 (≈ 7 голов).
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter

LINE = (38, 28, 26)
SKIN = (214, 168, 136)
SKIN_SH = (160, 112, 92)
SKIN_HI = (240, 196, 156)
RIM = (255, 170, 90)
HAIR = (78, 54, 38)
HAIR_SH = (50, 34, 26)
JACKET = (196, 152, 58)
JACKET_SH = (140, 104, 40)
JACKET_HI = (226, 186, 92)
PANTS = (56, 60, 68)
PANTS_SH = (38, 40, 48)
BOOTS = (74, 52, 38)
BAG = (48, 128, 136)
BAG_SH = (30, 88, 96)
BANDANA = (176, 50, 44)
BANDANA_SH = (120, 32, 30)
GOG_RIM = (70, 72, 78)
GOG_LENS = (222, 156, 64)
REFL = (196, 200, 204)


def cr(pts, closed=True, n=10):
    """сплайн Катмулла–Рома через точки"""
    out = []
    P = list(pts)
    m = len(P)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed or i > 0 else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed or i + 2 < m else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = .5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = .5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(P[-1])
    return out


class Pen:
    """рисование в локальных координатах фигуры с масштабом и сглаживанием"""

    def __init__(self, size, ox, oy, s, ss=2):
        self.ss = ss
        self.W, self.H = size[0] * ss, size[1] * ss
        self.img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.ox, self.oy, self.s = ox, oy, s

    def T(self, pts):
        k = self.s * self.ss
        return [((self.ox + x * self.s) * self.ss, (self.oy + y * self.s) * self.ss) for x, y in pts]

    def w(self, v):
        return max(1, int(v * self.s * self.ss))

    def shape(self, pts, fill, line=True, lw=2.6, smooth=True, closed=True):
        P = self.T(cr(pts) if smooth else pts)
        if fill is not None:
            self.d.polygon(P, fill=fill)
        if line:
            self.d.line(P + ([P[0]] if closed else []), fill=LINE, width=self.w(lw), joint="curve")
        return P

    def curve(self, pts, col=LINE, lw=2.4, smooth=True):
        P = self.T(cr(pts, closed=False) if smooth else pts)
        self.d.line(P, fill=col, width=self.w(lw), joint="curve")

    def shade(self, base_pts, shade_pts, col, alpha=255, smooth_shade=True, soft=0):
        """тень/свет только внутри формы base; soft — размытие края тени"""
        m1 = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(m1).polygon(self.T(cr(base_pts)), fill=255)
        m2 = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(m2).polygon(self.T(cr(shade_pts) if smooth_shade else shade_pts), fill=alpha)
        if soft:
            m2 = m2.filter(ImageFilter.GaussianBlur(soft * self.s * self.ss))
        m = Image.fromarray(__import__("numpy").minimum(__import__("numpy").asarray(m1), __import__("numpy").asarray(m2)))
        layer = Image.new("RGBA", (self.W, self.H), col + (255,))
        self.img.paste(layer, (0, 0), m)

    def ellipse(self, cx, cy, rx, ry, fill, line=True, lw=2):
        b = self.T([(cx - rx, cy - ry), (cx + rx, cy + ry)])
        self.d.ellipse([b[0][0], b[0][1], b[1][0], b[1][1]], fill=fill, outline=LINE if line else None, width=self.w(lw) if line else 0)

    def result(self):
        return self.img.resize((self.W // self.ss, self.H // self.ss), Image.LANCZOS)


# ---------- части тела ----------
HEAD = [(0, 0), (34, 6), (52, 28), (56, 62), (54, 90), (46, 116), (28, 140), (0, 152), (-28, 140), (-46, 116), (-54, 90), (-56, 62), (-52, 28), (-34, 6)]


def face(p, expr="neutral", look=(0, 0), blink=False):
    # уши
    for sx in (-1, 1):
        p.shape([(sx * 52, 66), (sx * 64, 70), (sx * 66, 90), (sx * 58, 104), (sx * 50, 98)], SKIN)
    p.shape(HEAD, SKIN)
    # светотень: огонь справа — тень лежит серпом вдоль левой стороны лица
    p.shade(HEAD, [(-70, 10), (-40, 14), (-24, 40), (-30, 70), (-24, 100), (-12, 128), (-4, 150), (-70, 170)], SKIN_SH, 235, soft=3)
    p.shade(HEAD, [(-40, 52), (40, 52), (36, 64), (-36, 64)], SKIN_SH, 70, soft=4)          # глазницы
    p.shade(HEAD, [(18, 96), (44, 90), (40, 118), (22, 132), (12, 118)], SKIN_SH, 90, soft=4)  # под скулой
    p.shade(HEAD, [(52, 30), (60, 40), (60, 90), (50, 126), (46, 112), (52, 80), (50, 48)], RIM, 150, soft=2)  # контровой
    # щетина: лёгкая сизая тень по челюсти и редкие точки
    jaw = [(-48, 100), (-30, 106), (-14, 116), (14, 116), (30, 106), (48, 100), (40, 128), (20, 146), (0, 152), (-20, 146), (-40, 128)]
    p.shade(HEAD, jaw, (120, 96, 92), 80, soft=3)
    rnd = random.Random(5)
    for _ in range(90):
        a_ = rnd.uniform(.3, 2.85); r = rnd.uniform(.62, .95)
        x, y = math.cos(a_) * 44 * r, 104 + math.sin(a_) * 44 * r
        if abs(x) < 18 and y < 132:
            continue
        p.ellipse(x, y, .55, .55, (96, 70, 60), line=False)
    # глаза
    eh = 0 if blink else {"neutral": 5, "tense": 4, "smile": 4, "shock": 8, "worried": 6}[expr]
    for sx in (-1, 1):
        cx, cy = sx * 22, 72
        if eh == 0:
            p.curve([(cx - 13, cy), (cx, cy + 2), (cx + 13, cy)], lw=2.6)
        else:
            eye = [(cx - 13, cy), (cx - 4, cy - eh - 1), (cx + 8, cy - eh), (cx + 13, cy), (cx + 4, cy + eh * .7), (cx - 6, cy + eh * .7)]
            p.shape(eye, (236, 230, 222), line=False)
            ix, iy = cx + look[0] * 4, cy + look[1] * 2
            p.ellipse(ix, iy, 5.6, 5.6, (92, 104, 80), line=False)
            p.ellipse(ix, iy, 2.8, 2.8, (20, 18, 18), line=False)
            p.ellipse(ix + 1.8, iy - 2, 1.3, 1.3, (255, 255, 255), line=False)
            p.curve([(cx - 14, cy + 1), (cx - 5, cy - eh - 2), (cx + 8, cy - eh - 1), (cx + 14, cy + 1)], lw=3)   # верхнее веко
            p.curve([(cx - 9, cy + eh * .8 + 2), (cx + 2, cy + eh + 2), (cx + 10, cy + eh * .6 + 2)], col=(150, 104, 86), lw=1.4)   # мешки
        # брови
        tilt = {"neutral": 0, "tense": 4, "smile": -1, "shock": -5, "worried": -4}[expr]
        inner, outer = (sx * 8, 58 + tilt), (sx * 34, 56 - tilt * .4)
        if expr in ("shock",):
            inner, outer = (sx * 8, 50), (sx * 34, 50)
        p.shape([inner, ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 4), outer,
                 ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) + 1)], HAIR_SH, line=False)
    # нос: тень слева, кончик и ноздри
    p.shade(HEAD, [(-4, 72), (-12, 98), (-16, 108), (-2, 110), (-2, 90)], SKIN_SH, 170, soft=1.5)
    p.curve([(7, 90), (10, 102), (8, 107)], lw=1.8)
    p.curve([(-9, 106), (-3, 111), (4, 111), (9, 106)], lw=2)
    p.ellipse(-5, 107, 1.6, 1.2, (110, 70, 60), line=False)
    p.ellipse(5, 107, 1.6, 1.2, (110, 70, 60), line=False)
    p.shape([(-15, 82), (15, 80), (16, 89), (-14, 91)], (232, 208, 168), lw=1.4, smooth=False)
    # шрам
    p.curve([(36, 84), (40, 96), (44, 104)], col=(170, 96, 86), lw=2.2)
    # рот
    my = 124
    if expr == "smile":
        p.curve([(-16, my - 1), (-4, my + 4), (8, my + 3), (17, my - 3)], lw=2.6)
    elif expr == "shock":
        p.shape([(-9, my - 3), (9, my - 3), (8, my + 10), (-8, my + 10)], (90, 30, 30))
    elif expr in ("tense", "worried"):
        p.curve([(-15, my + 2), (0, my), (15, my + 3)], lw=2.6)
    else:
        p.curve([(-14, my), (0, my + 1), (14, my - 1)], lw=2.6)
    p.curve([(-8, my + 9), (0, my + 10), (8, my + 9)], col=(150, 100, 84), lw=1.6)   # нижняя губа
    # волосы: объём сверху, неровная чёлка прядями
    hair = [(-62, 66), (-66, 30), (-58, -2), (-40, -24), (-14, -36), (14, -36), (40, -26), (58, -4), (66, 28), (62, 66),
            (58, 38), (46, 26), (34, 32), (20, 24), (6, 34), (-8, 28), (-22, 40), (-36, 34), (-48, 48), (-56, 44)]
    p.shape(hair, HAIR)
    p.shade(hair, [(-80, -50), (-6, -50), (-18, 20), (-30, 70), (-80, 70)], HAIR_SH, 255, soft=3)
    p.shade(hair, [(20, -40), (50, -30), (40, -10), (14, -20)], (110, 80, 56), 200, soft=3)   # блик
    for k, (x0, x1) in enumerate(((-46, -40), (-30, -24), (-14, -4), (6, 12), (24, 28), (40, 46))):
        p.curve([(x0, -24 + abs(x0) * .1), (x0 + 4, 4), (x1, 34)], col=HAIR_SH, lw=1.4)
    # гогглы на лбу
    p.shape([(-60, 12), (60, 12), (60, 24), (-60, 24)], (40, 40, 44), lw=1.6, smooth=False)
    for sx in (-1, 1):
        p.ellipse(sx * 24, 14, 17, 15, GOG_RIM, lw=2.2)
        p.ellipse(sx * 24, 14, 11, 10, GOG_LENS, lw=1.6)
        p.ellipse(sx * 24 + 4, 10, 3.5, 2.5, (255, 232, 180), line=False)


def arm(p, side, pose):
    """рука: side −1 — левая на экране, +1 — правая"""
    sx = side
    sh = (sx * 104, 214)
    if pose == "out":    # рука в сторону с посылкой
        el, wr = (sx * 190, 300), (sx * 270, 360)
    elif pose == "strap":   # держит лямку рюкзака
        el, wr = (sx * 132, 360), (sx * 70, 300)
    else:
        el, wr = (sx * 128, 380), (sx * 122, 532)
    sleeve = [(sh[0] - sx * 26, sh[1] - 10), (sh[0] + sx * 22, sh[1] - 4), (el[0] + sx * 22, el[1]), (wr[0] + sx * 18, wr[1]),
              (wr[0] - sx * 16, wr[1] + 4), (el[0] - sx * 20, el[1] + 4), (sh[0] - sx * 30, sh[1] + 60)]
    p.shape(sleeve, JACKET)
    if sx < 0:
        p.shade(sleeve, [(sh[0] - 60, 150), (sh[0] + 4, 150), (el[0] + 6, el[1]), (wr[0] + 2, wr[1] + 10), (wr[0] - 60, wr[1] + 20)], JACKET_SH, 255)
    else:
        p.shade(sleeve, [(sh[0] + 14, 180), (sh[0] + 60, 180), (wr[0] + 60, wr[1]), (wr[0] + 10, wr[1])], RIM, 120)
    # светоотражающая полоса на рукаве
    t = .55
    a = (el[0] + (wr[0] - el[0]) * t, el[1] + (wr[1] - el[1]) * t)
    p.curve([(a[0] - sx * 20, a[1] - 4), (a[0] + sx * 20, a[1] + 2)], col=REFL, lw=7)
    p.curve([(el[0] - sx * 6, el[1] - 10), (el[0] + sx * 12, el[1] + 6)], col=JACKET_SH, lw=2)   # складка локтя
    # кисть
    hand = [(wr[0] - 14, wr[1]), (wr[0] + 14, wr[1]), (wr[0] + 16, wr[1] + 30), (wr[0] + 6, wr[1] + 44), (wr[0] - 8, wr[1] + 42), (wr[0] - 16, wr[1] + 26)]
    p.shape(hand, SKIN)
    if sx < 0:
        p.shade(hand, [(wr[0] - 30, wr[1] - 10), (wr[0], wr[1] - 10), (wr[0] - 2, wr[1] + 60), (wr[0] - 30, wr[1] + 60)], SKIN_SH)
    p.curve([(wr[0] - 6, wr[1] + 28), (wr[0] + 8, wr[1] + 30)], col=(150, 104, 86), lw=1.4)
    return (wr[0], wr[1] + 22)


def max_figure(size, ox, oy, s, expr="neutral", arms=("down", "down"), look=(0, 0), blink=False, head_only=False):
    """возвращает RGBA-картинку с Максом. (ox, oy) — макушка на итоговом холсте."""
    p = Pen(size, ox, oy, s)
    if not head_only:
        # рюкзак за спиной
        bag = [(-132, 168), (132, 168), (134, 470), (-134, 470)]
        p.shape(bag, BAG, smooth=False)
        p.shade(bag, [(-140, 160), (-40, 160), (-50, 480), (-140, 480)], BAG_SH, 255, smooth_shade=False)
        p.curve([(-128, 200), (128, 200)], col=BAG_SH, lw=3, smooth=False)
        p.shape([(-120, 230), (-96, 226), (-100, 290), (-122, 292)], (200, 196, 180), lw=1.4, smooth=False)   # скотч
        # ноги
        for sx in (-1, 1):
            leg = [(sx * 8, 500), (sx * 72, 500), (sx * 66, 700), (sx * 60, 900), (sx * 18, 900), (sx * 14, 700)]
            p.shape(leg, PANTS)
            if sx < 0:
                p.shade(leg, [(-90, 490), (-40, 490), (-36, 910), (-90, 910)], PANTS_SH)
            p.shape([(sx * 16, 676), (sx * 66, 676), (sx * 64, 730), (sx * 18, 730)], (44, 46, 52), lw=1.8)   # наколенник
            p.curve([(sx * 30, 760), (sx * 46, 790), (sx * 40, 840)], col=PANTS_SH, lw=1.6)
            p.shape([(sx * 14, 892), (sx * 64, 892), (sx * 70, 930), (sx * 82, 944), (sx * 80, 962), (sx * 10, 962), (sx * 10, 930)], BOOTS)
            p.curve([(sx * 12, 950), (sx * 80, 950)], col=(46, 32, 24), lw=3, smooth=False)
        # руки сзади (рукава) рисуем до торса
        hand_pts = [arm(p, -1, arms[0]), arm(p, 1, arms[1])]
        # торс — куртка
        torso = [(-104, 198), (-40, 178), (0, 184), (40, 178), (104, 198), (108, 300), (94, 420), (88, 520), (0, 528), (-88, 520), (-94, 420), (-108, 300)]
        p.shape(torso, JACKET)
        p.shade(torso, [(-130, 160), (-24, 160), (-34, 300), (-30, 540), (-130, 540)], JACKET_SH)
        p.shade(torso, [(78, 190), (120, 190), (120, 540), (84, 540)], RIM, 110)
        p.shade(torso, [(-120, 470), (120, 470), (120, 540), (-120, 540)], JACKET_SH, 140, smooth_shade=False)
        p.curve([(0, 186), (2, 360), (0, 526)], lw=2)   # молния
        for k, (a, b) in enumerate((((-80, 300), (-40, 330)), ((50, 260), (80, 300)), ((-60, 420), (-20, 440)), ((30, 440), (70, 460)))):
            p.curve([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 6), b], col=JACKET_SH, lw=2)   # складки
        p.shape([(-82, 340), (-40, 338), (-40, 378), (-84, 380)], (150, 140, 112), lw=1.6, smooth=False)   # заплатка
        for k in range(4):
            p.curve([(-78 + k * 11, 336), (-76 + k * 11, 344)], lw=1.2, smooth=False)
        # лямки и стяжка
        for sx in (-1, 1):
            p.shape([(sx * 44, 182), (sx * 66, 184), (sx * 62, 470), (sx * 42, 470)], (44, 46, 52), lw=1.6, smooth=False)
        p.shape([(-60, 300), (60, 300), (60, 314), (-60, 314)], (44, 46, 52), lw=1.4, smooth=False)
        p.ellipse(0, 307, 9, 9, (120, 122, 128), lw=1.4)
        # респиратор на лямке
        p.ellipse(54, 360, 22, 22, (96, 100, 106), lw=2)
        p.ellipse(54, 360, 12, 12, (60, 62, 68), lw=1.4)
        # шея + бандана
        neck = [(-24, 140), (24, 140), (26, 196), (-26, 196)]
        p.shape(neck, SKIN, smooth=False)
        p.shade(neck, [(-40, 130), (6, 130), (6, 200), (-40, 200)], SKIN_SH, smooth_shade=False)
        band = [(-52, 176), (52, 176), (40, 214), (6, 262), (-30, 222)]
        p.shape(band, BANDANA)
        p.shade(band, [(-60, 170), (-4, 170), (0, 270), (-60, 270)], BANDANA_SH)
        p.curve([(-30, 196), (0, 230), (28, 200)], col=BANDANA_SH, lw=1.6)
        # ремень и края
        p.curve([(-96, 512), (96, 512)], col=JACKET_SH, lw=3)
    face(p, expr, look, blink)
    out = p.result()
    hands = [] if head_only else [(ox + h[0] * s, oy + h[1] * s) for h in hand_pts]
    return out, hands
