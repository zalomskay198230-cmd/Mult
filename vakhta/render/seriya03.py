"""ВАХТА. Серия 3. Запуск: python3 seriya03.py ../tts/s03 ../seriya03.mp4"""
from toonlib import *

LINES = {
    "02": "Михалыч не дал открыть. Сказал — это трубы стучат. Металл на морозе.",
    "03": "Только трубы так не стучат. Три раза. Ровно.",
    "04": "Через час он сам заварил эту дверь. Молча. Даже не посмотрел, что внутри.",
    "05": "Тимур спросил: а если там человек? Михалыч ответил: там никого нет. И ушёл.",
    "06": "Ночью Тимур не выдержал. Поставил телефон напротив двери и включил запись.",
    "07": "Утром мы смотрели видео втроём.",
    "08": "Час ночи. Ничего. Два. Ничего. Три часа ночи.",
    "09": "Свет в коридоре мигнул. А когда загорелся снова — дверь была приоткрыта.",
    "10": "Мы побежали туда. Шов на месте. Дверь заварена. Её никто не трогал.",
}

PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2)], 0.4),
    ("s03", [("03", 0.2)], 0.6),
    ("s04", [("04", 0.2)], 0.5),
    ("s05", [("05", 0.2)], 0.5),
    ("s06", [("06", 0.2)], 0.6),
    ("s07", [("07", 0.2)], 0.6),
    ("s08", [("08", 0.2)], 0.5),
    ("s09", [("09", 0.2)], 1.2),
    ("s10", [("10", 0.2)], 3.4),
]
setup(LINES, PLAN)

CORR = ("corr_bg", (140, 144, 150), (100, 104, 110))
FLICK0, FLICK1 = 1.3, 3.3   # мигание света в s09 (локальное время)


def title(t, L, n):
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
    txt = f"серия {n}"
    d.text(((W - f2.getlength(txt)) / 2, 340), txt, font=f2, fill=(int(255 * a),) * 3, stroke_width=4, stroke_fill=INK)
    return img


def s01(t, L):
    return title(t, L, 3)


def s02(t, L):
    img = bg_room(*CORR).copy()
    floor_strip(img)
    door_close(img, t, dx=-170)
    toon(img, 520, 1240, 1.05, "misha", "serious", ("point", "front"), (-.8, 0), t, talk=True)
    return zoom(img, 1 + .05 * t / L, .5, .45)


def s03(t, L):
    img = bg_room(*CORR).copy()
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 80)
    for i, (x, y) in enumerate([(60, 160), (440, 260), (120, 400)]):  # призрачные «ТУК»
        a = .25 + .15 * math.sin(t * 3 + i)
        d.text((x, y), "тук", font=f, fill=tuple(int(140 + 60 * a) for _ in range(3)), stroke_width=4, stroke_fill=(110, 114, 120))
    toon(img, W / 2, 1330, 1.55, "ilya", "worried", ("down", "down"), (.6, -.2), t, talk=True)
    return zoom(img, 1 + .08 * t / L, .5, .42)


SPARKS = [(random.Random(i).uniform(-2.6, -.4), random.Random(i + 99).uniform(250, 520), random.Random(i + 7).random()) for i in range(40)]


def s04(t, L):
    img = bg_room(*CORR).copy()
    floor_strip(img)
    prog = min(1, max(0, (t - .4) / (L - 1.2)))
    x0, x1, y1 = door_close(img, t, dx=-150, weld=prog, hot=True, frost=False)
    spark_y = 120 + (1060 - 120) * prog
    hot_on = .4 < t < L - .8
    # Михалыч сдвигается вместе со швом, рука у точки сварки
    hand_y_off = 350 * .95 - 175 * .95 * math.sin(.15)
    hands = toon(img, 640, spark_y + hand_y_off, .95, "misha", "serious", ("point", "down"), (-1, 0), t, legs=spark_y < 760)
    # сварочная маска
    d = ImageDraw.Draw(img)
    hx, hy = 640, spark_y + hand_y_off - 505 * .95
    d.rounded_rectangle([hx - 92, hy - 80, hx + 80, hy + 96], radius=26, fill=(50, 54, 60), outline=INK, width=5)
    d.rectangle([hx - 66, hy - 20, hx + 40, hy + 20], fill=(30, 60, 50), outline=INK, width=4)
    sx, sy = x1, spark_y
    if hot_on:
        fl = .7 + .3 * math.sin(t * 40) * math.sin(t * 17)
        glow(img, (sx, sy), 160 * fl, (90, 120, 160), 1)
        glow(img, (sx, sy), 50, (200, 200, 255), 1)
        d = ImageDraw.Draw(img)
        for ang, sp, ph in SPARKS:
            life = (t * 2.2 + ph) % 1
            vx, vy = sp * math.cos(ang), sp * math.sin(ang)
            px = sx + vx * life * .6
            py = sy + vy * life * .6 + 900 * (life * .6) ** 2
            d.line([px, py, px - vx * .04, py - vy * .04], fill=(255, 230, 140), width=4)
    return img


def s05(t, L):
    img = bg_room(*CORR).copy()
    floor_strip(img)
    split = L * .48
    toon(img, 220, 1240, .95, "timur", "worried", ("front", "front"), (1, 0), t, talk=t < split)
    mx = 520 + (0 if t < split + 1.8 else (t - split - 1.8) * 520)
    walking = t > split + 1.8
    toon(img, mx, 1240, .95, "misha", "serious", ("down", "down"), (-1, 0) if not walking else (1, 0), t,
         talk=split < t < split + 1.8, walk=t if walking else None)
    return zoom(img, 1.02, .5, .5)


def phone(d, cx, cy, s=1.0, rec=True, t=0.0):
    w, h = 220 * s, 420 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(30 * s), fill=(30, 30, 36), outline=INK, width=6)
    d.rounded_rectangle([cx - w / 2 + 14 * s, cy - h / 2 + 30 * s, cx + w / 2 - 14 * s, cy + h / 2 - 30 * s], radius=int(12 * s), fill=(70, 86, 76))
    if rec and int(t * 2) % 2 == 0:
        d.ellipse([cx - w / 2 + 28 * s, cy - h / 2 + 44 * s, cx - w / 2 + 48 * s, cy - h / 2 + 64 * s], fill=(240, 50, 50))
    return [cx - w / 2 + 14 * s, cy - h / 2 + 30 * s, cx + w / 2 - 14 * s, cy + h / 2 - 30 * s]


def s06(t, L):
    img = Image.new("RGB", (W, H), WALL)
    corridor(img, cam=.2, prints=False, t=t)
    img = Image.eval(img, lambda v: int(v * .45))  # ночь
    d = ImageDraw.Draw(img)
    # штатив с телефоном
    d.line([360, 1050, 300, 1270], fill=INK, width=8); d.line([360, 1050, 420, 1270], fill=INK, width=8); d.line([360, 1050, 360, 1270], fill=INK, width=8)
    scr = phone(d, 360, 900, .8, rec=t > L * .6, t=t)
    glow(img, ((scr[0] + scr[2]) / 2, (scr[1] + scr[3]) / 2), 90, (20, 50, 30), .8)
    if t < L * .7:
        tx = 140 - 60 * max(0, t - L * .55) * 3
        toon(img, tx, 1330, .9, "timur", "worried", ("down", "front"), (1, 0), t, walk=t if t > L * .55 else None)
    return zoom(img, 1 + .06 * t / L, .5, .6)


def s07(t, L):
    img = bg_room("canteen", (128, 136, 130), (90, 96, 92)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1080, W, H], fill=(86, 88, 92)); d.line([0, 1080, W, 1080], fill=INK, width=6)
    for i, (who, x) in enumerate((("dasha", 140), ("ilya", 360), ("timur", 580))):
        toon(img, x, 1180, .72, who, "neutral" if t < L * .6 else "worried", ("down", "front"), (0, 1), t + i, legs=False)
    phone(ImageDraw.Draw(img), 360, 1120, .9, rec=False)
    return zoom(img, 1 + .05 * t / L, .5, .6)


def feed(t, ajar=0.0, dark=1.0, stamp="03:00"):
    """кадр с камеры телефона: ночной, зернистый"""
    img = bg_room(*CORR).copy()
    floor_strip(img)
    x0, x1, y1 = door_close(img, t, weld=1.0, ajar=ajar)
    if ajar > 0:
        img = vapor(img, t, x1 - 40, x1 + 60, y1, .8)
    g = np.asarray(img.convert("L")).astype(np.float32) * dark
    g = g * .9 + np.random.default_rng(int(t * 24)).normal(0, 14, g.shape)
    g[::4] *= .85
    rgb = np.stack([g * .62, g * .86, g * .66], -1)
    out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(FONT_B, 40)
    if int(t * 2) % 2 == 0:
        d.ellipse([40, 60, 72, 92], fill=(240, 50, 50))
    d.text((84, 54), "REC", font=f, fill=(240, 240, 240))
    d.text((W - 40 - f.getlength(stamp), 54), stamp, font=f, fill=(240, 240, 240))
    for (ax, ay, bx, by) in [(30, 30, 110, 30), (30, 30, 30, 110), (W - 30, 30, W - 110, 30), (W - 30, 30, W - 30, 110),
                             (30, H - 30, 110, H - 30), (30, H - 30, 30, H - 110), (W - 30, H - 30, W - 110, H - 30), (W - 30, H - 30, W - 30, H - 110)]:
        d.line([ax, ay, bx, by], fill=(240, 240, 240), width=5)
    return out


def s08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    hh = 1 if p < .3 else 2 if p < .62 else 3
    mm = int((t * 7) % 60)
    return feed(t, stamp=f"0{hh}:{mm:02d}:{int(t * 40) % 60:02d}")


def s09(t, L):
    if FLICK0 < t < FLICK1:
        rnd = random.Random(int(t * 12))
        dark = .08 if rnd.random() < .7 else .6
    else:
        dark = 1.0
    ajar = 1.0 if t >= FLICK1 else 0.0
    img = feed(t, ajar=ajar, dark=dark, stamp=f"03:{17 + int(t):02d}:{int(t * 24) % 60:02d}")
    if ajar:
        img = zoom(img, 1 + .25 * min(1, (t - FLICK1) / (L - FLICK1)), .78, .5)
    return img


def s10(t, L):
    half = 2.4
    if t < half:  # бегут по коридору
        img = Image.new("RGB", (W, H), WALL)
        corridor(img, cam=.3 * t / half, prints=True, t=t)
        for who, x, ph in (("dasha", 200, 0), ("ilya", 380, 1.2), ("timur", 540, 2.3)):
            s = .5 + .2 * t / half
            toon(img, x, 1100 + 140 * t / half, s, who, "scared", ("down", "down"), (0, 0), t + ph, walk=t + ph,
                 bob=8 * abs(math.sin((t + ph) * 9)))
        return shake(img, t, 4)
    tt = t - half
    img = bg_room(*CORR).copy()
    floor_strip(img)
    door_close(img, t, weld=1.0)
    img = zoom(img, 1.0 + .25 * min(1, tt / 3), .86, .5)   # наезд на холодный шов
    vo_end = .2 + dur("10.mp3")
    end = vo_end + 1.6
    if t > end:
        a = min(1, (t - end) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f2 = ImageFont.truetype(FONT_SUB, 64)
            for j, line in enumerate(("серия 4", "скоро")):
                dd.text(((W - f2.getlength(line)) / 2, 520 + j * 84), line, font=f2, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    s4, l4 = span("s04")
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(s4 + .4, s4 + l4 - .8), (span("s08")[0], span("s09")[0] + span("s09")[1])],
        hits=[span("s09")[0] + FLICK1, span("s10")[0] + 2.4])
