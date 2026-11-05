"""Скелетная анимация Макса: вид спереди (стоит, идёт к камере) и сбоку (идёт, бежит).

Все углы в градусах. Нога/рука: угол от вертикали вниз, «+» — вперёд (по ходу движения),
колено/локоть — сгиб сустава. Земля — y = GROUND в локальных координатах (подошва).
"""
import math, random
from PIL import Image, ImageDraw
import realman as R
from realman import Pen, cr, LINE

GROUND = 962
HIP_Y, SH_Y = 510, 212
THIGH, SHIN = 200, 196
UPPER, FORE = 160, 150


def rad(a):
    return a * math.pi / 180


def seg_poly(a, b, w1, w2):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    return [(a[0] + nx * w1 / 2, a[1] + ny * w1 / 2), (b[0] + nx * w2 / 2, b[1] + ny * w2 / 2),
            (b[0] - nx * w2 / 2, b[1] - ny * w2 / 2), (a[0] - nx * w1 / 2, a[1] - ny * w1 / 2)]


def limb(p, joints, widths, col, dark=None, lw=2.6):
    """конечность из нескольких сегментов: сначала общий контур, потом заливка"""
    segs = list(zip(joints[:-1], joints[1:], widths[:-1], widths[1:]))
    for pass_ in (0, 1):
        for a, b, w1, w2 in segs:
            grow = 0 if pass_ else lw * 2
            P = p.T(seg_poly(a, b, w1 + grow, w2 + grow))
            p.d.polygon(P, fill=LINE if not pass_ else col)
        for j, w in zip(joints, widths):
            r = (w + (0 if pass_ else lw * 2)) / 2
            p.ellipse(j[0], j[1], r, r, LINE if not pass_ else col, line=False)
    if dark:
        for a, b, w1, w2 in segs:   # тень по одной стороне
            P = seg_poly(a, b, w1 * .45, w2 * .45)
            off = ((w1 + w2) / 4 * .55)
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            P = [(x + nx * off, y + ny * off) for x, y in P]
            p.d.polygon(p.T(P), fill=dark)


def hand_at(p, w, ang=0, dark=False):
    c = R.SKIN_SH if dark else R.SKIN
    p.ellipse(w[0], w[1] + 14, 15, 20, c, lw=2.2)


def boot(p, ankle, foot_ang, facing=1, dark=False, scale=1.0):
    """ботинок сбоку: носок по направлению facing"""
    a = rad(foot_ang)
    pts = [(-16, -14), (18, -16), (30, 2), (64, 6), (70, 22), (-18, 22)]
    P = []
    for x, y in pts:
        x *= facing * scale; y *= scale
        P.append((ankle[0] + x * math.cos(a) - y * math.sin(a) * facing, ankle[1] + x * math.sin(a) * facing + y * math.cos(a)))
    p.shape(P, (52, 36, 28) if dark else R.BOOTS, smooth=False, lw=2.4)


# ---------- вид сбоку (лицом вправо) ----------
def leg_joints(hip, th, kn):
    knee = (hip[0] + THIGH * math.sin(rad(th)), hip[1] + THIGH * math.cos(rad(th)))
    ank = (knee[0] + SHIN * math.sin(rad(th - kn)), knee[1] + SHIN * math.cos(rad(th - kn)))
    return knee, ank


def arm_joints(sh, a, e):
    el = (sh[0] + UPPER * math.sin(rad(a)), sh[1] + UPPER * math.cos(rad(a)))
    wr = (el[0] + FORE * math.sin(rad(a + e)), el[1] + FORE * math.cos(rad(a + e)))
    return el, wr


def cycle(mode, ph):
    """углы для фазы ph (радианы): бедро, колено, плечо, локоть"""
    if mode == "run":
        th = 42 * math.sin(ph)
        kn = 12 + 95 * max(0, math.cos(ph)) ** 1.3
        arm = -50 * math.sin(ph)
        el = 85
    else:   # шаг
        th = 24 * math.sin(ph)
        kn = 4 + 38 * max(0, math.cos(ph)) ** 1.6
        arm = -22 * math.sin(ph)
        el = 18 + 8 * max(0, -math.sin(ph))
    return th, kn, arm, el


def side_head(p, expr="neutral", blink=False):
    head = [(-50, 30), (-30, 4), (0, -4), (30, 6), (48, 30), (52, 58), (56, 74), (66, 94), (56, 102), (56, 112), (52, 118),
            (54, 126), (46, 142), (24, 150), (0, 146), (-14, 130), (-40, 112), (-54, 80)]
    p.shape(head, R.SKIN)
    p.shade(head, [(-70, -20), (6, -20), (2, 60), (8, 140), (-70, 160)], R.SKIN_SH, 220, soft=3)
    p.shade(head, [(44, 30), (60, 50), (70, 94), (54, 140), (48, 120), (52, 80)], R.RIM, 140, soft=2)
    p.shade(head, [(-4, 104), (40, 112), (50, 130), (30, 150), (0, 146), (-14, 128)], (120, 96, 92), 80, soft=3)   # щетина
    # ухо
    p.shape([(-6, 70), (8, 72), (10, 92), (0, 104), (-10, 96)], R.SKIN_SH)
    # глаз в профиль
    if blink:
        p.curve([(30, 74), (40, 76)], lw=2.4)
    else:
        p.shape([(28, 72), (38, 68), (44, 74), (36, 79)], (236, 230, 222), line=False)
        p.ellipse(39, 73, 3.4, 3.8, (40, 40, 34), line=False)
        p.curve([(27, 72), (38, 66), (45, 73)], lw=2.6)
    p.shape([(26, 60), (44, 56), (48, 60), (30, 64)], R.HAIR_SH, line=False)   # бровь
    # нос, пластырь, рот
    p.shape([(50, 84), (60, 82), (62, 90), (52, 92)], (232, 208, 168), lw=1.4, smooth=False)
    mouth = {"shock": [(46, 118), (54, 116), (54, 126), (46, 126)], "smile": None}.get(expr)
    if mouth:
        p.shape(mouth, (90, 30, 30), smooth=False)
    else:
        p.curve([(42, 120), (54, 118 if expr != "smile" else 116)], lw=2.2)
    # волосы
    hair = [(-56, 76), (-60, 30), (-40, -6), (-10, -22), (20, -18), (44, 4), (54, 30), (46, 34), (38, 26), (26, 36), (14, 24),
            (0, 40), (-20, 44), (-26, 70), (-40, 100)]
    p.shape(hair, R.HAIR)
    p.shade(hair, [(-80, -40), (0, -40), (-10, 120), (-80, 120)], R.HAIR_SH, 255, soft=3)
    # ремень гогглов и линза спереди
    p.curve([(-54, 30), (0, 18), (40, 16)], col=(40, 40, 44), lw=10)
    p.ellipse(34, 14, 12, 14, R.GOG_RIM, lw=2)
    p.ellipse(38, 14, 7, 9, R.GOG_LENS, lw=1.4)


def side_figure(size, ox, ground_y, s, t, mode="walk", speed=1.0, expr="neutral", blink=None):
    """Макс сбоку. ox — центр бёдер по x, ground_y — линия земли на холсте."""
    f = (1.0 if mode == "walk" else 1.55) * speed
    ph = 2 * math.pi * f * t
    near = cycle(mode, ph)
    far = cycle(mode, ph + math.pi)
    hip = (0, HIP_Y)
    kn_n, an_n = leg_joints(hip, near[0], near[1])
    kn_f, an_f = leg_joints(hip, far[0], far[1])
    low = max(an_n[1], an_f[1]) + 22
    lift = (GROUND - low)
    if mode == "run":
        lift -= 16 * abs(math.sin(ph))   # фаза полёта
    oy = ground_y - (GROUND - lift) * s - (lift * s - lift * s)   # подошва на земле
    oy = ground_y - GROUND * s + lift * s
    p = Pen(size, ox, oy, s)
    lean = .16 if mode == "run" else .04
    # дальняя рука и нога (темнее)
    shoulder = (0, SH_Y)
    def U(pt):   # наклон корпуса вперёд вокруг бедра
        return (pt[0] + lean * (HIP_Y - pt[1]), pt[1])
    el_f, wr_f = arm_joints(U(shoulder), far[2], far[3])
    limb(p, [U(shoulder), el_f, wr_f], [44, 38, 32], R.JACKET_SH)
    hand_at(p, wr_f, dark=True)
    limb(p, [hip, kn_f, an_f], [70, 56, 44], R.PANTS_SH)
    boot(p, an_f, max(-10, min(30, -(far[0] - far[1]) * .5)), dark=True)
    # рюкзак за спиной
    bag = [U(pt) for pt in [(-40, 176), (-136, 180), (-140, 470), (-40, 474)]]
    p.shape(bag, R.BAG, smooth=False)
    p.shade(bag, [U(pt) for pt in [(-150, 160), (-100, 160), (-100, 490), (-150, 490)]], R.BAG_SH, smooth_shade=False)
    # корпус
    torso = [U(pt) for pt in [(-40, 186), (20, 180), (46, 210), (48, 330), (40, 520), (-40, 524), (-46, 330)]]
    p.shape(torso, R.JACKET)
    p.shade(torso, [U(pt) for pt in [(-60, 170), (-10, 170), (-14, 540), (-60, 540)]], R.JACKET_SH)
    p.shade(torso, [U(pt) for pt in [(34, 190), (60, 190), (60, 540), (34, 540)]], R.RIM, 110)
    p.curve([U((-38, 196)), U((-30, 360)), U((-34, 470))], col=(44, 46, 52), lw=12)   # лямка
    p.ellipse(*U((30, 340)), 16, 16, (96, 100, 106), lw=1.8)                        # респиратор
    # ближняя нога
    limb(p, [hip, kn_n, an_n], [74, 60, 46], R.PANTS, dark=R.PANTS_SH)
    boot(p, an_n, max(-10, min(30, -(near[0] - near[1]) * .5)))
    # шея, бандана, голова
    hx, hy = 10 + lean * (HIP_Y - 186), 0   # голова сидит на шее, а не уезжает с наклоном
    p.ox += hx * p.s
    p.oy += (hy) * p.s
    neck = [(-10, 140), (24, 140), (24, 190), (-12, 190)]
    p.shape(neck, R.SKIN, smooth=False)
    p.shape([(-16, 176), (34, 172), (30, 214), (10, 236), (-14, 206)], R.BANDANA)
    if blink is None:
        blink = (t % 3.1) < .1
    side_head(p, expr, blink)
    p.ox -= hx * p.s
    p.oy -= hy * p.s
    # ближняя рука поверх всего
    el_n, wr_n = arm_joints(U(shoulder), near[2], near[3])
    limb(p, [U(shoulder), el_n, wr_n], [46, 40, 34], R.JACKET, dark=R.JACKET_SH)
    a = (el_n[0] * .45 + wr_n[0] * .55, el_n[1] * .45 + wr_n[1] * .55)
    p.ellipse(a[0], a[1], 10, 4, R.REFL, line=False)
    hand_at(p, wr_n)
    return p.result()


# ---------- вид спереди: стоит / идёт к камере ----------
def front_figure(size, ox, ground_y, s, t, mode="idle", expr="neutral", look=(0, 0)):
    ph = 2 * math.pi * 1.0 * t
    p = Pen(size, ox, 0, s)
    lifts = [0, 0]
    bob = 3 * math.sin(2 * math.pi * .35 * t) if mode == "idle" else 0
    if mode == "walk":
        lifts = [max(0, math.sin(ph)), max(0, math.sin(ph + math.pi))]
        bob = -8 * abs(math.cos(ph))
    p.oy = ground_y - GROUND * s + bob * s
    # рюкзак
    bag = [(-132, 168), (132, 168), (134, 470), (-134, 470)]
    p.shape(bag, R.BAG, smooth=False)
    p.shade(bag, [(-140, 160), (-40, 160), (-50, 480), (-140, 480)], R.BAG_SH, 255, smooth_shade=False)
    # ноги (поднятая выше и чуть крупнее — шагает к камере)
    for i, sx in enumerate((-1, 1)):
        L = lifts[i]
        hip = (sx * 40, 520)
        knee = (sx * 42, 706 - 40 * L)
        ank = (sx * 40, 900 - 64 * L)
        limb(p, [hip, knee, ank], [68, 56, 46 + 8 * L], R.PANTS, dark=R.PANTS_SH if sx < 0 else None)
        p.shape([(knee[0] - 26, knee[1] - 22), (knee[0] + 26, knee[1] - 22), (knee[0] + 24, knee[1] + 24), (knee[0] - 24, knee[1] + 24)], (44, 46, 52), lw=1.8)
        k = 1 + .18 * L
        bt = [(ank[0] - 30 * k, ank[1] - 8), (ank[0] + 30 * k, ank[1] - 8), (ank[0] + 36 * k, ank[1] + 46 * k), (ank[0] - 36 * k, ank[1] + 46 * k)]
        p.shape(bt, R.BOOTS, lw=2.4)
    # руки: качаются вперёд-назад (в кадре — вверх-вниз и чуть внутрь)
    for i, sx in enumerate((-1, 1)):
        sw = math.sin(ph + (0 if sx < 0 else math.pi)) if mode == "walk" else 0
        sh = (sx * 104, 214)
        el = (sx * (128 - 6 * max(0, sw)), 380 - 14 * max(0, sw))
        wr = (sx * (122 - 26 * max(0, sw)), 532 - 50 * max(0, sw) + 10 * max(0, -sw))
        limb(p, [sh, el, wr], [52, 44, 36], R.JACKET, dark=R.JACKET_SH if sx < 0 else None)
        a = (el[0] * .4 + wr[0] * .6, el[1] * .4 + wr[1] * .6)
        p.ellipse(a[0], a[1], 18, 4, R.REFL, line=False)
        hand_at(p, wr, dark=sx < 0)
    # торс — как в realman
    torso = [(-104, 198), (-40, 178), (0, 184), (40, 178), (104, 198), (108, 300), (94, 420), (88, 520), (0, 528), (-88, 520), (-94, 420), (-108, 300)]
    p.shape(torso, R.JACKET)
    p.shade(torso, [(-130, 160), (-24, 160), (-34, 300), (-30, 540), (-130, 540)], R.JACKET_SH)
    p.shade(torso, [(78, 190), (120, 190), (120, 540), (84, 540)], R.RIM, 110)
    p.curve([(0, 186), (2, 360), (0, 526)], lw=2)
    p.shape([(-82, 340), (-40, 338), (-40, 378), (-84, 380)], (150, 140, 112), lw=1.6, smooth=False)
    for sx in (-1, 1):
        p.shape([(sx * 44, 182), (sx * 66, 184), (sx * 62, 470), (sx * 42, 470)], (44, 46, 52), lw=1.6, smooth=False)
    p.shape([(-60, 300), (60, 300), (60, 314), (-60, 314)], (44, 46, 52), lw=1.4, smooth=False)
    p.ellipse(54, 360, 22, 22, (96, 100, 106), lw=2)
    p.ellipse(54, 360, 12, 12, (60, 62, 68), lw=1.4)
    neck = [(-24, 140), (24, 140), (26, 196), (-26, 196)]
    p.shape(neck, R.SKIN, smooth=False)
    band = [(-52, 176), (52, 176), (40, 214), (6, 262), (-30, 222)]
    p.shape(band, R.BANDANA)
    p.shade(band, [(-60, 170), (-4, 170), (0, 270), (-60, 270)], R.BANDANA_SH)
    # голова: лёгкий поворот головы — смещение по x, дыхание
    p.ox += (2 * math.sin(t * .9) if mode == "idle" else 0) * s
    R.face(p, expr, look, blink=(t % 3.3) < .1)
    return p.result()
