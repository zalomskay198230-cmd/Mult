"""Рекламная вставка klassvpn (вертикальная, 720×1280) и иконка в угол кадра.
Ассеты — den365/ad: logo.jpg, mascot_rocket_cut.png (вырезан cutout.py).
Отдельный ролик: python3 ad_klassvpn.py ../ad/klassvpn_insert.mp4 [длительность]"""
import os, sys, math, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.join(HERE, "..", "ad")
W, H, FPS = 720, 1280, 24
FONT_SUB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
YEL = (255, 206, 40)
MARK = "РЕКЛАМА"          # сюда — «Реклама. Рекламодатель, erid: …», когда пришлют данные

_cache = {}


def _load():
    if _cache:
        return _cache
    logo = Image.open(os.path.join(AD, "logo.jpg")).convert("RGB")
    m = logo.crop((60, 60, 580, 580))
    _cache["tile"] = m
    _cache["rocket"] = Image.open(os.path.join(AD, "mascot_rocket_cut.png")).convert("RGBA")
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):   # тёмно-синий космос
        k = y / H
        d.line([0, y, W, y], fill=(int(8 + 6 * k), int(10 + 10 * k), int(22 + 22 * k)))
    glow = Image.new("RGB", (W, H))
    ImageDraw.Draw(glow).ellipse([60, 330, 660, 930], fill=(30, 70, 150))
    bg = ImageChops.add(bg, glow.filter(ImageFilter.GaussianBlur(120)))
    rnd = random.Random(7)
    stars = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(stars)
    for _ in range(260):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice((.8, 1, 1.2, 1.8))
        c = rnd.randint(120, 230)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, min(255, c + 25)))
    _cache["bg"] = bg
    _cache["stars"] = stars
    return _cache


def tile(size, radius_k=.22):
    """логотип в скруглённом квадрате (как иконка приложения)"""
    t = _load()["tile"].resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius_k), fill=255)
    out = t.convert("RGBA"); out.putalpha(m)
    return out


def corner_icon(img, x=None, y=150, size=72, a=1.0):
    """иконка klassvpn в углу кадра (под правой шкалой HUD)"""
    x = W - 40 - size if x is None else x
    ic = tile(size)
    sh = Image.new("L", (size + 20, size + 20), 0)
    ImageDraw.Draw(sh).rounded_rectangle([10, 14, size + 10, size + 14], radius=int(size * .22), fill=int(140 * a))
    img.paste((0, 0, 0), (x - 10, y - 10), sh.filter(ImageFilter.GaussianBlur(6)))
    if a < 1:
        al = ic.getchannel("A").point(lambda v: int(v * a)); ic.putalpha(al)
    img.paste(ic, (x, y), ic)
    return img


def ease(k):
    k = max(0.0, min(1.0, k))
    return 1 - (1 - k) ** 3


def frame(t, L=5.0):
    c = _load()
    # звёзды чуть летят — ощущение скорости (отдельный слой, фон не сдвигается)
    img = ImageChops.add(c["bg"], ImageChops.offset(c["stars"], int(-t * 40) % W, int(t * 22) % H))
    # ракета с кроликом влетает снизу слева и зависает
    k = ease(t / 1.1)
    rk = c["rocket"]
    s = 430
    r = rk.resize((s, int(rk.height * s / rk.width)), Image.LANCZOS)
    x = int(-380 + (150 - -380) * k)
    y = int(1150 + (330 - 1150) * k + 10 * math.sin(t * 3))
    trail = Image.new("RGB", (W, H))
    td = ImageDraw.Draw(trail)
    tx, ty = x + 70, y + int(r.height * .62)
    for i, (w, col) in enumerate(((26, (40, 90, 200)), (14, (90, 150, 255)), (6, (200, 230, 255)))):
        td.line([tx, ty, tx - 700, ty + 420], fill=col, width=w)
    img = ImageChops.add(img, trail.filter(ImageFilter.GaussianBlur(10)))
    img.paste(r, (x, y), r)
    d = ImageDraw.Draw(img)
    # логотип и название
    if t > .9:
        a = ease((t - .9) / .35)
        ic = tile(110)
        lay = img.copy()
        lay.paste(ic, (110, 880), ic)
        ld = ImageDraw.Draw(lay)
        ld.text((240, 878), "klassvpn", font=F(92, FONT_SUB), fill=(255, 255, 255))
        img = Image.blend(img, lay, a)
    if t > 1.4:
        a = ease((t - 1.4) / .35)
        lay = img.copy()
        ld = ImageDraw.Draw(lay)
        f = F(44, FONT_SUB)
        for i, (txt, col) in enumerate((("НАДЁЖНЫЙ VPN —", (255, 255, 255)), ("КОТОРЫЙ НЕ НУЖНО", YEL), ("МЕНЯТЬ", YEL))):
            ld.text(((W - f.getlength(txt)) / 2, 1030 + i * 58), txt, font=f, fill=col)
        img = Image.blend(img, lay, a)
    # пометка «Реклама»
    fm = F(20)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([24, 24, 48 + fm.getlength(MARK), 60], radius=8, fill=(0, 0, 0))
    d.text((36, 31), MARK, font=fm, fill=(200, 200, 206))
    # мягкий вход/выход
    edge = min(1, t / .2, (L - t) / .25)
    if edge < 1:
        img = Image.blend(Image.new("RGB", (W, H)), img, max(0, edge))
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AD, "klassvpn_insert.mp4")
    L = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    if os.environ.get("PREVIEW"):
        for ts in os.environ["PREVIEW"].split(","):
            frame(float(ts), L).save(f"{out}_{ts}.png")
        sys.exit()
    wav = out + ".wav"   # «вжух» ракеты + лёгкий гул
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                           f"anoisesrc=color=pink:amplitude=0.5:d={L}", "-af",
                           f"highpass=f=300,lowpass=f=4000,volume='0.9*exp(-((t-0.5)*2.2)^2)+0.05':eval=frame,afade=t=out:st={L-.4}:d=.4",
                           "-ar", "44100", "-ac", "2", wav])
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", out],
                          stdin=subprocess.PIPE)
    for i in range(int(L * FPS)):
        ff.stdin.write(frame(i / FPS, L).tobytes())
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print("готово:", out)
