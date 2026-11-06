"""ВЕРНУТЬ МИЛЛИОН. Серия 1 — «347 рублей». Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "vakhta", "render"))
from toonlib import *
import person

LINES = {
    "01": "Три дня назад у меня был миллион. Сейчас — триста сорок семь рублей.",
    "02": "И самое обидное — я сам нажал каждую кнопку.",
    "03": "День первый. Мне пишет старый друг Артём.",
    "04": "Он никогда мне не врал. Я закинул триста тысяч.",
    "05": "К вечеру — плюс сто двадцать. Вот тут мне надо было остановиться.",
    "06": "День второй. Я перевёл всё. Весь миллион.",
    "07": "Мама звонила три раза. Я не взял. Потом расскажу почему.",
    "08": "День третий. Канала больше нет. Токен — ноль.",
    "09": "Артём не отвечает. Нигде.",
    "10": "А вчера он выложил фото. С ключами от новой квартиры.",
    "11": "Я понял, куда ушёл мой миллион. И я знаю, где эта квартира.",
    "12": "У меня есть план. И первый пункт вам не понравится.",
    "13": "День первый. На счету триста сорок семь рублей. Поехали.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[-1] = ("s13", [("13", 0.05)], 2.2)
setup(LINES, PLAN)

F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
F_REG = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
GREEN, RED, BLUE = (60, 200, 120), (230, 60, 56), (60, 130, 230)


def rub(n):
    return f"{n:,}".replace(",", " ") + " ₽"


def paste(img, fig):
    img.paste(fig, (0, 0), fig)
    return img


def counter_plate(img, t):
    """фирменный счётчик сериала в углу"""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([400, 26, 700, 108], radius=16, fill=(16, 18, 22), outline=(80, 84, 96), width=2)
    d.text((418, 34), "БАЛАНС", font=F(18), fill=(150, 154, 166))
    d.text((418, 56), "347 ₽", font=F(36, FONT_SUB), fill=RED)
    d.text((560, 34), "ЦЕЛЬ", font=F(18), fill=(150, 154, 166))
    d.text((560, 62), "1 000 000", font=F(26, FONT_SUB), fill=GREEN)


def day_plate(img, txt, a=1.0):
    d = ImageDraw.Draw(img)
    f = F(44, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([40, 130, 80 + w, 200], radius=14, fill=(230, 60, 56) if "ВОЗВРАТ" not in txt else (40, 170, 100))
    d.text((60, 138), txt, font=f, fill=(255, 255, 255))


# ---------- телефон ----------
PX0, PY0, PX1, PY1 = 90, 150, 630, 1180


def phone(img, dark=False):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([PX0 - 24, PY0 - 24, PX1 + 24, PY1 + 24], radius=70, fill=(20, 20, 24), outline=INK, width=6)
    d.rounded_rectangle([PX0, PY0, PX1, PY1], radius=50, fill=(14, 16, 20) if dark else (246, 246, 248))
    d.rounded_rectangle([290, PY0 + 14, 430, PY0 + 46], radius=16, fill=(10, 10, 12))
    return d


def room_bg(dark=.6):
    img = vgrad(W, H, (54, 58, 70), (24, 26, 32))
    return Image.eval(img, lambda v: int(v * dark / .6))


def hand_hold(img, side=1):
    return   # рука-«пятно» убрана: телефон крупно читается лучше
    d = ImageDraw.Draw(img)
    sk = (214, 170, 140)
    x = PX1 - 30 if side > 0 else PX0 + 30
    d.rounded_rectangle([x - 70, PY1 - 160, x + 70, PY1 + 140], radius=60, fill=sk, outline=INK, width=4)
    d.polygon([(x - 90, PY1 + 80), (x + 90, PY1 + 80), (x + 120, H + 20), (x - 140, H + 20)], fill=(84, 88, 96), outline=INK)


def old_s01(t, L, cue):
    """хук: баланс падает с миллиона до 347"""
    img = room_bg(.45)
    d = phone(img, dark=True)
    d.text((PX0 + 40, PY0 + 90), "Мой банк", font=F(34), fill=(200, 204, 214))
    d.text((PX0 + 40, PY0 + 170), "Баланс", font=F(30, F_REG), fill=(140, 146, 160))
    p = min(1, max(0, (t - .3) / 2.6))
    p = p * p * (3 - 2 * p)
    val = int(1_000_000 - (1_000_000 - 347) * p)
    if p > .02:   # «дрожащие» промежуточные значения
        val = max(347, val + int(random.Random(int(t * 30)).uniform(-9000, 9000) * (1 - p)))
    col = (240, 240, 244) if p < .05 else RED
    d.text((PX0 + 40, PY0 + 210), rub(val), font=F(76, FONT_SUB), fill=col)
    rows = [("КриптоКанал", "−300 000 ₽"), ("КриптоКанал", "−820 000 ₽"), ("Комиссия", "−4 653 ₽")]
    for i, (a, b) in enumerate(rows):
        y = PY0 + 380 + i * 110
        if p > .25 + i * .2:
            d.rounded_rectangle([PX0 + 30, y, PX1 - 30, y + 90], radius=18, fill=(30, 32, 40))
            d.text((PX0 + 56, y + 26), a, font=F(26, F_REG), fill=(200, 204, 214))
            d.text((PX1 - 56 - F(28).getlength(b), y + 24), b, font=F(28), fill=RED)
    hand_hold(img)
    if .2 < p < .95 and int(t * 12) % 2 == 0:   # красная вспышка
        img = Image.blend(img, Image.new("RGB", (W, H), (120, 10, 10)), .12)
    img = zoom(img, 1.12 - .08 * t / L, .5, .32)
    return shake(img, t, 6 * (1 - p) if p > .02 else 0)


def denis_bust(img, x, y, s, t, expr="tense", look=(0, 0), phone_glow=True):
    fig, _ = person.figure((W, H), x, y, s, "denis", expr, look, blink=(t % 3.4) < .1)
    img = paste(img, fig)
    if phone_glow:
        glow(img, (x, y + 330 * s), 200 * s, (30, 60, 100), .9)
    return img


def old_s02(t, L):
    img = room_bg(.4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1040, W, H], fill=(30, 30, 36))   # пол пустой комнаты
    d.rectangle([520, 200, 700, 560], fill=(70, 80, 100), outline=INK, width=6)   # окно
    img = denis_bust(img, W / 2, 380, 1.15, t, "sad", (0, .8))
    counter_plate(img, t)
    return zoom(img, 1.0 + .05 * t / L, .5, .4)


def office_bg():
    img = vgrad(W, H, (196, 204, 214), (150, 158, 170))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 180):
        d.rectangle([x + 20, 160, x + 150, 560], fill=(170, 186, 204), outline=(120, 130, 146), width=4)
    d.rectangle([0, 980, W, H], fill=(120, 110, 100))
    return img


def old_s03(t, L):
    img = office_bg()
    img = denis_bust(img, W / 2 + 40, 340, 1.1, t, "neutral", (.6, .6), phone_glow=False)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1000, W, H], fill=(120, 96, 76), outline=INK, width=5)   # стол
    vib = 6 * math.sin(t * 60) if (t % 1.2) < .5 else 0
    d.rounded_rectangle([110 + vib, 1010, 250 + vib, 1070], radius=10, fill=(24, 24, 28), outline=INK, width=3)
    d.text((126 + vib, 1022), "Артём", font=F(24), fill=(240, 240, 240))
    day_plate(img, "ДЕНЬ 1")
    counter_plate(img, t)
    return img


def bubble(d, y, txt, mine=False, w=380):
    f = F(30, F_REG)
    lines, cur = [], ""
    for wd in txt.split():
        if f.getlength((cur + " " + wd).strip()) > w - 50:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    h = 30 + 40 * len(lines)
    x0 = PX1 - 30 - w if mine else PX0 + 30
    d.rounded_rectangle([x0, y, x0 + w, y + h], radius=24, fill=(70, 140, 240) if mine else (232, 234, 240))
    for i, ln in enumerate(lines):
        d.text((x0 + 22, y + 14 + i * 40), ln, font=f, fill=(255, 255, 255) if mine else (30, 30, 36))
    return y + h + 20


def old_s04(t, L, cue):
    img = room_bg(.5)
    d = phone(img)
    d.rectangle([PX0, PY0 + 60, PX1, PY0 + 150], fill=(236, 238, 244))
    d.ellipse([PX0 + 30, PY0 + 74, PX0 + 92, PY0 + 136], fill=(176, 138, 86))
    d.text((PX0 + 110, PY0 + 86), "Артём", font=F(32), fill=(20, 20, 24))
    d.text((PX0 + 110, PY0 + 122), "в сети", font=F(20, F_REG), fill=GREEN)
    p = (t - cue["04"]) / dur("04.mp3")
    msgs = [(0, "Брат, есть закрытый канал. Токен растёт каждый день", False), (.1, "Заходи, пока не поздно. Я уже х3", False),
            (.55, "Закинул 300к", True)]
    y = PY0 + 190
    for when, txt, mine in msgs:
        if p > when:
            y = bubble(d, y, txt, mine)
    hand_hold(img)
    counter_plate(img, t)
    return zoom(img, 1.04, .5, .4)


def chart(d, x0, y0, x1, y1, pts, col):
    d.rectangle([x0, y0, x1, y1], fill=(22, 24, 30))
    for k in range(5):
        y = y0 + (y1 - y0) * k / 4
        d.line([x0, y, x1, y], fill=(40, 44, 52), width=2)
    P = [(x0 + (x1 - x0) * i / (len(pts) - 1), y1 - (y1 - y0) * v) for i, v in enumerate(pts)]
    d.line(P, fill=col, width=7, joint="curve")
    d.ellipse([P[-1][0] - 10, P[-1][1] - 10, P[-1][0] + 10, P[-1][1] + 10], fill=col)


def old_s05(t, L):
    img = room_bg(.5)
    d = phone(img, dark=True)
    k = min(1, t / (L * .7))
    n = 2 + int(28 * k)
    rnd = random.Random(3)
    pts, v = [], .2
    for i in range(30):
        v += rnd.uniform(-.02, .05)
        pts.append(min(.95, v))
    chart(d, PX0 + 30, PY0 + 320, PX1 - 30, PY0 + 800, pts[:n], GREEN)
    d.text((PX0 + 40, PY0 + 100), "$TOKEN", font=F(34), fill=(200, 204, 214))
    bal = int(300_000 + 120_000 * k)
    d.text((PX0 + 40, PY0 + 160), rub(bal + 700_000), font=F(64, FONT_SUB), fill=GREEN)
    d.text((PX0 + 40, PY0 + 240), f"+{rub(int(120_000 * k))}", font=F(34), fill=GREEN)
    hand_hold(img)
    counter_plate(img, t)
    return zoom(img, 1.04 + .04 * t / L, .5, .4)


def old_s06(t, L, cue):
    img = room_bg(.5)
    d = phone(img)
    d.text((PX0 + 40, PY0 + 100), "Перевод", font=F(40), fill=(20, 20, 24))
    d.text((PX0 + 40, PY0 + 180), "Получатель", font=F(26, F_REG), fill=(130, 134, 146))
    d.text((PX0 + 40, PY0 + 214), "КриптоКанал · кошелёк", font=F(32), fill=(20, 20, 24))
    d.text((PX0 + 40, PY0 + 300), "Сумма", font=F(26, F_REG), fill=(130, 134, 146))
    d.text((PX0 + 40, PY0 + 336), rub(1_000_000), font=F(70, FONT_SUB), fill=(20, 20, 24))
    d.text((PX0 + 40, PY0 + 430), "Весь доступный остаток", font=F(24, F_REG), fill=RED)
    p = (t - cue["06"]) / dur("06.mp3")
    by = PY1 - 200
    pressed = p > .55
    d.rounded_rectangle([PX0 + 40, by, PX1 - 40, by + 110], radius=30, fill=(40, 100, 210) if pressed else BLUE)
    txt = "Отправлено ✓" if p > .7 else "Подтвердить"
    f = F(38, FONT_SUB)
    d.text(((PX0 + PX1) / 2 - f.getlength(txt) / 2, by + 30), txt, font=f, fill=(255, 255, 255))
    # палец
    fy = by + 60 + (0 if pressed else 120 * (1 - min(1, p / .55)))
    sk = (214, 170, 140)
    d.rounded_rectangle([340, fy, 420, fy + 260], radius=40, fill=sk, outline=INK, width=4)
    d.polygon([(300, fy + 200), (460, fy + 200), (500, H + 20), (260, H + 20)], fill=sk, outline=INK)
    day_plate(img, "ДЕНЬ 2")
    counter_plate(img, t)
    return zoom(img, 1.04, .5, .55)


def old_s07(t, L, cue):
    img = room_bg(.4)
    d = phone(img, dark=True)
    # аватар мамы в кружке
    ava = Image.new("RGB", (300, 300), (60, 70, 90))
    fig, _ = person.figure((300, 300), 150, 46, 1.4, "mama", "worried", head_only=True)
    ava.paste(fig, (0, 0), fig)
    m = Image.new("L", (300, 300), 0); ImageDraw.Draw(m).ellipse([0, 0, 300, 300], fill=255)
    img.paste(ava.resize((260, 260)), (230, PY0 + 140), m.resize((260, 260)))
    d = ImageDraw.Draw(img)
    f = F(56, FONT_SUB)
    d.text((360 - f.getlength("Мама") / 2, PY0 + 430), "Мама", font=f, fill=(240, 240, 244))
    p = (t - cue["07"]) / dur("07.mp3")
    calls = 1 + min(2, int(p * 3.2))
    d.text((360 - F(30, F_REG).getlength(f"входящий вызов · {calls}") / 2, PY0 + 510), f"входящий вызов · {calls}", font=F(30, F_REG), fill=(160, 166, 180))
    for i, (x, col, ic) in enumerate(((210, RED, "✕"), (510, GREEN, "✓"))):
        y = PY1 - 220
        r = 70 + (6 * math.sin(t * 10) if i == 1 else 0)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # палец сбрасывает
    if int(p * 3.2 * 2) % 2 == 1:
        sk = (214, 170, 140)
        d.rounded_rectangle([170, PY1 - 230, 250, H], radius=40, fill=sk, outline=INK, width=4)
    hand_hold(img)
    counter_plate(img, t)
    return shake(zoom(img, 1.04, .5, .4), t, 3 if (t % .8) < .3 else 0)


def old_s08(t, L):
    img = room_bg(.5)
    d = phone(img, dark=True)
    k = min(1, t / 1.2)
    rnd = random.Random(3)
    pts, v = [], .2
    for i in range(24):
        v += rnd.uniform(-.02, .05)
        pts.append(min(.95, v))
    pts += [pts[-1] * (1 - k * j / 4) for j in range(1, 5)]
    chart(d, PX0 + 30, PY0 + 320, PX1 - 30, PY0 + 800, pts, RED if k > .2 else GREEN)
    d.text((PX0 + 40, PY0 + 160), rub(int(1_120_000 * (1 - k))), font=F(64, FONT_SUB), fill=RED)
    if t > 1.0:
        d.rounded_rectangle([PX0 + 30, PY0 + 860, PX1 - 30, PY0 + 980], radius=24, fill=(60, 20, 22))
        d.text((PX0 + 60, PY0 + 890), "Канал удалён", font=F(44, FONT_SUB), fill=(255, 120, 110))
    hand_hold(img)
    day_plate(img, "ДЕНЬ 3")
    counter_plate(img, t)
    return shake(zoom(img, 1.04, .5, .45), t, 8 if .8 < t < 1.4 else 0)


def old_s09(t, L):
    img = room_bg(.45)
    d = phone(img, dark=True)
    f = F(56, FONT_SUB)
    d.text((360 - f.getlength("Артём") / 2, PY0 + 300), "Артём", font=f, fill=(240, 240, 244))
    status = "Абонент недоступен" if t > 1.0 else "Вызов…"
    d.text((360 - F(32, F_REG).getlength(status) / 2, PY0 + 380), status, font=F(32, F_REG), fill=RED if t > 1.0 else (160, 166, 180))
    for i, app in enumerate(("Telegram", "WhatsApp", "ВКонтакте")):
        y = PY0 + 520 + i * 100
        if t > 1.2 + i * .4:
            d.rounded_rectangle([PX0 + 40, y, PX1 - 40, y + 80], radius=20, fill=(30, 32, 40))
            d.text((PX0 + 64, y + 22), app, font=F(30), fill=(200, 204, 214))
            d.text((PX1 - 64 - F(28).getlength("не в сети"), y + 24), "не в сети", font=F(28), fill=RED)
    hand_hold(img)
    counter_plate(img, t)
    return zoom(img, 1.04, .5, .45)


def old_s10(t, L):
    img = room_bg(.4)
    d = phone(img)
    d.ellipse([PX0 + 30, PY0 + 74, PX0 + 92, PY0 + 136], fill=(176, 138, 86))
    d.text((PX0 + 110, PY0 + 86), "artem.life", font=F(30), fill=(20, 20, 24))
    d.text((PX0 + 110, PY0 + 122), "вчера", font=F(20, F_REG), fill=(140, 140, 150))
    # фото: Артём с ключами на фоне новостройки
    ph = vgrad(PX1 - PX0, 640, (150, 190, 230), (230, 220, 200))
    pd = ImageDraw.Draw(ph)
    for k in range(6):
        pd.rectangle([20 + k * 90, 120 - (k % 2) * 40, 90 + k * 90, 640], fill=(200, 200, 206), outline=(150, 150, 160), width=3)
        for wy in range(140, 600, 50):
            pd.rectangle([34 + k * 90, wy, 76 + k * 90, wy + 30], fill=(140, 170, 200))
    fig, _ = person.figure((PX1 - PX0, 640), 250, 60, .7, "artem", "smug", (0, 0))
    ph.paste(fig, (0, 0), fig)
    img.paste(ph, (PX0, PY0 + 160))
    d = ImageDraw.Draw(img)
    d.text((PX0 + 30, PY0 + 820), "♥ 348   Новая глава. Своя квартира!", font=F(28), fill=(20, 20, 24))
    hand_hold(img)
    counter_plate(img, t)
    return zoom(img, 1.0 + .25 * min(1, t / L), .55, .4)


def old_s11(t, L):
    img = room_bg(.35)
    img = denis_bust(img, W / 2, 300, 1.45, t, "tense", (0, 0))
    glow(img, (W / 2, 1100), 300, (30, 60, 100), .8)
    counter_plate(img, t)
    return zoom(img, 1.0 + .08 * t / L, .5, .3)


def old_s12(t, L, cue):
    img = room_bg(.45)
    d = phone(img)
    d.text((PX0 + 40, PY0 + 100), "Заметки", font=F(26, F_REG), fill=(230, 170, 30))
    d.text((PX0 + 40, PY0 + 160), "ПЛАН", font=F(54, FONT_SUB), fill=(20, 20, 24))
    d.text((PX0 + 40, PY0 + 226), "вернуть 1 000 000", font=F(34), fill=(20, 20, 24))
    rows = ["1. Устроиться", "2. Узнать, кто", "3. Забрать своё"]
    p = (t - cue["12"]) / dur("12.mp3")
    for i, row in enumerate(rows):
        y = PY0 + 330 + i * 90
        if p > i * .15:
            d.text((PX0 + 40, y), row, font=F(38), fill=(20, 20, 24))
    # всё, кроме номеров, размыто — зритель не видит план
    blur = img.crop((PX0 + 90, PY0 + 320, PX1 - 20, PY0 + 620)).filter(ImageFilter.GaussianBlur(12))
    img.paste(blur, (PX0 + 90, PY0 + 320))
    hand_hold(img)
    counter_plate(img, t)
    return zoom(img, 1.04 + .1 * t / L, .5, .35)


def old_s13(t, L, cue):
    vo_end = cue["13"] + dur("13.mp3")
    img = vgrad(W, H, (20, 22, 28), (8, 8, 10))
    d = ImageDraw.Draw(img)
    pop = min(1, t / .3)
    f1, f2 = F(int(120 * (.8 + .2 * pop)), FONT_SUB), F(70, FONT_SUB)
    d.text((W / 2 - f1.getlength("347 ₽") / 2, 380), "347 ₽", font=f1, fill=RED, stroke_width=4, stroke_fill=INK)
    d.text((W / 2 - F(60).getlength("↓") / 2, 540), "↓", font=F(60), fill=(150, 150, 160))
    d.text((W / 2 - f2.getlength("1 000 000 ₽") / 2, 630), "1 000 000 ₽", font=f2, fill=GREEN, stroke_width=4, stroke_fill=INK)
    day_plate(img, "ДЕНЬ 1 ВОЗВРАТА")
    if t > vo_end + .4:
        a = min(1, (t - vo_end - .4) / .3)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f3 = F(60, FONT_SUB)
            for j, line in enumerate(("серия 2", "скоро")):
                dd.text(((W - f3.getlength(line)) / 2, 520 + j * 80), line, font=f3, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img



# =====================================================================
# Версия с экшеном: Денис двигается в кадре, телефон — всплывающая панель
# =====================================================================
import denis_rig as DR

PANEL_BOX = (PX0 - 24, PY0 - 24, PX1 + 24, PY1 + 24)


def ui(fn, t, L, cue=None):
    """рисует экран телефона старой сцены и вырезает сам телефон"""
    img = fn(t, L, cue) if fn.__code__.co_argcount >= 3 else fn(t, L)
    # старые сцены зумят кадр — рисуем без зума: временно подменяем zoom/shake
    return img


def ui_raw(fn, t, L, cue=None):
    g = fn.__globals__
    z, sh = g["zoom"], g["shake"]
    g["zoom"] = lambda im, *a, **k: im
    g["shake"] = lambda im, *a, **k: im
    try:
        img = fn(t, L, cue) if fn.__code__.co_argcount >= 3 else fn(t, L)
    finally:
        g["zoom"], g["shake"] = z, sh
    return img.crop(PANEL_BOX)


def panel(img, fn, t, L, cue=None, pos=(400, 150), w=290, t0=0.0, tilt=-4):
    """телефон-вставка: всплывает за 0.25 с, слегка наклонён, с тенью"""
    if t < t0:
        return img
    k = min(1, (t - t0) / .25)
    k = 1 - (1 - k) ** 3
    ph = ui_raw(fn, t, L, cue)
    h = int(w * ph.height / ph.width)
    sc = .6 + .4 * k
    ph = ph.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width, ph.height], radius=int(36 * sc), fill=255)
    ph.putalpha(m)
    ph = ph.rotate(tilt + 6 * (1 - k), expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", ph.size, (0, 0, 0, 0))
    shadow.putalpha(ph.getchannel("A").point(lambda v: int(v * .5)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    x, y = int(pos[0] + w * (1 - sc) / 2), int(pos[1] + h * (1 - sc) / 2)
    base = img.convert("RGBA")
    base.alpha_composite(shadow, (x + 12, y + 18))
    base.alpha_composite(ph, (x, y))
    return base.convert("RGB")


def rain(img, t, n=120, seed=4, col=(170, 184, 206), slant=-.18):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(n):
        x0, y0, sp, ln = rnd.uniform(0, W + 200), rnd.uniform(0, H), rnd.uniform(1300, 1900), rnd.uniform(30, 70)
        y = (y0 + sp * t) % (H + 100) - 50
        x = (x0 + slant * sp * t) % (W + 200) - 100
        d.line([x, y, x + slant * ln, y + ln], fill=col, width=2)


def street_bg(scroll, t):
    img = vgrad(W, H, (18, 22, 36), (30, 34, 48))
    d = ImageDraw.Draw(img)
    for layer, (sp, top, col, lit) in enumerate(((.25, 300, (30, 34, 50), (90, 84, 60)), (.6, 420, (40, 44, 58), (200, 170, 100)))):
        rnd = random.Random(layer + 1)
        x = -(scroll * sp) % 260 - 260
        k = int(scroll * sp // 260)
        while x < W + 260:
            r2 = random.Random(k * 7 + layer)
            bw, bh = r2.uniform(140, 240), r2.uniform(300, 700)
            d.rectangle([x, top + 700 - bh, x + bw, 1000], fill=col)
            for wy in range(int(top + 720 - bh), 980, 44):
                for wx in range(int(x + 14), int(x + bw - 20), 34):
                    if r2.random() < .22:
                        d.rectangle([wx, wy, wx + 16, wy + 22], fill=lit)
            x += bw + 30; k += 1
    d.rectangle([0, 1000, W, H], fill=(26, 28, 36))
    for k in range(-1, 4):   # фонари и отражения
        x = k * 300 - (scroll * .9) % 300
        d.line([x, 1000, x, 640], fill=(50, 52, 60), width=8)
        d.ellipse([x - 16, 620, x + 16, 652], fill=(255, 220, 150))
        glow(img, (x, 640), 90, (110, 90, 50), .8)
        d = ImageDraw.Draw(img)
        d.rectangle([x - 24, 1010, x + 24, 1180], fill=(70, 66, 56))
    return img


def room_night():
    img = vgrad(W, H, (44, 46, 58), (22, 24, 30))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 160, 300, 520], fill=(30, 40, 66), outline=INK, width=8)   # окно
    d.line([180, 160, 180, 520], fill=INK, width=6)
    d.rectangle([0, 1040, W, H], fill=(52, 44, 40)); d.line([0, 1040, W, 1040], fill=INK, width=5)
    d.rounded_rectangle([420, 860, 760, 1040], radius=30, fill=(70, 60, 84), outline=INK, width=5)   # диван
    return img


def stair_bg(scroll):
    img = vgrad(W, H, (120, 122, 118), (80, 82, 80))
    d = ImageDraw.Draw(img)
    for k in range(-1, 6):
        x = k * 220 - (scroll % 220)
        d.rectangle([x, 300, x + 8, 1000], fill=(90, 92, 90))
        d.rectangle([x + 60, 360, x + 160, 520], fill=(70, 90, 110), outline=INK, width=4)   # двери квартир
    d.rectangle([0, 1000, W, H], fill=(96, 92, 86)); d.line([0, 1000, W, 1000], fill=INK, width=5)
    d.rectangle([0, 160, W, 190], fill=(60, 62, 60))
    for k in range(4):
        glow(img, (k * 240 - (scroll * .5) % 240, 200), 80, (90, 90, 60), .7)
    return img


def newbuild_bg(t, lit_k=1.0):
    img = vgrad(W, H, (16, 20, 34), (34, 36, 50))
    d = ImageDraw.Draw(img)
    d.rectangle([150, 60, 600, 1000], fill=(56, 60, 74), outline=(30, 32, 40), width=6)
    for row in range(16):
        for col in range(5):
            x, y = 180 + col * 84, 90 + row * 56
            lit = (row, col) == (6, 3)
            d.rectangle([x, y, x + 50, y + 34], fill=(255, 210, 130) if lit else (38, 42, 56))
    glow(img, (457, 443), 70, (140, 100, 40), lit_k)
    d = ImageDraw.Draw(img)
    d.rectangle([310, 860, 450, 1000], fill=(200, 196, 180), outline=INK, width=4)   # подъезд
    d.rectangle([0, 1000, W, H], fill=(28, 30, 38))
    return img


DEN_X, GROUND_Y = 230, 1250


def s01(t, L, cue):
    img = street_bg(300 + t * 560, t)
    img = paste(img, DR.side((W, H), DEN_X, GROUND_Y - 60, .66, t, "run", "shock", hood_up=True))
    rain(img, t)
    img = panel(img, old_s01, t, L, cue, pos=(400, 120), w=290, t0=.15)
    corner = ImageDraw.Draw(img)
    return shake(img, t, 3)


def s02(t, L):
    img = room_night()
    img = paste(img, DR.front((W, H), 250, GROUND_Y, .82, t, ("head", "head"), "idle", "sad"))
    img = panel(img, old_s01, 99, 1, {"01": 0}, pos=(410, 170), w=270)
    counter_plate(img, t)
    return zoom(img, 1.0 + .04 * t / L, .3, .5)


def s03(t, L, cue):
    img = office_bg()
    look = t > .9
    img = paste(img, DR.front((W, H), 240, GROUND_Y, .82, t, ("down", "phone" if look else "down"), "idle",
                              "neutral", (.4, .8) if look else (0, 0), phone_hand="r" if look else None))
    if not look:   # телефон вибрирует в кармане — значок
        d = ImageDraw.Draw(img)
        vib = 6 * math.sin(t * 60)
        d.text((300 + vib, 760), "≋", font=F(60), fill=(250, 220, 90))
    img = panel(img, old_s04, cue["03"] + .01, L, {"04": cue["03"] + 99}, pos=(400, 190), w=280, t0=.9)
    day_plate(img, "ДЕНЬ 1")
    counter_plate(img, t)
    return img


def s04(t, L, cue):
    img = office_bg()
    img = paste(img, DR.front((W, H), 240, GROUND_Y, .82, t, ("down", "phone"), "idle", "neutral", (.4, .8), phone_hand="r"))
    img = panel(img, old_s04, t, L, cue, pos=(400, 150), w=290)
    counter_plate(img, t)
    return zoom(img, 1.0 + .05 * t / L, .3, .5)


def s05(t, L, cue):
    img = office_bg()
    p = (t - cue["05"]) / dur("05.mp3")
    jump = 0.0
    if .15 < p < .5:   # прыжок радости
        q = (p - .15) / .35
        jump = 110 * math.sin(q * math.pi)
    arms = ("out", "fist_up") if .1 < p < .6 else ("down", "phone")
    img = paste(img, DR.front((W, H), 250, GROUND_Y, .82, t, arms, "jump" if jump > 5 else "idle",
                              "smile" if p < .6 else "worried", (0, 0), jump=jump, phone_hand=None if arms[1] == "fist_up" else "r"))
    img = panel(img, old_s05, t, L, None, pos=(410, 140), w=280)
    counter_plate(img, t)
    return shake(img, t, 5 if .4 < p < .5 else 0)


def s06(t, L, cue):
    img = room_night()
    p = (t - cue["06"]) / dur("06.mp3")
    img = paste(img, DR.front((W, H), 240, GROUND_Y, .82, t, ("down", "phone"), "idle", "tense", (.5, .8), phone_hand="r"))
    img = panel(img, old_s06, t, L, cue, pos=(380, 120), w=310)
    day_plate(img, "ДЕНЬ 2")
    counter_plate(img, t)
    z = 1.0 + .12 * min(1, p / .55)   # наезд к нажатию
    img = zoom(img, z, .7, .4)
    return shake(img, t, 9 if .55 < p < .62 else 0)


def s07(t, L, cue):
    img = room_night()
    tilt = math.sin(t * 5) * .8   # мотает головой — не беру
    img = paste(img, DR.front((W, H), 240, GROUND_Y, .82, t, ("down", "phone"), "idle", "worried", (.5, .8), phone_hand="r", head_tilt=tilt))
    img = panel(img, old_s07, t, L, cue, pos=(400, 150), w=290)
    counter_plate(img, t)
    return img


def s08(t, L, cue):
    img = room_night()
    p = (t - cue["08"]) / dur("08.mp3")
    if p < .45:
        arms, expr, hold = ("down", "phone"), "shock", "r"
    elif p < .6:
        arms, expr, hold = ("down", "wind"), "tense", "r"
    elif p < .7:
        arms, expr, hold = ("down", "release"), "tense", None
    else:
        arms, expr, hold = ("head", "head"), "shock", None
    img = paste(img, DR.front((W, H), 260, GROUND_Y, .82, t, arms, "idle", expr, (0, 0), phone_hand=hold))
    if p >= .6:   # телефон летит на диван
        q = min(1, (p - .6) / .2)
        x, y = 470 + 160 * q, 330 + 560 * q - 300 * math.sin(q * math.pi)
        ph = Image.new("RGBA", (60, 100), (0, 0, 0, 0))
        ImageDraw.Draw(ph).rounded_rectangle([0, 0, 59, 99], radius=10, fill=(24, 24, 28), outline=INK, width=3)
        ph = ph.rotate(720 * q, expand=True)
        img.paste(ph, (int(x), int(y)), ph)
    if p < .62:
        img = panel(img, old_s08, t, L, None, pos=(400, 150), w=290)
    day_plate(img, "ДЕНЬ 3")
    counter_plate(img, t)
    return shake(img, t, 10 if .68 < p < .78 else 0)


def s09(t, L):
    img = room_night()
    x = 250 + 120 * math.sin(t * 1.6)   # мечется по комнате
    img = paste(img, DR.front((W, H), x, GROUND_Y, .82, t, ("down", "ear"), "walk", "worried", (0, 0), phone_hand="r"))
    img = panel(img, old_s09, t, L, None, pos=(420, 170), w=270)
    counter_plate(img, t)
    return img


def s10(t, L):
    img = room_night()
    img = paste(img, DR.front((W, H), 220, GROUND_Y, .82, t, ("down", "phone"), "idle", "shock" if t > 1.2 else "tense", (.5, .8), phone_hand="r"))
    img = panel(img, old_s10, t, L, None, pos=(360, 110), w=330)
    counter_plate(img, t)
    return zoom(img, 1.0 + .06 * t / L, .6, .4)


def s11(t, L):
    img = stair_bg(t * 520)
    img = paste(img, DR.side((W, H), 300, GROUND_Y - 40, .7, t, "run", "tense"))
    counter_plate(img, t)
    return shake(img, t, 3)


def s12(t, L, cue):
    img = newbuild_bg(t)
    img = paste(img, DR.front((W, H), 200, GROUND_Y + 10, .78, t, ("down", "phone"), "idle", "tense", (0, -1), phone_hand="r"))
    rain(img, t, n=90)
    img = panel(img, old_s12, t, L, cue, pos=(420, 520), w=260, tilt=4)
    counter_plate(img, t)
    return zoom(img, 1.0 + .05 * t / L, .3, .5)


def s13(t, L, cue):
    vo_end = cue["13"] + dur("13.mp3")
    img = newbuild_bg(t)
    k = min(1, t / max(1, vo_end))
    img = paste(img, DR.side((W, H), 80 + 230 * k, GROUND_Y + 10, .78, t, "walk", "tense"))
    rain(img, t, n=90)
    d = ImageDraw.Draw(img)
    f1, f2 = F(96, FONT_SUB), F(56, FONT_SUB)
    d.text((W / 2 - f1.getlength("347 ₽") / 2, 250), "347 ₽", font=f1, fill=RED, stroke_width=5, stroke_fill=INK)
    d.text((W / 2 - f2.getlength("→ 1 000 000 ₽") / 2, 370), "→ 1 000 000 ₽", font=f2, fill=GREEN, stroke_width=4, stroke_fill=INK)
    day_plate(img, "ДЕНЬ 1 ВОЗВРАТА")
    if t > vo_end + .4:
        a = min(1, (t - vo_end - .4) / .3)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f3 = F(60, FONT_SUB)
            for j, line in enumerate(("серия 2", "скоро")):
                dd.text(((W - f3.getlength(line)) / 2, 520 + j * 80), line, font=f3, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    c06 = span("s06")[0] + 0.05
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .4, c06 + dur("06.mp3") * .58, span("s08")[0] + .05 + dur("08.mp3") * .7,
              span("s10")[0] + 1.2, span("s12")[0] + span("s12")[1] - .6])
