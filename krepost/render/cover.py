"""обложка «Крепости» поверх арта: «КРЕПОСТЬ» + красная плашка «ДЕНЬ N».
python3 cover.py <арт> <N> <out.png>"""
import sys
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
src, n, out = sys.argv[1], sys.argv[2], sys.argv[3]
img = Image.open(src).convert("RGB")
W, H = img.size
s = W / 720
grad = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(grad)
for y in range(int(H * .3)):
    gd.line([0, y, W, y], fill=int(175 * (1 - y / (H * .3))))
img.paste((0, 0, 0), (0, 0), grad)
d = ImageDraw.Draw(img)
txt, size = "КРЕПОСТЬ", 132
f = ImageFont.truetype(FB, int(size * s))
while f.getlength(txt) > W * .9:
    size -= 4; f = ImageFont.truetype(FB, int(size * s))
d.text(((W - f.getlength(txt)) / 2, 80 * s), txt, font=f, fill=(244, 238, 228), stroke_width=int(9 * s), stroke_fill=(12, 10, 10))
f = ImageFont.truetype(FB, int(38 * s)); lab = f"ДЕНЬ {n}"
w = f.getlength(lab) + 52 * s
y0 = 250 * s
for x0, x1 in ((W / 2 - w / 2 - 130 * s, W / 2 - w / 2 - 14 * s), (W / 2 + w / 2 + 14 * s, W / 2 + w / 2 + 130 * s)):
    d.line([x0, y0 + 30 * s, x1, y0 + 30 * s], fill=(230, 60, 40), width=int(5 * s))
d.rounded_rectangle([W / 2 - w / 2, y0, W / 2 + w / 2, y0 + 60 * s], radius=int(30 * s), fill=(160, 30, 26), outline=(12, 10, 10), width=int(3 * s))
d.text((W / 2 - f.getlength(lab) / 2, y0 + 8 * s), lab, font=f, fill=(255, 255, 255))
img.save(out)
