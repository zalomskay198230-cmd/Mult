"""ВАХТА. Серия 5. Запуск: python3 seriya05.py ../tts/s05 ../seriya05.mp4"""
from toonlib import *

LINES = {
    "02": "Михалыч вернулся под утро. Сказал, что был в машинном отделении. Про рацию — ни слова.",
    "03": "А в обед пропал Тимур.",
    "04": "Мы обыскали всю платформу. Каюты, склад, буровую. Даже вертолётную площадку.",
    "05": "Даша вызывала его каждые пять минут.",
    "05r": "«Тимур, ответь. Тимур, приём. Тимур!»",
    "06": "Тогда я спустился вниз. По опоре. Туда, где у самой воды служебная площадка.",
    "07": "Зимой туда никто не ходит. Волны захлёстывают решётку, всё во льду.",
    "08": "На решётке лежал телефон Тимура. Экраном вниз. Мокрый.",
    "09": "Он ещё работал. Последнее видео — сегодня, двенадцать сорок. Сорок секунд.",
    "10": "Я нажал «воспроизвести».",
}

PLAN = [
    ("s01", [], 3.0),
    ("s02", [("02", 0.2)], 0.4),
    ("s03", [("03", 0.3)], 1.2),
    ("s04", [("04", 0.2)], 0.5),
    ("s05", [("05", 0.2), ("05r", None)], 0.6),
    ("s06", [("06", 0.2)], 0.6),
    ("s07", [("07", 0.2)], 0.5),
    ("s08", [("08", 0.2)], 0.6),
    ("s09", [("09", 0.2)], 0.6),
    ("s10", [("10", 0.3)], 4.4),
]
setup(LINES, PLAN)

CORR = ("corr_bg", (140, 144, 150), (100, 104, 110))


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


def s01(t, L):
    return title(t, L, 5)


def s02(t, L):
    img = Image.new("RGB", (W, H), WALL)
    corridor(img, cam=.1, prints=False, t=t)
    mz = min(1, t / 3.0)
    s = .45 + .45 * mz   # Михалыч идёт к камере по коридору
    toon(img, 360, 1000 + 330 * mz, s, "misha", "neutral", ("down", "down"), (0, 0), t,
         walk=t if mz < 1 else None, talk=mz >= 1, bob=0 if mz >= 1 else 5 * abs(math.sin(t * 9)))
    # Илья и Даша смотрят из-за края кадра
    toon(img, 70, 1620, 1.0, "ilya", "serious", ("down", "down"), (1, 0), t, legs=False)
    toon(img, 660, 1640, .95, "dasha", "worried", ("down", "down"), (-1, 0), t, legs=False)
    return img


def bunk(img, t, hat=True):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 980, W, H], fill=(96, 92, 88)); d.line([0, 980, W, 980], fill=INK, width=6)
    d.rectangle([60, 700, 660, 900], fill=(60, 84, 140), outline=INK, width=6)
    d.rounded_rectangle([80, 660, 260, 730], radius=20, fill=(236, 236, 232), outline=INK, width=5)
    d.rectangle([60, 900, 660, 960], fill=(120, 120, 126), outline=INK, width=5)
    d.rectangle([60, 960, 90, 1000], fill=(120, 120, 126), outline=INK, width=4)
    d.rectangle([630, 960, 660, 1000], fill=(120, 120, 126), outline=INK, width=4)
    if hat:  # жёлтая каска Тимура
        cx, cy = 450, 700
        d.chord([cx - 90, cy - 80, cx + 90, cy + 60], 180, 360, fill=(232, 170, 60), outline=INK, width=6)
        d.rounded_rectangle([cx - 110, cy - 14, cx + 110, cy + 6], radius=6, fill=(232, 170, 60), outline=INK, width=5)
        d.arc([cx - 60, cy - 66, cx, cy - 10], 200, 260, fill=(250, 220, 150), width=9)


def s03(t, L):
    img = bg_room("cabin", (150, 140, 124), (110, 104, 94)).copy()
    bunk(img, t)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 40)
    d.rounded_rectangle([230, 180, 490, 260], radius=10, fill=(240, 240, 236), outline=INK, width=5)
    d.text((360 - f.getlength("ТИМУР") / 2, 196), "ТИМУР", font=f, fill=INK)
    return zoom(img, 1 + .25 * min(1, t / L), .6, .55)


SEARCH = [("каюты", -100, 140), ("склад", -150, -160), ("буровая", 85, -110), ("площадка", 230, 130)]


def s04(t, L):
    img = Image.new("RGB", (W, H), SEA)
    d = ImageDraw.Draw(img)
    rnd = random.Random(1)
    for i in range(70):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        d.line([(x0 + 30 * t) % W, y0, (x0 + 30 * t) % W + 40, y0], fill=(70, 84, 104), width=5)
    cx, cy = W / 2 + 10, H / 2 - 40
    platform_top(img, cx, cy, 1.0, t)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_SUB, 34)
    for i, (name, dx, dy) in enumerate(SEARCH):
        t0 = 2.6 + i * 1.3
        if t < t0:
            continue
        a = min(1, (t - t0) / .2)
        x, y = cx + dx, cy + dy
        r = 34 * a
        d.line([x - r, y - r, x + r, y + r], fill=(230, 50, 50), width=12)
        d.line([x - r, y + r, x + r, y - r], fill=(230, 50, 50), width=12)
        d.text((x - f.getlength(name) / 2, y + 42), name, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=INK)
    SNOW.draw(img, t)
    return zoom(img, 1.05)


def s05(t, L, cue):
    img = bg_room("radio", (70, 92, 88), (46, 58, 56)).copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1000, W, H], fill=(84, 88, 90), outline=INK, width=6)
    rt = cue["05r"]
    talking = rt <= t < rt + dur("05r.mp3")
    hands = toon(img, W / 2, 1290, 1.4, "dasha", "worried" if t < rt + 4 else "scared", ("down", "ear"), (.3, 0), t, talk=talking)
    # тангента рации в руке
    hx, hy = hands[1]
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([hx - 26, hy - 60, hx + 26, hy + 30], radius=10, fill=(40, 40, 46), outline=INK, width=5)
    d.line([hx, hy + 30, hx - 80, hy + 300], fill=INK, width=5)
    hand(d, (hx, hy + 6), 1.4)
    # часы — каждые пять минут
    f = ImageFont.truetype(FONT_B, 44)
    mins = 13 * 60 + 5 + 5 * int(t / 1.6)
    d.rounded_rectangle([40, 140, 240, 220], radius=12, fill=(20, 26, 24), outline=INK, width=5)
    d.text((62, 152), f"{mins // 60}:{mins % 60:02d}", font=f, fill=(240, 80, 70))
    return zoom(img, 1 + .05 * t / L, .5, .45)


def leg_scene(img, t, prog):
    """спуск по опоре: колонна с лестницей едет вверх, внизу появляется море"""
    d = ImageDraw.Draw(img)
    scroll = prog * 1500
    water_y = 1900 - scroll
    # колонна
    d.rectangle([150, -10, 570, H + 10], fill=(214, 216, 222), outline=INK, width=7)
    for k in range(-2, 12):
        y = (k * 260 - scroll * .9) % 2860 - 260
        d.line([150, y, 570, y], fill=(180, 184, 192), width=6)
    stripe = 1500 - scroll
    if stripe < H:
        d.rectangle([150, stripe, 570, stripe + 40], fill=(232, 96, 60), outline=INK, width=5)
    if stripe + 40 < H:
        d.rectangle([150, stripe + 40, 570, H + 10], fill=(40, 42, 48), outline=INK, width=6)
    # лестница
    d.line([300, -10, 300, H + 10], fill=(110, 114, 124), width=12)
    d.line([420, -10, 420, H + 10], fill=(110, 114, 124), width=12)
    for k in range(-1, 30):
        y = (k * 70 - scroll) % 2100 - 70
        d.line([300, y, 420, y], fill=(110, 114, 124), width=10)
    # море снизу
    if water_y < H:
        pts = [(0, H)] + [(x, water_y + 16 * math.sin(x * .02 + t * 3)) for x in range(0, W + 10, 10)] + [(W, H)]
        d.polygon(pts, fill=SEA)
        d.line(pts[1:-1], fill=(200, 220, 236), width=6)
    return water_y


def s06(t, L):
    img = vgrad(W, H, (90, 94, 104), (60, 64, 74))
    prog = min(1, t / L)
    leg_scene(img, t, prog)
    k = math.sin(t * 6)
    toon(img, 360, 820 + 10 * k, .95, "ilya", "worried", ("up" if k > 0 else "out", "out" if k > 0 else "up"), (0, 1), t)
    STORM.draw(img, t, streak=True)
    return shake(img, t, 2)


def s07(t, L):
    img = vgrad(W, H, (78, 82, 94), (50, 54, 64))
    d = ImageDraw.Draw(img)
    pts = [(0, 760)] + [(x, 700 + 20 * math.sin(x * .015 + t * 2)) for x in range(0, W + 10, 12)] + [(W, 760)]
    d.rectangle([0, 700, W, 760], fill=SEA)
    d.polygon(pts + [(W, 700), (0, 700)], fill=SEA)
    # опора уходит вверх
    d.rectangle([520, -10, 700, 860], fill=(214, 216, 222), outline=INK, width=6)
    d.rectangle([520, 600, 700, 640], fill=(232, 96, 60), outline=INK, width=5)
    d.rectangle([520, 640, 700, 860], fill=(40, 42, 48), outline=INK, width=5)
    grating(img, 860, t, waves=False)
    toon(img, 290, 1180, .95, "ilya", "worried", ("down", "down"), (.5, .3), t)
    grating(img, 860, t, base=False)
    SNOW.draw(img, t, wind=400)
    return zoom(img, 1.02)


def s08(t, L):
    img = Image.new("RGB", (W, H), (44, 50, 62))
    grating(img, 0, t, waves=False)
    d = ImageDraw.Draw(img)
    # телефон экраном вниз
    cx, cy = 360, 640
    d.rounded_rectangle([cx - 140, cy - 260, cx + 140, cy + 260], radius=36, fill=(30, 30, 36), outline=INK, width=7)
    d.rounded_rectangle([cx - 90, cy - 230, cx - 10, cy - 130], radius=24, fill=(50, 50, 58), outline=INK, width=5)
    for (ox, oy) in ((-62, -200), (-38, -160)):
        d.ellipse([cx + ox - 16, cy + oy - 16, cx + ox + 16, cy + oy + 16], fill=(16, 16, 20), outline=(80, 80, 90), width=3)
    rnd = random.Random(6)
    for _ in range(26):   # капли
        x, y, r = cx + rnd.uniform(-130, 130), cy + rnd.uniform(-250, 250), rnd.uniform(4, 11)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(90, 120, 150), outline=INK, width=2)
        d.ellipse([x - r * .4, y - r * .6, x, y - r * .2], fill=(220, 236, 250))
    # рука Ильи тянется к телефону
    k = min(1, max(0, (t - (L - 2.4)) / 1.2))
    if k > 0:
        hx, hy = cx + 40, H + 120 - 560 * k
        d.line([hx, H + 200, hx, hy], fill=INK, width=72); d.line([hx, H + 200, hx, hy], fill=COVER, width=60)
        hand(d, (hx, hy), 2.0)
    return zoom(img, 1 + .06 * t / L, .5, .5)


def phone_ui(img, t, playing=False, play_t=0.0):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 90, 90, 630, 1190
    d.rounded_rectangle([x0 - 26, y0 - 26, x1 + 26, y1 + 26], radius=60, fill=(24, 24, 30), outline=INK, width=8)
    d.rounded_rectangle([x0, y0, x1, y1], radius=36, fill=(16, 18, 24))
    f = ImageFont.truetype(FONT_B, 28)
    d.text((x0 + 30, y0 + 20), "12:52", font=f, fill=(240, 240, 240))
    d.rounded_rectangle([x1 - 90, y0 + 24, x1 - 40, y0 + 48], radius=5, outline=(240, 240, 240), width=3)
    d.rectangle([x1 - 86, y0 + 28, x1 - 80, y0 + 44], fill=(240, 60, 60))
    d.text((x1 - 150, y0 + 20), "3%", font=f, fill=(240, 60, 60))
    # превью видео: тёмная вода
    vx0, vy0, vx1, vy1 = x0 + 30, y0 + 150, x1 - 30, y0 + 820
    rng = np.random.default_rng(int(t * 24) if playing else 1)
    g = np.full((vy1 - vy0, vx1 - vx0), 26, np.float32)
    yy = np.arange(vy1 - vy0)[:, None]
    xx = np.arange(vx1 - vx0)[None, :]
    wave = 40 * np.sin(xx * .03 + (t * 2 if playing else 0)) + (vy1 - vy0) * .55
    g[yy > wave] = 44
    g += rng.normal(0, 10, g.shape)
    vid = Image.fromarray(np.clip(np.stack([g * .8, g * .95, g * 1.15], -1), 0, 255).astype(np.uint8))
    img.paste(vid, (vx0, vy0))
    d.rectangle([vx0, vy0, vx1, vy1], outline=(60, 64, 76), width=3)
    fb = ImageFont.truetype(FONT_B, 34)
    if not playing:
        cx, cy = (vx0 + vx1) / 2, (vy0 + vy1) / 2
        d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(240, 240, 240))
        d.polygon([(cx - 22, cy - 36), (cx - 22, cy + 36), (cx + 40, cy)], fill=(20, 20, 26))
        d.text((vx0 + 20, vy1 - 56), "0:40", font=fb, fill=(240, 240, 240), stroke_width=3, stroke_fill=INK)
    else:
        p = min(1, (t - play_t) / 40)
        d.line([vx0 + 20, vy1 - 30, vx1 - 20, vy1 - 30], fill=(120, 120, 130), width=6)
        d.line([vx0 + 20, vy1 - 30, vx0 + 20 + (vx1 - vx0 - 40) * p, vy1 - 30], fill=(240, 60, 60), width=6)
        s = int(t - play_t)
        d.text((vx0 + 20, vy1 - 80), f"0:{s:02d} / 0:40", font=ImageFont.truetype(FONT_B, 26), fill=(240, 240, 240))
    d.text((x0 + 30, vy1 + 30), "Сегодня, 12:40", font=fb, fill=(240, 240, 240))
    d.text((x0 + 30, vy1 + 80), "Видео · 0:40", font=ImageFont.truetype(FONT_B, 26), fill=(150, 150, 160))
    # трещины на экране
    for pts in ([(560, 140), (500, 260), (520, 380), (460, 470)], [(500, 260), (610, 330)], [(520, 380), (420, 360)]):
        d.line(pts, fill=(200, 210, 220), width=3)
    return img


def s09(t, L):
    img = Image.new("RGB", (W, H), (10, 12, 16))
    phone_ui(img, t)
    return zoom(img, 1.0 + .05 * t / L)


def s10(t, L):
    tap = .3 + dur("10.mp3") + .2
    if t < tap:   # лицо Ильи, подсвеченное экраном
        img = vgrad(W, H, (24, 28, 36), (12, 14, 20))
        glow(img, (360, 1200), 420, (40, 70, 110), 1)
        toon(img, W / 2, 1330, 1.55, "ilya", "scared", ("down", "down"), (0, .8), t)
        return zoom(img, 1 + .08 * t / tap, .5, .42)
    img = Image.new("RGB", (W, H), (10, 12, 16))
    phone_ui(img, t, playing=True, play_t=tap)
    d = ImageDraw.Draw(img)
    if t < tap + .35:   # касание пальцем
        r = 40 + 200 * (t - tap)
        d.ellipse([360 - r, 575 - r, 360 + r, 575 + r], outline=(255, 255, 255), width=6)
    img = zoom(img, 1 + .5 * min(1, (t - tap) / 3), .5, .38)
    return end_card(img, t, tap + 3.0, 6)


if __name__ == "__main__":
    s5, l5 = span("s05")
    tap = span("s10")[0] + .3 + dur("10.mp3") + .2
    run({n: globals()[n] for n, *_ in PLAN},
        static=[(s5, s5 + l5), (tap, tap + 3.0)],
        hits=[span("s03")[0] + .5, span("s08")[0] + .3, tap])
