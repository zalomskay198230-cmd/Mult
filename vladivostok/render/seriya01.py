"""«ТУМАН». Серия 1. Paper-cut: бумажные слои с тенями и параллаксом (paper.py), озвучка — Дмитрий.
Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from paper import W, H, Layer, hills, compose, glow, rough

LINES = {
    "01": "Во Владивостоке закрыли Русский мост. Военные. С обеих сторон.",
    "02": "Моя сестра — на острове. В общежитии ДВФУ. Последнее сообщение от неё: «Они в коридоре».",
    "03": "Всё началось утром. В бухту Золотой Рог сам зашёл сухогруз. Без экипажа.",
    "04": "Портовые поднялись на борт. Через час их не стало слышно. Через два — они спустились обратно.",
    "05": "Правило первое: они идут на звук. А город, где все сигналят в пробке, — это кормушка.",
    "06": "Правило второе: туман. Здесь он приходит с моря за десять минут. В тумане они слепые. Но и ты тоже.",
    "07": "По мосту не пустят. Значит, по воде. У отца лодка в Спортивной гавани. Бензина — на один рейс.",
    "08": "Набережная. Тихо. Фонари мигают. На лавке сидит человек и смотрит на залив. Не моргая.",
    "09": "Я отвязал лодку. Мотор завёлся с третьего раза. Слишком громко.",
    "10": "Человек на лавке встал. Потом встали все. Вся набережная.",
    "11": "Я вышел в залив. Сзади — город. Впереди — остров. И туман.",
    "12": "А из тумана навстречу шёл сухогруз. Тот самый. И с палубы кто-то светил фонарём. Прямо на меня.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.35) for k in LINES]
PLAN[0] = ("s01", [("01", 0.3)], 0.3)
PLAN[-1] = ("s12", [("12", 0.1)], 3.4)
setup(LINES, PLAN)

F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
FULL = [(-40, -40), (W + 40, -40), (W + 40, H + 40), (-40, H + 40)]


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


# ---------- бумажные элементы ----------
def stars(L, n=60, seed=3, ymax=600):
    r = random.Random(seed)
    for _ in range(n):
        x, y, s = r.uniform(0, W), r.uniform(0, ymax), r.choice((2, 2, 3, 4))
        L.hole([x - s, y - s, x + s, y + s])


def wave(color, y, amp, k, t, speed, depth, seed):
    L = Layer(color, depth, seed)
    return L.poly([(x, y + amp * math.sin(x * k + t * speed)) for x in range(-40, W + 60, 20)] + [(W + 60, H + 40), (-40, H + 40)])


def fog(color, y, t, speed, depth, seed, amp=34, drift=0.0):
    L = Layer(color, depth, seed)
    return L.poly([(x + drift, y + amp * math.sin(x * .013 + t * speed + seed)) for x in range(-80, W + 100, 30)] + [(W + 100, H + 40), (-80, H + 40)])


def person(L, x, y, s=1.0, hunch=0.0, col=None, lean=0.0):
    """бумажный силуэт человека; y — уровень ступней; hunch — сутулость (зомби)"""
    hx = x + 18 * s * hunch + lean * 10 * s
    L.ellipse([hx - 17 * s, y - 168 * s + 18 * s * hunch, hx + 17 * s, y - 134 * s + 18 * s * hunch], col)
    L.poly([(x - 24 * s, y - 132 * s + 10 * s * hunch), (x + 24 * s + 14 * s * hunch, y - 132 * s + 14 * s * hunch),
            (x + 22 * s, y - 64 * s), (x - 22 * s, y - 64 * s)], col)
    L.poly([(x - 20 * s, y - 66 * s), (x - 4 * s, y - 66 * s), (x - 8 * s, y), (x - 22 * s, y)], col)
    L.poly([(x + 4 * s, y - 66 * s), (x + 20 * s, y - 66 * s), (x + 22 * s, y), (x + 8 * s, y)], col)
    if hunch:   # руки висят вперёд
        L.line([(x + 18 * s, y - 120 * s), (x + 40 * s, y - 80 * s)], int(9 * s), col)
    return L


def tag(img, title, sub="", y=150, col=(200, 50, 46)):
    """бумажная бирка с надписью"""
    f1, f2 = F(34, FONT_SUB), F(22)
    w = max(f1.getlength(title), f2.getlength(sub) if sub else 0) + 48
    h = 62 if not sub else 96
    lay = Layer((244, 238, 224), 1, 77)
    x0 = (W - w) / 2
    lay.poly([(x0, y), (x0 + w, y + 4), (x0 + w - 4, y + h), (x0 + 4, y + h - 3)])
    lay.rect(x0 - 4, y + 6, x0 + 10, y + h - 8, col)
    pic = compose((0, 0, 0), [lay])
    m = lay.img.getchannel("A")
    sh = m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .5))
    shadow = Image.new("L", (W, H), 0); shadow.paste(sh, (4, 7))
    img.paste((0, 0, 0), (0, 0), shadow)
    img.paste(pic, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.text((x0 + 26, y + 10), title, font=f1, fill=(30, 28, 30))
    if sub:
        d.text((x0 + 26, y + 56), sub, font=f2, fill=(90, 84, 80))


# ---------- сцены ----------
def russky_bridge(t, lights=True):
    back = Layer((236, 228, 196), .1, 11).ellipse([510, 140, 630, 260]).rect(-40, -40, W + 40, 620, (120, 130, 170))
    sky = Layer((22, 34, 70), .2, 1).poly(FULL)
    stars(sky)
    sky.hole([520, 150, 620, 250])
    far = hills(Layer((40, 56, 98), .4, 2), 720, 260, 5)
    mid = hills(Layer((30, 42, 78), .7, 3), 780, 170, 8, 3)
    br = Layer((214, 216, 222), 1.0, 4)
    for px in (150, 590):
        br.poly([(px - 40, 860), (px - 8, 300), (px + 8, 300), (px + 40, 860), (px + 22, 860), (px, 420), (px - 22, 860)])
        for k in range(9):
            for sgn in (-1, 1):
                br.line([(px, 330 + k * 12), (px + sgn * (40 + k * 38), 800)], 2)
    br.rect(-40, 795, W + 40, 818)
    army = Layer((24, 30, 30), 1.4, 7)
    army.poly([(60, 790), (90, 760), (250, 760), (280, 790)]).rect(110, 740, 200, 762).line([(200, 750), (280, 735)], 6)
    for wx in (95, 150, 205, 255):
        army.ellipse([wx - 16, 778, wx + 16, 810], (14, 16, 18))
    army.rect(320, 770, 330, 800).line([(325, 772), (520, 772)], 8, (200, 60, 60))
    water = wave((20, 48, 84), 860, 10, .05, t, 2, 1.2, 5)
    w2 = wave((14, 36, 66), 1000, 14, .035, t, -1.6, 1.6, 6)
    img = compose((14, 22, 48), [back, sky, far, mid, br, army, water, w2], shift=(math.sin(t * .5) * 8, 0))
    if lights:
        glow(img, (170, 735), 40, (255, 60, 60) if int(t * 4) % 2 else (60, 90, 255), .9)
    return img


def s01(t, L, cue):
    img = russky_bridge(t)
    tag(img, "РУССКИЙ МОСТ", "закрыт · военные", 150)
    return shake(img, t, 4 if t < .4 else 0)


def s02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    back = Layer((250, 210, 120), .1, 21).rect(80, 220, 640, 760)
    dorm = Layer((44, 46, 70), .3, 22).poly(FULL)
    for r in range(5):
        for c in range(4):
            if (r * 4 + c) % 3:
                dorm.hole_rect([110 + c * 136, 250 + r * 100, 190 + c * 136, 310 + r * 100])
    phone = Layer((24, 24, 28), 1.4, 23).poly([(150, 420), (570, 400), (590, 1200), (170, 1220)])
    screen = Layer((238, 236, 230), 1.5, 24).poly([(176, 470), (548, 452), (564, 1150), (192, 1166)])
    bub = Layer((90, 150, 220), 1.7, 25)
    if p > .55:
        bub.poly([(210, 760), (520, 748), (526, 840), (214, 852)])
    img = compose((30, 30, 50), [back, dorm, phone, screen, bub])
    d = ImageDraw.Draw(img)
    d.text((214, 500), "Аня", font=F(40, FONT_SUB), fill=(30, 30, 34))
    d.text((214, 552), "ДВФУ · общежитие · 21:40", font=F(20), fill=(110, 110, 116))
    if p > .55:
        d.text((236, 782), "Они в коридоре", font=F(34, FONT_SUB), fill=(255, 255, 255))
    return img


def zolotoy(t, ship_x):
    sky = Layer((200, 206, 214), .2, 31).poly(FULL)
    sun = Layer((246, 220, 170), .25, 32).ellipse([480, 200, 600, 320])
    far = hills(Layer((150, 160, 176), .4, 33), 760, 280, 3)
    city = Layer((110, 120, 140), .6, 34)
    r = random.Random(6)
    x = -20
    while x < W:
        w, h = r.randint(40, 90), r.randint(80, 220)
        city.rect(x, 820 - h, x + w, 840)
        x += w + 4
    br = Layer((236, 238, 240), .9, 35)   # Золотой мост: V-образные пилоны
    for px in (170, 560):
        br.poly([(px - 50, 300), (px - 34, 300), (px + 2, 800), (px - 14, 800)])
        br.poly([(px + 34, 300), (px + 50, 300), (px + 14, 800), (px - 2, 800)])
        for k in range(8):
            for sgn in (-1, 1):
                br.line([(px, 330 + k * 14), (px + sgn * (30 + k * 30), 640)], 2)
    br.rect(-40, 636, W + 40, 652)
    sea = wave((70, 96, 120), 860, 8, .05, t, 1.4, 1.0, 36)
    ship = Layer((110, 60, 46), 1.2, 37)
    sx = ship_x
    ship.poly([(sx, 860), (sx + 360, 860), (sx + 330, 920), (sx + 20, 920)])
    ship.rect(sx + 250, 790, sx + 330, 862, (130, 76, 60)).rect(sx + 270, 760, sx + 316, 792, (150, 90, 70))
    for k in range(4):
        ship.rect(sx + 40 + k * 50, 820, sx + 84 + k * 50, 862, ((60, 100, 140), (170, 70, 50), (70, 120, 80), (200, 160, 60))[k])
    near = wave((50, 76, 100), 960, 12, .04, t, -1.2, 1.5, 38)
    return compose((180, 186, 196), [sky, sun, far, city, br, sea, ship, near], shift=(math.sin(t * .4) * 6, 0))


def s03(t, L, cue):
    img = zolotoy(t, -360 + 520 * ease(t / L))
    tag(img, "БУХТА ЗОЛОТОЙ РОГ", "07:40 · экипажа нет", 150)
    return img


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    sky = Layer((90, 96, 110), .2, 41).poly(FULL)
    hull = Layer((96, 52, 40), .8, 42).poly([(-40, 300), (W + 40, 260), (W + 40, 900), (-40, 940)])
    for k in range(9):
        hull.rect(20 + k * 80, 320, 34 + k * 80, 880, (84, 44, 34))
    gang = Layer((170, 172, 178), 1.1, 43).poly([(560, 320), (600, 330), (180, 1040), (130, 1030)])
    pier = Layer((60, 62, 68), 1.3, 44).rect(-40, 1030, W + 40, H + 40)
    walk = Layer((22, 22, 26), 1.5, 45)
    if p > .55:   # спускаются обратно — сутулые
        k = ease((p - .55) / .45)
        for i in range(3):
            q = min(1, max(0, k * 1.3 - i * .2))
            x = 560 - 400 * q
            y = 330 + 700 * q
            person(walk, x, y, .9, hunch=1.0)
    else:         # поднимаются на борт
        for i in range(3):
            q = min(1, max(0, p / .5 * 1.2 - i * .2))
            x = 160 + 400 * q
            y = 1040 - 700 * q
            person(walk, x, y, .9)
    img = compose((70, 74, 86), [sky, hull, gang, pier, walk])
    tag(img, "+2 часа" if p > .55 else "+1 час", "", 150, (60, 60, 66))
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    board = Layer((230, 224, 206), .1, 51).poly(FULL)
    road = Layer((70, 72, 80), .5, 52).rect(-40, 640, W + 40, 900)
    cars = Layer((60, 110, 170), 1.0, 53)
    for i, cx in enumerate((40, 200, 360, 520)):
        col = ((60, 110, 170), (200, 60, 50), (240, 240, 236), (60, 140, 90))[i]
        cars.poly([(cx, 820), (cx + 30, 770), (cx + 110, 770), (cx + 140, 820), (cx + 140, 860), (cx, 860)], col)
        cars.ellipse([cx + 14, 846, cx + 46, 878], (20, 20, 24)).ellipse([cx + 94, 846, cx + 126, 878], (20, 20, 24))
    rings = Layer((200, 50, 46), 1.2, 54)
    k = (t * 1.2) % 1
    for j in range(3):   # звуковые волны от сигналящей машины
        r = 40 + (k + j / 3) % 1 * 160
        rings.d.arc([270 - r, 790 - r, 270 + r, 790 + r], 200, 340, fill=(200, 50, 46, 255), width=6)
    zs = Layer((26, 26, 30), 1.4, 55)
    if p > .35:
        q = ease((p - .35) / .5)
        for i, (x0, y0) in enumerate(((-60, 1150), (120, 1250), (620, 1180), (780, 1240), (360, 1300))):
            x = x0 + (270 - x0) * q * .55
            y = y0 + (980 - y0) * q * .5
            person(zs, x, y, .8, hunch=1)
    img = compose((220, 214, 196), [board, road, cars, rings, zs])
    tag(img, "ПРАВИЛО №1", "они идут на звук", 150)
    return img


def s06(t, L, cue):
    k = ease(t / (L * .8))
    sky = Layer((40, 52, 80), .2, 61).poly(FULL)
    far = hills(Layer((54, 70, 104), .4, 62), 760, 300, 2)
    mid = hills(Layer((38, 50, 82), .7, 63), 860, 200, 9, 3)
    sea = wave((24, 46, 76), 900, 10, .04, t, 1.2, 1.0, 64)
    f1 = fog((150, 160, 176), 1200 - 620 * k, t, .6, 1.2, 65, drift=-200 + 200 * k)
    f2 = fog((186, 192, 204), 1320 - 560 * k, t, -.4, 1.6, 66, drift=200 - 200 * k)
    img = compose((30, 40, 64), [sky, far, mid, sea, f1, f2])
    tag(img, "ПРАВИЛО №2", "туман · 10 минут", 150)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    sea = Layer((60, 110, 160), .1, 71).poly(FULL)
    land = Layer((210, 196, 160), .6, 72)
    land.poly([(-40, 300), (330, 280), (420, 420), (380, 560), (240, 640), (100, 600), (-40, 620)])   # Эгершельд / город
    land.poly([(300, 840), (560, 760), (W + 40, 780), (W + 40, 1240), (420, 1200), (260, 1020)])       # остров Русский
    route = Layer((200, 50, 46), 1.2, 73)
    pts = [(260, 600), (330, 680), (380, 760), (430, 860)]
    n = int(len(pts) * min(1, max(0, p / .7)) + .5)
    for i in range(max(0, n - 1)):
        route.line([pts[i], pts[i + 1]], 7)
    route.ellipse([250, 590, 270, 610]).ellipse([420, 850, 440, 870])
    img = compose((60, 110, 160), [sea, land, route])
    d = ImageDraw.Draw(img)
    d.text((40, 360), "ГОРОД", font=F(32, FONT_SUB), fill=(60, 50, 40))
    d.text((480, 980), "о. РУССКИЙ", font=F(32, FONT_SUB), fill=(60, 50, 40))
    d.text((120, 640), "Спортивная гавань", font=F(22), fill=(60, 50, 40))
    if p > .7:
        tag(img, "БЕНЗИН", "на 1 рейс", 150)
    return img


def embank(t, rise=0.0, glowk=1.0):
    pale = Layer((150, 156, 190), .1, 13).rect(-40, -40, W + 40, 520)
    sky = Layer((26, 30, 52), .2, 1).poly(FULL)
    stars(sky, 40, 9, 500)
    warm = Layer((250, 206, 120), .4, 12)
    city = Layer((36, 40, 64), .5, 2)
    r = random.Random(4)
    x = -20
    while x < W:
        w, h = r.randint(60, 120), r.randint(200, 420)
        city.rect(x, 760 - h, x + w, 800)
        warm.d.rectangle([x + 4, 764 - h, x + w - 4, 800], fill=(250, 206, 120, 255))
        for wy in range(780 - h, 760, 34):
            for wx in range(x + 10, x + w - 16, 22):
                if r.random() < .25:
                    city.hole_rect([wx, wy, wx + 10, wy + 14])
        x += w + 6
    walk = Layer((70, 66, 70), 1.0, 3).rect(-40, 880, W + 40, H + 40)
    rail = Layer((40, 40, 46), 1.2, 4)
    for x in range(0, W + 40, 60):
        rail.rect(x, 820, x + 8, 890)
    rail.rect(-40, 816, W + 40, 828)
    lamp = Layer((30, 30, 36), 1.3, 5).rect(560, 420, 572, 900).rect(530, 410, 600, 430)
    bench = Layer((110, 70, 44), 1.5, 6).rect(150, 960, 420, 980).rect(170, 980, 184, 1040).rect(386, 980, 400, 1040).rect(150, 900, 420, 920)
    man = Layer((20, 22, 26), 1.6, 7)
    if rise <= 0:
        man.ellipse([255, 820, 315, 880]).poly([(240, 880), (330, 880), (340, 970), (230, 970)])
    else:
        person(man, 285, 1040 - 20 * rise, 1.0, hunch=1)
    crowd = Layer((16, 18, 22), 1.9, 8)
    if rise > 0:
        rr = random.Random(2)
        for i in range(9):
            x0 = rr.uniform(-20, W + 20)
            q = min(1, max(0, rise * 1.6 - i * .08))
            person(crowd, x0, H + 40 + (1 - q) * 260 - rr.uniform(0, 120), 1.3, hunch=1)
    img = compose((20, 24, 44), [pale, sky, warm, city, walk, rail, lamp, bench, man, crowd])
    if int(t * 6) % 5 and glowk > 0:
        glow(img, (566, 430), 60, (255, 220, 150), .8 * glowk)
    return img


def s08(t, L, cue):
    img = embank(t)
    tag(img, "СПОРТИВНАЯ НАБЕРЕЖНАЯ", "23:10", 150, (60, 60, 66))
    return img


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    water = Layer((20, 40, 64), .2, 91).poly(FULL)
    hullb = Layer((180, 120, 60), .8, 92).poly([(-40, 760), (W + 40, 700), (W + 40, H + 40), (-40, H + 40)])
    motor = Layer((44, 46, 52), 1.2, 93).poly([(380, 580), (420, 540), (580, 530), (620, 580), (610, 760), (390, 780)]).rect(470, 770, 520, 1000, (30, 30, 34))
    motor.rect(420, 600, 590, 640, (220, 120, 40)).poly([(440, 990), (550, 990), (530, 1030), (460, 1030)], (60, 62, 70))
    hand = Layer((214, 168, 132), 1.6, 94)
    sleeve = Layer((60, 80, 120), 1.55, 96)
    pull = [0, .3, .6]
    k = 0
    for q in pull:
        if q < p < q + .2:
            k = (p - q) / .2
    hx = 360 - 220 * k
    hand.line([(390, 640), (hx, 660 + 40 * k)], 4, (230, 230, 230))
    hand.ellipse([hx - 30, 630 + 40 * k, hx + 20, 690 + 40 * k])
    for f in range(4):   # пальцы на ручке
        hand.ellipse([hx + 4, 630 + 40 * k + f * 14, hx + 30, 646 + 40 * k + f * 14])
    sleeve.poly([(-40, 700 + 60 * k), (hx - 20, 640 + 40 * k), (hx - 14, 690 + 40 * k), (-40, 800 + 60 * k)])
    smoke = Layer((160, 160, 168), 1.4, 95)
    if p > .62:
        for i in range(5):
            life = (t * .9 + i / 5) % 1
            r = 20 + 40 * life
            smoke.ellipse([620 + 60 * life - r, 600 - 200 * life - r, 620 + 60 * life + r, 600 - 200 * life + r])
    img = compose((20, 40, 64), [water, hullb, motor, smoke, sleeve, hand])
    if p > .62:
        tag(img, "ДРРРРР", "слишком громко", 150, (200, 50, 46))
    return shake(img, t, 7 if p > .62 else 2 * k)


def s10(t, L, cue):
    p = (t - cue["10"]) / dur("10.mp3")
    img = embank(t, rise=ease(p * 1.1))
    return shake(img, t, 3 if p > .6 else 0)


def s11(t, L, cue):
    """вид сбоку: город слева позади, остров справа, справа же наползает стена тумана"""
    k = ease(t / L)
    sky = Layer((30, 34, 58), .2, 111).poly(FULL)
    stars(sky, 40, 4, 600)
    warm = Layer((250, 206, 120), .35, 113)
    city = Layer((40, 44, 70), .4, 112)
    r = random.Random(8)
    x = -20
    while x < 330:
        w, h = r.randint(30, 60), r.randint(80, 240)
        city.rect(x, 990 - h, x + w, 1000)
        warm.d.rectangle([x + 3, 994 - h, x + w - 3, 1000], fill=(250, 206, 120, 255))
        for wy in range(1010 - h, 980, 26):
            if r.random() < .5:
                city.hole_rect([x + 8, wy, x + 16, wy + 10])
        x += w + 3
    island = hills(Layer((34, 40, 60), .5, 118), 1000, 120, 11, 2)
    island.d.rectangle([-40, 0, 420, H], fill=(0, 0, 0, 0))
    sea = wave((22, 42, 70), 1010, 8, .05, t, 1.4, 1.0, 114)
    fx = 760 - 330 * k   # левый край тумана ползёт к лодке
    fogw = Layer((176, 182, 194), .8, 115)
    fogw.poly([(fx + 30 * math.sin(y * .02 + t), y) for y in range(-40, H + 60, 40)] + [(W + 60, H + 40), (W + 60, -40)])
    boat = Layer((180, 120, 60), 1.2, 116)
    bx = 200 + 140 * k
    boat.poly([(bx - 60, 1070), (bx + 70, 1070), (bx + 46, 1116), (bx - 44, 1116)])
    person(boat, bx - 10, 1072, .5)
    near = wave((16, 32, 56), 1130, 14, .04, t, -1.6, 1.6, 117)
    return compose((26, 30, 52), [sky, warm, city, island, sea, boat, fogw, near])


def s12(t, L, cue):
    vo_end = cue["12"] + dur("12.mp3")
    k = ease(t / (L * .7))
    sky = Layer((90, 98, 112), .2, 121).poly(FULL)
    fog1 = fog((150, 156, 164), 520, t, .3, .5, 122, 30)
    hull = Layer((58, 40, 36), 1.0, 123)
    s = .6 + .5 * k
    cx = W / 2
    P = lambda x, y: (cx + (x - 360) * s, 400 + (y - 400) * s)
    hull.rect(*P(250, 250), *P(470, 400), (78, 56, 48)).rect(*P(290, 190), *P(430, 260), (88, 62, 52))
    hull.poly([P(120, 400), P(600, 400), P(560, 520), P(360, 1000), P(160, 520)])
    hull.poly([P(360, 400), P(600, 400), P(560, 520), P(360, 1000)], (46, 32, 30))
    hull.rect(*P(110, 392), *P(610, 412), (40, 28, 26))
    for ax in (250, 470):
        hull.ellipse([*P(ax - 16, 450), *P(ax + 16, 482)], (20, 14, 14))
    fog2 = fog((176, 182, 190), 760, t, -.4, 1.3, 124, 40)
    sea = wave((34, 50, 66), 1010, 12, .05, t, 1, 1.6, 125)
    boat = Layer((180, 120, 60), 2.0, 126)
    boat.poly([(120, H + 40), (300, 1120), (420, 1120), (600, H + 40)]).rect(250, 1110, 470, 1130, (120, 80, 40))
    img = compose((70, 78, 92), [sky, fog1, hull, fog2, sea, boat], shift=(0, math.sin(t) * 4))
    lx, ly = P(380, 360)
    p = (t - cue["12"]) / dur("12.mp3")
    if p > .6:
        glow(img, (lx, ly), 50, (255, 240, 200), 1.0)
        beam = Image.new("L", (W, H), 0)
        ImageDraw.Draw(beam).polygon([(lx - 8, ly), (lx + 8, ly), (lx + 260, H), (lx - 260, H)], fill=int(70 * min(1, (p - .6) * 4)))
        img.paste(Image.new("RGB", (W, H), (255, 244, 210)), (0, 0), beam.filter(ImageFilter.GaussianBlur(20)))
    if t > vo_end + .8:
        a = min(1, (t - vo_end - .8) / .5)
        img = Image.blend(img, Image.new("RGB", (W, H), (240, 240, 236)), a)   # всё тонет в белом тумане
        if a >= 1:
            d = ImageDraw.Draw(img)
            f1, f2 = F(70, FONT_SUB), F(32, FONT_SUB)
            d.text(((W - f1.getlength("ТУМАН")) / 2, 500), "ТУМАН", font=f1, fill=(40, 40, 44))
            d.text(((W - f2.getlength("продолжение следует")) / 2, 600), "продолжение следует", font=f2, fill=(120, 120, 126))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .3, span("s10")[0] + span("s10")[1] * .6, span("s12")[0] + span("s12")[1] * .5])
