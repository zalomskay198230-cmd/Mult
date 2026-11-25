"""Гибрид как в «Глубине»: 3D-фон (vl_bg_bridge.png) + 2D-герой (denis_rig) с тенью и подкраской под свет сцены."""
import sys, os
ROOT = "/home/user/Mult"
sys.path.insert(0, os.path.join(ROOT, "million", "render"))
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
from PIL import Image, ImageDraw, ImageFilter
import denis_rig as DR
W, H = 720, 1280
bg = Image.open(os.path.join(ROOT, "vladivostok", "render3d", "vl_bg_bridge.png")).convert("RGB").resize((W, H))
DR.use("vnuk", hoodie=True)
fig = DR.front((W, H), 520, 1235, .62, .6, ("down", "phone"), "idle", "worried", (-.6, -.4), phone_hand="r")
a = fig.getchannel("A")
x0, y0, x1, y1 = a.getbbox()
sh = Image.new("L", (W, H), 0)
cx, w = (x0 + x1) / 2, (x1 - x0) * .55
ImageDraw.Draw(sh).ellipse([cx - w, y1 - 16, cx + w, y1 + 18], fill=140)
bg.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
tint = (1.0, .78, .68)   # закатный тёплый свет
R, G, B = fig.convert("RGB").split()
fig = Image.merge("RGBA", (R.point(lambda v: int(v * tint[0])), G.point(lambda v: int(v * tint[1])), B.point(lambda v: int(v * tint[2])), a))
bg.paste(fig, (0, 0), fig)
from PIL import ImageChops
edge = ImageChops.subtract(a, ImageChops.offset(a, -4, 2)).filter(ImageFilter.GaussianBlur(1.5))   # тонкий контровой свет справа
bg.paste((255, 190, 130), (0, 0), edge.point(lambda v: int(v * .7)))
bg.save(sys.argv[1])
