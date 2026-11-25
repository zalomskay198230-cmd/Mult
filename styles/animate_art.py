"""Оживление нейросетевой иллюстрации: медленный наезд камеры с параллаксом, мерцание источников света,
пыль в воздухе, зерно плёнки, виньетка, лёгкое «дыхание» кадра.
python3 animate_art.py <арт> <out.mp4> <сек> [свет_x,свет_y,радиус;...] (координаты в долях кадра 0..1)"""
import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H, FPS = 720, 1280, 24
src, out, L = sys.argv[1], sys.argv[2], float(sys.argv[3])
lights = [tuple(map(float, l.split(","))) for l in sys.argv[4].split(";")] if len(sys.argv) > 4 else []

art = Image.open(src).convert("RGB")
# вписать в 9:16 с запасом под движение камеры (cover)
k = max(W * 1.18 / art.width, H * 1.18 / art.height)
big = art.resize((int(art.width * k), int(art.height * k)), Image.LANCZOS)
BW, BH = big.size
rng = np.random.default_rng(1)
dust = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(.6, 2.2), rng.uniform(4, 16), rng.uniform(0, 6.28)) for _ in range(70)]
yy, xx = np.mgrid[0:H, 0:W]
VIG = np.clip(1.15 - .55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2), .35, 1)[:, :, None].astype(np.float32)


def frame(t):
    p = t / L
    z = 1.0 + .1 * (p * p * (3 - 2 * p))                          # плавный наезд
    cw, ch = W * BW / (W * 1.18) / z, H * BH / (H * 1.18) / z
    cx = BW / 2 + 18 * math.sin(t * .35)                            # «дыхание» камеры
    cy = BH / 2 + 10 * math.sin(t * .27 + 1)
    img = big.resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    # мерцание источников света
    if lights:
        glow = Image.new("RGB", (W, H))
        gd = ImageDraw.Draw(glow)
        for lx, ly, lr in lights:
            fl = .65 + .35 * abs(math.sin(t * 7.3 + lx * 10)) * (.4 if (int(t * 9) % 17 == 0) else 1)
            px = (lx * art.width * k - (cx - cw / 2)) / cw * W
            py = (ly * art.height * k - (cy - ch / 2)) / ch * H
            r = lr * W
            gd.ellipse([px - r, py - r, px + r, py + r], fill=tuple(int(c * fl) for c in (255, 190, 110)))
        img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(lights[0][2] * W * .7)))
    # пыль
    d = ImageDraw.Draw(img)
    for x0, y0, r, sp, ph in dust:
        x = (x0 + 6 * math.sin(t * .8 + ph)) % W
        y = (y0 - sp * t) % H
        a = int(70 + 60 * math.sin(t * 2 + ph))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(a, a, a + 10))
    arr = np.asarray(img).astype(np.float32) * VIG
    arr += rng.normal(0, 7, (H, W, 1)).astype(np.float32)          # зерно
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
for i in range(int(L * FPS)):
    ff.stdin.write(frame(i / FPS).tobytes())
ff.stdin.close(); ff.wait()
print("готово:", out)
