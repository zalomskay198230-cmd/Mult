"""«БЕЗ СВЕТА». Серия 1. Во всём мире отключили электричество. Плоский 2D от первого лица.
Таймер — время без света. Холодный старт: город гаснет. Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, os.path.join(ROOT, "den365", "render"))
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(ROOT, "morg", "tts", "s01"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("morg_s01", os.path.join(ROOT, "morg", "render", "seriya01.py"))
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)          # субтитры, плашки, карточки выбора, фонарь
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter
import flatworld as FW
from flatworld import SD, chibi, OUT

W, H, K, F = M.W, M.H, M.K, M.F
RED, YEL, WHITE = M.RED, M.YEL, M.WHITE
FW.CHAR["hero"] = dict(skin=(236, 192, 160), hair=(40, 32, 30), top=(70, 74, 90), pants=(40, 46, 60), shoes=(230, 230, 232), style="short")
for i, (top, hair, st) in enumerate((((200, 80, 60), (90, 60, 40), "short"), ((70, 150, 110), (220, 190, 110), "long"),
                                     ((150, 110, 190), (40, 30, 30), "spiky"), ((230, 180, 60), (60, 50, 40), "bald"))):
    FW.CHAR[f"p{i}"] = dict(skin=(232, 190, 156), hair=hair, top=top, pants=(50, 56, 72), shoes=(40, 40, 44), style=st)

LINES = {
    "01": "В четырнадцать ноль семь погасло ^всё^. Во всём *мире*.",
    "02": "Телефон — ^ноль^ сети. Машины на дороге — ^встали^.",
    "03": "*Девятый* этаж. Лифт стоит. Из крана — ^тишина^.",
    "04": "Карта ^не^ ^проходит^. Наличных — *двести* рублей.",
    "05": "Час *первый*. Соседи ещё смеются.",
    "06": "Час *шестой*. У магазина — очередь до ^угла^.",
    "07": "Час *двенадцатый*. Весь город — ^чёрный^. Ни одного окна.",
    "08": "И только на крыше соседней многоэтажки горит *свет*. Кто-то ^знал^ заранее.",
    "09": "Сидеть дома с запасом на два дня — или идти к *свету*? ^Решай^. И отправь другу — он бы пошёл?",
}
PLAN = [(f"e{k}", [(k, 0.04)], 0.12) for k in LINES]
PLAN[0] = ("e01", [("01", 0.0)], 0.15)
PLAN[-1] = ("e09", [("09", 0.05)], 1.0)
setup(LINES, PLAN)
HOURS = {"e01": 0, "e02": 0, "e03": 0, "e04": 0, "e05": 1, "e06": 6, "e07": 12, "e08": 12, "e09": 12}


def blackout_timer(img, name, t):
    h = HOURS[name]
    tot = h * 3600 + int(t * 37) % 3600 if h else int(t * 11)
    txt = f"БЕЗ СВЕТА  {tot // 3600:02d}:{tot // 60 % 60:02d}:{tot % 60:02d}"
    d = ImageDraw.Draw(img)
    f = F(24, FONT_SUB)
    w = f.getlength(txt) + 30
    d.rounded_rectangle([W / 2 - w / 2, 40, W / 2 + w / 2, 82], radius=10, fill=(14, 10, 10), outline=(180, 40, 40), width=2)
    d.text((W / 2 - f.getlength(txt) / 2, 49), txt, font=f, fill=(255, 210, 200))


def city(lit=1.0, night=0.0, roof_light=False, seed=5):
    """панорама города: lit — доля горящих окон, night — темнота неба"""
    img = Image.new("RGB", (W * K, H * K))
    d = SD(img, 0, 0, K)
    top = tuple(int(a + (b - a) * night) for a, b in zip((120, 160, 210), (6, 8, 16)))
    bot = tuple(int(a + (b - a) * night) for a, b in zip((230, 200, 170), (14, 16, 26)))
    for y in range(0, 900, 4):
        k = y / 900
        d.rectangle([0, y, W, y + 4], fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    if night > .5:
        rnd = random.Random(1)
        for _ in range(120):
            x, y = rnd.uniform(0, W), rnd.uniform(0, 600)
            d.ellipse([x - 1.2, y - 1.2, x + 1.2, y + 1.2], fill=(220, 220, 236))
    rnd = random.Random(seed)
    for layer, (col, hmin, hmax, base) in enumerate((((50, 56, 76), 260, 520, 900), ((32, 36, 50), 300, 640, 1000))):
        x = -20
        while x < W:
            w, h = rnd.randint(70, 140), rnd.randint(hmin, hmax)
            c = tuple(int(v * (1 - .5 * night)) for v in col)
            d.rectangle([x, base - h, x + w, base], fill=c)
            for wy in range(base - h + 16, base - 20, 28):
                for wx in range(x + 10, x + w - 14, 20):
                    on = rnd.random()
                    if on < .5 * lit:
                        d.rectangle([wx, wy, wx + 10, wy + 14], fill=(250, 210, 120))
                    elif on < .5:
                        d.rectangle([wx, wy, wx + 10, wy + 14], fill=(20, 22, 30))
            x += w + rnd.randint(2, 18)
    if roof_light:
        d.rectangle([520, 380, 640, 1000], fill=(20, 22, 30))
        d.rectangle([570, 360, 590, 380], fill=(60, 60, 66))
    d.rectangle([0, 1000, W, H], fill=tuple(int(v * (1 - .6 * night)) for v in (60, 62, 70)))
    img = M.done(img)
    if roof_light:
        img = img.copy()
        from toonlib import glow
        glow(img, (580, 352), 80, (255, 230, 160), 1.0)
        glow(img, (580, 352), 24, (255, 255, 230), 1.0)
    return img


def window_frame(img):
    """рама окна квартиры поверх города — вид изнутри"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=(30, 26, 26)); d.rectangle([0, 1120, W, H], fill=(30, 26, 26))
    d.rectangle([0, 0, 40, H], fill=(30, 26, 26)); d.rectangle([W - 40, 0, W, H], fill=(30, 26, 26))
    d.rectangle([W / 2 - 14, 0, W / 2 + 14, H], fill=(36, 32, 32))
    d.rectangle([0, 600, W, 624], fill=(36, 32, 32))
    return img


def phone_big(img, t, a=1.0, signal=False):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 170, 300, 550, 980
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(20, 20, 24), outline=(70, 70, 76), width=6)
    d.rounded_rectangle([x0 + 16, y0 + 22, x1 - 16, y1 - 22], radius=26, fill=(36, 40, 52))
    d.text((x0 + 40, y0 + 40), "14:07", font=F(40, FONT_SUB), fill=WHITE)
    for i in range(4):   # пустые палочки сети
        d.rectangle([x1 - 120 + i * 20, y0 + 70 - i * 10, x1 - 108 + i * 20, y0 + 80], outline=(150, 150, 160), width=2)
    d.text((x0 + 40, y0 + 110), "Нет сети", font=F(28, FONT_SUB), fill=(255, 110, 100))
    d.rectangle([x1 - 90, y0 + 40, x1 - 40, y0 + 62], outline=(150, 150, 160), width=2)
    d.rectangle([x1 - 88, y0 + 42, x1 - 80, y0 + 60], fill=(255, 90, 80))   # батарея на исходе
    f = F(30, FONT_SUB)
    for i, ln in enumerate(("Звонок не удался", "SOS недоступен")):
        d.rounded_rectangle([x0 + 34, y0 + 300 + i * 90, x1 - 34, y0 + 370 + i * 90], radius=14, fill=(54, 58, 72))
        d.text((x0 + 54, y0 + 318 + i * 90), ln, font=F(24, FONT_SUB), fill=(230, 230, 236))
    return Image.blend(img, lay, a)


# ---------- сцены ----------
def e01(t, L, cue):   # холодный старт: город гаснет кварталами
    p = (t - cue["01"]) / dur("01.mp3")
    lit = 1.0 if p < .35 else max(0, 1 - (p - .35) / .25)
    img = city(lit=lit, night=.55)
    if p > .35:
        M.big(img, "ПОГАСЛО ВСЁ", 220, RED, 90)
    blackout_timer(img, "e01", 0 if p < .35 else t)
    return shake(img, t, 6 if .35 < p < .45 else 0)


def e02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    if p < .5:
        img = Image.new("RGB", (W, H), (14, 14, 18))
        img = phone_big(img, t)
    else:   # дорога: машины встали, светофоры мёртвые
        img = Image.new("RGB", (W * K, H * K))
        d = SD(img, 0, 0, K)
        d.rectangle([0, 0, W, H], fill=(150, 170, 196))
        d.rectangle([0, 640, W, H], fill=(70, 72, 80))
        for x in range(0, W, 120):
            d.rectangle([x, 900, x + 60, 912], fill=(220, 220, 210))
        rnd = random.Random(4)
        for i in range(7):
            x, y = (i % 4) * 190 - 40, 760 + (i // 4) * 260
            col = rnd.choice(((200, 60, 50), (60, 110, 180), (230, 230, 226), (60, 140, 90)))
            d.rounded_rectangle([x, y, x + 170, y + 80], radius=18, fill=col, outline=OUT, width=3)
            d.rounded_rectangle([x + 30, y - 40, x + 140, y + 10], radius=14, fill=col, outline=OUT, width=3)
            for wx in (x + 34, x + 136):
                d.ellipse([wx - 18, y + 62, wx + 18, y + 98], fill=(26, 26, 30))
        d.rectangle([600, 300, 616, 640], fill=(50, 52, 58))
        d.rounded_rectangle([576, 300, 640, 460], radius=10, fill=(30, 30, 34))
        for k in range(3):
            d.ellipse([590, 314 + k * 48, 626, 350 + k * 48], fill=(60, 60, 64))   # светофор не горит
        img = M.done(img)
        M.tag(img, "ДОРОГИ ВСТАЛИ", 110, (150, 30, 30), WHITE, 30)
    blackout_timer(img, "e02", t)
    return img


def e03(t, L, cue):   # подъезд: лифт стоит, кран сухой
    p = (t - cue["03"]) / dur("03.mp3")
    img = Image.new("RGB", (W * K, H * K))
    d = SD(img, 0, 0, K)
    d.rectangle([0, 0, W, H], fill=(70, 80, 84))
    d.rectangle([180, 220, 540, 1100], fill=(130, 134, 140), outline=OUT, width=6)   # лифт
    d.line([(360, 220), (360, 1100)], fill=OUT, width=4)
    d.rounded_rectangle([580, 560, 640, 660], radius=10, fill=(40, 40, 44))
    d.ellipse([594, 592, 626, 624], fill=(70, 70, 74))   # кнопка не горит
    d.rectangle([250, 140, 470, 200], fill=(20, 20, 24))
    f = F(44, FONT_SUB)
    d.text((360 - f.getlength("— —") / 2, 146), "— —", font=f, fill=(90, 40, 40))
    img = M.done(img)
    if p > .68:   # кран — тишина
        dd = ImageDraw.Draw(img)
        dd.rectangle([0, 0, W, H], fill=(30, 34, 38))
        dd.rectangle([200, 640, 520, 700], fill=(200, 204, 210))
        dd.rectangle([330, 420, 370, 640], fill=(170, 176, 182))
        dd.rectangle([330, 420, 470, 460], fill=(170, 176, 182))
        dd.rectangle([450, 460, 470, 500], fill=(170, 176, 182))
        M.tag(img, "ВОДЫ НЕТ", 110, (40, 70, 110), WHITE, 30)
    M.tag(img, "9 ЭТАЖ", 180, (20, 22, 24), YEL, 28)
    blackout_timer(img, "e03", t)
    return img


def e04(t, L, cue):   # терминал: отказ
    p = (t - cue["04"]) / dur("04.mp3")
    img = Image.new("RGB", (W, H), (40, 44, 52))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([210, 160, 510, 560], radius=30, fill=(30, 30, 34), outline=(80, 80, 86), width=6)
    d.rectangle([240, 200, 480, 360], fill=(10, 12, 14))
    d.text((360 - F(40, FONT_SUB).getlength("ОТКАЗ") / 2, 254), "ОТКАЗ", font=F(40, FONT_SUB), fill=(255, 80, 70))
    if p > .5:
        d.rounded_rectangle([140, 620, 580, 780], radius=16, fill=(170, 200, 160), outline=OUT, width=4)
        d.text((360 - F(64, FONT_SUB).getlength("200 ₽") / 2, 660), "200 ₽", font=F(64, FONT_SUB), fill=(40, 70, 40))
    blackout_timer(img, "e04", t)
    return shake(img, t, 3 if p < .2 else 0)


def e05(t, L, cue):   # час 1: соседи во дворе смеются
    img = city(lit=0, night=.2)
    d = SD(img, 0, 0, 1)
    for i in range(4):
        chibi(d, f"p{i}", 140 + i * 150, 1180, 1.3, t, "smile", 0, arm="up" if i % 2 else None)
    M.tag(img, "ЧАС 1", 110, (20, 22, 24), YEL, 34)
    blackout_timer(img, "e05", t)
    return img


def e06(t, L, cue):   # час 6: очередь
    img = city(lit=0, night=.45)
    d = SD(img, 0, 0, 1)
    d.rectangle([420, 820, 720, 1060], fill=(150, 60, 50), outline=OUT, width=4)
    d.rectangle([440, 790, 700, 830], fill=(230, 220, 200))
    d.text((452, 794), "ПРОДУКТЫ", font=F(28, FONT_SUB), fill=(40, 30, 30))
    for i in range(9):
        chibi(d, f"p{i % 4}", 420 - i * 60, 1140 + (i % 2) * 20, .9, t + i, "sad" if i % 3 else "angry", 1)
    M.tag(img, "ЧАС 6", 110, (20, 22, 24), YEL, 34)
    blackout_timer(img, "e06", t)
    return img


def e07(t, L, cue):   # час 12: город чёрный
    img = window_frame(city(lit=0, night=1.0))
    d = SD(img, 0, 0, 1)
    M.tag(img, "ЧАС 12", 140, (20, 22, 24), YEL, 34)
    blackout_timer(img, "e07", t)
    return img


def e08(t, L, cue):   # свет на крыше
    p = (t - cue["08"]) / dur("08.mp3")
    img = city(lit=0, night=1.0, roof_light=p > .15)
    img = window_frame(img)
    img = toonlib.zoom(img, 1 + .6 * M.ease(max(0, p - .2) / .8), .78, .3)
    if p > .65:
        M.big(img, "КТО-ТО ЗНАЛ", 170, YEL, 84)
    blackout_timer(img, "e08", t)
    return img


_cards = {}


def card_art(kind):
    """мини-кадры для карточек выбора (кешируются)"""
    if kind in _cards:
        return _cards[kind]
    if kind == "home":   # тёмная квартира: окно в чёрный город, свеча на подоконнике, запасы
        img = city(lit=0, night=1.0)
        img = window_frame(img)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 900, W, H], fill=(28, 22, 20))
        d.rectangle([40, 880, W - 40, 910], fill=(70, 54, 44))   # подоконник
        for i, (x, col) in enumerate(((120, (200, 60, 50)), (220, (60, 110, 180)), (500, (230, 190, 80)))):
            d.rounded_rectangle([x, 760, x + 80, 880], radius=10, fill=col, outline=(14, 12, 12), width=4)   # банки и пачки
        d.rectangle([330, 760, 380, 880], fill=(240, 236, 220), outline=(14, 12, 12), width=3)   # свеча
        from toonlib import glow
        glow(img, (355, 735), 120, (255, 170, 70), .9)
        d = ImageDraw.Draw(img)
        d.ellipse([344, 712, 366, 750], fill=(255, 210, 110))
    else:                # к свету: город и фонарь на крыше
        img = city(lit=0, night=1.0, roof_light=True)
        img = toonlib.zoom(img, 1.6, .78, .3)
        d = ImageDraw.Draw(img)
        d.polygon([(0, H), (W, H), (W * .62, 700), (W * .5, 700)], fill=(24, 24, 30))   # дорога к дому со светом
        cx, cy = W * .5, 1010   # силуэт со спины, идёт к свету
        d.ellipse([cx - 26, cy - 160, cx + 26, cy - 108], fill=(8, 8, 12))
        d.rounded_rectangle([cx - 40, cy - 110, cx + 40, cy - 10], radius=18, fill=(8, 8, 12))
        d.rectangle([cx - 30, cy - 20, cx - 8, cy + 60], fill=(8, 8, 12))
        d.rectangle([cx + 8, cy - 30, cx + 30, cy + 48], fill=(8, 8, 12))
    _cards[kind] = img
    return img


def pretty_card(img, x0, y0, w, h, kind, num, title, col, a=1.0, pulse=0.0):
    art = card_art(kind).resize((w, int(w * H / W)), Image.LANCZOS)
    top = max(0, int(art.height * .5 - h * .42))
    art = art.crop((0, top, w, top + h))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=28, fill=255)
    lay = img.copy()
    glow_l = Image.new("RGB", (W, H))
    ImageDraw.Draw(glow_l).rounded_rectangle([x0 - 6, y0 - 6, x0 + w + 6, y0 + h + 6], radius=34, fill=tuple(int(c * (.55 + .45 * pulse)) for c in col))
    from PIL import ImageChops
    lay = ImageChops.add(lay, glow_l.filter(ImageFilter.GaussianBlur(18)))
    lay.paste(art, (x0, y0), m)
    d = ImageDraw.Draw(lay)
    # затемнение низа карточки под подпись
    shade = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(shade)
    for yy in range(h // 2, h):
        sd.line([0, yy, w, yy], fill=int(220 * (yy - h / 2) / (h / 2)))
    shade = ImageChops.multiply(shade, m)
    lay.paste((6, 6, 10), (x0, y0), shade)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=28, outline=col, width=5)
    d.ellipse([x0 + w / 2 - 34, y0 - 34, x0 + w / 2 + 34, y0 + 34], fill=col, outline=(10, 10, 14), width=5)
    fn = F(40, FONT_SUB)
    d.text((x0 + w / 2 - fn.getlength(num) / 2, y0 - 26), num, font=fn, fill=WHITE)
    f = F(30, FONT_SUB)
    for i, ln in enumerate(title.split("\n")):
        d.text((x0 + w / 2 - f.getlength(ln) / 2, y0 + h - 96 + i * 38), ln, font=f, fill=WHITE, stroke_width=3, stroke_fill=(8, 8, 10))
    return Image.blend(img, lay, a)


def e09(t, L, cue):
    bg = city(lit=0, night=1.0).filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(bg, Image.new("RGB", (W, H)), .55)
    d = ImageDraw.Draw(img)
    f = F(44, FONT_SUB)
    d.text(((W - f.getlength("ЧТО ДЕЛАТЬ?")) / 2, 170), "ЧТО ДЕЛАТЬ?", font=f, fill=WHITE, stroke_width=4, stroke_fill=(8, 8, 10))
    pulse = .5 + .5 * math.sin(t * 4)
    img = pretty_card(img, 36, 300, 310, 470, "home", "1", "Сидеть дома\nзапас на 2 дня", (90, 150, 230), min(1, t / .3), pulse)
    img = pretty_card(img, 374, 300, 310, 470, "light", "2", "Идти\nк свету", (240, 170, 60), min(1, max(0, t - .25) / .3), 1 - pulse)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 40, 495, W / 2 + 40, 575], fill=YEL, outline=(10, 10, 14), width=5)
    fi = F(24, FONT_SUB)
    d.text((W / 2 - fi.getlength("ИЛИ") / 2, 520), "ИЛИ", font=fi, fill=(20, 20, 24))
    p = (t - cue["09"]) / dur("09.mp3")
    if p > .55:
        M.big(img, "РЕШАЙ", 800, RED, 84)
    fp = F(30, FONT_SUB)
    txt = "ОТПРАВЬ ДРУГУ — ОН БЫ ПОШЁЛ?"
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 22, 1110, W / 2 + fp.getlength(txt) / 2 + 22, 1168], radius=28, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 1121), txt, font=fp, fill=(20, 20, 24))
    blackout_timer(img, "e09", t)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("e01")[0] + span("e01")[1] * .35, span("e08")[0] + span("e08")[1] * .15])
