"""обложка серии: крупный кадр + огромное название + плашка «ЧАСТЬ N». python3 cover.py <N> <out.png>"""
import sys, os
sys.argv, N, OUTP = [sys.argv[0], "/tmp/claude-0/-home-user-Mult/74a29afb-5c43-5da2-8351-58a94d2921e0/scratchpad/dumM", "x"], sys.argv[1], sys.argv[2]
import seriya01 as M
from PIL import Image, ImageDraw
img, d = M.corridor(light=.42, door_open=.4)
M.draw_gurneys(d, light=.5)
for i in range(7):   # босые следы к боксу 3
    k = i / 7
    M.footprint(d, M.lerp(250, 520, k) + (12 if i % 2 else -12), M.lerp(1120, 720, k), M.lerp(1.3, .5, k), i % 2 == 0)
M.chibi(d, "intern", 330, 1270, 3.0, 0.5, "shock", 1)
img = M.done(img)
M.flashlight(img, 420, 1000, 520, 700, 120, 70)
from PIL import ImageFilter
import numpy as np
yy, xx = np.mgrid[0:M.H, 0:M.W]
vig = np.clip(1.15 - .9 * (((xx - M.W / 2) / (M.W / 2)) ** 2 + ((yy - M.H * .55) / (M.H / 2)) ** 2), .15, 1)[:, :, None]
img = Image.fromarray((np.asarray(img).astype(float) * vig * np.array([1.0, .92, .92])).clip(0, 255).astype("uint8"))
dd = ImageDraw.Draw(img)
for size, txt, y, col in ((120, "НОЧНАЯ", 90, (240, 240, 236)), (120, "СМЕНА", 210, M.RED)):
    f = M.F(size, M.FONT_SUB)
    dd.text(((M.W - f.getlength(txt)) / 2, y), txt, font=f, fill=col, stroke_width=8, stroke_fill=(8, 8, 10))
f = M.F(32, M.FONT_SUB); lab = f"ЧАСТЬ {N}"
w = f.getlength(lab) + 40
dd.rounded_rectangle([M.W / 2 - w / 2, 350, M.W / 2 + w / 2, 400], radius=24, fill=(150, 30, 30))
dd.text((M.W / 2 - f.getlength(lab) / 2, 357), lab, font=f, fill=(255, 255, 255))
img.save(OUTP)
