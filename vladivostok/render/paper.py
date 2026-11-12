"""Paper-cut: каждый слой — вырезанный лист бумаги (текстура волокон, неровный край),
под ним мягкая тень на нижний слой; слои двигаются с разной скоростью (параллакс)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 720, 1280
_tex = {}


def texture(seed=0):
    """волокнистая текстура бумаги (множитель яркости ~0.9..1.05)"""
    if seed not in _tex:
        rnd = np.random.default_rng(seed)
        n = rnd.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        img = Image.fromarray(((n * 18) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        img = img.filter(ImageFilter.GaussianBlur(1.2))
        fib = Image.new("L", (W, H), 128)
        d = ImageDraw.Draw(fib)
        r = random.Random(seed)
        for _ in range(900):   # волокна
            x, y = r.uniform(0, W), r.uniform(0, H)
            a, L = r.uniform(0, math.pi), r.uniform(6, 22)
            d.line([x, y, x + L * math.cos(a), y + L * math.sin(a)], fill=r.choice((112, 144)), width=1)
        img = ImageChops.add(img, fib, scale=2.0)
        arr = np.asarray(img).astype(np.float32) / 128.0
        _tex[seed] = (0.9 + 0.1 * arr).clip(.85, 1.08)[:, :, None]
    return _tex[seed]


def rough(pts, amp=1.6, seed=0, step=10):
    """неровный край ножниц: дробим контур и чуть дёргаем точки"""
    r = random.Random(seed)
    out = []
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + r.uniform(-amp, amp), y0 + (y1 - y0) * t + r.uniform(-amp, amp)))
    return out


class Layer:
    """лист бумаги: набор фигур одного цвета (или нескольких), рисуется в RGBA"""
    def __init__(self, color, depth=1.0, seed=0):
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.color, self.depth, self.seed = color, depth, seed

    def poly(self, pts, color=None, amp=1.6):
        self.d.polygon(rough(pts, amp, self.seed + len(pts)), fill=(color or self.color) + (255,))
        return self

    def rect(self, x0, y0, x1, y1, color=None):
        return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color)

    def ellipse(self, box, color=None):
        self.d.ellipse(box, fill=(color or self.color) + (255,))
        return self

    def line(self, pts, w, color=None):
        self.d.line(pts, fill=(color or self.color) + (255,), width=w)
        return self

    def hole(self, box):
        """вырезанная дырка (окно/звезда)"""
        self.d.ellipse(box, fill=(0, 0, 0, 0))
        return self

    def hole_rect(self, box):
        self.d.rectangle(box, fill=(0, 0, 0, 0))
        return self


def hills(layer, base, amp, seed, peaks=4, step=30):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    pts = [(x, base - amp * (0.55 + 0.25 * math.sin(x / W * peaks * 1.7 + ph[0]) + 0.15 * math.sin(x / W * peaks * 4.1 + ph[1])
                               + 0.08 * math.sin(x / W * peaks * 9 + ph[2])))
           for x in range(-40, W + 60, step)]
    return layer.poly(pts + [(W + 60, H + 40), (-40, H + 40)])


def compose(bg_color, layers, shift=(0, 0), light=None):
    """layers: список Layer от дальнего к ближнему. shift — смещение камеры (параллакс по depth)."""
    base = Image.new("RGB", (W, H), bg_color)
    arr = (np.asarray(base).astype(np.float32) * texture(99)).clip(0, 255).astype(np.uint8)
    base = Image.fromarray(arr)
    for i, L in enumerate(layers):
        dx, dy = int(shift[0] * L.depth), int(shift[1] * L.depth)
        if dx or dy:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.paste(L.img, (dx, dy))
        else:
            lay = L.img
        a = lay.getchannel("A")
        # тень листа на то, что под ним
        sh = a.filter(ImageFilter.GaussianBlur(7 + 3 * L.depth)).point(lambda v: int(v * .55))
        shadow = Image.new("L", (W, H), 0)
        shadow.paste(sh, (int(4 + 2 * L.depth), int(7 + 3 * L.depth)))
        base.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), shadow)
        rgb = np.asarray(lay.convert("RGB")).astype(np.float32) * texture(i + 1)
        lit = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))
        base.paste(lit, (0, 0), a)
        # светлый срез по верхней кромке листа
        edge = ImageChops.subtract(a, ImageChops.offset(a, 0, 2)).filter(ImageFilter.GaussianBlur(.6)).point(lambda v: int(v * .35))
        base.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), edge)
    return base


def glow(img, xy, r, col, k=1.0):
    r = int(r); size = r * 4
    lay = Image.new("RGB", (size, size))
    ImageDraw.Draw(lay).ellipse([r, r, 3 * r, 3 * r], fill=tuple(int(c * k) for c in col))
    lay = lay.filter(ImageFilter.GaussianBlur(r * .6))
    bx, by = int(xy[0] - 2 * r), int(xy[1] - 2 * r)
    img.paste(ImageChops.add(img.crop((bx, by, bx + size, by + size)), lay), (bx, by))
