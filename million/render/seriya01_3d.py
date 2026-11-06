"""ВЕРНУТЬ МИЛЛИОН. Серия 1 — 3D-версия.
Фон и Денис — кадры из Blender (million/render3d/frames, 12 к/с, «пластилиновая» анимация),
поверх — телефон-вставки, субтитры, счётчик и плашки из 2D-версии.
Запуск: python3 seriya01_3d.py ../tts/s01 ../seriya01_3d.mp4"""
import os, math
from PIL import Image
import seriya01 as E
from toonlib import *

FR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "render3d", "frames")
_cache = {}


def bg(name, t):
    f = int(t * 12)
    while f >= 0:
        path = os.path.join(FR, f"{name}_{f:04d}.png")
        if os.path.exists(path):
            break
        f -= 1
    if path not in _cache:
        if len(_cache) > 40:
            _cache.clear()
        _cache[path] = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
    return _cache[path].copy()


def s01(t, L, cue):
    img = bg("s01", t)
    E.rain(img, t)
    img = E.panel(img, E.old_s01, t, L, cue, pos=(410, 120), w=280, t0=.15)
    return shake(img, t, 3)


def s02(t, L):
    img = bg("s02", t)
    img = E.panel(img, E.old_s01, 99, 1, {"01": 0}, pos=(430, 170), w=250)
    E.counter_plate(img, t)
    return img


def s03(t, L, cue):
    img = bg("s03", t)
    img = E.panel(img, E.old_s04, cue["03"] + .01, L, {"04": cue["03"] + 99}, pos=(420, 190), w=260, t0=.9)
    E.day_plate(img, "ДЕНЬ 1")
    E.counter_plate(img, t)
    return img


def s04(t, L, cue):
    img = bg("s04", t)
    img = E.panel(img, E.old_s04, t, L, cue, pos=(420, 160), w=270)
    E.counter_plate(img, t)
    return img


def s05(t, L, cue):
    img = bg("s05", t)
    img = E.panel(img, E.old_s05, t, L, None, pos=(430, 150), w=260)
    E.counter_plate(img, t)
    p = (t - cue["05"]) / dur("05.mp3")
    return shake(img, t, 5 if .4 < p < .5 else 0)


def s06(t, L, cue):
    img = bg("s06", t)
    p = (t - cue["06"]) / dur("06.mp3")
    img = E.panel(img, E.old_s06, t, L, cue, pos=(410, 130), w=290)
    E.day_plate(img, "ДЕНЬ 2")
    E.counter_plate(img, t)
    return shake(img, t, 9 if .55 < p < .62 else 0)


def s07(t, L, cue):
    img = bg("s07", t)
    img = E.panel(img, E.old_s07, t, L, cue, pos=(420, 150), w=270)
    E.counter_plate(img, t)
    return img


def s08(t, L, cue):
    img = bg("s08", t)
    p = (t - cue["08"]) / dur("08.mp3")
    if p < .6:
        img = E.panel(img, E.old_s08, t, L, None, pos=(420, 150), w=270)
    E.day_plate(img, "ДЕНЬ 3")
    E.counter_plate(img, t)
    return shake(img, t, 10 if .68 < p < .78 else 0)


def s09(t, L):
    img = bg("s09", t)
    img = E.panel(img, E.old_s09, t, L, None, pos=(440, 170), w=250)
    E.counter_plate(img, t)
    return img


def s10(t, L):
    img = bg("s10", t)
    img = E.panel(img, E.old_s10, t, L, None, pos=(380, 110), w=320)
    E.counter_plate(img, t)
    return img


def s11(t, L):
    img = bg("s11", t)
    E.counter_plate(img, t)
    return shake(img, t, 3)


def s12(t, L, cue):
    img = bg("s12", t)
    E.rain(img, t, n=90)
    img = E.panel(img, E.old_s12, t, L, cue, pos=(440, 540), w=240, tilt=4)
    E.counter_plate(img, t)
    return img


def s13(t, L, cue):
    vo_end = cue["13"] + dur("13.mp3")
    img = bg("s13", t)
    E.rain(img, t, n=90)
    d = ImageDraw.Draw(img)
    f1, f2 = E.F(96, FONT_SUB), E.F(56, FONT_SUB)
    d.text((W / 2 - f1.getlength("347 ₽") / 2, 250), "347 ₽", font=f1, fill=E.RED, stroke_width=5, stroke_fill=INK)
    d.text((W / 2 - f2.getlength("→ 1 000 000 ₽") / 2, 370), "→ 1 000 000 ₽", font=f2, fill=E.GREEN, stroke_width=4, stroke_fill=INK)
    E.day_plate(img, "ДЕНЬ 1 ВОЗВРАТА")
    if t > vo_end + .4:
        a = min(1, (t - vo_end - .4) / .3)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f3 = E.F(60, FONT_SUB)
            for j, line in enumerate(("серия 2", "скоро")):
                dd.text(((W - f3.getlength(line)) / 2, 520 + j * 80), line, font=f3, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    c06 = span("s06")[0] + 0.05
    run({n: globals()[n] for n, *_ in E.PLAN},
        hits=[span("s01")[0] + .4, c06 + dur("06.mp3") * .58, span("s08")[0] + .05 + dur("08.mp3") * .7,
              span("s10")[0] + 1.2, span("s12")[0] + span("s12")[1] - .6])
