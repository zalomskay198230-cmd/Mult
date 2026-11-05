"""Тётя Зина, 60 лет — диспетчер пункта выдачи. Рисуется по пояс (она всегда за стойкой).
Тот же стиль, что у Макса: кривые, светотень, тонкий контур."""
import math
import realman as R
from realman import Pen

Z_SKIN = (206, 160, 132)
Z_SKIN_SH = (150, 106, 90)
Z_HAIR = (178, 176, 180)
Z_HAIR_SH = (130, 128, 136)
CARDIGAN = (112, 52, 58)
CARDIGAN_SH = (76, 34, 40)
SCARF = (60, 92, 120)
WARM = (255, 170, 90)       # свет от буржуйки слева

HEAD = [(0, 2), (32, 8), (50, 30), (54, 62), (52, 90), (44, 114), (26, 136), (0, 146), (-26, 136), (-44, 114), (-52, 90), (-54, 62), (-50, 30), (-32, 8)]


def zina_bust(size, ox, oy, s, t=0.0, expr="neutral", look=(0, 0), talk=False, smoke=True):
    p = Pen(size, ox, oy, s)
    # туловище по пояс: кофта, шарф
    body = [(-120, 320), (-104, 184), (-50, 156), (0, 162), (50, 156), (104, 184), (120, 320), (130, 470), (-130, 470)]
    p.shape(body, CARDIGAN)
    p.shade(body, [(40, 160), (160, 160), (160, 480), (30, 480)], CARDIGAN_SH)
    p.shade(body, [(-150, 180), (-108, 180), (-100, 480), (-150, 480)], WARM, 90, soft=4)
    for k in range(-100, 110, 22):   # вязка
        p.curve([(k, 230), (k + 4, 320), (k, 460)], col=CARDIGAN_SH, lw=1.2)
    p.curve([(0, 190), (2, 470)], lw=2)
    for y in (260, 330, 400):
        p.ellipse(8, y, 5, 5, (220, 210, 190), lw=1.2)
    neck = [(-22, 128), (22, 128), (24, 166), (-24, 166)]
    p.shape(neck, Z_SKIN, smooth=False)
    p.shape([(-56, 150), (56, 150), (46, 190), (0, 206), (-46, 190)], SCARF)
    # уши, голова
    for sx in (-1, 1):
        p.shape([(sx * 50, 62), (sx * 62, 66), (sx * 64, 86), (sx * 56, 98), (sx * 48, 92)], Z_SKIN)
        p.ellipse(sx * 58, 100, 3.2, 4.5, (220, 186, 90), lw=1)   # серьги
    p.shape(HEAD, Z_SKIN)
    p.shade(HEAD, [(70, 10), (30, 14), (22, 40), (26, 70), (20, 100), (10, 128), (4, 150), (70, 170)], Z_SKIN_SH, 230, soft=3)
    p.shade(HEAD, [(-50, 30), (-58, 40), (-58, 90), (-48, 120), (-44, 106), (-50, 80), (-48, 48)], WARM, 140, soft=2)
    # морщины
    for y in (40, 46):
        p.curve([(-24, y), (0, y - 2), (24, y)], col=(160, 116, 98), lw=1.2)
    for sx in (-1, 1):
        p.curve([(sx * 18, 104), (sx * 26, 118), (sx * 22, 128)], col=(150, 106, 90), lw=1.6)   # носогубные
        p.curve([(sx * 38, 66), (sx * 44, 70)], col=(150, 106, 90), lw=1.2)
        p.curve([(sx * 38, 74), (sx * 44, 76)], col=(150, 106, 90), lw=1.2)
    # глаза (прищур)
    open_ = 3.5 if expr != "shock" else 6
    blink = (t % 3.6) < .1
    for sx in (-1, 1):
        cx, cy = sx * 21, 70
        if blink:
            p.curve([(cx - 11, cy), (cx + 11, cy + 1)], lw=2.4)
        else:
            p.shape([(cx - 11, cy), (cx, cy - open_), (cx + 11, cy), (cx, cy + open_ * .6)], (230, 224, 214), line=False)
            p.ellipse(cx + look[0] * 3, cy, 4.2, 4.2, (70, 80, 90), line=False)
            p.ellipse(cx + look[0] * 3, cy, 2, 2, (20, 18, 18), line=False)
            p.curve([(cx - 12, cy), (cx, cy - open_ - 2), (cx + 12, cy)], lw=2.6)
        tilt = 4 if expr == "stern" else 0
        p.shape([(sx * 8, 58 + tilt), (sx * 22, 54), (sx * 32, 58), (sx * 20, 57)], Z_HAIR_SH, line=False)
    # нос, рот
    p.shade(HEAD, [(2, 72), (10, 98), (14, 106), (2, 108)], Z_SKIN_SH, 160, soft=1.5)
    p.curve([(-8, 104), (0, 109), (8, 104)], lw=2)
    my = 120
    if talk and (math.sin(t * 15) + math.sin(t * 9.7)) > .4:
        p.shape([(-10, my - 2), (10, my - 2), (8, my + 7), (-8, my + 7)], (110, 50, 50))
    else:
        p.curve([(-14, my + 1), (0, my - 1), (14, my + 2)], lw=2.4)
    # сигарета в уголке рта
    if smoke:
        p.shape([(12, my), (44, my + 6), (44, my + 11), (12, my + 5)], (236, 232, 222), lw=1.2, smooth=False)
        p.ellipse(45, my + 8, 3, 3, (240, 110, 50), line=False)
    # волосы: седое каре с начёсом
    hair = [(-60, 100), (-62, 40), (-50, 4), (-24, -14), (10, -16), (40, -6), (60, 24), (62, 70), (60, 104), (50, 70), (44, 40),
            (20, 24), (-10, 30), (-40, 36), (-50, 70)]
    p.shape(hair, Z_HAIR)
    p.shade(hair, [(10, -40), (80, -40), (80, 120), (20, 120)], Z_HAIR_SH, 255, soft=3)
    for k in range(-44, 50, 14):
        p.curve([(k, -6), (k + 6, 16), (k + 2, 30)], col=Z_HAIR_SH, lw=1.2)
    # очки на цепочке
    for sx in (-1, 1):
        p.ellipse(sx * 21, 71, 15, 12, None, lw=1.8)
    p.curve([(-6, 70), (6, 70)], lw=1.8, smooth=False)
    return p.result()
