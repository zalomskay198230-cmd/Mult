"""Пробный кадр Владивостока в плоском стиле (как «Без света»/«Ночная смена»): Золотой мост, бухта, сопки, герой."""
import sys, math, random
sys.path.insert(0, "/home/user/Mult/den365/render")
import flatworld as FW
from flatworld import SD, chibi, OUT
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H, K = 720, 1280, 2
FW.CHAR["hero"] = dict(skin=(236, 192, 160), hair=(40, 32, 30), top=(70, 74, 90), pants=(40, 46, 60), shoes=(230, 230, 232), style="short")


def glow(img, xy, r, col, k=1.0):
    r = int(r); s = r * 4
    lay = Image.new("RGB", (s, s))
    ImageDraw.Draw(lay).ellipse([r, r, 3 * r, 3 * r], fill=tuple(int(c * k) for c in col))
    lay = lay.filter(ImageFilter.GaussianBlur(r * .6))
    bx, by = int(xy[0] - 2 * r), int(xy[1] - 2 * r)
    img.paste(ImageChops.add(img.crop((bx, by, bx + s, by + s)), lay), (bx, by))


img = Image.new("RGB", (W * K, H * K))
d = SD(img, 0, 0, K)
for y in range(0, 760, 4):   # закатное небо
    k = y / 760
    d.rectangle([0, y, W, y + 4], fill=(int(40 + 200 * k), int(36 + 90 * k), int(80 + 40 * k)))
rnd = random.Random(2)
for _ in range(60):
    x, y = rnd.uniform(0, W), rnd.uniform(0, 300)
    d.ellipse([x - 1.3, y - 1.3, x + 1.3, y + 1.3], fill=(230, 230, 240))
# сопки с домами
for layer, (col, base, amp, seed) in enumerate((((70, 60, 96), 640, 200, 3), ((48, 42, 72), 720, 160, 7))):
    pts = [(x, base - amp * (.5 + .3 * math.sin(x / 120 + seed) + .2 * math.sin(x / 47 + seed * 2))) for x in range(-20, W + 40, 20)]
    d.polygon(pts + [(W + 40, 900), (-20, 900)], fill=col)
    r2 = random.Random(seed)
    for _ in range(70 + 40 * layer):
        x = r2.uniform(0, W)
        top = base - amp * (.5 + .3 * math.sin(x / 120 + seed) + .2 * math.sin(x / 47 + seed * 2))
        y = r2.uniform(top + 10, 880)
        w, h = r2.uniform(14, 34), r2.uniform(20, 60)
        d.rectangle([x, y - h, x + w, y], fill=tuple(int(c * 1.15) for c in col))
        for wy in range(int(y - h + 6), int(y - 6), 12):
            if r2.random() < .55:
                d.rectangle([x + 4, wy, x + 9, wy + 6], fill=(255, 214, 130))
# бухта Золотой Рог
d.rectangle([0, 860, W, H], fill=(28, 40, 76))
for i in range(40):
    y = 880 + i * 10
    d.line([(rnd.uniform(0, W), y), (rnd.uniform(0, W), y)], fill=(70, 80, 130), width=2)
# Золотой мост: два V-пилона, ванты, пролёт
deck = 780
d.rectangle([-20, deck, W + 20, deck + 18], fill=(230, 226, 220), outline=OUT, width=3)
for px in (190, 540):
    d.polygon([(px - 46, 380), (px - 30, 380), (px + 4, deck), (px - 12, deck)], fill=(240, 238, 232), outline=OUT)
    d.polygon([(px + 30, 380), (px + 46, 380), (px + 12, deck), (px - 4, deck)], fill=(240, 238, 232), outline=OUT)
    d.rectangle([px - 44, 400, px + 44, 412], fill=(240, 238, 232), outline=OUT, width=2)
    for k in range(10):
        for sg in (-1, 1):
            d.line([(px, 420 + k * 14), (px + sg * (40 + k * 34), deck)], fill=(250, 246, 238), width=2)
    d.rectangle([px - 18, deck + 18, px + 18, 900], fill=(200, 196, 190), outline=OUT, width=3)
for x in range(0, W, 30):   # огни на мосту
    d.ellipse([x - 3, deck - 4, x + 3, deck + 2], fill=(255, 220, 140))
# набережная и герой
d.rectangle([0, 1120, W, H], fill=(60, 56, 64))
for x in range(0, W, 50):
    d.rectangle([x, 1080, x + 6, 1122], fill=(30, 30, 34))
d.rectangle([0, 1076, W, 1086], fill=(30, 30, 34))
chibi(d, "hero", 470, 1240, 2.4, .5, "neutral", -1)
img = img.resize((W, H), Image.LANCZOS)
for x in range(0, W, 30):
    glow(img, (x, 778), 10, (255, 200, 120), .5)
glow(img, (630, 760), 90, (255, 150, 80), .45)   # закатное солнце за сопкой
dd = ImageDraw.Draw(img)
img.save(sys.argv[1])
