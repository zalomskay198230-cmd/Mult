"""Обложки для рилсов «Вернуть миллион» (1080×1920; главное — в центральной зоне 3:4 для сетки профиля).
Запуск: python3 oblozhki.py <2|3> <out.png>"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
EP = sys.argv[1]
OUT = os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

FONT_SUB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
YELLOW, RED, GREEN, INK = (250, 226, 90), (230, 60, 56), (60, 200, 120), (26, 24, 28)
CW, CH = 1080, 1920
SP = os.environ.get("SP", "/tmp")


def frame(ep, t):
    """кадр серии через режим PREVIEW её сборки"""
    base = os.path.join(SP, f"cover_e{ep}")
    subprocess.check_call(["python3", f"seriya0{ep}.py", f"../tts/s0{ep}", base], cwd=HERE,
                          env={**os.environ, "PREVIEW": str(t), "NOSUBS": "1"}, stdout=subprocess.DEVNULL)
    return Image.open(f"{base}_{t}.png").convert("RGB")


def text_c(d, y, txt, size, col, stroke=8):
    f = ImageFont.truetype(FONT_SUB, size)
    while f.getlength(txt) > CW - 80:
        size -= 4
        f = ImageFont.truetype(FONT_SUB, size)
    d.text(((CW - f.getlength(txt)) / 2, y), txt, font=f, fill=col, stroke_width=stroke, stroke_fill=INK)
    return y + size + 14


def badge(d, txt, col, y=330):
    f = ImageFont.truetype(FONT_SUB, 52)
    w = f.getlength(txt)
    d.rounded_rectangle([(CW - w) / 2 - 30, y, (CW + w) / 2 + 30, y + 90], radius=20, fill=col)
    d.text(((CW - w) / 2, y + 12), txt, font=f, fill=(255, 255, 255))


def base_img(img, crop_box=None, bright=1.0):
    if crop_box:
        img = img.crop(crop_box)
    img = img.resize((CW, CH), Image.LANCZOS)
    img = ImageEnhance.Brightness(img).enhance(bright)
    # затемнение сверху и снизу под текст
    grad = Image.new("L", (1, CH))
    for y in range(CH):
        k = max(0, 1 - y / 700) * 210 + max(0, (y - 1200) / 720) * 230
        grad.putpixel((0, y), int(min(230, k)))
    img.paste(Image.new("RGB", (CW, CH)), (0, 0), grad.resize((CW, CH)))
    return img


if EP == "2":
    img = base_img(frame(2, 72.6), crop_box=(40, 120, 680, 1258), bright=1.1)
    d = ImageDraw.Draw(img)
    badge(d, "СЕРИЯ 2", RED)
    y = text_c(d, 470, "КТО ОТКРЫЛ", 132, (255, 255, 255))
    text_c(d, y, "ДВЕРЬ?", 170, YELLOW)
    y = text_c(d, 1440, "я курьер в доме человека,", 52, (240, 240, 244), 5)
    text_c(d, y, "который украл мой миллион", 52, (240, 240, 244), 5)
    text_c(d, 1640, "1 247 ₽ / 1 000 000", 64, RED, 6)
else:
    img = base_img(frame(3, float(os.environ.get("T3", "47.0"))), crop_box=(0, 100, 720, 1280), bright=1.1)
    d = ImageDraw.Draw(img)
    badge(d, "ФИНАЛ", (40, 170, 100), y=200)
    y = text_c(d, 310, "Я НАШЁЛ ЕГО", 150, YELLOW)
    y = text_c(d, 1440, "хозяин канала оказался", 52, (240, 240, 244), 5)
    text_c(d, y, "ближе, чем я думал", 52, (240, 240, 244), 5)
    text_c(d, 1640, "600 347 ₽ / 1 000 000", 64, YELLOW, 6)
img.save(OUT)
print("готово:", OUT)
