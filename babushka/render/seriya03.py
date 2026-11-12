"""«БАБУШКУ УКУСИЛИ». Серия 3 — финал. Гибрид: 3D-фоны (babushka/frames_bg) + 2D-персонажи.
Запуск: python3 seriya03.py ../tts/s03 ../seriya03.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, os.path.join(ROOT, "million", "render"))
import toonlib

# хелперы второй серии (а через неё — первой)
_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s02"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("babushka_s02", os.path.join(HERE, "seriya02.py"))
B2 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(B2)
sys.argv[:] = _argv
B1 = B2.B1
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s03"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya03.mp4"
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import denis_rig as DR

LINES = {
    "01": "Фургон сорок семь я нашёл в шесть утра. У стадиона. Туда свозят всех укушенных.",
    "02": "Внутрь не пускали. Лекарство давали только по списку. Бабушки в списке не было.",
    "03": "Я перелез через забор. На поле — сотни людей. И все одинаково молчат.",
    "04": "Я узнал её по банке вишнёвого варенья. Она держала её двумя руками.",
    "05": "Она меня не узнала. Смотрела сквозь.",
    "06": "До конца десятых суток — четыре часа. Пункт, где колют лекарство, — на другом конце города.",
    "07": "Машин нет. Метро закрыто. Я взял её на руки и пошёл.",
    "08": "Двенадцать километров. Она молчала. А потом тихо запела. Ту самую песню, у открытого окна.",
    "09": "Мы вошли в пункт за девятнадцать минут до конца срока.",
    "10": "Укол. Час. Два. Она спала.",
    "11": "А утром я проснулся от запаха. Блинов.",
    "12b": "Сашенька, блины на плите. Не забудь выключить.",
    "13": "Я не выключил. Мы ели их вдвоём. С вишнёвым вареньем.",
    "14": "Подпишись. Скоро новая история.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.3) for k in LINES if k != "14"]
PLAN[0] = ("s01", [("01", 0.3)], 0.3)
PLAN[-1] = ("s13", [("13", 0.1), ("14", 1.0 + 0.1)], 1.6)
setup(LINES, PLAN)
# «14» стартует через секунду после конца «13»: пересчитаем таймлайн с точной задержкой
_d13 = dur("13.mp3")
PLAN[-1] = ("s13", [("13", 0.1), ("14", 0.1 + _d13 + 1.1)], 1.6)
setup(LINES, PLAN)

F, GY = B1.F, B1.GY
bg, char, sasha, patrol, plate, steam, window = B1.bg, B1.char, B1.sasha, B1.patrol, B1.plate, B1.steam, B1.window
babushka, van = B2.babushka, B2.van


def clock(img, txt, y=150, col=(240, 70, 80)):
    d = ImageDraw.Draw(img)
    f = F(56, FONT_SUB)
    w = f.getlength(txt)
    d.rounded_rectangle([W - w - 80, y, W - 30, y + 80], radius=16, fill=(14, 14, 18), outline=col, width=4)
    d.text((W - w - 55, y + 10), txt, font=f, fill=(255, 255, 255))


def crowd(img, t, n=26, y0=900, seed=4, scale=.36):
    """молчащая толпа укушенных на поле"""
    rnd = random.Random(seed)
    pts = sorted([(rnd.uniform(-40, W + 40), y0 + rnd.uniform(0, 300)) for _ in range(n)], key=lambda p: p[1])
    for x, y in pts:
        s = scale * (.7 + .6 * (y - y0) / 300)
        DR.use(rnd.choice(("host", "kid", "mama", "artem")), hoodie=False)
        fig = DR.front((W, H), x, y, s, t + x, ("down", "down"), "idle", "neutral", (0, 0))
        R, G, B = fig.convert("RGB").split()
        a = fig.getchannel("A")
        fig = Image.merge("RGBA", (R.point(lambda v: int(v * .55 + 20)), G.point(lambda v: int(v * .6 + 24)), B.point(lambda v: int(v * .65 + 30)), a))
        img.paste(fig, (0, 0), fig)
    return img


def fence(d, y=780):
    for x in range(0, W, 40):
        d.line([x, y, x, y + 420], fill=(90, 96, 104), width=6)
    for x in range(-420, W, 20):
        d.line([x, y, x + 420, y + 420], fill=(110, 116, 124), width=2)
        d.line([x + 420, y, x, y + 420], fill=(110, 116, 124), width=2)
    d.line([0, y, W, y], fill=(90, 96, 104), width=8)
    for x in range(0, W, 30):   # колючка
        d.line([x, y - 12, x + 16, y + 4], fill=(150, 150, 156), width=3)


def carry(img, x, s, t, ground=GY, walk=True):
    """Саша несёт бабушку на руках"""
    DR.use("vnuk", hoodie=True)
    fig = DR.front((W, H), x, ground, s, t, ("out", "out"), "walk" if walk else "idle", "tense", (0, .2))
    img = char(img, fig)
    DR.use("babushka", top=(112, 84, 64), hoodie=False)
    bf = DR.front((W, H), W / 2, H, s * .82, 1.0, ("down", "down"), "idle", "neutral", (0, 0))
    bb = bf.getbbox()
    bf = bf.crop(bb).rotate(78, expand=True, resample=Image.BICUBIC)
    bob = 6 * math.sin(t * 8) * s if walk else 0
    cx, cy = x, ground - 962 * s + 400 * s + bob
    img.paste(bf, (int(cx - bf.width / 2), int(cy - bf.height / 2)), bf)
    return img


def notes(img, t, x, y, col=(70, 70, 150)):
    d = ImageDraw.Draw(img)
    for i in range(4):
        life = (t * .45 + i / 4) % 1
        nx, ny = x - 70 * life + 20 * math.sin(life * 6 + i), y - 220 * life
        d.ellipse([nx, ny + 30, nx + 24, ny + 48], fill=col)
        d.line([nx + 22, ny + 38, nx + 22, ny], fill=col, width=5)
        d.line([nx + 22, ny, nx + 38, ny + 12], fill=col, width=5)


def night(img, k=.45, col=(10, 16, 40)):
    return Image.blend(img, Image.new("RGB", (W, H), col), k)


# ---------- сцены ----------
def s01(t, L, cue):   # фургон 47 у стадиона, рассвет
    img = night(bg("b1_street", 1.2), .25, (60, 40, 70))
    d = ImageDraw.Draw(img)
    van(d, 260, 780)
    img = sasha(img, 150, .8, t, ("down", "down"), "tense", (.8, 0))
    clock(img, "06:00", y=240, col=(250, 210, 90))
    plate(img, "СТАДИОН · КАРАНТИН", col=(160, 30, 30))
    return zoom(img, 1.0 + .05 * t / L, .6, .65)


def s02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    img = night(bg("b1_street", 1.1), .25, (60, 40, 70))
    img = patrol(img, 470, .8, t)
    d = ImageDraw.Draw(img)   # список на планшете
    d.rounded_rectangle([60, 300, 380, 760], radius=16, fill=(246, 246, 240), outline=INK, width=5)
    d.rectangle([170, 284, 270, 320], fill=(150, 150, 156), outline=INK, width=3)
    f = F(24)
    names = ["Иванов А.", "Петрова Н.", "Орлов К.", "Смирнова Е.", "Ким Д.", "Белова О."]
    for i, n in enumerate(names):
        d.text((86, 350 + i * 56), n, font=f, fill=INK)
        d.line([86, 382 + i * 56, 350, 382 + i * 56], fill=(200, 200, 206), width=2)
    if p > .7:
        d.text((90, 690), "бабушки нет", font=F(30, FONT_SUB), fill=(210, 40, 40))
    clock(img, "06:20", col=(250, 210, 90))
    return img


def s03(t, L, cue):
    img = night(bg("b1_street", .9), .4)
    img = crowd(img, t)
    d = ImageDraw.Draw(img)
    fence(d, 760 - min(1, t / 2) * 300)   # камера «перелезает» через забор
    return img


def s04(t, L, cue):
    img = night(bg("b1_street", .9), .4)
    img = crowd(img, t, 14, 960, 9, .3)
    img = babushka(img, W / 2, 1.2, t, ("down", "phone"), "neutral", (0, .3), ground=1700, coat=True, jar=True)
    return zoom(img, 1.0 + .08 * t / L, .5, .55)


def s05(t, L, cue):
    img = night(bg("b1_street", .8), .45)
    img = babushka(img, 470, 1.25, t, ("down", "phone"), "neutral", (-1, -.6), ground=1780, coat=True, jar=True)
    img = sasha(img, 170, 1.25, t, ("out", "down"), "sad", (1, 0), ground=1780)
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    img = night(bg("b1_street", .7), .55)
    d = ImageDraw.Draw(img)
    # схема города: точка А → точка Б
    d.line([120, 900, 300, 640, 470, 720, 600, 420], fill=(250, 210, 90), width=8)
    for (x, y, lab, col) in ((120, 900, "СТАДИОН", (240, 70, 80)), (600, 420, "ПУНКТ", (90, 220, 120))):
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=col, outline=INK, width=4)
        d.text((x - F(28, FONT_SUB).getlength(lab) / 2, y + 30), lab, font=F(28, FONT_SUB), fill=(255, 255, 255), stroke_width=3, stroke_fill=INK)
    clock(img, "04:00" if p < .4 else "03:59")
    if p > .55:
        plate(img, "12 км", col=(30, 60, 110))
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    img = night(bg("b1_street", 1.0), .35)
    if p < .55:
        img = babushka(img, 470, .82, t, ("down", "phone"), "neutral", (-.5, 0), coat=True, jar=True)
        img = sasha(img, 230, .82, t, ("down", "down"), "tense", (.8, 0))
    else:
        img = carry(img, W / 2, .82, t, walk=False)
    return img


def s08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    shift = int(t * 60) % W
    base = night(bg("b1_street", 1.0), .35)
    img = Image.new("RGB", (W, H))
    img.paste(base, (-shift, 0)); img.paste(base, (W - shift, 0))   # улица едет мимо
    img = carry(img, W / 2, .82, t)
    if p > .45:
        notes(img, t, W / 2 + 60, 360)
    km = min(12, int(1 + p * 11.5))
    plate(img, f"{km} км из 12", col=(30, 60, 110))
    left = 4 * 60 - int(p * 220)
    clock(img, f"{left // 60:02d}:{left % 60:02d}")
    return img


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = bg("b1_door", 1.1)
    d = ImageDraw.Draw(img)
    d.rectangle([60, 260, 660, 340], fill=(40, 140, 80), outline=INK, width=4)
    f = F(40, FONT_SUB)
    d.text(((W - f.getlength("ПУНКТ ВАКЦИНАЦИИ")) / 2, 278), "ПУНКТ ВАКЦИНАЦИИ", font=f, fill=(255, 255, 255))
    img = carry(img, W / 2, .82, t, walk=False)
    clock(img, "00:19", y=370)
    return img


def s10(t, L, cue):
    p = (t - cue["10"]) / dur("10.mp3")
    img = night(bg("b1_kitchen", .8, 4), .3, (30, 40, 60))
    d = ImageDraw.Draw(img)
    # койка, бабушка спит, капельница
    d.rounded_rectangle([60, 960, 660, 1060], radius=20, fill=(230, 232, 236), outline=INK, width=5)
    d.rounded_rectangle([80, 900, 240, 970], radius=26, fill=(250, 250, 250), outline=INK, width=4)
    d.ellipse([110, 860, 210, 950], fill=B1.SKIN_B, outline=INK, width=4)
    d.chord([106, 850, 214, 930], 180, 360, fill=(214, 212, 216), outline=INK, width=3)
    d.line([140, 906, 156, 906], fill=INK, width=3); d.line([168, 906, 184, 906], fill=INK, width=3)
    d.rounded_rectangle([230, 930, 640, 1000], radius=20, fill=(160, 190, 220), outline=INK, width=4)   # одеяло
    d.line([620, 400, 620, 960], fill=(150, 150, 156), width=6)
    d.rounded_rectangle([580, 400, 660, 520], radius=12, fill=(200, 230, 250), outline=INK, width=3)
    hours = "укол" if p < .3 else ("1 час" if p < .55 else "2 часа")
    plate(img, hours, col=(30, 60, 110))
    for i in range(3):   # Zzz
        life = (t * .4 + i / 3) % 1
        d.text((220 + 40 * life, 800 - 120 * life), "z", font=F(int(30 + 20 * life), FONT_SUB), fill=(220, 220, 240))
    return img


def s11(t, L, cue):
    img = bg("b1_kitchen", 1.15)
    img = Image.blend(img, Image.new("RGB", (W, H), (255, 220, 160)), .12)   # утренний свет
    img = steam(img, t, 360, 700)
    img = sasha(img, 470, .86, t, ("down", "down"), "shock", (-.8, 0))
    plate(img, "утро")
    return img


def s12b(t, L, cue):
    img = bg("b1_kitchen", 1.15)
    img = Image.blend(img, Image.new("RGB", (W, H), (255, 220, 160)), .12)
    img = B1.babushka(img, 360, .9, t, ("down", "phone"), "smile", (.4, .2), prop="pan")
    img = steam(img, t, 500, 720)
    return zoom(img, 1.0 + .06 * t / L, .45, .4)


def s13(t, L, cue):
    vo14 = cue["14"]
    img = bg("b1_kitchen", 1.15)
    img = Image.blend(img, Image.new("RGB", (W, H), (255, 220, 160)), .12)
    img = babushka(img, 200, .86, t, ("down", "down"), "smile", (1, 0))
    img = sasha(img, 520, .86, t, ("down", "down"), "smile", (-1, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([180, 1060, 540, 1110], radius=10, fill=(150, 104, 70), outline=INK, width=4)   # стол
    d.ellipse([260, 1010, 460, 1066], fill=(240, 240, 236), outline=INK, width=4)
    for k in range(5):
        d.ellipse([280, 1004 - k * 12, 440, 1040 - k * 12], fill=(232, 176, 84), outline=(160, 100, 40), width=2)
    d.ellipse([330, 930, 390, 956], fill=(150, 20, 40))
    img = steam(img, t, 360, 960, 3)
    if t > vo14 - .4:
        a = min(1, (t - vo14 + .4) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f0, f1, f2 = F(36, FONT_SUB), F(64, FONT_SUB), F(36, FONT_SUB)
            dd.text(((W - f0.getlength("БАБУШКУ УКУСИЛИ · КОНЕЦ")) / 2, 380), "БАБУШКУ УКУСИЛИ · КОНЕЦ", font=f0, fill=(200, 200, 206))
            pop = 1 + .05 * math.sin((t - vo14) * 7)
            f1 = F(int(64 * pop), FONT_SUB)
            dd.text(((W - f1.getlength("ПОДПИШИСЬ")) / 2, 470), "ПОДПИШИСЬ", font=f1, fill=(240, 240, 244), stroke_width=4, stroke_fill=INK)
            dd.text(((W - f2.getlength("скоро новая история")) / 2, 566), "скоро новая история", font=f2, fill=(240, 70, 80))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .3, span("s05")[0] + .2, span("s09")[0] + .3])
