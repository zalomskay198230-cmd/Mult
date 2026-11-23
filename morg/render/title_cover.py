"""накладывает название сериала и плашку «ЧАСТЬ N» на иллюстрацию обложки.
python3 title_cover.py <арт.jpg> <N> <out.png> [строка1] [строка2]
Квадратный или горизонтальный арт достраивается до 9:16 тёмным небом сверху."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
src, n, out = sys.argv[1], sys.argv[2], sys.argv[3]
L1 = sys.argv[4] if len(sys.argv) > 4 else "НОЧНАЯ"
L2 = sys.argv[5] if len(sys.argv) > 5 else "СМЕНА"
img = Image.open(src).convert("RGB")
W, H = img.size
DY = 0
if H / W < 16 / 9 - .01:   # достроить до вертикали: верхняя полоска арта тянется вверх по колонкам и уходит в темноту
    import numpy as np
    H2 = int(W * 16 / 9)
    ext = H2 - H
    arr = np.asarray(img).astype(np.float32)
    strip = arr[2:10].mean(axis=0)                                   # цвет каждой колонки у верхнего края
    k = np.linspace(.35, 1.0, ext)[:, None, None] ** 1.6            # затемнение к самому верху
    top = (strip[None, :, :] * k).clip(0, 255).astype(np.uint8)
    canvas = Image.fromarray(np.concatenate([top, arr.astype(np.uint8)], axis=0))
    DY = ext * .42   # название ниже — в пустое небо и в зону, которую видно в сетке профиля (3:4)
    img, H = canvas, H2
s = W / 720
# затемнение сверху, чтобы надпись читалась
grad = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(grad)
for y in range(int(H * .4 + DY)):
    gd.line([0, y, W, y], fill=int(170 * (1 - y / (H * .4 + DY))))
img.paste((0, 0, 0), (0, 0), grad)
d = ImageDraw.Draw(img)
for txt, y, col, size in ((L1, 70, (242, 238, 230), 128), (L2, 196, (226, 52, 44), 128)):
    f = ImageFont.truetype(FB, int(size * s))
    while f.getlength(txt) > W * .92:
        size -= 4; f = ImageFont.truetype(FB, int(size * s))
    d.text(((W - f.getlength(txt)) / 2, y * s + DY), txt, font=f, fill=col, stroke_width=int(8 * s), stroke_fill=(10, 10, 12))
f = ImageFont.truetype(FB, int(34 * s)); lab = f"ЧАСТЬ {n}"
w = f.getlength(lab) + 48 * s
y0 = 340 * s + DY
d.line([W / 2 - w / 2 - 120 * s, y0 + 27 * s, W / 2 - w / 2 - 14 * s, y0 + 27 * s], fill=(226, 52, 44), width=int(4 * s))
d.line([W / 2 + w / 2 + 14 * s, y0 + 27 * s, W / 2 + w / 2 + 120 * s, y0 + 27 * s], fill=(226, 52, 44), width=int(4 * s))
d.rounded_rectangle([W / 2 - w / 2, y0, W / 2 + w / 2, y0 + 54 * s], radius=int(27 * s), fill=(150, 30, 30), outline=(10, 10, 12), width=int(3 * s))
d.text((W / 2 - f.getlength(lab) / 2, y0 + 7 * s), lab, font=f, fill=(255, 255, 255))
img.save(out)
