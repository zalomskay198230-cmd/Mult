"""Плоский мир «365 дней» в разрезе: рисуется в K-кратном разрешении (сглаживание), камера вырезает кусок.
Координаты везде в «мировых» единицах; View переводит их в пиксели кадра."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

K = 2                                  # суперсэмплинг
WW, WH, GR = 1600, 2000, 900           # мир и уровень земли
PIT_X0, PIT_X1 = 760, 1180
OUT = (34, 28, 34)                     # контур
SECT = (214, 128, 128)                 # стены в разрезе (розовые)
SECT_D = (160, 86, 92)


def mix(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


def dk(c, k=.75):
    return tuple(int(v * k) for v in c)


class SD:
    """ImageDraw с масштабом и сдвигом: рисуем в мировых координатах"""
    def __init__(self, img, ox=0.0, oy=0.0, k=K):
        self.d, self.ox, self.oy, self.k = ImageDraw.Draw(img), ox, oy, k

    def _xy(self, xy):
        if isinstance(xy[0], (tuple, list)):
            return [((x - self.ox) * self.k, (y - self.oy) * self.k) for x, y in xy]
        return [((xy[i] - self.ox) * self.k if i % 2 == 0 else (xy[i] - self.oy) * self.k) for i in range(len(xy))]

    def _kw(self, kw):
        for n in ("width", "radius"):
            if n in kw:
                kw[n] = max(1, int(round(kw[n] * self.k)))
        return kw

    def __getattr__(self, name):
        f = getattr(self.d, name)

        def call(xy, *a, **kw):
            return f(self._xy(xy), *a, **self._kw(kw))
        return call


def vgrad(w, h, top, bottom):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - a) + np.array(bottom)[None, None, :] * a
    return Image.fromarray(np.repeat(arr, w, axis=1).astype(np.uint8), "RGB")


def soft(img, x, y, r, col, k=1.0, ox=0, oy=0, s=K):
    """мягкое свечение (аддитивно) в мировых координатах"""
    r2 = int(r * s)
    size = r2 * 4
    if size < 4:
        return
    lay = Image.new("RGB", (size, size))
    ImageDraw.Draw(lay).ellipse([r2, r2, 3 * r2, 3 * r2], fill=tuple(int(c * k) for c in col))
    lay = lay.filter(ImageFilter.GaussianBlur(r2 * .6))
    bx, by = int((x - ox) * s - 2 * r2), int((y - oy) * s - 2 * r2)
    img.paste(ImageChops.add(img.crop((bx, by, bx + size, by + size)), lay), (bx, by))


def beam(img, poly, col, alpha, blur, ox=0, oy=0, s=K):
    """мягкий луч/конус света"""
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0 = int((min(xs) - ox) * s) - blur * 3, int((min(ys) - oy) * s) - blur * 3
    x1, y1 = int((max(xs) - ox) * s) + blur * 3, int((max(ys) - oy) * s) + blur * 3
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([((px - ox) * s - x0, (py - oy) * s - y0) for px, py in poly], fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.new("RGB", m.size, col), (x0, y0), m)


# ---------- слои мира ----------
def sky(img, d, day, lights):
    rnd = random.Random(1)
    if not day:
        for _ in range(320):
            x, y = rnd.uniform(0, WW), rnd.uniform(0, GR - 280)
            r = rnd.choice((1, 1, 1.4, 2))
            c = rnd.randint(150, 240)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, min(255, c + 15)))
        soft(img, 1250, 180, 90, (60, 70, 100), .9)
        d = SD(img)
        d.ellipse([1210, 140, 1290, 220], fill=(240, 236, 214))
        for cx, cy, r in ((1236, 166, 10), (1264, 196, 7), (1250, 176, 5)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(218, 212, 192))
    for i in range(5):   # облака
        cx, cy = rnd.uniform(0, WW), rnd.uniform(120, 420)
        col = (240, 244, 250) if day else (40, 46, 70)
        for j in range(4):
            r = rnd.uniform(26, 50)
            d.ellipse([cx + j * 36 - r, cy - r * .6, cx + j * 36 + r, cy + r * .6], fill=col)
    return SD(img)


def city(d, lights_on, day):
    for layer, (col, hmin, hmax, wincol, step) in enumerate((((30, 36, 60) if not day else (150, 170, 200), 260, 520, (120, 110, 90), 26),
                                                             ((20, 24, 40) if not day else (110, 130, 160), 160, 380, (240, 196, 110), 30))):
        rnd = random.Random(3 + layer * 7)
        x = -30 + layer * 40
        while x < WW:
            w, h = rnd.randint(70, 160), rnd.randint(hmin, hmax)
            d.rectangle([x, GR - h, x + w, GR], fill=col)
            if rnd.random() < .3:   # антенна / бак
                d.line([x + w * .7, GR - h, x + w * .7, GR - h - 40], fill=col, width=3)
            if lights_on and not day:
                for wy in range(GR - h + 16, GR - 20, step):
                    for wx in range(x + 10, x + w - 14, 22):
                        if rnd.random() < (.18 if layer == 0 else .3):
                            d.rectangle([wx, wy, wx + 10, wy + 14], fill=wincol)
            x += w + rnd.randint(0, 24)


def lamp_post(img, d, x, on):
    d.line([x, GR, x, GR - 260], fill=(60, 64, 72), width=7)
    d.line([x, GR - 260, x + 50, GR - 260], fill=(60, 64, 72), width=6)
    d.rounded_rectangle([x + 34, GR - 268, x + 74, GR - 252], radius=4, fill=(90, 94, 100))
    if on:
        beam(img, [(x + 40, GR - 254), (x + 68, GR - 254), (x + 160, GR), (x - 50, GR)], (255, 220, 150), 46, 16)
        soft(img, x + 54, GR - 252, 26, (255, 210, 130), .9)


def earth(img):
    top = vgrad(WW * K, (WH - GR) * K, (58, 46, 44), (20, 18, 22))
    img.paste(top, (0, GR * K))
    d = SD(img)
    rnd = random.Random(5)
    for i, (y, col) in enumerate(((GR + 60, (66, 52, 48)), (GR + 260, (48, 40, 40)), (GR + 520, (36, 32, 34)), (GR + 760, (28, 26, 30)))):
        pts = [(x, y + 18 * math.sin(x * .006 + i)) for x in range(0, WW + 40, 40)]
        d.polygon(pts + [(WW, y + 70), (0, y + 70)], fill=col)   # слои грунта
    for _ in range(520):   # камни с бликом
        x, y, r = rnd.uniform(0, WW), rnd.uniform(GR + 30, WH), rnd.uniform(4, 16)
        base = rnd.choice(((74, 64, 60), (60, 54, 54), (86, 74, 66)))
        d.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=base)
        d.ellipse([x - r * .5, y - r * .5, x + r * .1, y - r * .1], fill=mix(base, (140, 130, 120), .4))
    d.rectangle([0, GR - 10, WW, GR + 10], fill=(70, 104, 62))   # газон
    for x in range(0, WW, 9):
        h = rnd.uniform(6, 16)
        d.line([x, GR - 8, x + rnd.uniform(-3, 3), GR - 8 - h], fill=(84, 126, 70), width=2)
    for k_ in range(6):   # корни у дерева
        a = -1.2 + k_ * .45
        d.line([720, GR + 6, 720 + 120 * math.sin(a), GR + 60 + 50 * math.cos(a) + k_ * 10], fill=(80, 60, 46), width=5)
    # трубы, как в инженерном разрезе
    d.line([300, GR - 40, 300, WH], fill=(70, 130, 210), width=14)            # водопровод из дома
    d.line([300, GR + 620, 760, GR + 620], fill=(70, 130, 210), width=14)
    d.line([0, GR + 120, 700, GR + 120], fill=(90, 90, 98), width=22)          # канализация
    for x in range(40, 700, 120):
        d.rectangle([x, GR + 106, x + 14, GR + 134], fill=(70, 70, 78))
    d.line([1300, GR - 10, 1300, GR + 480], fill=(220, 160, 50), width=8)      # кабель
    d.line([1300, GR + 480, WW, GR + 480], fill=(220, 160, 50), width=8)


def house(img, d, lights_on):
    x0, x1, y0 = 60, 640, GR - 300
    wall = (70, 64, 76) if lights_on else (34, 32, 40)
    d.rectangle([x0, y0, x1, GR], fill=wall)
    for x in range(x0 + 20, x1, 34):   # обои
        d.line([x, y0 + 10, x, GR - 8], fill=mix(wall, (255, 255, 255), .04), width=10)
    d.rectangle([x0, GR - 36, x1, GR], fill=dk(wall, .8))   # плинтус/пол
    d.polygon([(x0 - 40, y0 + 4), ((x0 + x1) / 2, y0 - 160), (x1 + 40, y0 + 4)], fill=(96, 52, 56))   # крыша
    for k_ in range(6):
        yy = y0 - 150 + k_ * 26
        half = (yy - (y0 - 160)) / 164 * ((x1 - x0) / 2 + 40)
        d.line([(x0 + x1) / 2 - half, yy, (x0 + x1) / 2 + half, yy], fill=(74, 40, 44), width=4)
    d.rectangle([x0 - 8, y0 - 8, x1 + 8, GR + 6], outline=SECT, width=16)       # стены в разрезе
    d.rectangle([x0 - 16, y0 - 16, x1 + 16, GR + 14], outline=SECT_D, width=4)
    d.rectangle([352, y0, 368, GR - 150], fill=SECT)                              # перегородка
    # кухня
    d.rounded_rectangle([86, GR - 170, 146, GR - 2], radius=6, fill=(214, 218, 224), outline=OUT, width=3)   # холодильник
    d.line([92, GR - 110, 140, GR - 110], fill=OUT, width=2); d.line([136, GR - 160, 136, GR - 120], fill=(120, 124, 130), width=4)
    d.rectangle([176, GR - 66, 330, GR - 54], fill=(150, 104, 70), outline=OUT, width=2)
    for lx in (186, 320):
        d.line([lx, GR - 54, lx, GR - 2], fill=(130, 90, 60), width=6)
    d.rounded_rectangle([238, GR - 84, 256, GR - 66], radius=3, fill=(230, 230, 236))   # кружка
    d.rectangle([90, y0 + 40, 330, y0 + 70], fill=(120, 94, 76))                        # полка
    for i, c in enumerate(((200, 80, 70), (90, 150, 200), (220, 190, 80), (120, 180, 110))):
        d.rounded_rectangle([104 + i * 52, y0 + 6, 140 + i * 52, y0 + 40], radius=4, fill=c)
    # спальня
    d.rounded_rectangle([410, GR - 60, 610, GR - 2], radius=8, fill=(84, 104, 160), outline=OUT, width=3)
    d.rounded_rectangle([414, GR - 84, 470, GR - 58], radius=10, fill=(236, 236, 240), outline=OUT, width=2)
    d.rectangle([406, GR - 100, 416, GR - 2], fill=(120, 84, 60))
    d.rectangle([470, y0 + 50, 590, y0 + 150], fill=(14, 20, 40), outline=SECT, width=8)    # окно
    d.line([530, y0 + 54, 530, y0 + 146], fill=SECT, width=5)
    d.polygon([(466, y0 + 46), (494, y0 + 46), (484, y0 + 160), (462, y0 + 160)], fill=(160, 70, 80))   # шторы
    d.polygon([(566, y0 + 46), (594, y0 + 46), (598, y0 + 160), (576, y0 + 160)], fill=(160, 70, 80))
    d.rectangle([380, y0 + 70, 440, y0 + 120], fill=(200, 170, 110), outline=OUT, width=3)  # картина
    d.ellipse([380, GR - 14, 640, GR + 4], fill=(120, 60, 66))                             # коврик
    for lx in (210, 500):   # лампы
        d.line([lx, y0 + 8, lx, y0 + 30], fill=(40, 40, 44), width=3)
        d.chord([lx - 22, y0 + 26, lx + 22, y0 + 56], 180, 360, fill=(230, 200, 120) if lights_on else (80, 76, 70))
        if lights_on:
            beam(img, [(lx - 18, y0 + 42), (lx + 18, y0 + 42), (lx + 140, GR), (lx - 140, GR)], (255, 230, 170), 36, 14)
            soft(img, lx, y0 + 44, 30, (255, 220, 150), .8)


def tree(d, x):
    d.rectangle([x - 8, GR - 120, x + 8, GR], fill=(90, 62, 44))
    for cx, cy, r in ((x - 34, GR - 150, 48), (x + 30, GR - 160, 52), (x, GR - 200, 56), (x, GR - 140, 50)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 92, 58))
    for cx, cy, r in ((x - 20, GR - 210, 26), (x + 34, GR - 182, 22)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 120, 72))


def fence(d, x0, x1):
    d.line([x0, GR - 50, x1, GR - 50], fill=(110, 86, 64), width=6)
    for x in range(int(x0), int(x1), 22):
        d.polygon([(x, GR), (x, GR - 70), (x + 7, GR - 78), (x + 14, GR - 70), (x + 14, GR)], fill=(132, 100, 72), outline=dk((132, 100, 72), .7))


def garage(img, d, lights_on):
    x0, x1, y0 = 800, 1140, GR - 220
    d.rectangle([x0, y0, x1, GR], fill=(58, 60, 68))
    for y in range(y0 + 14, GR, 28):
        d.line([x0 + 12, y, x1 - 12, y], fill=(64, 66, 74), width=3)
    d.rectangle([x0 - 8, y0 - 8, x1 + 8, GR + 6], outline=SECT, width=16)
    d.polygon([(x0 - 30, y0 - 8), (x1 + 30, y0 - 8), (x1 + 30, y0 - 36), (x0 - 30, y0 - 36)], fill=(104, 108, 118), outline=OUT)
    d.rectangle([832, GR - 160, 990, GR - 2], fill=(84, 88, 98), outline=OUT, width=3)   # ворота-рольставня
    for y in range(GR - 150, GR - 4, 12):
        d.line([836, y, 986, y], fill=(70, 74, 82), width=3)
    d.rectangle([1010, GR - 70, 1120, GR - 56], fill=(130, 92, 62))                         # верстак
    d.line([1018, GR - 56, 1018, GR - 2], fill=(110, 78, 52), width=5); d.line([1112, GR - 56, 1112, GR - 2], fill=(110, 78, 52), width=5)
    d.rectangle([1016, GR - 160, 1120, GR - 100], fill=(70, 72, 80))                         # щит с инструментом
    for i in range(4):
        d.line([1028 + i * 26, GR - 150, 1028 + i * 26, GR - 112], fill=(180, 184, 190), width=4)
    for i in range(3):   # шины
        d.ellipse([1024 + i * 4, GR - 30 - i * 20, 1074 + i * 4, GR - 8 - i * 20], fill=(30, 30, 34), outline=(60, 60, 66), width=3)
    d.line([970, y0 + 2, 970, y0 + 30], fill=(40, 40, 44), width=3)
    d.ellipse([962, y0 + 28, 978, y0 + 44], fill=(255, 230, 160) if lights_on else (90, 90, 80))
    if lights_on:
        soft(img, 970, y0 + 36, 30, (255, 220, 150), .7)


def container(d, x0, y0, x1, y1, col=(176, 72, 52), door=True, label="SMKU 4410"):
    d.rectangle([x0, y0, x1, y1], fill=col, outline=OUT, width=4)
    for x in range(int(x0) + 14, int(x1) - 6, 18):
        d.line([x, y0 + 8, x, y1 - 8], fill=dk(col, .8), width=6)
        d.line([x + 4, y0 + 8, x + 4, y1 - 8], fill=mix(col, (255, 255, 255), .12), width=2)
    d.rectangle([x0, y0, x1, y0 + 10], fill=dk(col, .7)); d.rectangle([x0, y1 - 10, x1, y1], fill=dk(col, .7))
    rnd = random.Random(int(x0 * 7 + y0))
    for _ in range(10):   # ржавчина
        x, y, r = rnd.uniform(x0 + 8, x1 - 8), rnd.uniform(y0 + 8, y1 - 8), rnd.uniform(5, 16)
        d.ellipse([x - r, y - r * .5, x + r, y + r * .5], fill=(122, 66, 38))
    if door:
        cx = (x0 + x1) / 2
        d.rectangle([cx - 34, y1 - 126, cx + 34, y1 - 6], fill=(36, 36, 42), outline=OUT, width=3)
        d.line([cx - 10, y1 - 100, cx - 10, y1 - 30], fill=(160, 160, 166), width=4)
        d.line([cx + 10, y1 - 100, cx + 10, y1 - 30], fill=(160, 160, 166), width=4)


def scrapyard(img, d, night):
    fence_c = (84, 88, 96)
    for x in range(1230, WW, 26):
        d.line([x, GR - 120, x, GR], fill=fence_c, width=3)
    for x in range(1230, WW, 13):   # сетка
        d.line([x, GR - 116, x + 26, GR - 4], fill=dk(fence_c, .8), width=1)
    d.line([1230, GR - 118, WW, GR - 118], fill=fence_c, width=4)
    container(d, 1270, GR - 110, 1520, GR, (60, 96, 130), False)
    container(d, 1300, GR - 220, 1560, GR - 110, (176, 72, 52), False)
    container(d, 1330, GR - 330, 1580, GR - 220, (70, 120, 80), False)
    for i in range(4):
        d.ellipse([1240 + i * 18, GR - 26, 1284 + i * 18, GR - 4], fill=(30, 30, 34), outline=(60, 60, 66), width=3)


def pit(d, dug, cont):
    depth = 340 * dug
    if depth <= 0:
        return
    d.rectangle([PIT_X0, GR + 10, PIT_X1, GR + 10 + depth], fill=(54, 42, 38))
    for y in range(int(GR + 30), int(GR + depth), 46):   # следы лопаты
        d.line([PIT_X0 + 10, y, PIT_X1 - 10, y + 4], fill=(62, 50, 44), width=3)
    if dug > .5:   # распорки из досок
        for x in (PIT_X0 + 6, PIT_X1 - 14):
            d.rectangle([x, GR + 10, x + 8, GR + depth], fill=(132, 96, 64))
        for y in range(int(GR + 60), int(GR + depth - 20), 110):
            d.rectangle([PIT_X0 + 6, y, PIT_X0 + 60, y + 8], fill=(132, 96, 64))
    d.rectangle([PIT_X0, GR + 10, PIT_X1, GR + 10 + depth], outline=(96, 76, 64), width=5)
    for k_ in range(int(depth // 32)):   # лестница
        d.line([PIT_X1 - 64, GR + 24 + k_ * 32, PIT_X1 - 24, GR + 24 + k_ * 32], fill=(170, 124, 74), width=5)
    d.line([PIT_X1 - 64, GR - 30, PIT_X1 - 64, GR + depth], fill=(170, 124, 74), width=7)
    d.line([PIT_X1 - 24, GR - 30, PIT_X1 - 24, GR + depth], fill=(170, 124, 74), width=7)
    if dug < 1:   # ведро и куча земли
        d.polygon([(PIT_X0 + 30, GR + depth), (PIT_X0 + 60, GR + depth - 26), (PIT_X0 + 100, GR + depth)], fill=(80, 62, 50))
    if cont:
        container(d, PIT_X0 + 20, GR + 120, PIT_X1 - 84, GR + 344)
        d.rectangle([PIT_X0 + 100, GR + 10, PIT_X0 + 120, GR + 120], fill=(110, 116, 126))   # вентиляция
        d.rectangle([PIT_X0 + 92, GR - 30, PIT_X0 + 128, GR + 10], fill=(130, 136, 146), outline=OUT, width=3)


_cache = {}


def world(day=False, lights=True, dug=0.0, cont=False):
    key = (day, lights, round(dug, 2), cont)
    if key in _cache:
        return _cache[key]
    top, bot = ((120, 170, 222), (206, 226, 242)) if day else ((8, 12, 28), (30, 40, 70))
    img = vgrad(WW * K, WH * K, top, bot)
    d = sky(img, SD(img), day, lights)
    city(d, lights, day)
    earth(img)
    d = SD(img)
    lamp_post(img, d, 690 + 40, lights and not day)
    d = SD(img)
    house(img, d, lights and not day)
    d = SD(img)
    tree(d, 722)
    fence(d, 650, 790)
    garage(img, d, lights and not day)
    d = SD(img)
    scrapyard(img, d, not day)
    pit(d, dug, cont)
    if len(_cache) > 10:
        _cache.clear()
    _cache[key] = img
    return img


# ---------- камера ----------
class View:
    """кусок мира под камерой; рисуем в мировых координатах, out() — кадр W×H"""
    def __init__(self, wimg, c, W, H):
        cx, cy, z = c
        w, h = W / z, H / z
        cx = min(max(cx, w / 2), WW - w / 2)
        cy = min(max(cy, h / 2), WH - h / 2)
        self.x0, self.y0, self.W, self.H = cx - w / 2, cy - h / 2, W, H
        box = (int(self.x0 * K), int(self.y0 * K), int((self.x0 + w) * K), int((self.y0 + h) * K))
        self.img = wimg.crop(box)
        self.x0, self.y0 = box[0] / K, box[1] / K
        self.d = SD(self.img, self.x0, self.y0)
        self.d.view = self

    def shade(self, x, y, rx, a=110):
        """полупрозрачная тень под ногами"""
        w, h = int(rx * 2 * K) + 20, int(rx * .4 * K) + 20
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).ellipse([10, 10, w - 10, h - 10], fill=a)
        m = m.filter(ImageFilter.GaussianBlur(4))
        self.img.paste(Image.new("RGB", (w, h)), (int((x - self.x0) * K - w / 2), int((y - self.y0) * K - h / 2)), m)

    def glow(self, x, y, r, col, k=1.0):
        soft(self.img, x, y, r, col, k, self.x0, self.y0)

    def beam(self, poly, col, alpha, blur=10):
        beam(self.img, poly, col, alpha, int(blur * K), self.x0, self.y0)

    def screen(self, x, y):
        return ((x - self.x0) * K / self.img.width * self.W, (y - self.y0) * K / self.img.height * self.H)

    def out(self):
        return self.img.resize((self.W, self.H), Image.LANCZOS)


# ---------- персонажи ----------
CHAR = {
    "me": dict(skin=(240, 194, 158), hair=(46, 36, 34), top=(56, 116, 204), pants=(44, 54, 76), shoes=(230, 230, 232), style="short"),
    "wife": dict(skin=(244, 202, 170), hair=(232, 186, 86), top=(66, 164, 124), pants=(56, 52, 66), shoes=(150, 70, 70), style="long"),
    "son": dict(skin=(242, 198, 166), hair=(126, 82, 50), top=(222, 72, 62), pants=(44, 62, 96), shoes=(240, 240, 240), style="spiky"),
    "mil": dict(skin=(236, 196, 172), hair=(206, 206, 212), top=(146, 92, 156), pants=(74, 62, 84), shoes=(90, 60, 50), style="bun", glasses=True),
    "neigh": dict(skin=(220, 172, 136), hair=(220, 172, 136), top=(244, 142, 40), pants=(54, 58, 66), shoes=(60, 50, 44), style="bald"),
}


def chibi(d, who, x, y, s=1.0, t=0.0, face="neutral", look=0, walk=False, arm=None, shadow=True):
    """плоский человечек с контуром; x, y — точка на полу, рост ~120*s"""
    c = CHAR[who]
    ow = 2.6 * s
    bob = 1.6 * math.sin(t * 2.6 + x * .1) * s
    lg = 9 * math.sin(t * 11) * s if walk else 0
    if shadow and hasattr(d, "view"):
        d.view.shade(x, y, 30 * s)
    for sx, off in ((-1, lg), (1, -lg)):   # ноги + обувь
        lx = x + sx * 10 * s + off
        d.rounded_rectangle([lx - 7.5 * s, y - 36 * s, lx + 7.5 * s, y - 6 * s], radius=5 * s, fill=c["pants"], outline=OUT, width=ow)
        d.rounded_rectangle([lx - 9 * s + sx * 2 * s, y - 10 * s, lx + 9 * s + sx * 3 * s, y], radius=4 * s, fill=c["shoes"], outline=OUT, width=ow)
    by = y - 32 * s + bob
    top = c["top"]
    hand = lambda hx, hy: d.ellipse([hx - 6.5 * s, hy - 6.5 * s, hx + 6.5 * s, hy + 6.5 * s], fill=c["skin"], outline=OUT, width=ow)
    sleeve = lambda a, b: (d.line([a, b], fill=OUT, width=13 * s), d.line([a, b], fill=dk(top, .85), width=8.5 * s))
    # дальняя рука
    if arm == "phone":
        sleeve((x - 18 * s, by - 40 * s), (x - 4 * s, by - 50 * s))
    else:
        sleeve((x - 20 * s, by - 40 * s), (x - 28 * s, by - 12 * s))
    d.rounded_rectangle([x - 23 * s, by - 50 * s, x + 23 * s, by], radius=13 * s, fill=top, outline=OUT, width=ow)   # тело
    d.rounded_rectangle([x + 4 * s, by - 46 * s, x + 20 * s, by - 4 * s], radius=9 * s, fill=dk(top, .86))           # тень на боку
    d.line([x - 10 * s, by - 48 * s, x - 6 * s, by - 38 * s], fill=mix(top, (255, 255, 255), .25), width=2 * s)       # ворот
    if arm == "phone":
        hand(x - 2 * s, by - 52 * s)
        d.rounded_rectangle([x - 10 * s, by - 72 * s, x + 6 * s, by - 50 * s], radius=3 * s, fill=(30, 30, 36), outline=OUT, width=ow * .7)
        d.rectangle([x - 7 * s, by - 69 * s, x + 3 * s, by - 54 * s], fill=(170, 220, 255))
    else:
        hand(x - 28 * s, by - 10 * s)
    if arm == "up":   # ближняя рука
        sleeve((x + 20 * s, by - 42 * s), (x + 34 * s, by - 80 * s))
        hand(x + 35 * s, by - 84 * s)
    elif arm == "shovel":
        sleeve((x + 20 * s, by - 40 * s), (x + 34 * s, by - 28 * s))
        hand(x + 36 * s, by - 26 * s)
    else:
        sleeve((x + 20 * s, by - 40 * s), (x + 28 * s, by - 12 * s))
        hand(x + 28 * s, by - 10 * s)
    # голова
    hy = by - 50 * s - 27 * s
    R = 29 * s
    hair = c["hair"]
    if c["style"] == "long":
        d.rounded_rectangle([x - R - 5 * s, hy - R, x + R + 5 * s, hy + R + 22 * s], radius=16 * s, fill=hair, outline=OUT, width=ow)
    d.ellipse([x - R, hy - R, x + R, hy + R], fill=c["skin"], outline=OUT, width=ow)
    d.ellipse([x + R * .2, hy - R * .7, x + R * .95, hy + R * .8], fill=dk(c["skin"], .93))   # тень на щеке
    for sx in (-1, 1):   # уши
        d.ellipse([x + sx * R - 5 * s, hy - 3 * s, x + sx * R + 5 * s, hy + 9 * s], fill=c["skin"], outline=OUT, width=ow * .7)
    if c["style"] in ("short", "long"):
        d.chord([x - R - 1 * s, hy - R - 3 * s, x + R + 1 * s, hy + R * .5], 180, 360, fill=hair, outline=OUT, width=ow)
        d.polygon([(x - R * .9, hy - 11 * s), (x - R * .3, hy - 18 * s), (x - R * .1, hy - 10 * s), (x + R * .4, hy - 18 * s), (x + R * .9, hy - 11 * s), (x + R, hy - R * .3), (x - R, hy - R * .3)], fill=hair)
    elif c["style"] == "spiky":
        d.chord([x - R, hy - R - 2 * s, x + R, hy + R * .3], 180, 360, fill=hair, outline=OUT, width=ow)
        for k_ in range(5):
            bx = x - R * .8 + k_ * R * .4
            d.polygon([(bx - 7 * s, hy - R * .6), (bx, hy - R - 10 * s), (bx + 7 * s, hy - R * .6)], fill=hair)
    elif c["style"] == "bun":
        d.chord([x - R, hy - R - 1 * s, x + R, hy + R * .3], 180, 360, fill=hair, outline=OUT, width=ow)
        d.ellipse([x - 12 * s, hy - R - 20 * s, x + 12 * s, hy - R + 4 * s], fill=hair, outline=OUT, width=ow)
    elif c["style"] == "bald":
        d.chord([x - R + 3 * s, hy - 4 * s, x + R - 3 * s, hy + R + 8 * s], 0, 180, fill=(126, 92, 70), outline=OUT, width=ow)
        d.arc([x - R * .6, hy - R * .9, x - R * .1, hy - R * .5], 200, 320, fill=(255, 240, 220), width=2 * s)   # блик на лысине
    # лицо
    ex = look * 5 * s
    blink = (t * 1.0 + x * .013) % 3.6 < .12
    for sx in (-1, 1):
        cx_ = x + sx * 10 * s + ex
        if blink:
            d.line([cx_ - 4 * s, hy + 1 * s, cx_ + 4 * s, hy + 1 * s], fill=OUT, width=2 * s)
        else:
            big = 1.35 if face == "shock" else 1.0
            d.ellipse([cx_ - 5.5 * s * big, hy - 6 * s * big, cx_ + 5.5 * s * big, hy + 6 * s * big], fill=(255, 255, 255), outline=OUT, width=1.4 * s)
            d.ellipse([cx_ - 3.2 * s + ex * .3, hy - 3 * s, cx_ + 3.2 * s + ex * .3, hy + 3.4 * s], fill=(30, 26, 30))
            d.ellipse([cx_ - 1.6 * s + ex * .3, hy - 2.4 * s, cx_ + .2 * s + ex * .3, hy - .6 * s], fill=(255, 255, 255))
    if c.get("glasses"):
        for sx in (-1, 1):
            cx_ = x + sx * 10 * s + ex
            d.ellipse([cx_ - 8.5 * s, hy - 8.5 * s, cx_ + 8.5 * s, hy + 8.5 * s], outline=OUT, width=1.8 * s)
    if face == "angry" or face == "shock":
        for sx in (-1, 1):
            cx_ = x + sx * 10 * s + ex
            d.line([cx_ - 6 * s, hy - 12 * s - (2 * s if face == "shock" else 0), cx_ + 6 * s, hy - 12 * s - (sx * 3 * s if face == "angry" else 2 * s)], fill=OUT, width=2.2 * s)
    for sx in (-1, 1):   # румянец
        d.ellipse([x + sx * 17 * s + ex - 5 * s, hy + 7 * s, x + sx * 17 * s + ex + 5 * s, hy + 12 * s], fill=mix(c["skin"], (240, 120, 120), .35))
    my = hy + 15 * s
    if face == "shock":
        d.ellipse([x - 5 * s + ex, my - 3 * s, x + 5 * s + ex, my + 9 * s], fill=(110, 40, 44), outline=OUT, width=1.6 * s)
    elif face == "smile":
        d.chord([x - 9 * s + ex, my - 6 * s, x + 9 * s + ex, my + 6 * s], 0, 180, fill=(110, 40, 44), outline=OUT, width=1.6 * s)
    elif face == "sad":
        d.arc([x - 7 * s + ex, my, x + 7 * s + ex, my + 9 * s], 200, 340, fill=OUT, width=2 * s)
    else:
        d.line([x - 5 * s + ex, my + 1 * s, x + 5 * s + ex, my + 1 * s], fill=OUT, width=2 * s)


def shovel(d, x, y, s=1.0, ang=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    d.line([P(0, -130), P(0, -26)], fill=OUT, width=9 * s)
    d.line([P(0, -130), P(0, -26)], fill=(176, 126, 76), width=5.5 * s)
    d.line([P(-12, -130), P(12, -130)], fill=(176, 126, 76), width=6 * s)
    d.polygon([P(-15, -28), P(15, -28), P(11, 4), P(0, 12), P(-11, 4)], fill=(176, 182, 192), outline=OUT)
