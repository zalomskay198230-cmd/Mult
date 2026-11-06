"""Параметрические персонажи «Вернуть миллион» в стиле графического романа
(тот же движок, что у Макса из «Курьера»: kurer/render/realman.py)."""
import os, sys, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "kurer", "render"))
from realman import Pen, cr, LINE

HEAD = [(0, 0), (34, 6), (52, 28), (56, 62), (54, 90), (46, 116), (28, 140), (0, 152), (-28, 140), (-46, 116), (-54, 90), (-56, 62), (-52, 28), (-34, 6)]
HEAD_F = [(0, 4), (32, 10), (48, 30), (52, 62), (50, 90), (42, 114), (24, 136), (0, 146), (-24, 136), (-42, 114), (-50, 90), (-52, 62), (-48, 30), (-32, 10)]


def dk(c, k=.72):
    return tuple(int(v * k) for v in c)


def lt(c, k=1.18):
    return tuple(min(255, int(v * k)) for v in c)


CAST = {
    "denis": dict(name="ДЕНИС", sub="28 лет · потерял миллион", skin=(214, 170, 140), hair=(52, 40, 34), hair_style="messy",
                  stubble=True, bags=True, eyes=(96, 84, 64), top="hoodie", top_col=(84, 88, 96), pants=(62, 86, 120),
                  shoes=(232, 232, 228), female=False, prop="phone"),
    "artem": dict(name="АРТЁМ", sub="29 лет · «друг» со ссылкой", skin=(220, 178, 146), hair=(176, 138, 86), hair_style="slick",
                  beard=True, eyes=(80, 110, 130), top="leather", top_col=(36, 34, 38), inner=(236, 236, 232), chain=True,
                  pants=(40, 40, 46), shoes=(236, 236, 232), female=False, prop="keys"),
    "mama": dict(name="МАМА", sub="Ольга Петровна · 55 лет", skin=(222, 180, 154), hair=(150, 70, 46), hair_style="bob",
                 glasses=True, wrinkles=True, eyes=(100, 90, 70), top="cardigan", top_col=(196, 172, 132), inner=(120, 60, 70),
                 pants=(70, 66, 80), shoes=(90, 60, 50), female=True, prop="phone_call"),
    "owner": dict(name="???", sub="хозяин канала", hooded=True, top="hood_coat", top_col=(26, 26, 30), pants=(30, 30, 34),
                  shoes=(20, 20, 22), skin=(40, 40, 44), female=False),
}

LIGHT_RIM = (255, 214, 170)


def face(p, c, expr="neutral", look=(0, 0), blink=False):
    skin, sh = c["skin"], dk(c["skin"], .74)
    H_ = HEAD_F if c.get("female") else HEAD
    if c.get("hooded"):   # капюшон и тьма вместо лица
        hood = [(-74, 150), (-80, 40), (-50, -24), (0, -40), (50, -24), (80, 40), (74, 150), (40, 160), (-40, 160)]
        p.shape(hood, c["top_col"])
        p.shape([(-48, 140), (-52, 50), (-30, 6), (0, -4), (30, 6), (52, 50), (48, 140), (0, 156)], (6, 6, 8))
        for sx in (-1, 1):   # отблеск экрана в глазах
            p.ellipse(sx * 18, 78, 3, 2, (150, 200, 255), line=False)
        return
    for sx in (-1, 1):
        p.shape([(sx * 52, 66), (sx * 64, 70), (sx * 66, 90), (sx * 58, 104), (sx * 50, 98)], skin)
    p.shape(H_, skin)
    p.shade(H_, [(-70, 10), (-40, 14), (-24, 40), (-30, 70), (-24, 100), (-12, 128), (-4, 150), (-70, 170)], sh, 220, soft=3)
    p.shade(H_, [(52, 30), (60, 40), (60, 90), (50, 126), (46, 112), (52, 80), (50, 48)], LIGHT_RIM, 120, soft=2)
    p.shade(H_, [(-40, 52), (40, 52), (36, 64), (-36, 64)], sh, 60, soft=4)
    if c.get("stubble"):
        jaw = [(-48, 100), (-30, 106), (-14, 116), (14, 116), (30, 106), (48, 100), (40, 128), (20, 146), (0, 152), (-20, 146), (-40, 128)]
        p.shade(H_, jaw, (120, 100, 96), 70, soft=3)
    if c.get("beard"):
        beard = [(-52, 84), (-44, 110), (-26, 136), (0, 150), (26, 136), (44, 110), (52, 84), (40, 104), (20, 112), (0, 108), (-20, 112), (-40, 104)]
        p.shape(beard, dk(c["hair"], .8), lw=1.6)
        p.shape([(-22, 116), (0, 112), (22, 116), (14, 122), (-14, 122)], dk(c["hair"], .8), line=False)   # усы
    if c.get("wrinkles"):
        for y in (40, 46):
            p.curve([(-22, y), (0, y - 2), (22, y)], col=dk(skin, .8), lw=1.1)
        for sx in (-1, 1):
            p.curve([(sx * 18, 104), (sx * 26, 118), (sx * 22, 128)], col=dk(skin, .74), lw=1.4)
    eh = {"neutral": 5, "tense": 4, "smile": 4, "shock": 8, "worried": 6, "sad": 4.5, "smug": 3.5}[expr]
    if c.get("female"):
        eh += .6
    for sx in (-1, 1):
        cx, cy = sx * 22, 72
        if blink:
            p.curve([(cx - 13, cy), (cx, cy + 2), (cx + 13, cy)], lw=2.6)
        else:
            eye = [(cx - 13, cy), (cx - 4, cy - eh - 1), (cx + 8, cy - eh), (cx + 13, cy), (cx + 4, cy + eh * .7), (cx - 6, cy + eh * .7)]
            p.shape(eye, (236, 230, 222), line=False)
            ix, iy = cx + look[0] * 4, cy + look[1] * 2
            p.ellipse(ix, iy, 5.6, 5.6, c["eyes"], line=False)
            p.ellipse(ix, iy, 2.8, 2.8, (20, 18, 18), line=False)
            p.ellipse(ix + 1.8, iy - 2, 1.3, 1.3, (255, 255, 255), line=False)
            p.curve([(cx - 14, cy + 1), (cx - 5, cy - eh - 2), (cx + 8, cy - eh - 1), (cx + 14, cy + 1)], lw=3.2 if c.get("female") else 3)
            if c.get("female"):   # ресницы
                p.curve([(cx + sx * 13, cy), (cx + sx * 17, cy - 4)], lw=2)
            if c.get("bags"):
                p.curve([(cx - 10, cy + eh * .8 + 3), (cx + 2, cy + eh + 4), (cx + 10, cy + eh * .6 + 3)], col=(140, 100, 96), lw=1.8)
        tilt = {"neutral": 0, "tense": 4, "smile": -1, "shock": -5, "worried": -4, "sad": -5, "smug": 2}[expr]
        inner, outer = (sx * 8, 58 + tilt), (sx * 34, 56 - tilt * .4)
        if expr == "smug" and sx > 0:
            inner, outer = (sx * 8, 54), (sx * 34, 50)
        thick = 4 if c.get("female") else 0
        p.shape([inner, ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 4 + thick * .3), outer,
                 ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) + 1)], dk(c["hair"], .7) if not c.get("female") else (90, 60, 50), line=False)
    if c.get("glasses"):
        for sx in (-1, 1):
            p.ellipse(sx * 22, 72, 17, 13, None, lw=2)
        p.curve([(-6, 70), (6, 70)], lw=2, smooth=False)
    # нос
    p.shade(H_, [(-4, 74), (-12, 98), (-16, 108), (-2, 110), (-2, 90)], sh, 150, soft=1.5)
    p.curve([(7, 90), (10, 102), (8, 107)], lw=1.8)
    p.curve([(-9, 106), (-3, 111), (4, 111), (9, 106)], lw=2)
    # рот
    my = 124
    lip = (186, 96, 96) if c.get("female") else None
    if expr == "smile":
        p.curve([(-16, my - 1), (-4, my + 4), (8, my + 3), (17, my - 3)], lw=2.6)
    elif expr == "smug":
        p.curve([(-14, my + 1), (2, my + 2), (16, my - 5)], lw=2.6)
    elif expr == "shock":
        p.shape([(-9, my - 3), (9, my - 3), (8, my + 10), (-8, my + 10)], (90, 30, 30))
    elif expr in ("sad", "worried"):
        p.curve([(-15, my + 3), (0, my), (15, my + 3)], lw=2.6)
    else:
        p.curve([(-14, my), (0, my + 1), (14, my - 1)], lw=2.6)
    if lip:
        p.curve([(-12, my + 2), (0, my + 5), (12, my + 2)], col=lip, lw=4)
    # волосы
    hc, hs = c["hair"], dk(c["hair"], .62)
    st = c["hair_style"]
    if st == "messy":
        hair = [(-60, 62), (-64, 26), (-54, -4), (-30, -26), (0, -32), (30, -26), (54, -6), (64, 24), (60, 62), (54, 38),
                (42, 30), (30, 40), (16, 26), (0, 38), (-14, 26), (-28, 40), (-40, 28), (-50, 44)]
        p.shape(hair, hc)
        p.shade(hair, [(-80, -40), (-4, -40), (-18, 70), (-80, 70)], hs, 255, soft=3)
        for k in range(-44, 50, 14):
            p.curve([(k, -20), (k + 6, 4), (k + 2, 30)], col=hs, lw=1.4)
    elif st == "slick":
        hair = [(-58, 60), (-62, 24), (-52, -10), (-24, -30), (10, -34), (40, -26), (58, -4), (62, 26), (58, 60), (52, 30),
                (40, 16), (10, 12), (-20, 14), (-44, 22), (-52, 40)]
        p.shape(hair, hc)
        p.shade(hair, [(-80, -40), (-10, -40), (-20, 70), (-80, 70)], hs, 255, soft=3)
        for k in range(5):   # зачёс назад
            p.curve([(-40 + k * 10, 18), (-10 + k * 14, -16), (40 + k * 4, -14)], col=lt(hc, 1.2), lw=1.6)
        p.curve([(-22, 2), (-24, 20)], col=hs, lw=2.2)   # пробор
    elif st == "bob":
        back = [(-70, 140), (-72, 40), (-56, -6), (-20, -26), (20, -26), (56, -6), (72, 40), (70, 140), (50, 150), (56, 70), (-56, 70), (-50, 150)]
        p.shape(back, hs)
        hair = [(-66, 120), (-68, 34), (-50, -6), (-16, -24), (24, -22), (54, -4), (68, 34), (66, 120), (54, 112), (52, 60),
                (40, 30), (16, 24), (-6, 36), (-30, 26), (-50, 44), (-56, 112)]
        p.shape(hair, hc)
        p.shade(hair, [(-90, -40), (-10, -40), (-26, 140), (-90, 140)], hs, 220, soft=3)
        p.ellipse(56, 104, 3.4, 5, (226, 196, 110), lw=1)   # серьга


def figure(size, ox, oy, s, who, expr="neutral", look=(0, 0), blink=False, head_only=False):
    c = CAST[who]
    p = Pen(size, ox, oy, s)
    hands = []
    if not head_only:
        top, tc = c["top"], c["top_col"]
        tsh = dk(tc, .7)
        fem = c.get("female")
        # ноги
        for sx in (-1, 1):
            leg = [(sx * 8, 500), (sx * (66 if fem else 72), 500), (sx * 62, 700), (sx * 56, 900), (sx * 18, 900), (sx * 14, 700)]
            p.shape(leg, c["pants"])
            if sx < 0:
                p.shade(leg, [(-90, 490), (-40, 490), (-36, 910), (-90, 910)], dk(c["pants"], .7))
            p.curve([(sx * 30, 760), (sx * 46, 790), (sx * 40, 840)], col=dk(c["pants"], .7), lw=1.6)
            p.shape([(sx * 12, 896), (sx * 62, 896), (sx * 72, 934), (sx * 80, 960), (sx * 8, 960)], c["shoes"])
            p.curve([(sx * 10, 948), (sx * 78, 948)], col=dk(c["shoes"], .7), lw=3, smooth=False)
        # руки: обычная рисуется до торса, рука с реквизитом — поверх
        prop = c.get("prop")

        def draw_arm(sx):
            sh = (sx * (96 if fem else 104), 214)
            el, wr = (sx * 124, 380), (sx * 118, 530)
            if prop == "phone" and sx > 0:
                el, wr = (sx * 128, 390), (sx * 70, 330)
            if prop == "phone_call" and sx > 0:
                el, wr = (sx * 150, 300), (sx * 66, 112)
            if prop == "keys" and sx > 0:
                el, wr = (sx * 170, 300), (sx * 210, 190)
            if prop == "phone_call" and sx > 0:   # поднятая рука — из двух сегментов
                import rig
                rig.limb(p, [sh, el, wr], [52, 46, 34], tc, dark=tsh)
                p.ellipse(wr[0], wr[1] + 10, 15, 20, c["skin"], lw=2.2)
                return wr
            sl = [(sh[0] - sx * 24, sh[1] - 10), (sh[0] + sx * 22, sh[1] - 4), (el[0] + sx * 22, el[1]), (wr[0] + sx * 16, wr[1]),
                  (wr[0] - sx * 16, wr[1] + 4), (el[0] - sx * 20, el[1] + 4), (sh[0] - sx * 28, sh[1] + 60)]
            p.shape(sl, tc)
            if sx < 0:
                p.shade(sl, [(sh[0] - 60, 150), (sh[0] + 4, 150), (el[0] + 6, el[1]), (wr[0] + 2, wr[1] + 10), (wr[0] - 60, wr[1] + 20)], tsh)
            if not c.get("hooded"):
                hand = [(wr[0] - 14, wr[1]), (wr[0] + 14, wr[1]), (wr[0] + 16, wr[1] + 30), (wr[0] + 6, wr[1] + 44), (wr[0] - 8, wr[1] + 42), (wr[0] - 16, wr[1] + 26)]
                p.shape(hand, c["skin"])
            return wr

        hands = [draw_arm(-1), None]
        if not prop:
            hands[1] = draw_arm(1)
        # торс
        if fem:
            torso = [(-96, 198), (-40, 180), (0, 186), (40, 180), (96, 198), (100, 300), (84, 400), (94, 520), (0, 528), (-94, 520), (-84, 400), (-100, 300)]
        else:
            torso = [(-104, 198), (-40, 178), (0, 184), (40, 178), (104, 198), (108, 300), (94, 420), (88, 520), (0, 528), (-88, 520), (-94, 420), (-108, 300)]
        if top in ("leather", "cardigan"):   # нижний слой — футболка/блузка
            p.shape([(-50, 186), (50, 186), (46, 520), (-46, 520)], c["inner"], smooth=False)
        if top in ("leather", "cardigan"):
            for sx in (-1, 1):
                half = [pt for pt in torso if pt[0] * sx >= 0] if False else None
                flap = [(sx * 104 if not fem else sx * 96, 198), (sx * 36, 182), (sx * 30, 300), (sx * 34, 520), (sx * 88 if not fem else sx * 94, 520), (sx * 94 if not fem else sx * 84, 420), (sx * 108 if not fem else sx * 100, 300)]
                p.shape(flap, tc)
                if sx < 0:
                    p.shade(flap, [(-130, 160), (-40, 160), (-40, 540), (-130, 540)], tsh)
                else:
                    p.shade(flap, [(76, 190), (120, 190), (120, 540), (80, 540)], LIGHT_RIM, 70)
            if top == "leather":
                for sx in (-1, 1):   # лацканы и блики кожи
                    p.shape([(sx * 36, 182), (sx * 70, 196), (sx * 40, 270)], dk(tc, 1.4), lw=1.6)
                    p.curve([(sx * 70, 300), (sx * 76, 420)], col=(90, 88, 96), lw=2.4)
                p.curve([(-36, 310), (-30, 520)], lw=2.6, col=(150, 150, 156))   # молния
            if top == "cardigan":
                for y in (260, 330, 400, 470):
                    p.ellipse(-30, y, 5, 5, (230, 220, 200), lw=1.2)
                for k in range(-90, -30, 16):
                    p.curve([(k, 220), (k + 2, 360), (k, 510)], col=tsh, lw=1.1)
                for k in range(40, 96, 16):
                    p.curve([(k, 220), (k + 2, 360), (k, 510)], col=tsh, lw=1.1)
        else:
            p.shape(torso, tc)
            p.shade(torso, [(-130, 160), (-24, 160), (-34, 300), (-30, 540), (-130, 540)], tsh)
            p.shade(torso, [(78, 190), (120, 190), (120, 540), (84, 540)], LIGHT_RIM, 70)
            if top == "hoodie":
                p.shape([(-70, 190), (-40, 176), (0, 200), (40, 176), (70, 190), (40, 236), (0, 250), (-40, 236)], dk(tc, .85), lw=1.8)   # капюшон на спине
                p.shape([(-60, 400), (60, 400), (70, 480), (-70, 480)], dk(tc, .9), lw=1.6)   # карман-кенгуру
                for sx in (-1, 1):
                    p.curve([(sx * 16, 236), (sx * 18, 290), (sx * 14, 310)], col=(220, 220, 216), lw=2.4)   # шнурки
                p.shape([(-92, 506), (92, 506), (90, 528), (-90, 528)], dk(tc, .8), lw=1.4, smooth=False)
            if top == "hood_coat":
                p.curve([(0, 190), (0, 528)], col=(10, 10, 12), lw=3)
        # шея
        if not c.get("hooded"):
            neck = [(-22, 136), (22, 136), (24, 192), (-24, 192)]
            p.shape(neck, c["skin"], smooth=False)
            p.shade(neck, [(-40, 130), (6, 130), (6, 200), (-40, 200)], dk(c["skin"], .74), smooth_shade=False)
        if c.get("chain"):
            p.curve([(-28, 190), (0, 232), (28, 190)], col=(226, 190, 80), lw=4)
        if prop in ("phone", "keys"):
            hands[1] = draw_arm(1)
        if prop == "phone_call":
            hands[1] = (66, 112)
        # реквизит
        if c.get("prop") == "phone":
            wx, wy = hands[1]
            p.shape([(wx - 22, wy - 40), (wx + 22, wy - 40), (wx + 22, wy + 40), (wx - 22, wy + 40)], (24, 24, 28), lw=2, smooth=False)
            p.shape([(wx - 18, wy - 34), (wx + 18, wy - 34), (wx + 18, wy + 34), (wx - 18, wy + 34)], (120, 170, 220), line=False, smooth=False)
            p.shape([(wx - 18, wy + 6), (wx + 18, wy + 6), (wx + 18, wy + 34), (wx - 18, wy + 34)], (220, 60, 50), line=False, smooth=False)
        if c.get("prop") == "keys":
            wx, wy = hands[1]
            p.ellipse(wx, wy - 30, 12, 12, None, lw=3)
            for k, ang in enumerate((-30, 10, 40)):
                a = math.radians(ang)
                x2, y2 = wx + 50 * math.sin(a), wy - 30 - 50 * math.cos(a) * -1 + 10
                p.curve([(wx, wy - 22), (x2, y2)], col=(214, 190, 110), lw=7, smooth=False)
            p.shape([(wx + 6, wy + 10), (wx + 40, wy + 4), (wx + 44, wy + 30), (wx + 10, wy + 34)], (200, 40, 40), lw=1.6, smooth=False)   # брелок
    face(p, c, expr, look, blink)
    if not head_only and c.get("prop") == "phone_call":   # трубка у уха поверх лица
        draw_arm(1)
        wx, wy = 66, 112
        p.shape([(wx - 16, wy - 50), (wx + 8, wy - 54), (wx + 12, wy + 6), (wx - 12, wy + 10)], (40, 40, 46), lw=2, smooth=False)
    return p.result(), hands
