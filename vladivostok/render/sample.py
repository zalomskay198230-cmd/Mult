"""пробные кадры paper-cut для «Тумана»"""
import sys, math, random
from PIL import Image, ImageDraw, ImageFilter
from paper import *

OUT = sys.argv[1]


def stars(L, n=60, seed=3, ymax=600):
    r = random.Random(seed)
    for _ in range(n):
        x, y, s = r.uniform(0, W), r.uniform(0, ymax), r.choice((2, 2, 3, 4))
        L.hole([x - s, y - s, x + s, y + s])


def bridge(t):
    glowl = Layer((236, 228, 196), .1, 11).ellipse([510, 140, 630, 260]).rect(-40, -40, W + 40, 620, (120, 130, 170))
    sky = Layer((22, 34, 70), .2, 1).rect(-40, -40, W + 40, H + 40)
    stars(sky)
    sky.hole([520, 150, 620, 250])                        # луна — вырезанный круг, за ним светлый лист
    far = hills(Layer((40, 56, 98), .4, 2), 720, 260, 5)  # дальние сопки
    mid = hills(Layer((30, 42, 78), .7, 3), 780, 170, 8, 3)
    br = Layer((214, 216, 222), 1.0, 4)                   # Русский мост: два пилона-«А» и веер вантов
    for px in (150, 590):
        br.poly([(px - 40, 860), (px - 8, 300), (px + 8, 300), (px + 40, 860), (px + 22, 860), (px, 420), (px - 22, 860)])
        for k in range(9):
            for sgn in (-1, 1):
                br.line([(px, 330 + k * 12), (px + sgn * (40 + k * 38), 800)], 2)
    br.rect(-40, 795, W + 40, 818)
    water = Layer((20, 48, 84), 1.2, 5)
    water.poly([(x, 860 + 10 * math.sin(x * .05 + t * 2)) for x in range(-40, W + 60, 20)] + [(W + 60, H + 40), (-40, H + 40)])
    w2 = Layer((14, 36, 66), 1.6, 6)
    w2.poly([(x, 1000 + 14 * math.sin(x * .035 - t * 1.6)) for x in range(-40, W + 60, 20)] + [(W + 60, H + 40), (-40, H + 40)])
    army = Layer((24, 30, 30), 1.4, 7)                    # БТР и шлагбаум на въезде
    army.poly([(60, 790), (90, 760), (250, 760), (280, 790)]).rect(110, 740, 200, 762).line([(200, 750), (280, 735)], 6)
    for wx in (95, 150, 205, 255):
        army.ellipse([wx - 16, 778, wx + 16, 810], (14, 16, 18))
    army.rect(320, 770, 330, 800).line([(325, 772), (520, 772)], 8, (200, 60, 60))
    img = compose((14, 22, 48), [glowl, sky, far, mid, br, army, water, w2], shift=(math.sin(t * .5) * 6, 0))
    col = (255, 60, 60) if int(t * 4) % 2 else (60, 90, 255)
    glow(img, (170, 735), 40, col, .9)
    return img


def ship(t):
    sky = Layer((90, 98, 112), .2, 1).rect(-40, -40, W + 40, H + 40)
    fog1 = Layer((150, 156, 164), .5, 2)
    fog1.poly([(x, 520 + 30 * math.sin(x * .012 + t * .3)) for x in range(-40, W + 60, 30)] + [(W + 60, H + 40), (-40, H + 40)])
    hull = Layer((58, 40, 36), 1.0, 3)                   # нос сухогруза из тумана (вид спереди — клин)
    hull.rect(250, 250, 470, 400, (78, 56, 48)).rect(290, 190, 430, 260, (88, 62, 52))      # надстройка за палубой
    hull.poly([(120, 400), (600, 400), (560, 520), (360, 1000), (160, 520)])
    hull.poly([(360, 400), (600, 400), (560, 520), (360, 1000)], (46, 32, 30))               # тень на правой скуле
    hull.rect(110, 392, 610, 412, (40, 28, 26))                                                # фальшборт
    for ax in (250, 470):
        hull.ellipse([ax - 16, 450, ax + 16, 482], (20, 14, 14))                               # клюзы
        hull.line([(ax, 482), (ax + (8 if ax > 360 else -8), 600)], 4, (90, 70, 60))           # ржавые потёки
    hull.rect(330, 560, 390, 590, (200, 190, 170))
    fog2 = Layer((176, 182, 190), 1.3, 4)
    fog2.poly([(x, 760 + 40 * math.sin(x * .02 - t * .4)) for x in range(-40, W + 60, 30)] + [(W + 60, H + 40), (-40, H + 40)])
    sea = Layer((34, 50, 66), 1.6, 5)
    sea.poly([(x, 1010 + 12 * math.sin(x * .05 + t)) for x in range(-40, W + 60, 20)] + [(W + 60, H + 40), (-40, H + 40)])
    boat = Layer((180, 120, 60), 2.0, 6)                  # нос нашей лодки снизу
    boat.poly([(120, H + 40), (300, 1120), (420, 1120), (600, H + 40)]).rect(250, 1110, 470, 1130, (120, 80, 40))
    img = compose((70, 78, 92), [sky, fog1, hull, fog2, sea, boat], shift=(0, math.sin(t) * 4))
    glow(img, (380, 360), 50, (255, 240, 200), 1.0)       # фонарь на палубе
    beam = Image.new("L", (W, H), 0)
    ImageDraw.Draw(beam).polygon([(372, 360), (388, 360), (600, H), (200, H)], fill=60)
    img.paste(Image.new("RGB", (W, H), (255, 244, 210)), (0, 0), beam.filter(ImageFilter.GaussianBlur(20)))
    return img


def embank(t):
    pale = Layer((150, 156, 190), .1, 13).rect(-40, -40, W + 40, 520)
    sky = Layer((26, 30, 52), .2, 1).rect(-40, -40, W + 40, H + 40)
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
    man = Layer((20, 22, 26), 1.6, 7)                     # силуэт на лавке
    man.ellipse([255, 820, 315, 880]).poly([(240, 880), (330, 880), (340, 970), (230, 970)])
    img = compose((20, 24, 44), [pale, sky, warm, city, walk, rail, lamp, bench, man])
    if int(t * 6) % 5:
        glow(img, (566, 430), 60, (255, 220, 150), .8)
    return img


for name, fn, t in (("bridge", bridge, .3), ("embank", embank, .2), ("ship", ship, .5)):
    fn(t).save(f"{OUT}_{name}.png")
