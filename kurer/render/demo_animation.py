"""Демо анимаций Макса: стоит → идёт к камере → идёт сбоку → бежит.
Запуск: python3 demo_animation.py ../demo_animacii.mp4"""
import os, sys, math, random, subprocess
OUT = sys.argv[1] if len(sys.argv) > 1 else "demo.mp4"
sys.argv = [sys.argv[0], ".", OUT]
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vakhta", "render"))
from toonlib import FONT_SUB, YELLOW
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from character_sheet import bg_city
import rig

W, H, FPS = 720, 1280, 24
CITY = bg_city(3600, H, seed=7)
CITY_NEAR = bg_city(3600, H, seed=11)
F = ImageFont.truetype(FONT_SUB, 52)
SEGS = [("стоит", 3.0), ("идёт", 3.2), ("идёт · сбоку", 3.4), ("бежит", 3.6)]
TOTAL = sum(d for _, d in SEGS)


def caption(img, txt):
    d = ImageDraw.Draw(img)
    d.text(((W - F.getlength(txt)) / 2, 90), txt, font=F, fill=YELLOW, stroke_width=5, stroke_fill=(40, 34, 14))


def city_bg(scroll):
    x = int(scroll) % (3600 - W)
    img = CITY.crop((x, 0, x + W, H))
    return img


RUN_F = 1.55          # шагов-циклов в секунду при беге (как в rig)
RUN_SCROLL = 520      # скорость дороги, px/с
RUN_X, RUN_S = W / 2 - 20, .8


def foot_contacts(lt):
    """моменты касания земли и x точки касания на экране"""
    out = []
    k = 0
    while True:
        for leg_ph0 in (math.pi / 2, 3 * math.pi / 2):   # ближняя нога и дальняя
            tc = (leg_ph0 + 2 * math.pi * k) / (2 * math.pi * RUN_F) - .03
            if tc > lt:
                return out
            th, kn, _, _ = rig.cycle("run", 2 * math.pi * RUN_F * tc + (0 if leg_ph0 < math.pi else -math.pi))
            dx = rig.THIGH * math.sin(math.radians(th)) + rig.SHIN * math.sin(math.radians(th - kn))
            out.append((tc, RUN_X + (dx + 40) * RUN_S))
        k += 1


def dust(img, lt, ground):
    """облачка пыли из-под каждого шага: остаются на дороге, расплываются и тают"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for tc, x0 in foot_contacts(lt):
        age = lt - tc
        if age > .7:
            continue
        k = age / .7
        x = x0 - RUN_SCROLL * age
        rnd = random.Random(int(tc * 1000))
        for i in range(5):
            ox = rnd.uniform(-30, 10) - 40 * k * rnd.uniform(.5, 1.2)
            oy = -rnd.uniform(4, 26) * k - 4
            r = 12 + 40 * k * rnd.uniform(.7, 1.2)
            a = int(175 * (1 - k) ** 1.3)
            d.ellipse([x + ox - r, ground + oy - r * .55, x + ox + r, ground + oy + r * .55], fill=(156, 146, 134, a))
    return Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(3))).convert("RGB")


def frame(t):
    start = 0
    for name, dur in SEGS:
        if t < start + dur:
            lt = t - start
            break
        start += dur
    ground = int(H * .72) + 140
    if name == "стоит":
        img = city_bg(200)
        expr = "neutral" if lt < 1.8 else "tense"
        look = (0, 0) if lt < 1.2 else (.8, 0)
        fig = rig.front_figure((W, H), W / 2, ground, .82, lt, "idle", expr, look)
    elif name == "идёт":
        img = city_bg(200)
        k = lt / dur
        s = .52 + .3 * k
        fig = rig.front_figure((W, H), W / 2, int(H * .72) + 30 + 110 * k, s, lt, "walk", "neutral")
    elif name == "идёт · сбоку":
        img = city_bg(400 + lt * 160)
        fig = rig.side_figure((W, H), W / 2 - 40, ground, .8, lt, "walk")
    else:
        img = city_bg(1000 + lt * RUN_SCROLL)
        img = dust(img, lt, ground - 4)   # пыль позади ног
        fig = rig.side_figure((W, H), RUN_X, ground, RUN_S, lt, "run", expr="shock")
    img.paste(fig, (0, 0), fig)
    caption(img, name)
    a = min(lt / .2, (dur - lt) / .2, 1)
    if a < 1:
        img = Image.blend(Image.new("RGB", (W, H)), img, max(0, a) * .7 + .3)
    return img


if __name__ == "__main__":
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("готово:", OUT)
