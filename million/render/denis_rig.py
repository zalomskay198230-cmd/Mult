"""Анимируемый Денис: вид спереди с позами рук/ног и вид сбоку (шаг/бег).
Стиль и движок — как у Макса (kurer/render/realman.py, rig.py)."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "kurer", "render"))
from realman import Pen, LINE
import rig
import person

C = person.CAST["denis"]
SKIN, SKIN_SH = C["skin"], person.dk(C["skin"], .74)
TOP, TOP_SH = C["top"] and C["top_col"], person.dk(C["top_col"], .7)
JEANS, JEANS_SH = C["pants"], person.dk(C["pants"], .7)
SHOE = C["shoes"]
HAIR, HAIR_SH = C["hair"], person.dk(C["hair"], .62)
GROUND = 962


def lerp(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


# позы рук (вид спереди): локоть и кисть для правой руки (x>0); левая — зеркально
ARM = {
    "down": ((124, 380), (118, 530)),
    "phone": ((128, 392), (70, 312)),
    "ear": ((150, 300), (66, 112)),
    "fist_up": ((176, 150), (150, -16)),
    "head": ((176, 120), (62, 6)),
    "out": ((176, 320), (214, 452)),
    "wind": ((176, 140), (236, 40)),      # замах
    "release": ((176, 300), (290, 330)),  # бросок
}
TOP_LAYER = ("ear", "head", "fist_up", "wind")   # руки, которые рисуются поверх головы


def arm_pts(sx, pose):
    el, wr = ARM[pose] if isinstance(pose, str) else pose
    return (sx * 104, 214), (sx * el[0], el[1]), (sx * wr[0], wr[1])


def draw_arm(p, sx, pose, holding_phone=False):
    sh, el, wr = arm_pts(sx, pose)
    rig.limb(p, [sh, el, wr], [52, 44, 36], TOP, dark=TOP_SH if sx < 0 else None)
    p.ellipse(wr[0], wr[1] + 12, 16, 21, SKIN if sx > 0 else SKIN_SH, lw=2.2)
    if holding_phone:
        x, y = wr
        p.shape([(x - 20, y - 40), (x + 20, y - 40), (x + 20, y + 32), (x - 20, y + 32)], (24, 24, 28), lw=2, smooth=False)
        p.shape([(x - 16, y - 34), (x + 16, y - 34), (x + 16, y + 26), (x - 16, y + 26)], (120, 170, 220), line=False, smooth=False)
    return wr


def front(size, ox, ground, s, t, arms=("down", "down"), legs="idle", expr="neutral", look=(0, 0), jump=0.0, phone_hand=None, head_tilt=0.0):
    """arms: позы (левая, правая) — имя из ARM или ((x,y),(x,y)); legs: idle | walk | jump.
    phone_hand: 'r' или 'l' — в какой руке телефон."""
    p = Pen(size, ox, 0, s)
    ph = 2 * math.pi * 1.6 * t
    bob = 2 * math.sin(2 * math.pi * .35 * t)
    lifts = [0, 0]
    if legs == "walk":
        lifts = [max(0, math.sin(ph)), max(0, math.sin(ph + math.pi))]
        bob = -7 * abs(math.cos(ph))
    p.oy = ground - GROUND * s + bob * s - jump * s
    # ноги
    for i, sx in enumerate((-1, 1)):
        L = lifts[i]
        hip = (sx * 40, 520)
        if legs == "jump":
            knee, ank = (sx * 70, 690), (sx * 46, 860)
        else:
            knee, ank = (sx * 42, 706 - 40 * L), (sx * 40, 900 - 64 * L)
        rig.limb(p, [hip, knee, ank], [70, 58, 48], JEANS, dark=JEANS_SH if sx < 0 else None)
        k = 1 + .15 * L
        p.shape([(ank[0] - 30 * k, ank[1] - 6), (ank[0] + 30 * k, ank[1] - 6), (ank[0] + 38 * k, ank[1] + 50 * k), (ank[0] - 38 * k, ank[1] + 50 * k)], SHOE, lw=2.4)
        p.curve([(ank[0] - 36 * k, ank[1] + 38 * k), (ank[0] + 36 * k, ank[1] + 38 * k)], col=(170, 170, 170), lw=3, smooth=False)
    # руки, которые не над головой — до торса
    late = []
    for sx, pose in zip((-1, 1), arms):
        hold = phone_hand == ("l" if sx < 0 else "r")
        if pose in TOP_LAYER:
            late.append((sx, pose, hold))
        elif pose in ("phone",):
            late.append((sx, pose, hold))   # телефон перед грудью — поверх торса
        else:
            draw_arm(p, sx, pose, hold)
    # торс-толстовка
    torso = [(-104, 198), (-40, 178), (0, 184), (40, 178), (104, 198), (108, 300), (94, 420), (88, 520), (0, 528), (-88, 520), (-94, 420), (-108, 300)]
    p.shape(torso, TOP)
    p.shade(torso, [(-130, 160), (-24, 160), (-34, 300), (-30, 540), (-130, 540)], TOP_SH)
    p.shade(torso, [(78, 190), (120, 190), (120, 540), (84, 540)], person.LIGHT_RIM, 60)
    p.shape([(-70, 190), (-40, 176), (0, 200), (40, 176), (70, 190), (40, 236), (0, 250), (-40, 236)], person.dk(TOP, .85), lw=1.8)
    p.shape([(-60, 400), (60, 400), (70, 480), (-70, 480)], person.dk(TOP, .9), lw=1.6)
    for sx in (-1, 1):
        p.curve([(sx * 16, 236), (sx * 18, 290), (sx * 14, 310)], col=(220, 220, 216), lw=2.4)
    p.shape([(-92, 506), (92, 506), (90, 528), (-90, 528)], person.dk(TOP, .8), lw=1.4, smooth=False)
    neck = [(-22, 136), (22, 136), (24, 192), (-24, 192)]
    p.shape(neck, SKIN, smooth=False)
    # руки перед грудью
    for sx, pose, hold in late:
        if pose == "phone":
            draw_arm(p, sx, pose, hold)
    # голова (лёгкий наклон — сдвиг)
    p.ox += head_tilt * 14 * s
    person.face(p, C, expr, look, blink=(t % 3.4) < .1)
    p.ox -= head_tilt * 14 * s
    for sx, pose, hold in late:
        if pose != "phone":
            draw_arm(p, sx, pose, hold)
    return p.result()


# ---------- вид сбоку (лицом вправо) ----------
def side_head(p, expr="neutral"):
    head = [(-50, 30), (-30, 4), (0, -4), (30, 6), (48, 30), (52, 58), (56, 74), (66, 94), (56, 102), (56, 112), (52, 118),
            (54, 126), (46, 142), (24, 150), (0, 146), (-14, 130), (-40, 112), (-54, 80)]
    p.shape(head, SKIN)
    p.shade(head, [(-70, -20), (6, -20), (2, 60), (8, 140), (-70, 160)], SKIN_SH, 220, soft=3)
    p.shade(head, [(-4, 104), (40, 112), (50, 130), (30, 150), (0, 146), (-14, 128)], (120, 100, 96), 70, soft=3)
    p.shape([(-6, 70), (8, 72), (10, 92), (0, 104), (-10, 96)], SKIN_SH)
    p.shape([(28, 72), (38, 68), (44, 74), (36, 79)], (236, 230, 222), line=False)
    p.ellipse(39, 73, 3.4, 3.8, (40, 40, 34), line=False)
    p.curve([(27, 72), (38, 66), (45, 73)], lw=2.6)
    p.shape([(26, 60), (44, 56), (48, 60), (30, 64)], HAIR_SH, line=False)
    if expr == "shock":
        p.shape([(46, 118), (54, 116), (54, 126), (46, 126)], (90, 30, 30), smooth=False)
    else:
        p.curve([(42, 120), (54, 118)], lw=2.2)
    hair = [(-56, 76), (-62, 30), (-44, -10), (-12, -26), (20, -22), (44, 0), (56, 26), (48, 30), (40, 20), (30, 34), (18, 22),
            (4, 36), (-14, 30), (-24, 60), (-40, 96)]
    p.shape(hair, HAIR)
    p.shade(hair, [(-80, -40), (0, -40), (-10, 120), (-80, 120)], HAIR_SH, 255, soft=3)


def side(size, ox, ground, s, t, mode="run", expr="tense", hood_up=False):
    f = 1.0 if mode == "walk" else 1.6
    ph = 2 * math.pi * f * t
    near, far = rig.cycle(mode, ph), rig.cycle(mode, ph + math.pi)
    hip = (0, rig.HIP_Y)
    kn_n, an_n = rig.leg_joints(hip, near[0], near[1])
    kn_f, an_f = rig.leg_joints(hip, far[0], far[1])
    lift = GROUND - (max(an_n[1], an_f[1]) + 22)
    if mode == "run":
        lift -= 16 * abs(math.sin(ph))
    p = Pen(size, ox, ground - GROUND * s + lift * s, s)
    lean = .16 if mode == "run" else .04
    U = lambda pt: (pt[0] + lean * (rig.HIP_Y - pt[1]), pt[1])
    shoulder = (0, rig.SH_Y)
    el_f, wr_f = rig.arm_joints(U(shoulder), far[2], far[3])
    rig.limb(p, [U(shoulder), el_f, wr_f], [44, 38, 32], TOP_SH)
    p.ellipse(wr_f[0], wr_f[1] + 12, 14, 18, SKIN_SH, lw=2)
    rig.limb(p, [hip, kn_f, an_f], [70, 56, 44], JEANS_SH)
    rig.boot(p, an_f, max(-10, min(30, -(far[0] - far[1]) * .5)), dark=True, col=SHOE)
    torso = [U(pt) for pt in [(-46, 186), (20, 180), (46, 210), (48, 330), (40, 520), (-44, 524), (-50, 330)]]
    p.shape(torso, TOP)
    p.shade(torso, [U(pt) for pt in [(-60, 170), (-10, 170), (-14, 540), (-60, 540)]], TOP_SH)
    p.shape([U(pt) for pt in [(-50, 190), (-20, 176), (-10, 230), (-46, 250)]], person.dk(TOP, .85), lw=1.6)   # капюшон на спине
    rig.limb(p, [hip, kn_n, an_n], [74, 60, 46], JEANS, dark=JEANS_SH)
    rig.boot(p, an_n, max(-10, min(30, -(near[0] - near[1]) * .5)), col=SHOE)
    hx = 10 + lean * (rig.HIP_Y - 186)
    p.ox += hx * p.s
    p.shape([(-10, 140), (24, 140), (24, 190), (-12, 190)], SKIN, smooth=False)
    side_head(p, expr)
    if hood_up:
        p.shape([(-62, 100), (-66, 20), (-40, -20), (0, -34), (40, -20), (58, 20), (40, 30), (10, 4), (-30, 20), (-40, 120)], person.dk(TOP, .9))
    p.ox -= hx * p.s
    el_n, wr_n = rig.arm_joints(U(shoulder), near[2], near[3])
    rig.limb(p, [U(shoulder), el_n, wr_n], [46, 40, 34], TOP, dark=TOP_SH)
    p.ellipse(wr_n[0], wr_n[1] + 12, 15, 19, SKIN, lw=2.2)
    return p.result()
