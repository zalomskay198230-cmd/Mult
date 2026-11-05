"""ВАХТА. Серия 2. Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4"""
from toonlib import *

LINES = {
    "02": "Следы шли до жилого блока. А дальше — мокрая дорожка по коридору.",
    "03": "Михалыч сказал: никому не выходить. Собрал всех в столовой и пересчитал.",
    "04": "Девятнадцать. Все на месте. Никто наружу не выходил.",
    "05": "Тогда чьи это следы?",
    "06": "Мы с Тимуром пошли по коридору. Следы обрывались у стены. Просто у стены.",
    "07": "Тимур достал план жилого блока. На плане двадцать кают.",
    "08": "Я пересчитал двери. Двадцать одна.",
    "09": "На последней двери нет номера. Её нет на плане. А из-под неё тянет холодом и пахнет морем.",
    "10": "И тут изнутри кто-то постучал. Три раза.",
}

PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2)], 0.4),
    ("s03", [("03", 0.1)], 0.4),
    ("s04", [("04", 0.1)], 0.5),
    ("s05", [("05", 0.3)], 0.8),
    ("s06", [("06", 0.2)], 0.5),
    ("s07", [("07", 0.2)], 0.5),
    ("s08", [("08", 0.2)], 0.8),
    ("s09", [("09", 0.2)], 0.6),
    ("s10", [("10", 0.2)], 4.6),
]
setup(LINES, PLAN)

WALL, WALL_D, FLOOR, CEIL = (156, 160, 164), (132, 136, 142), (96, 100, 106), (118, 122, 128)
DOOR = (186, 176, 150)


# ---------- коридор в перспективе ----------
VX, VY, F = W / 2, 560, 400


def pj(X, Y, Z):
    return (VX + X * F / Z, VY + Y * F / Z)


def corridor(img, cam=0.0, zmax=6.0, prints=True, doors=21, t=0.0):
    d = ImageDraw.Draw(img)
    ze = zmax - cam
    # стены, пол, потолок
    d.polygon([pj(-1, -1.4, .2), pj(1, -1.4, .2), pj(1, -1.4, ze), pj(-1, -1.4, ze)], fill=CEIL)
    d.polygon([pj(-1, 1.8, .2), pj(1, 1.8, .2), pj(1, 1.8, ze), pj(-1, 1.8, ze)], fill=FLOOR)
    d.polygon([pj(-1, -1.4, .2), pj(-1, 1.8, .2), pj(-1, 1.8, ze), pj(-1, -1.4, ze)], fill=WALL)
    d.polygon([pj(1, -1.4, .2), pj(1, 1.8, .2), pj(1, 1.8, ze), pj(1, -1.4, ze)], fill=WALL_D)
    d.rectangle([*pj(-1, -1.4, ze), *pj(1, 1.8, ze)], fill=(170, 174, 178), outline=INK, width=4)
    for a, b in [((-1, -1.4), (-1, 1.8)), ((1, -1.4), (1, 1.8))]:
        pass
    for X, Y in [(-1, -1.4), (1, -1.4), (-1, 1.8), (1, 1.8)]:
        d.line([pj(X, Y, .2), pj(X, Y, ze)], fill=INK, width=5)
    # плинтус
    for X in (-1, 1):
        d.polygon([pj(X, 1.6, .3), pj(X, 1.8, .3), pj(X, 1.8, ze), pj(X, 1.6, ze)], fill=(80, 84, 92))
    # двери (по очереди слева/справа), дальние рисуем первыми
    items = []
    for i in range(doors):
        side = -1 if i % 2 == 0 else 1
        z0 = 1.1 + (i // 2) * 0.48 - cam
        if z0 < .35 or z0 + .3 > ze:
            continue
        items.append((z0, side, i))
    for z0, side, i in sorted(items, reverse=True):
        z1 = z0 + .3
        q = [pj(side, -.5, z0), pj(side, -.5, z1), pj(side, 1.8, z1), pj(side, 1.8, z0)]
        d.polygon(q, fill=DOOR, outline=INK, width=max(2, int(6 / z0)))
        hx, hy = pj(side, .7, z0 + .25)
        r = max(2, 9 / z0)
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(120, 120, 126), outline=INK)
    # лампы на потолке
    for k in range(6):
        z = 1.3 + k * .9 - cam
        if z < .4 or z > ze:
            continue
        a, b = pj(-.25, -1.4, z), pj(.25, -1.4, z + .25)
        d.rectangle([a[0], a[1], b[0], b[1] + 3], fill=(250, 248, 224), outline=INK, width=2)
        glow(img, ((a[0] + b[0]) / 2, a[1] + 10), max(10, 70 / z), (70, 66, 46), .8)
    # мокрые следы по полу
    if prints:
        d = ImageDraw.Draw(img)
        for k in range(14):
            z = 1.0 + k * .34 - cam
            if z < .5 or z > ze - .1:
                continue
            x, y = pj(.16 if k % 2 else -.16, 1.8, z)
            boot_print(d, x, y, 1.1 / z, 0, k % 2 == 0)


def big_number(img, txt, y, size=150, col=YELLOW, pop=1.0):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, int(size * (0.8 + 0.2 * pop)))
    x = (W - f.getlength(txt)) / 2
    d.text((x, y), txt, font=f, fill=col, stroke_width=6, stroke_fill=(58, 50, 14))


# ---------- сцены ----------
def s01(t, L):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    rnd = random.Random(1)
    for i in range(70):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        x = (x0 + 30 * t) % W
        d.line([x, y0, x + 40, y0], fill=(70, 84, 104), width=5)
    platform_top(img, W / 2 + 30, H / 2 + 120, 1.0, t)
    SNOW.draw(img, t)
    img = zoom(img, 1.12 - .1 * t / L)
    d = ImageDraw.Draw(img)
    a = min(1, max(0, (t - .3) / .5))
    f = ImageFont.truetype(FONT_SUB, 140)
    tw = f.getlength("ВАХТА")
    mask = Image.new("L", (W, H)); ImageDraw.Draw(mask).text(((W - tw) / 2, 170), "ВАХТА", font=f, fill=int(255 * a), stroke_width=12)
    img.paste(Image.new("RGB", (W, H), (200, 170, 50)), (0, 0), mask.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .6)))
    d.text(((W - tw) / 2, 170), "ВАХТА", font=f, fill=tuple(int(c * a) for c in YELLOW), stroke_width=5, stroke_fill=(58, 50, 14))
    f2 = ImageFont.truetype(FONT_SUB, 46)
    d.text(((W - f2.getlength("серия 2")) / 2, 340), "серия 2", font=f2, fill=(int(255 * a),) * 3, stroke_width=4, stroke_fill=INK)
    return img


def s02(t, L):
    img = Image.new("RGB", (W, H), WALL)
    corridor(img, cam=.5 * t / L, t=t)
    return img


def crowd(d, y, seed, n=7, s=.55):
    rnd = random.Random(seed)
    for i in range(n):
        x = 60 + i * (600 / (n - 1)) + rnd.uniform(-15, 15)
        yy = y + rnd.uniform(-10, 10)
        R = 46 * s * 2
        d.rounded_rectangle([x - 70 * s, yy + 30 * s, x + 70 * s, yy + 200 * s], radius=int(20 * s), fill=rnd.choice([COVER, NAVY, (60, 110, 80)]), outline=INK, width=4)
        d.ellipse([x - R / 2, yy - R / 2, x + R / 2, yy + R / 2], fill=SKIN, outline=INK, width=4)
        if rnd.random() < .6:
            d.chord([x - R / 2, yy - R * .62, x + R / 2, yy + 4], 180, 360, fill=rnd.choice([(232, 170, 60), (240, 240, 240), (36, 36, 42)]), outline=INK, width=4)
        for side in (-1, 1):
            d.ellipse([x + side * 11 * s * 2 - 8, yy - 6, x + side * 11 * s * 2 + 8, yy + 10], fill=(255, 255, 255), outline=INK, width=2)
            d.ellipse([x + side * 11 * s * 2 - 3, yy - 1, x + side * 11 * s * 2 + 3, yy + 5], fill=INK)


def s03(t, L):
    img = bg_room("canteen", (128, 136, 130), (90, 96, 92)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 760, W, H], fill=(86, 88, 92)); d.line([0, 760, W, 760], fill=INK, width=6)
    crowd(d, 690, 3)
    crowd(d, 900, 4, n=5, s=.75)
    toon(img, 560, 1210, 1.0, "misha", "serious", ("down", "point"), (-.8, 0), t, talk=True)
    # счётчик людей
    n = min(19, int(1 + 18 * max(0, (t - 2.6) / (L - 3.0))))
    if t > 2.6:
        big_number(img, str(n), 120, 170, pop=(t * 6) % 1)
    return zoom(img, 1 + .05 * t / L, .5, .5)


def s04(t, L):
    img = bg_room("canteen", (128, 136, 130), (90, 96, 92)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1050, W, H], fill=(86, 88, 92)); d.line([0, 1050, W, 1050], fill=INK, width=6)
    for i, (who, x, face) in enumerate([("timur", 110, "neutral"), ("dasha", 280, "worried"), ("misha", 450, "serious"), ("ilya", 620, "worried")]):
        toon(img, x, 1160, .62, who, face, ("down", "down"), (0, 0), t + i, bob=2 * math.sin(t * 2 + i))
    pop = min(1, t / .25)
    big_number(img, "19 / 19", 140, 130, pop=pop)
    # зелёная галочка
    cx, cy, r = W / 2, 400, 70 * pop
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(80, 190, 110), outline=INK, width=6)
    if pop > .5:
        d.line([cx - 32, cy + 2, cx - 8, cy + 28, cx + 36, cy - 26], fill=(255, 255, 255), width=14, joint="curve")
    return img


def s05(t, L):
    img = bg_room("corr_bg", (140, 144, 150), (100, 104, 110)).copy()
    toon(img, W / 2, 1330, 1.55, "ilya", "scared", ("down", "down"), (0, 0), t, talk=t < 2.6)
    img = zoom(img, 1 + .12 * t / L, .5, .42)
    return shake(img, t, 3 if t < .6 else 0)


def s06(t, L):
    half = L * .5
    if t < half:
        img = Image.new("RGB", (W, H), WALL)
        corridor(img, cam=.25 * t / half, t=t)
        # Илья и Тимур идут к камере
        for who, x, ph in (("timur", 270, 0), ("ilya", 450, 1.4)):
            s = .55 + .18 * t / half
            hands = toon(img, x, 1080 + 120 * t / half, s, who, "worried", ("down", "point" if who == "timur" else "down"), (0, .3), t + ph, walk=t + ph,
                         bob=6 * abs(math.sin((t + ph) * 9)))
            if who == "timur":
                hx, hy = hands[1]
                lay = Image.new("L", (W, H)); ImageDraw.Draw(lay).polygon([(hx, hy), (hx + 260, hy + 520), (hx - 40, hy + 560)], fill=80)
                img.paste(Image.new("RGB", (W, H), (255, 246, 210)), (0, 0), lay.filter(ImageFilter.GaussianBlur(14)))
        return img
    tt = t - half
    # вид сверху: следы упираются в стену
    base = Image.new("RGB", (W, H), FLOOR)
    d = ImageDraw.Draw(base)
    for y in range(400, H, 52):
        d.line([0, y, W, y], fill=(88, 92, 98), width=3)
    d.rectangle([0, 0, W, 400], fill=(170, 174, 178)); d.line([0, 400, W, 400], fill=INK, width=8)
    d.rectangle([0, 380, W, 400], fill=(80, 84, 92))
    for k in range(9):
        y = 1240 - k * 98
        boot_print(d, 340 + (30 if k % 2 else -30), y, 1.1, 0, k % 2 == 0)
    dark = Image.eval(base, lambda v: int(v * .35))
    cy = 1100 - 640 * min(1, tt / (L - half - .4))
    m = Image.new("L", (W, H)); ImageDraw.Draw(m).ellipse([360 - 230, cy - 230, 360 + 230, cy + 230], fill=255)
    img = Image.composite(base, dark, m.filter(ImageFilter.GaussianBlur(30)))
    return zoom(img, 1.02 + .05 * tt / (L - half))


def s07(t, L):
    img = bg_room("corr_bg", (140, 144, 150), (100, 104, 110)).copy()
    d = ImageDraw.Draw(img)
    px0, py0, px1, py1 = 70, 120, 650, 1080
    d.rectangle([px0 + 10, py0 + 12, px1 + 10, py1 + 12], fill=(60, 60, 66))
    d.rectangle([px0, py0, px1, py1], fill=(236, 226, 196), outline=INK, width=6)
    f = ImageFont.truetype(FONT_B, 30)
    d.text(((W - f.getlength("ЖИЛОЙ БЛОК · ПЛАН")) / 2, py0 + 24), "ЖИЛОЙ БЛОК · ПЛАН", font=f, fill=(60, 70, 110))
    # коридор и каюты
    cx0, cx1 = 315, 405
    d.rectangle([cx0, 200, cx1, 1040], outline=(60, 70, 110), width=4)
    fn = ImageFont.truetype(FONT_B, 34)
    shown = int(min(20, 20 * max(0, (t - 2.4) / 2.2)))
    for i in range(20):
        col, row = i % 2, i // 2
        x0 = 110 if col == 0 else cx1 + 10
        x1 = cx0 - 10 if col == 0 else 610
        y0 = 210 + row * 82
        hl = i < shown
        d.rectangle([x0, y0, x1, y0 + 74], fill=(250, 226, 120) if hl else None, outline=(60, 70, 110), width=4)
        num = str(i + 1)
        d.text(((x0 + x1) / 2 - fn.getlength(num) / 2, y0 + 16), num, font=fn, fill=(60, 70, 110))
    # руки Тимура держат план
    for x in (130, 590):
        hand(d, (x, py1 + 6), 1.6)
    if shown >= 20:
        big_number(img, "20", 1100, 120)
    return zoom(img, 1 + .05 * t / L, .5, .4)


def s08(t, L):
    """боковая стена с дверями, камера едет вправо, двери считаются"""
    img = vgrad(W, H, (160, 164, 168), (140, 144, 150))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 930, W, H], fill=FLOOR); d.line([0, 930, W, 930], fill=INK, width=6)
    sp = 230
    total_shift = 21 * sp - W / 2 - 40
    prog = min(1, t / max(1, L - 2.2))
    prog = prog * prog * (3 - 2 * prog)
    shift = -120 + total_shift * prog
    fn = ImageFont.truetype(FONT_B, 26)
    fb = ImageFont.truetype(FONT_SUB, 64)
    counted = 0
    for i in range(21):
        x = 120 + i * sp - shift
        if x < -200 or x > W + 200:
            if x < W / 2:
                counted = i + 1
            continue
        last = i == 20
        d.rectangle([x - 70, 520, x + 70, 930], fill=DOOR if not last else (170, 176, 184), outline=INK, width=6)
        d.ellipse([x + 38, 720, x + 56, 738], fill=(120, 120, 126), outline=INK, width=3)
        d.rectangle([x - 40, 560, x + 40, 600], fill=(240, 240, 236) if not last else (150, 156, 164), outline=INK, width=4)
        if not last:
            nm = str(i + 1)
            d.text((x - fn.getlength(nm) / 2, 566), nm, font=fn, fill=INK)
        else:  # иней по краям
            for k in range(14):
                yy = 530 + k * 28
                d.line([x - 70, yy, x - 52, yy + 10], fill=(236, 246, 255), width=3)
                d.line([x + 70, yy + 8, x + 52, yy + 18], fill=(236, 246, 255), width=3)
        if x <= W / 2 + 10:
            counted = i + 1
            col = (240, 80, 70) if last else YELLOW
            txt = "?" if last else str(i + 1)
            d.text((x - fb.getlength(txt) / 2, 410), txt, font=fb, fill=col, stroke_width=5, stroke_fill=INK)
    big_number(img, str(max(1, counted)), 110, 160, col=(240, 80, 70) if counted >= 21 else YELLOW)
    return img


def door_close(img, t, knock=0.0):
    d = ImageDraw.Draw(img)
    jx = knock * 6 * math.sin(t * 80)
    x0, y0, x1, y1 = 150 + jx, 120, 570 + jx, 1060
    d.rectangle([x0 - 26, y0 - 26, x1 + 26, y1], fill=(120, 124, 130), outline=INK, width=6)
    d.rectangle([x0, y0, x1, y1], fill=(170, 176, 184), outline=INK, width=7)
    # пустая табличка
    d.rectangle([x0 + 130, y0 + 90, x1 - 130, y0 + 170], fill=(150, 156, 164), outline=INK, width=5)
    for sx in (x0 + 146, x1 - 146):
        d.ellipse([sx - 6, y0 + 124, sx + 6, y0 + 136], fill=INK)
    d.ellipse([x1 - 80, 590, x1 - 40, 630], fill=(120, 120, 126), outline=INK, width=5)
    d.rectangle([x1 - 120, 600, x1 - 60, 620], fill=(120, 120, 126), outline=INK, width=4)
    # иней
    rnd = random.Random(4)
    for k in range(40):
        side = rnd.choice([0, 1, 2])
        if side == 0:
            x, y = x0 + rnd.uniform(0, 30), rnd.uniform(y0, y1)
        elif side == 1:
            x, y = x1 - rnd.uniform(0, 30), rnd.uniform(y0, y1)
        else:
            x, y = rnd.uniform(x0, x1), y0 + rnd.uniform(0, 30)
        a = rnd.uniform(0, 6.3); l = rnd.uniform(10, 26)
        d.line([x, y, x + l * math.cos(a), y + l * math.sin(a)], fill=(236, 246, 255), width=3)
    return (x0, x1, y1)


def floor_strip(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1060, W, H], fill=FLOOR); d.line([0, 1060, W, 1060], fill=INK, width=6)


def vapor(img, t, x0, x1, y1, k=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    rnd = random.Random(8)
    for i in range(16):
        ph = rnd.random()
        life = (t * .35 + ph) % 1
        x = rnd.uniform(x0, x1) + 40 * math.sin(t + i)
        y = y1 - 10 - life * 260
        r = 30 + 70 * life
        a = int(110 * (1 - life) * k)
        ld.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(230, 240, 250, a))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(10))).convert("RGB")


def puddle(img, t, x0, x1, y1, grow):
    d = ImageDraw.Draw(img)
    w = (x1 - x0) * (.45 + .6 * grow)
    cx = (x0 + x1) / 2
    d.ellipse([cx - w / 2, y1 - 14, cx + w / 2, y1 + 60 + 90 * grow], fill=WET, outline=INK, width=4)
    d.arc([cx - w / 3, y1 + 10, cx + w / 4, y1 + 40 + 50 * grow], 190, 300, fill=(150, 196, 226), width=6)
    # свет из-под двери
    d.rectangle([x0 + 4, y1 - 8, x1 - 4, y1], fill=(150, 210, 240))


def s09(t, L):
    img = bg_room("corr_bg", (140, 144, 150), (100, 104, 110)).copy()
    floor_strip(img)
    x0, x1, y1 = door_close(img, t)
    puddle(img, t, x0, x1, y1, min(1, t / L))
    img = vapor(img, t, x0, x1, y1)
    toon(img, 600, 1660, 1.0, "ilya", "scared", ("down", "down"), (-.8, -.4), t, legs=False)
    return zoom(img, 1 + .08 * t / L, .5, .5)


KNOCKS = []  # заполняется ниже, локальное время сцены s10


def s10(t, L, cue):
    vo_end = cue["10"] + dur("10.mp3")
    ks = [vo_end + .3, vo_end + .85, vo_end + 1.4]
    k = max([max(0, 1 - (t - kt) / .25) for kt in ks if t >= kt] + [0])
    img = bg_room("corr_bg", (140, 144, 150), (100, 104, 110)).copy()
    floor_strip(img)
    x0, x1, y1 = door_close(img, t, knock=k)
    puddle(img, t, x0, x1, y1, 1)
    img = vapor(img, t, x0, x1, y1)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 90)
    for i, kt in enumerate(ks):
        if kt <= t < kt + .6:
            a = 1 - (t - kt) / .6
            x, y = [(120, 330), (430, 470), (180, 620)][i]
            d.text((x, y - 30 * (1 - a)), "ТУК", font=f, fill=tuple(int(c * (.4 + .6 * a)) for c in YELLOW), stroke_width=6, stroke_fill=INK)
    img = zoom(img, 1.05 + .2 * min(1, max(0, t - vo_end) / 2.5), .5, .45)
    img = shake(img, t, 14 * k)
    end = ks[-1] + 1.0
    if t > end:
        a = min(1, (t - end) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f2 = ImageFont.truetype(FONT_SUB, 64)
            for j, line in enumerate(("серия 3", "скоро")):
                dd.text(((W - f2.getlength(line)) / 2, 520 + j * 84), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    s10s, _ = span("s10")
    vo_end = s10s + 0.2 + dur("10.mp3")
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s05")[0] + .2, span("s09")[0] + .1],
        knocks=[vo_end + .3, vo_end + .85, vo_end + 1.4])
