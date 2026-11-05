"""ВАХТА. Серия 7. Запуск: python3 seriya07.py ../tts/s07 ../seriya07.mp4"""
from toonlib import *

LINES = {
    "02": "Тимур вёл себя как раньше. Шутил, помогал. Только он больше не мёрз. Ходил по палубе без куртки.",
    "03": "И не ел. Совсем. Даша заметила первой.",
    "04": "А по ночам он стоял у заваренной двери. Просто стоял. И слушал.",
    "05": "На третью ночь погас факел.",
    "06": "Без газа нет тепла. Через пару часов в каютах был мороз. Трубы начали лопаться.",
    "07": "Михалыч сказал: факел надо разжечь вручную. На самом конце стрелы. В шторм.",
    "08": "Тимур вызвался сам. Я пошёл с ним. «Не верь мне» — я это помнил.",
    "09": "Мы ползли по стреле. Ветер бил так, что звенели перила. Тимур был впереди.",
    "10": "У самого факела он обернулся. И сказал голосом Михалыча:",
    "10r": "«Они ещё ничего не знают».",
    "11": "И шагнул ко мне.",
}

PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2)], 0.4),
    ("s03", [("03", 0.2)], 0.5),
    ("s04", [("04", 0.2)], 0.6),
    ("s05", [("05", 0.2)], 2.6),
    ("s06", [("06", 0.2)], 0.5),
    ("s07", [("07", 0.2)], 0.4),
    ("s08", [("08", 0.2)], 0.6),
    ("s09", [("09", 0.2)], 0.5),
    ("s10", [("10", 0.2), ("10r", None), ("11", None)], 2.4),
]
setup(LINES, PLAN)

SHIRT, SHIRT_D = (176, 178, 186), (90, 94, 104)
CORR = ("corr_bg", (140, 144, 150), (100, 104, 110))


def end_card(img, t, start, lines):
    if t <= start:
        return img
    a = min(1, (t - start) / .4)
    img = Image.blend(img, Image.new("RGB", (W, H)), a)
    if a >= 1:
        dd = ImageDraw.Draw(img)
        f2 = ImageFont.truetype(FONT_SUB, 64)
        for j, line in enumerate(lines):
            dd.text(((W - f2.getlength(line)) / 2, 520 + j * 84), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


def breath(img, x, y, t, k=1.0):
    """пар изо рта на морозе"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i in range(3):
        life = (t * .7 + i / 3) % 1
        r = 14 + 40 * life
        ld.ellipse([x + 60 * life - r, y - 30 * life - r * .6, x + 60 * life + r, y - 30 * life + r * .6], fill=(235, 240, 250, int(150 * (1 - life) * k)))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(6))).convert("RGB")


def timur_shirt(img, x, y, s, face, arms, look, t, **kw):
    return toon(img, x, y, s, "timur", face, arms, look, t, outfit_c=SHIRT, pants_c=SHIRT_D, **kw)


def deck_bg(t, dark=1.0):
    img = vgrad(W, H, (80, 86, 98), (56, 60, 72))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=DECK); d.line([0, 1040, W, 1040], fill=INK, width=6)
    railing(d, 900)
    if dark < 1:
        img = Image.eval(img, lambda v: int(v * dark))
    return img


# ---------- сцены ----------
def s01(t, L):
    return title(t, L, 7)


def s02(t, L):
    img = deck_bg(t)
    sh = 3 * math.sin(t * 40)   # Илья дрожит
    toon(img, 200 + sh, 1180, .9, "ilya", "worried", ("front", "front"), (1, 0), t)
    img = breath(img, 230, 1180 - 505 * .9 + 60, t)
    timur_shirt(img, 520, 1180, .9, "smile", ("down", "down"), (-1, 0), t, talk=False)
    STORM.draw(img, t, streak=True)
    return zoom(img, 1.02, .5, .55)


def s03(t, L):
    img = bg_room("canteen", (128, 136, 130), (90, 96, 92)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=(86, 88, 92)); d.line([0, 1040, W, 1040], fill=INK, width=6)
    timur_shirt(img, 520, 1100, .85, "smile", ("down", "down"), (0, 0), t, legs=False)
    toon(img, 180, 1100, .85, "dasha", "worried", ("down", "down"), (1, 0), t, legs=False)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, 1080], fill=(150, 112, 80), outline=INK, width=5)   # стол
    for i, (x, full) in enumerate(((180, False), (520, True))):
        d.ellipse([x - 110, 1010, x + 110, 1070], fill=(240, 240, 236), outline=INK, width=5)
        if full:   # нетронутая тарелка: котлета и пюре
            d.ellipse([x - 70, 1018, x + 10, 1050], fill=(236, 214, 150), outline=INK, width=4)
            d.ellipse([x + 4, 1020, x + 70, 1048], fill=(130, 80, 50), outline=INK, width=4)
    if t > L * .5:   # стрелочка от Даши к тарелке
        d.line([260, 760, 470, 980], fill=(230, 60, 50), width=8)
        d.polygon([(470, 980), (430, 970), (460, 940)], fill=(230, 60, 50))
    return zoom(img, 1 + .06 * t / L, .5, .6)


def s04(t, L):
    img = bg_room(*CORR).copy()
    floor_strip(img)
    door_close(img, t, weld=1.0, dx=-120)
    img = Image.eval(img, lambda v: int(v * .4))   # ночь
    glow(img, (430, 1050), 200, (40, 50, 60), .8)
    timur_shirt(img, 560, 1240, 1.0, "neutral", ("point", "down"), (-1, 0), t, blink=False)
    return zoom(img, 1 + .08 * t / L, .55, .5)


def flare_scene(img, t, fire):
    """платформа сбоку и факельная стрела; fire 1 → 0 — факел гаснет"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 900, W, H], fill=SEA)
    paste_platform(img, 300, 904, .7, lit=fire > .3, light_k=fire)
    d = ImageDraw.Draw(img)
    bx0, by0, bx1, by1 = 380, 780, 680, 330
    d.line([bx0, by0, bx1, by1], fill=(140, 144, 152), width=16)
    d.line([bx0, by0, bx1, by1], fill=INK, width=4)
    for k in range(10):
        f0 = k / 10
        x, y = bx0 + (bx1 - bx0) * f0, by0 + (by1 - by0) * f0
        d.line([x, y, x + 20, y + 26], fill=INK, width=3)
    if fire > .02:
        flame(img, bx1, by1 - 6, t, .9 * fire + .1)
    else:   # дым
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for i in range(6):
            life = (t * .5 + i / 6) % 1
            r = 20 + 60 * life
            ld.ellipse([bx1 - 40 * life - r, by1 - 40 - 200 * life - r, bx1 - 40 * life + r, by1 - 40 - 200 * life + r], fill=(60, 60, 66, int(160 * (1 - life))))
        img.paste(Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(6))).convert("RGB"))
    return img


def s05(t, L):
    img = vgrad(W, H, (30, 34, 46), (20, 24, 34))
    out0 = 1.4
    fire = 1.0 if t < out0 else max(0, 1 - (t - out0) / .5)
    flick = 1 if t < out0 - .8 else (.5 + .5 * math.sin(t * 30))
    img = flare_scene(img, t, fire * flick if t < out0 else fire)
    SNOW.draw(img, t)
    return zoom(img, 1.1 - .08 * t / L, .7, .4)


def s06(t, L):
    img = bg_room("cabin", (150, 140, 124), (110, 104, 94)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1000, W, H], fill=(96, 92, 88)); d.line([0, 1000, W, 1000], fill=INK, width=6)
    # труба под потолком
    d.rectangle([0, 150, W, 200], fill=(150, 154, 162), outline=INK, width=5)
    burst = t > L * .6
    if burst:
        d.polygon([(410, 150), (440, 120), (460, 160), (480, 118), (500, 150)], fill=(150, 154, 162), outline=INK)
        rnd = random.Random(int(t * 24))
        for _ in range(26):
            a = rnd.uniform(.3, 2.8); r = rnd.uniform(20, 200)
            x, y = 455 + r * math.cos(a), 200 + r * math.sin(a)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=ICE)
    # иней растёт от краёв
    fz = min(1, t / L)
    rnd = random.Random(2)
    for _ in range(int(260 * fz)):
        side = rnd.choice([0, 1, 2, 3])
        depth = rnd.uniform(0, 160 * fz)
        if side == 0:
            x, y = depth, rnd.uniform(0, H)
        elif side == 1:
            x, y = W - depth, rnd.uniform(0, H)
        elif side == 2:
            x, y = rnd.uniform(0, W), 200 + depth
        else:
            x, y = rnd.uniform(0, W), 1000 - depth * .4
        a = rnd.uniform(0, 6.3); l = rnd.uniform(10, 30)
        d.line([x, y, x + l * math.cos(a), y + l * math.sin(a)], fill=(236, 246, 255), width=3)
    # термометр
    temp = int(18 - 30 * fz)
    f = ImageFont.truetype(FONT_SUB, 60)
    d.rounded_rectangle([470, 260, 680, 360], radius=14, fill=(240, 240, 236), outline=INK, width=5)
    txt = f"{temp:+d}°"
    d.text((575 - f.getlength(txt) / 2, 270), txt, font=f, fill=(60, 110, 200) if temp < 0 else (200, 70, 50))
    sh = 3 * math.sin(t * 40)
    toon(img, 210 + sh, 1480, 1.0, "ilya", "worried", ("front", "front"), (.5, -.5), t, legs=False)
    toon(img, 520 - sh, 1490, .95, "dasha", "worried", ("front", "front"), (-.5, -.5), t, legs=False)
    img = breath(img, 240, 1480 - 505 + 60, t)
    img = breath(img, 545, 1490 - 480 + 60, t + .4)
    return img


def s07(t, L):
    img = bg_room("radio", (70, 92, 88), (46, 58, 56)).copy()
    img = Image.eval(img, lambda v: int(v * .8))
    d = ImageDraw.Draw(img)
    # схема на доске: стрела и факел
    d.rectangle([60, 140, 660, 560], fill=(40, 60, 50), outline=INK, width=8)
    d.line([120, 500, 560, 220], fill=(236, 236, 230), width=6)
    for k in range(8):
        x = 120 + k * 55; y = 500 - k * 35
        d.line([x, y, x + 14, y + 20], fill=(236, 236, 230), width=3)
    d.ellipse([540, 190, 590, 240], outline=(250, 120, 110), width=6)
    f = ImageFont.truetype(FONT_B, 30)
    d.text((440, 260), "факел", font=f, fill=(250, 120, 110))
    d.text((120, 170), "~ 40 м", font=f, fill=(236, 236, 230))
    toon(img, W / 2 + 60, 1290, 1.2, "misha", "serious", ("point", "down"), (-.6, -.4), t, talk=True)
    return zoom(img, 1 + .04 * t / L, .5, .5)


def s08(t, L):
    img = bg_room("radio", (70, 92, 88), (46, 58, 56)).copy()
    img = Image.eval(img, lambda v: int(v * .8))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 70)
    if t > L * .5:   # призрачное «не верь мне»
        a = .3 + .2 * math.sin(t * 3)
        d.text(((W - f.getlength("не верь мне")) / 2, 200), "не верь мне", font=f, fill=tuple(int(100 + 80 * a) for _ in range(3)), stroke_width=3, stroke_fill=(70, 80, 76))
    timur_shirt(img, 490, 1290, 1.0, "smile", ("down", "up"), (0, 0), t, blink=False)
    toon(img, 180, 1330, .95, "ilya", "serious" if t < L * .5 else "worried", ("down", "down"), (1, 0), t, legs=False)
    return zoom(img, 1 + .05 * t / L, .5, .5)


def s09(t, L):
    img = vgrad(W, H, (40, 44, 56), (24, 28, 38))
    d = ImageDraw.Draw(img)
    # стрела по диагонали через кадр
    ax, ay, bx, by = -60, 1300, 780, 120
    for off, col in ((-60, (120, 124, 132)), (60, (120, 124, 132))):
        d.line([ax + off, ay + off * .7, bx + off, by + off * .7], fill=col, width=14)
    for k in range(16):
        f0 = k / 16
        x, y = ax + (bx - ax) * f0, ay + (by - ay) * f0
        d.line([x - 60, y - 42, x + 60, y + 42], fill=(100, 104, 112), width=8)
    vib = 4 * math.sin(t * 50)
    d.line([ax - 60, ay - 150 + vib, bx - 60, by - 150 + vib], fill=(226, 110, 40), width=7)   # перила
    # двое ползут вверх по стреле
    p = t / L
    for who, f0, ph in (("ilya", .28, 0), ("timur", .48, 1.3)):
        f1 = f0 + .12 * p
        x, y = ax + (bx - ax) * f1, ay + (by - ay) * f1
        k = math.sin(t * 5 + ph)
        if who == "timur":
            timur_shirt(img, x, y - 20, .55, "neutral", ("up", "out"), (1, -1), t, bob=6 * k)
        else:
            toon(img, x, y - 20, .55, "ilya", "scared", ("up", "out"), (1, -1), t, bob=6 * k)
    STORM.draw(img, t, streak=True)
    return shake(img, t, 5)


def s10(t, L, cue):
    rt, nt = cue["10r"], cue["11"]
    img = vgrad(W, H, (34, 38, 50), (20, 24, 34))
    d = ImageDraw.Draw(img)
    # горелка факела позади
    d.rectangle([420, 300, 520, 620], fill=(70, 72, 80), outline=INK, width=6)
    d.ellipse([400, 270, 540, 330], fill=(40, 40, 46), outline=INK, width=6)
    speaking = rt <= t < rt + dur("10r.mp3")
    pupil = 0 if t < rt - .3 else min(1, (t - rt + .3) / .6)
    step = 0 if t < nt else min(1, (t - nt) / 1.2)
    timur_shirt(img, W / 2, 1330 + 300 * step, 1.55 + 1.2 * step, "neutral", ("down", "down"), (0, 0), t,
                talk=speaking, blink=False, pupil=pupil)
    STORM.draw(img, t, streak=True)
    img = zoom(img, 1 + .06 * t / L, .5, .42)
    img = shake(img, t, 3 + 6 * step)
    return end_card(img, t, nt + 1.4, ("финал", "скоро"))


if __name__ == "__main__":
    s10s, _ = span("s10")
    cue10 = {c: s for n, st, l, sc in scenes if n == "s10" for s, c, d in sc}
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s05")[0] + 1.4, span("s06")[0] + span("s06")[1] * .6, s10s + cue10["10r"], s10s + cue10["11"]])
