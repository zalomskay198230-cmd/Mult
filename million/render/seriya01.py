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


def s01(t, L, cue):
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


def s02(t, L):
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


def s03(t, L):
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


def s04(t, L, cue):
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


def s05(t, L):
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


def s06(t, L, cue):
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


def s07(t, L, cue):
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


def s08(t, L):
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


def s09(t, L):
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


def s10(t, L):
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


def s11(t, L):
    img = room_bg(.35)
    img = denis_bust(img, W / 2, 300, 1.45, t, "tense", (0, 0))
    glow(img, (W / 2, 1100), 300, (30, 60, 100), .8)
    counter_plate(img, t)
    return zoom(img, 1.0 + .08 * t / L, .5, .3)


def s12(t, L, cue):
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


def s13(t, L, cue):
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


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .4, span("s08")[0] + .9, span("s10")[0] + .3, span("s12")[0] + span("s12")[1] - .6])
