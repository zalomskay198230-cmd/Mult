"""ВЕРНУТЬ МИЛЛИОН. Серия 1 — гибрид: 3D-окружение из Blender + 2D-Денис.
Фоны: million/render3d/frames_bg (без персонажа). Денис, телефоны, субтитры — из 2D-версии (seriya01.py).
Запуск: python3 seriya01_hybrid.py ../tts/s01 ../seriya01_hybrid.mp4"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import seriya01 as E
import toonlib
from toonlib import *

FR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "render3d", "frames_bg")
CUR = {"name": "s01", "t": 0.0}
_cache = {}
NIGHT = {"s01", "s02", "s06", "s07", "s08", "s09", "s10", "s12", "s13"}
TINT = {"night": (.84, .88, 1.0), "day": (1.0, 1.0, 1.0), "stairs": (.95, .95, .9)}


def bg3d(*_a, **_k):
    name, t = CUR["name"], CUR["t"]
    f = int(t * 12)
    path = None
    while f >= 0:
        p = os.path.join(FR, f"{name}_{f:04d}.png")
        if os.path.exists(p):
            path = p
            break
        f -= 1
    if path not in _cache:
        if len(_cache) > 30:
            _cache.clear()
        im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
        im = ImageEnhance.Brightness(im).enhance(1.35 if name in NIGHT else 1.05)
        _cache[path] = im
    return _cache[path].copy()


def paste_char(img, fig):
    """2D-персонаж на 3D-фоне: тень под ногами + подкраска под свет сцены"""
    name = CUR["name"]
    a = fig.getchannel("A")
    bbox = a.getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        sh = Image.new("L", (W, H), 0)
        cx, w = (x0 + x1) / 2, (x1 - x0) * .55
        ImageDraw.Draw(sh).ellipse([cx - w, y1 - 16, cx + w, y1 + 18], fill=150)
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), sh)
    kind = "stairs" if name == "s11" else "night" if name in NIGHT else "day"
    r, g, b = TINT[kind]
    if kind != "day":
        rgb = fig.convert("RGB")
        R, G, B = rgb.split()
        rgb = Image.merge("RGB", (R.point(lambda v: int(v * r)), G.point(lambda v: int(v * g)), B.point(lambda v: int(v * b))))
        fig = Image.merge("RGBA", (*rgb.split(), a))
    img.paste(fig, (0, 0), fig)
    return img


# подменяем фоны 2D-версии на 3D-кадры, а вставку персонажа — на «с тенью и подкраской»
for fn in ("street_bg", "room_night", "office_bg", "stair_bg", "newbuild_bg"):
    setattr(E, fn, bg3d)
E.paste = paste_char


def wrap(name, fn):
    def scene(t, L, cue=None):
        CUR["name"], CUR["t"] = name, t
        return fn(t, L, cue) if fn.__code__.co_argcount >= 3 else fn(t, L)
    scene.__code__ = scene.__code__   # 3 аргумента — toonlib передаст cue
    return scene


FUNCS = {n: wrap(n, getattr(E, n)) for n, *_ in E.PLAN}

if __name__ == "__main__":
    c06 = span("s06")[0] + 0.05
    run(FUNCS, hits=[span("s01")[0] + .4, c06 + dur("06.mp3") * .58, span("s08")[0] + .05 + dur("08.mp3") * .7,
                     span("s10")[0] + 1.2, span("s12")[0] + span("s12")[1] - .6])
