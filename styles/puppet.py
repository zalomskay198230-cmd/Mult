"""Кукольная анимация поверх нейросетевой иллюстрации («говорящая картинка»):
голова качается/дрожит, глаза моргают и бегают, рот открывается по громкости голоса, рука с фонарём трясётся,
рука из двери ползёт, капля пота стекает. Координаты частей — для morg/cover_s01_art.jpg (941×1672).
python3 puppet.py <арт> <голос.mp3> <out.mp4>"""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

src, voice, out = sys.argv[1], sys.argv[2], sys.argv[3]
FPS, W, H = 24, 720, 1280
art = Image.open(src).convert("RGB")
AW, AH = art.size

# --- части лица/тела (в координатах арта)
HEAD_C, HEAD_R, PIVOT = (300, 690), (235, 330), (300, 1010)
EYES = [((245, 710), (60, 34)), ((372, 722), (32, 32))]
MOUTH = (232, 826, 362, 910)          # рамка рта
LIP_TOP = 842
HAND = (40, 1250, 340, 1560)          # рука с фонарём
BEAM = (232, 1480)
GHOST = (628, 690, 712, 800)          # рука из двери
SKIN = np.array(art.crop((280, 795, 320, 815)).resize((1, 1), Image.LANCZOS).getpixel((0, 0)))
SKIN2 = np.array(art.crop((270, 920, 330, 945)).resize((1, 1), Image.LANCZOS).getpixel((0, 0)))


def soft_ellipse(size, box, blur):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))


# --- рот без «нарисованного» рта: закрашиваем тоном кожи (градиент сверху-вниз), края мягкие
base = art.copy()
mx0, my0, mx1, my1 = MOUTH
patch = Image.new("RGB", (mx1 - mx0, my1 - my0))
pd = ImageDraw.Draw(patch)
for y in range(my1 - my0):
    k = y / (my1 - my0)
    pd.line([0, y, mx1 - mx0, y], fill=tuple(int(a + (b - a) * k) for a, b in zip(SKIN, SKIN2)))
pm = soft_ellipse(patch.size, [4, 4, patch.width - 4, patch.height - 4], 6)
base.paste(patch, (mx0, my0), pm)
mouth_img = art.crop(MOUTH)
mouth_mask = soft_ellipse(mouth_img.size, [2, 2, mouth_img.width - 2, mouth_img.height - 2], 4)

# --- голос → громкость по кадрам
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", voice, "-f", "f32le", "-ac", "1", "-ar", "24000", "-"])
a = np.abs(np.frombuffer(raw, np.float32))
spf = 24000 // FPS
env = np.array([a[i * spf:(i + 1) * spf].mean() if i * spf < len(a) else 0 for i in range(len(a) // spf + FPS)])
env = env / (np.percentile(env, 95) + 1e-6)
env = np.convolve(env, [.25, .5, .25], "same").clip(0, 1.2)
L = len(a) / 24000 + .8
N = int(L * FPS)

head_mask = soft_ellipse(art.size, [HEAD_C[0] - HEAD_R[0], HEAD_C[1] - HEAD_R[1], HEAD_C[0] + HEAD_R[0], HEAD_C[1] + HEAD_R[1] + 140], 40)
hand_mask = soft_ellipse(art.size, [HAND[0], HAND[1], HAND[2], HAND[3]], 30)
ghost_mask = soft_ellipse(art.size, [GHOST[0] - 20, GHOST[1] - 20, GHOST[2] + 20, GHOST[3] + 20], 12)
rng = np.random.default_rng(2)
blinks = [1.1, 3.6, 5.2, 7.9, 10.4]


def eyelid(img, t):
    """моргание: веко опускается тоном кожи + линия ресниц"""
    ph = min(abs(t - b) for b in blinks)
    close = max(0, 1 - ph / .09) if ph < .09 else 0
    if close <= 0:
        return
    d = ImageDraw.Draw(img)
    for (cx, cy), (rx, ry) in EYES:
        h = ry * 2 * close
        d.chord([cx - rx - 3, cy - ry - 4, cx + rx + 3, cy - ry - 4 + h * 2], 180, 360, fill=tuple(int(v * .92) for v in SKIN))
        d.line([cx - rx, cy - ry - 4 + h, cx + rx, cy - ry - 4 + h], fill=(40, 26, 22), width=4)


def look(img, t):
    """зрачки бегают: сдвиг содержимого глаза внутри эллипса"""
    dx = int(5 * math.sin(t * 1.3) + 3 * math.sin(t * 4.1))
    dy = int(2 * math.sin(t * 2.2))
    for (cx, cy), (rx, ry) in EYES:
        box = (cx - rx, cy - ry, cx + rx, cy + ry)
        eye = img.crop(box)
        shifted = ImageChops.offset(eye, dx, dy)
        m = soft_ellipse(eye.size, [3, 3, eye.width - 3, eye.height - 3], 3)
        img.paste(shifted, box[:2], m)


def frame(i):
    t = i / FPS
    e = env[min(i, len(env) - 1)]
    img = base.copy()
    # рот: высота по громкости голоса (закрыт → открыт сильнее оригинала)
    m = .35 + .9 * min(1, e)
    mh = max(6, int(mouth_img.height * m))
    mouth = mouth_img.resize((mouth_img.width, mh), Image.LANCZOS)
    mm = mouth_mask.resize((mouth_img.width, mh), Image.LANCZOS)
    img.paste(mouth, (mx0, LIP_TOP - int((LIP_TOP - my0) * m)), mm)
    look(img, t)
    eyelid(img, t)
    # капля пота по щеке
    dy = (t * 40) % 180
    d = ImageDraw.Draw(img)
    d.ellipse([92, 780 + dy, 104, 798 + dy], fill=(200, 226, 236), outline=(90, 110, 120))
    # голова: качание + дрожь вокруг шеи
    ang = 1.6 * math.sin(t * 1.4) + .5 * math.sin(t * 23) * (.5 + .5 * math.sin(t * .7))
    head = img.rotate(ang, resample=Image.BICUBIC, center=PIVOT, translate=(0, -3 * math.sin(t * 2.2)))
    img2 = art.copy() if False else img.copy()
    img2.paste(head, (0, 0), head_mask)
    # рука с фонарём дрожит
    sh = (int(4 * math.sin(t * 31)), int(3 * math.sin(t * 27 + 1)))
    hand = ImageChops.offset(img2, *sh)
    img2.paste(hand, (0, 0), hand_mask)
    # фонарь мерцает
    fl = .7 + .3 * abs(math.sin(t * 9)) * (0.3 if int(t * 12) % 19 == 0 else 1)
    g = Image.new("RGB", art.size)
    ImageDraw.Draw(g).ellipse([BEAM[0] - 90, BEAM[1] - 90, BEAM[0] + 90, BEAM[1] + 90], fill=tuple(int(c * fl) for c in (255, 190, 110)))
    img2 = ImageChops.add(img2, g.filter(ImageFilter.GaussianBlur(60)))
    # рука из двери медленно ползёт
    k = min(1, t / L)
    gh = ImageChops.offset(img2, int(-10 * k - 2 * math.sin(t * 3)), int(4 * k))
    img2.paste(gh, (0, 0), ghost_mask)
    # кадр 9:16 с лёгким дыханием камеры
    z = 1.04 + .03 * (t / L)
    cw, ch = AW / z, AH / z
    cx, cy = AW / 2 + 6 * math.sin(t * .4), AH / 2 + 4 * math.sin(t * .3)
    fr = img2.resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    arr = np.asarray(fr).astype(np.float32) + rng.normal(0, 6, (H, W, 1)).astype(np.float32)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


import tempfile, os
tmp = tempfile.mkdtemp()
for i in range(N):
    frame(i).save(os.path.join(tmp, f"{i:05d}.jpg"), quality=94)
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "%05d.jpg"), "-i", voice,
                       "-af", "aecho=0.8:0.5:40|70:0.25|0.15", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-shortest", out])
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
os.rmdir(tmp)
print("готово:", out)
