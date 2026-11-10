"""«365 ДНЕЙ». Серия 1. Гибрид: готовые 3D-фоны (кухня, комната, улица) + рисованные яма, гараж, свалка.
Герой знает, что через год — конец света. Нужен бункер на семью из 4 человек. Денег — ноль.
Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, os.path.join(ROOT, "million", "render"))
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import denis_rig as DR

LINES = {
    "01": "Мне пришло сообщение. С моего же номера. «Через триста шестьдесят пять дней — конец. Строй бункер».",
    "02": "Я бы посмеялся. Но там было написано, что завтра в два часа дня во всём районе погаснет свет. Погас. Минута в минуту.",
    "03": "Нас четверо: я, жена, сын и тёща. Тёща сказала, что я сошёл с ума. Жена промолчала. Это хуже.",
    "04": "Готовый бункер на четверых стоит от пяти миллионов. У меня на карте — ноль. И старый гараж.",
    "05": "Правило первое: бункер — это не стены. Это воздух, вода и еда на год. Стены — потом.",
    "06": "Человек с лопатой выкапывает около кубометра земли в день. Мне нужно шестьдесят. Два месяца без выходных.",
    "07": "День первый. Лопату я одолжил у соседа. Он спросил — зачем. Я сказал — погреб.",
    "08": "Бетон — дорого. Но на свалке за городом лежат списанные морские контейнеры. Сталь. Бесплатно — если вывезти до утра.",
    "09": "День сороковой. Яма готова. Контейнер на месте. Я впервые поверил, что успею.",
    "10": "А ночью из стены ямы раздался стук. Кто-то копал. С той стороны.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.3)], 0.25) for k in LINES]
PLAN[0] = ("s01", [("01", 0.4)], 0.3)
PLAN[-1] = ("s10", [("10", 0.1)], 4.4)
setup(LINES, PLAN)

F = lambda sz, f=FONT_B: ImageFont.truetype(f, sz)
ORANGE, CYAN, RED, GREEN = (250, 170, 60), (120, 210, 255), (255, 96, 86), (110, 230, 140)
BLUEPR, GRID = (16, 28, 48), (34, 52, 80)
GY = 1250
FR_M = os.path.join(ROOT, "million", "render3d", "frames_bg")
FR_B = os.path.join(ROOT, "babushka", "frames_bg")
_cache = {}


def bg(path, bright=1.0, blur=0):
    key = (path, bright, blur)
    if key not in _cache:
        im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
        im = ImageEnhance.Brightness(im).enhance(bright)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        _cache[key] = im
    return _cache[key].copy()


ROOM_N = os.path.join(FR_M, "e3_s10_0000.png")
STREET = os.path.join(FR_M, "e2_s08_0000.png")
KITCHEN = os.path.join(FR_B, "b1_kitchen_0000.png")


def char(img, fig, tint=None):
    a = fig.getchannel("A")
    bb = a.getbbox()
    if bb:
        x0, y0, x1, y1 = bb
        sh = Image.new("L", (W, H), 0)
        cx, w = (x0 + x1) / 2, (x1 - x0) * .55
        ImageDraw.Draw(sh).ellipse([cx - w, y1 - 16, cx + w, y1 + 18], fill=140)
        img.paste(Image.new("RGB", (W, H)), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    if tint:
        R, G, B = fig.convert("RGB").split()
        fig = Image.merge("RGBA", (R.point(lambda v: int(v * tint[0])), G.point(lambda v: int(v * tint[1])), B.point(lambda v: int(v * tint[2])), a))
    img.paste(fig, (0, 0), fig)
    return img


def person(img, who, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, tint=None, phone=None, legs="idle", **kw):
    DR.use(who, **kw)
    return char(img, DR.front((W, H), x, ground, s, t, arms, legs, expr, look, phone_hand=phone), tint)


def me(img, x, s, t, arms=("down", "down"), expr="neutral", look=(0, 0), ground=GY, tint=None, phone=None, legs="idle"):
    return person(img, "denis", x, s, t, arms, expr, look, ground, tint, phone, legs)


def L2S(ox, ground, s, x, y):
    return (ox + x * s, ground - 962 * s + y * s)


def hud(img, days, money="0 ₽"):
    """постоянные счётчики сериала: дни до конца и бюджет"""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([420, 26, 700, 104], radius=14, fill=(14, 12, 12), outline=(110, 60, 50), width=2)
    d.text((436, 32), "ДО КОНЦА", font=F(18), fill=(200, 150, 140))
    d.text((436, 54), f"{days} дн", font=F(36, FONT_SUB), fill=RED)
    d.text((586, 32), "БЮДЖЕТ", font=F(18), fill=(200, 150, 140))
    d.text((586, 54), money, font=F(36, FONT_SUB), fill=ORANGE)
    f = F(26, FONT_SUB)
    d.rounded_rectangle([30, 30, 60 + f.getlength("365 ДНЕЙ"), 80], radius=10, fill=(14, 12, 12))
    d.text((44, 38), "365 ДНЕЙ", font=f, fill=RED)


def tag(img, title, sub, y=1090, col=ORANGE):
    d = ImageDraw.Draw(img)
    f1, f2 = F(30, FONT_SUB), F(18)
    w = max(f1.getlength(title), f2.getlength(sub)) + 40
    d.rounded_rectangle([30, y, 30 + w, y + 74], radius=8, fill=(14, 14, 16))
    d.rectangle([30, y, 36, y + 74], fill=col)
    d.text((48, y + 6), title, font=f1, fill=(255, 255, 255))
    d.text((48, y + 44), sub, font=f2, fill=(160, 160, 166))


def blueprint(title=None):
    img = Image.new("RGB", (W, H), BLUEPR)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        d.line([x, 0, x, H], fill=GRID)
    for y in range(0, H, 40):
        d.line([0, y, W, y], fill=GRID)
    if title:
        f = F(54, FONT_SUB)
        d.text(((W - f.getlength(title)) / 2, 170), title, font=f, fill=ORANGE)
        d.line([(W - f.getlength(title)) / 2, 240, (W + f.getlength(title)) / 2, 240], fill=ORANGE, width=4)
    return img


def phone_screen(img, t, msgs, y=330):
    """крупный экран телефона с сообщениями"""
    d = ImageDraw.Draw(img)
    x0, x1, y1 = 120, 600, y + 620
    d.rounded_rectangle([x0, y, x1, y1], radius=40, fill=(16, 16, 20), outline=(60, 60, 66), width=8)
    d.rounded_rectangle([x0 + 20, y + 24, x1 - 20, y1 - 24], radius=26, fill=(236, 236, 240))
    d.text((x0 + 44, y + 44), "Отправитель:", font=F(20), fill=(120, 120, 126))
    d.text((x0 + 44, y + 70), "МОЙ НОМЕР", font=F(30, FONT_SUB), fill=RED)
    yy = y + 140
    for m in msgs:
        lines = m.split("\n")
        h = 40 + 34 * len(lines)
        d.rounded_rectangle([x0 + 40, yy, x1 - 40, yy + h], radius=18, fill=(220, 222, 230))
        for i, ln in enumerate(lines):
            d.text((x0 + 60, yy + 18 + i * 34), ln, font=F(26), fill=(20, 20, 24))
        yy += h + 20


def dirt(w=W, h=H, seed=4, top=(120, 92, 66), bottom=(70, 52, 38)):
    img = vgrad(w, h, top, bottom)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(260):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(3, 12)
        c = rnd.choice(((96, 74, 54), (140, 110, 80), (80, 64, 50)))
        d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=c)
    return img


def shovel(d, x, y, s=1.0, ang=-.3):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    d.line([P(0, -260), P(0, 120)], fill=(150, 104, 60), width=int(14 * s))
    d.line([P(-40, -260), P(40, -260)], fill=(150, 104, 60), width=int(14 * s))
    d.polygon([P(-46, 110), P(46, 110), P(40, 220), P(0, 260), P(-40, 220)], fill=(150, 156, 164), outline=INK)


def container(d, x0, y0, x1, y1, col=(170, 70, 50)):
    d.rectangle([x0, y0, x1, y1], fill=col, outline=INK, width=4)
    for x in range(int(x0) + 16, int(x1) - 8, 22):
        d.line([x, y0 + 8, x, y1 - 8], fill=tuple(int(c * .75) for c in col), width=6)
    rnd = random.Random(int(x0))
    for _ in range(14):   # ржавчина
        x, y, r = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(6, 20)
        d.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(120, 60, 34))


# ---------- сцены ----------
def s01(t, L, cue):   # ночь, телефон вибрирует в руке
    img = bg(ROOM_N, .7)
    img = me(img, 470, .9, t, ("phone", "down"), "shock" if t > 2 else "neutral", (-.4, .4), phone="l", tint=(.75, .8, 1.0))
    glow(img, (330, 760), 120, (160, 200, 255), .6)
    p = (t - cue["01"]) / dur("01.mp3")
    if p > .12:
        msgs = ["Через 365 дней —\nконец."]
        if p > .7:
            msgs.append("Строй бункер.")
        phone_screen(img, t, msgs, 300)
    hud(img, 365)
    return shake(img, t, 4 if t < .5 else 0)


def s02(t, L, cue):   # свет гаснет минута в минуту
    p = (t - cue["02"]) / dur("02.mp3")
    off = p > .78
    img = bg(STREET, .35 if off else 1.0)
    if off:
        img = Image.blend(img, Image.new("RGB", (W, H)), .5)
    img = me(img, 360, .8, t, ("phone", "down"), "shock" if off else "neutral", (0, -.4), phone="l",
             tint=(.45, .45, .55) if off else (.8, .8, .95))
    if p < .78:
        phone_screen(img, t, ["Завтра 14:00 —\nв районе\nпогаснет свет."], 260)
    tag(img, "14:00" if off else "13:59", "минута в минуту" if off else "завтра", 1090, RED)
    hud(img, 364)
    return shake(img, t, 6 if .78 < p < .84 else 0)


def s03(t, L, cue):   # семья на кухне
    p = (t - cue["03"]) / dur("03.mp3")
    img = bg(KITCHEN, 1.0)
    img = person(img, "babushka", 110, .62, t, ("down", "down") if p < .45 else ("out", "down"), "shock" if p > .45 else "neutral", (1, 0), hoodie=False)
    img = person(img, "host", 280, .66, t, ("down", "down"), "sad" if p > .7 else "neutral", (1, 0), hoodie=False)
    img = person(img, "vnuk", 440, .64, t, ("down", "down"), "neutral", (1, 0))
    img = me(img, 610, .7, t, ("out", "down"), "worried", (-1, 0))
    d = ImageDraw.Draw(img)
    for x, n in ((110, "ТЁЩА"), (280, "ЖЕНА"), (440, "СЫН"), (610, "Я")):
        f = F(24, FONT_SUB)
        d.rounded_rectangle([x - f.getlength(n) / 2 - 12, 500, x + f.getlength(n) / 2 + 12, 540], radius=8, fill=(14, 14, 16))
        d.text((x - f.getlength(n) / 2, 506), n, font=f, fill=(255, 255, 255))
    if p > .45:
        tag(img, "тёща", "«ты сошёл с ума»", 1090, RED)
    hud(img, 363)
    return img


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = blueprint("БУНКЕР НА 4")
    d = ImageDraw.Draw(img)
    f = F(84, FONT_SUB)
    d.text((W / 2 - f.getlength("5 000 000 ₽") / 2, 340), "5 000 000 ₽", font=f, fill=CYAN)
    if p > .5:
        d.text((W / 2 - F(40, FONT_SUB).getlength("У МЕНЯ") / 2, 560), "У МЕНЯ", font=F(40, FONT_SUB), fill=(200, 200, 206))
        f2 = F(150, FONT_SUB)
        d.text((W / 2 - f2.getlength("0 ₽") / 2, 620), "0 ₽", font=f2, fill=RED)
    if p > .8:   # гараж
        cx, cy = W / 2, 1000
        d.polygon([(cx - 160, cy), (cx, cy - 90), (cx + 160, cy), (cx + 160, cy + 140), (cx - 160, cy + 140)], outline=ORANGE, width=6)
        d.rectangle([cx - 100, cy + 30, cx + 100, cy + 140], outline=ORANGE, width=6)
        d.text((cx + 180, cy + 60), "гараж", font=F(34, FONT_SUB), fill=ORANGE)
    hud(img, 362)
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = blueprint("ПРАВИЛО №1")
    d = ImageDraw.Draw(img)
    items = (("ВОЗДУХ", CYAN, .3), ("ВОДА", (90, 170, 255), .45), ("ЕДА · 1 ГОД", GREEN, .6))
    for i, (txt, col, show) in enumerate(items):
        if p > show:
            y = 360 + i * 160
            d.rounded_rectangle([110, y, 610, y + 120], radius=20, outline=col, width=6)
            f = F(54, FONT_SUB)
            d.text((W / 2 - f.getlength(txt) / 2, y + 30), txt, font=f, fill=col)
    if p > .85:
        f = F(40, FONT_SUB)
        d.text((W / 2 - f.getlength("стены — потом") / 2, 880), "стены — потом", font=f, fill=(200, 200, 206))
    hud(img, 361)
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    img = blueprint("ЗЕМЛЯНЫЕ РАБОТЫ")
    d = ImageDraw.Draw(img)
    # куб земли
    cx, cy, a = W / 2, 470, 110
    d.polygon([(cx - a, cy), (cx, cy - a * .5), (cx + a, cy), (cx, cy + a * .5)], outline=ORANGE, width=5)
    d.line([cx - a, cy, cx - a, cy + a, cx, cy + a * 1.5, cx + a, cy + a, cx + a, cy], fill=ORANGE, width=5)
    d.line([cx, cy + a * .5, cx, cy + a * 1.5], fill=ORANGE, width=5)
    f = F(44, FONT_SUB)
    d.text((W / 2 - f.getlength("1 м³ / день") / 2, 680), "1 м³ / день", font=f, fill=ORANGE)
    if p > .45:
        f2 = F(90, FONT_SUB)
        d.text((W / 2 - f2.getlength("× 60") / 2, 780), "× 60", font=f2, fill=CYAN)
    if p > .7:
        f3 = F(56, FONT_SUB)
        d.text((W / 2 - f3.getlength("= 2 месяца") / 2, 930), "= 2 месяца", font=f3, fill=RED)
    hud(img, 360)
    return img


def garage_day(t):
    img = vgrad(W, H, (150, 190, 230), (220, 230, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 820, W, H], fill=(120, 110, 96))
    d.polygon([(60, 820), (60, 420), (380, 360), (380, 820)], fill=(150, 150, 146), outline=INK)   # гараж
    d.rectangle([110, 520, 340, 820], fill=(90, 96, 100), outline=INK, width=4)
    for y in range(540, 820, 30):
        d.line([110, y, 340, y], fill=(70, 74, 80), width=3)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    img = garage_day(t)
    d = ImageDraw.Draw(img)
    shovel(d, 600, 1000, 1.0, -.25)
    img = person(img, "artem", 470, .66, t, ("down", "down"), "smug" if p > .5 else "neutral", (-1, 0))
    img = me(img, 240, .7, t, ("out", "down"), "smile" if p > .75 else "neutral", (1, 0))
    tag(img, "ДЕНЬ 1", "лопата — в долг · «погреб»", 1090)
    if p > .45:
        tag(img, "СОСЕД", "«зачем?»", 150, CYAN)
    hud(img, 364)
    return img


def s08(t, L, cue):
    img = vgrad(W, H, (14, 18, 34), (30, 26, 30))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    for _ in range(80):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 500)
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(200, 200, 210))
    d.rectangle([0, 1000, W, H], fill=(40, 36, 34))
    container(d, -40, 700, 400, 880, (60, 90, 120))
    container(d, 260, 520, 760, 700, (170, 70, 50))
    container(d, 330, 820, 780, 1000, (70, 110, 80))
    img = me(img, 180, .6, t, ("out", "down"), "tense", (1, 0), ground=1180, tint=(.6, .65, .85))
    lay = Image.new("L", (W, H), 0)   # луч фонаря
    ImageDraw.Draw(lay).polygon([(220, 760), (560, 620), (620, 980)], fill=80)
    img.paste(Image.new("RGB", (W, H), (255, 240, 200)), (0, 0), lay.filter(ImageFilter.GaussianBlur(20)))
    tag(img, "свалка · 03:40", "бесплатно — до утра", 1090)
    hud(img, 345)
    return img


def pit(img, t, cont=True, night=False):
    d = ImageDraw.Draw(img)
    top = 440
    d.rectangle([0, 0, W, top], fill=(20, 24, 40) if night else (150, 190, 230))
    d.rectangle([0, top - 20, W, top], fill=(70, 110, 60))
    d.rectangle([110, top, 610, 1180], fill=(40, 30, 24))   # сама яма
    if cont:
        container(d, 140, 760, 580, 1170, (170, 70, 50))
        d.rectangle([330, 860, 400, 1050], fill=(30, 30, 34), outline=INK, width=4)   # дверь
    d.line([560, top - 40, 520, 1170], fill=(150, 104, 60), width=10)   # лестница
    d.line([600, top - 40, 560, 1170], fill=(150, 104, 60), width=10)
    for k in range(12):
        y = top + k * 62
        d.line([560 - k * 3.3, y, 600 - k * 3.3, y], fill=(150, 104, 60), width=8)


def s09(t, L, cue):
    img = dirt()
    pit(img, t)
    img = me(img, 300, .5, t, ("fist_up", "down"), "smile", (0, -.3), ground=750)
    tag(img, "ДЕНЬ 40", "яма · 60 м³ · контейнер", 1090, GREEN)
    hud(img, 325)
    return img


def s10(t, L, cue):
    vo_end = cue["10"] + dur("10.mp3")
    p = (t - cue["10"]) / dur("10.mp3")
    img = dirt(seed=9, top=(60, 46, 34), bottom=(30, 22, 18))
    img = Image.blend(img, Image.new("RGB", (W, H)), .35)
    lay = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lay).ellipse([140, 300, 640, 900], fill=120)
    img.paste(Image.new("RGB", (W, H), (255, 236, 190)), (0, 0), lay.filter(ImageFilter.GaussianBlur(60)))
    knocks = [cue["10"] + dur("10.mp3") * .35 + k * .55 for k in range(3)] + [vo_end + .4 + k * .5 for k in range(3)]
    hit = any(0 <= t - k < .15 for k in knocks)
    d = ImageDraw.Draw(img)
    n = sum(t > k for k in knocks)
    rnd = random.Random(1)
    for i in range(n * 6):   # осыпается земля
        x = 390 + rnd.uniform(-60, 60)
        y = 600 + ((t * 300 + i * 40) % 500)
        d.ellipse([x - 5, y - 4, x + 5, y + 4], fill=(110, 86, 60))
    if n:
        r = 40 + n * 14
        d.ellipse([390 - r, 600 - r * .7, 390 + r, 600 + r * .7], outline=(20, 14, 10), width=6)
    img = me(img, 140, 1.0, t, ("out", "down"), "shock", (1, 0), ground=1500, tint=(.8, .74, .62))
    hud(img, 325)
    img = shake(img, t, 9 if hit else 0)
    if t > vo_end + 2.2:
        a = min(1, (t - vo_end - 2.2) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(40, FONT_SUB), F(64, FONT_SUB), F(30, FONT_SUB)
            dd.text(((W - f1.getlength("365 ДНЕЙ")) / 2, 450), "365 ДНЕЙ", font=f1, fill=RED)
            dd.text(((W - f2.getlength("ДО КОНЦА: 325")) / 2, 510), "ДО КОНЦА: 325", font=f2, fill=(240, 240, 244))
            if t > vo_end + 3.0:
                q = "кто копает навстречу?"
                dd.text(((W - f3.getlength(q)) / 2, 620), q, font=f3, fill=(200, 200, 206))
    return img


if __name__ == "__main__":
    s10_knocks = [span("s10")[0] + .1 + dur("10.mp3") * .35 + k * .55 for k in range(3)]
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=s10_knocks + [span("s10")[0] + .1 + dur("10.mp3") + .4 + k * .5 for k in range(3)],
        hits=[span("s02")[0] + .05 + dur("02.mp3") * .78])
