"""накладывает название сериала и плашку «ЧАСТЬ N» на иллюстрацию обложки.
python3 title_cover.py <арт.jpg> <N> <out.png>"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
src, n, out = sys.argv[1], sys.argv[2], sys.argv[3]
img = Image.open(src).convert("RGB")
W, H = img.size
s = W / 720
# затемнение сверху, чтобы надпись читалась
grad = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(grad)
for y in range(int(H * .4)):
    gd.line([0, y, W, y], fill=int(170 * (1 - y / (H * .4))))
img.paste((0, 0, 0), (0, 0), grad)
d = ImageDraw.Draw(img)
for txt, y, col, size in (("НОЧНАЯ", 70, (242, 238, 230), 128), ("СМЕНА", 196, (226, 52, 44), 128)):
    f = ImageFont.truetype(FB, int(size * s))
    while f.getlength(txt) > W * .92:
        size -= 4; f = ImageFont.truetype(FB, int(size * s))
    d.text(((W - f.getlength(txt)) / 2, y * s), txt, font=f, fill=col, stroke_width=int(8 * s), stroke_fill=(10, 10, 12))
f = ImageFont.truetype(FB, int(34 * s)); lab = f"ЧАСТЬ {n}"
w = f.getlength(lab) + 48 * s
y0 = 340 * s
d.line([W / 2 - w / 2 - 120 * s, y0 + 27 * s, W / 2 - w / 2 - 14 * s, y0 + 27 * s], fill=(226, 52, 44), width=int(4 * s))
d.line([W / 2 + w / 2 + 14 * s, y0 + 27 * s, W / 2 + w / 2 + 120 * s, y0 + 27 * s], fill=(226, 52, 44), width=int(4 * s))
d.rounded_rectangle([W / 2 - w / 2, y0, W / 2 + w / 2, y0 + 54 * s], radius=int(27 * s), fill=(150, 30, 30), outline=(10, 10, 12), width=int(3 * s))
d.text((W / 2 - f.getlength(lab) / 2, y0 + 7 * s), lab, font=f, fill=(255, 255, 255))
img.save(out)
