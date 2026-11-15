"""«365 ДНЕЙ». Серия 3 (зрители выбрали «следить»). Структура: ставка для новичков → «вы выбрали» → серия → короткий титр.
Озвучка — пользователя (tts/s03_golos). Запуск: python3 seriya03.py ../tts/s03_golos ../seriya03.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s02_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s02", os.path.join(HERE, "seriya02.py"))
E2 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E2)
sys.argv[:] = _argv
E1 = E2.E1
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s03_golos"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya03.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter
from flatworld import world, chibi, shovel, GR, OUT, dk

W, H = toonlib.W, toonlib.H
V, hud, pill, bubble, dark_card, fade_in, ease, F = E1.V, E1.hud, E1.pill, E1.bubble, E1.dark_card, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE

LINES = {
    "01": "До конца света — *триста* *двадцать* *четыре* дня. Денег — ^ноль^. И я не один, кто *копает*.",
    "02": "Вы выбрали — *следить*.",
    "03": "Три ночи я сидел на крыше своего *гаража*. С отцовским *биноклем*.",
    "04": "Сосед копал с *полуночи* до *четырёх*. Каждую ночь. Ровно четыре часа.",
    "05": "Правило третье: кто роет ^ночью^ — тому есть что ^скрывать^.",
    "06": "На четвёртую ночь он вылез из ямы и сел на ведро. Достал *телефон*.",
    "07": "Экран светился ярко. Я видел каждую *букву*.",
    "08": "«Через триста шестьдесят пять дней — ^конец^. Строй бункер». С его *номера*.",
    "09": "Он пролистал вниз. Там было *второе* сообщение.",
    "10": "«Твой сосед уже ^копает^ к тебе. Не дай ему ^успеть^».",
    "11": "Он поднял голову. И посмотрел прямо на мою ^крышу^.",
    "12": "Четвёртая серия — *завтра*.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.3) for k in LINES]
PLAN[0] = ("s01", [("01", 0.1)], 0.15)
PLAN[1] = ("s02", [("02", 0.05)], 0.25)
PLAN[-2] = ("s11", [("11", 0.05)], 0.5)
PLAN[-1] = ("s12", [("12", 0.0)], 0.15)
setup(LINES, PLAN)

ROOF_Y = GR - 236          # крыша моего гаража
NB_X, NB_PIT_FLOOR = 1480, GR + 476
BUCKET_X = 1350


def big_hud(img, days, k=1.0):
    """крупные шкалы для новичков в первые секунды"""
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 300, W, 720], fill=(8, 10, 16))
    for i, (lab, val, col) in enumerate((("ДО КОНЦА СВЕТА", f"{days} дн", RED), ("БЮДЖЕТ", "0 ₽", YEL))):
        y = 340 + i * 190
        d.rounded_rectangle([90, y, W - 90, y + 160], radius=22, outline=(110, 150, 210), width=4)
        f1, f2 = F(26), F(86, FONT_SUB)
        d.text((W / 2 - f1.getlength(lab) / 2, y + 14), lab, font=f1, fill=(190, 210, 240))
        d.text((W / 2 - f2.getlength(val) / 2, y + 46), val, font=f2, fill=col)
    return Image.blend(img, lay, k)


def choice_banner(img, t, txt, full):
    if t >= full:
        return img
    a = min(1, t / .15, (full - t) / .25)
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 420, W, 760], fill=(10, 12, 18))
    d.rectangle([0, 420, W, 428], fill=YEL); d.rectangle([0, 752, W, 760], fill=YEL)
    f1, f2, f3 = F(40, FONT_SUB), F(80, FONT_SUB), F(26)
    for s_, f, y, col in (("ВЫ ВЫБРАЛИ", f1, 460, (200, 200, 206)), (txt, f2, 525, YEL), ("вариант №2 из комментариев", f3, 660, (170, 170, 176))):
        d.text(((W - f.getlength(s_)) / 2, y), s_, font=f, fill=col)
    return Image.blend(img, lay, a)


def bucket(d, x):
    d.polygon([(x - 22, GR - 50), (x + 22, GR - 50), (x + 16, GR - 4), (x - 16, GR - 4)], fill=(80, 120, 170), outline=OUT)
    d.arc([x - 22, GR - 66, x + 22, GR - 34], 180, 360, fill=OUT, width=3)


def binoculars(img, t, wobble=1.0):
    """вид через бинокль: два круга, вокруг темнота"""
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    dx, dy = 6 * math.sin(t * 1.7) * wobble, 5 * math.sin(t * 2.3) * wobble
    for cx in (W / 2 - 150, W / 2 + 150):
        md.ellipse([cx - 250 + dx, 640 - 250 + dy, cx + 250 + dx, 640 + 250 + dy], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(8))
    out = Image.new("RGB", (W, H), (4, 4, 6))
    out.paste(img, (0, 0), m)
    return out


def phone_closeup(img, lines, a=1.0, red=False):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 140, 400, 580, 900
    d.rounded_rectangle([x0, y0, x1, y1], radius=36, fill=(20, 20, 24), outline=(70, 70, 76), width=6)
    d.rounded_rectangle([x0 + 18, y0 + 24, x1 - 18, y1 - 24], radius=22, fill=(240, 240, 244))
    d.text((x0 + 40, y0 + 46), "ЕГО НОМЕР", font=F(26, FONT_SUB), fill=RED)
    yy = y0 + 100
    f = F(26)
    for i, ln in enumerate(lines):
        h = 30 * len(ln.split("\n")) + 30
        last_red = red and i == len(lines) - 1
        d.rounded_rectangle([x0 + 36, yy, x1 - 36, yy + h], radius=16, fill=(255, 220, 216) if last_red else (222, 224, 232))
        for j, l in enumerate(ln.split("\n")):
            d.text((x0 + 54, yy + 14 + j * 30), l, font=f, fill=(150, 20, 20) if last_red else (24, 24, 28))
        yy += h + 16
    return Image.blend(img, lay, a)


# ---------- сцены ----------
def s01(t, L, cue):
    v = V(world(lights=False, dug=1.0, cont=True, nb="open"), (1180, GR + 150, 1.0))
    chibi(v.d, "me", 1060, GR - 4, 1.0, t, "neutral", 1)
    chibi(v.d, "neigh", NB_X, NB_PIT_FLOOR, 1.0, t, "neutral", -1, arm="shovel")
    img = v.out()
    p = (t - cue["01"]) / dur("01.mp3")
    if p < .62:
        return big_hud(img, 324, min(1, t / .15))
    if p < .75:
        img = big_hud(img, 324, 1 - (p - .62) / .13)
    hud(img, 324)
    sx, sy = v.screen(NB_X, NB_PIT_FLOOR - 140)
    pill(img, "не один", sx, sy - 60, (140, 30, 30), WHITE, 30, anchor=(sx, sy))
    return img


def s02(t, L, cue):
    img = V(world(lights=False, dug=1.0, cont=True, nb="open"), (1180, GR + 150, 1.0)).out()
    hud(img, 324)
    return choice_banner(img, t, "СЛЕДИТЬ", L + .5)


def s03(t, L, cue):
    p = (t - cue["03"]) / dur("03.mp3")
    v = V(world(lights=False, dug=1.0, cont=True, nb="open"), (1080, ROOF_Y + 40, 1.9))
    chibi(v.d, "me", 1040, ROOF_Y, 1.0, t, "neutral", 1)
    d = v.d   # бинокль у глаз
    d.rounded_rectangle([1046, ROOF_Y - 104, 1072, ROOF_Y - 88], radius=4, fill=(30, 30, 34), outline=OUT, width=2)
    d.rounded_rectangle([1046, ROOF_Y - 88, 1072, ROOF_Y - 72], radius=4, fill=(30, 30, 34), outline=OUT, width=2)
    img = v.out()
    night = min(3, 1 + int(p * 3))
    pill(img, f"НОЧЬ {night}", W / 2, 200, (20, 22, 30), YEL, 34)
    hud(img, 324 - (night - 1))
    return img


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    v = V(world(lights=False, dug=1.0, cont=True, nb="open"), (1470, GR + 250, 1.6))
    sw = math.sin(t * 6)
    chibi(v.d, "neigh", NB_X, NB_PIT_FLOOR, 1.0, t, "neutral", -1, arm="shovel")
    shovel(v.d, NB_X + 40, NB_PIT_FLOOR - 20, 1.0, -.6 + .4 * sw)
    if sw > .6:   # летит земля
        for i in range(5):
            v.d.ellipse([NB_X + 60 + i * 12, NB_PIT_FLOOR - 140 - i * 20, NB_X + 70 + i * 12, NB_PIT_FLOOR - 130 - i * 20], fill=(110, 86, 62))
    img = v.out()
    hh = int(4 * min(1, p * 1.1))
    pill(img, f"0{hh}:{int(t * 47) % 60:02d}", W / 2, 200, (20, 22, 30), WHITE, 40)
    hud(img, 321)
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = V(world(lights=False, dug=1.0, cont=True, nb="open"), (1470, GR + 250, 1.6)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .35)
    rows = []
    if p > .35:
        rows.append(("РОЕТ НОЧЬЮ", "", 1.0, BLUE))
    if p > .7:
        rows.append(("= ЕСТЬ ЧТО СКРЫВАТЬ", "", 1.0, RED))
    dark_card(img, "ПРАВИЛО №3", rows, 220, fade_in(t, .05))
    hud(img, 321)
    return img


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    v = V(world(lights=False, dug=1.0, cont=True, nb="open"), (1400, GR - 40, 1.9))
    bucket(v.d, BUCKET_X)
    if p < .45:   # вылезает по лестнице
        y = NB_PIT_FLOOR - (NB_PIT_FLOOR - GR + 4) * ease(p / .45)
        chibi(v.d, "neigh", 1555, y, 1.0, t, "neutral", -1, arm="up")
    else:
        chibi(v.d, "neigh", BUCKET_X, GR - 14, 1.0, t, "neutral", 0, arm="phone" if p > .75 else None, shadow=False)
        bucket(v.d, BUCKET_X)
        if p > .75:
            v.glow(BUCKET_X - 2, GR - 14 - 92, 18, (150, 200, 255), .5)
    img = v.out()
    pill(img, "НОЧЬ 4", W / 2, 200, (20, 22, 30), YEL, 34)
    hud(img, 320)
    return img


def bino_view(t, glow_k=1.0, look_up=False):
    v = V(world(lights=False, dug=1.0, cont=True, nb="open"), (BUCKET_X, GR - 90, 2.8))
    chibi(v.d, "neigh", BUCKET_X, GR - 14, 1.0, t, "shock" if look_up else "neutral", 0, arm="phone", shadow=False)
    bucket(v.d, BUCKET_X)
    if glow_k:
        v.glow(BUCKET_X - 2, GR - 14 - 92, 16, (150, 200, 255), .45 * glow_k)
    return binoculars(v.out(), t)


def s07(t, L, cue):
    img = bino_view(t)
    hud(img, 320)
    return img


MSG1 = "Через 365 дней — конец.\nСтрой бункер."
MSG2 = "Твой сосед уже копает\nк тебе. Не дай ему\nуспеть."


def s08(t, L, cue):
    img = bino_view(t)
    img = phone_closeup(img, [MSG1], fade_in(t, .1))
    hud(img, 320)
    return img


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = bino_view(t)
    img = phone_closeup(img, [MSG1] + (["…"] if p > .5 else []))
    hud(img, 320)
    return img


def s10(t, L, cue):
    img = bino_view(t)
    img = phone_closeup(img, [MSG1, MSG2], 1.0, red=True)
    hud(img, 320)
    return shake(img, t, 3 if t < .3 else 0)


def s11(t, L, cue):
    p = (t - cue["11"]) / dur("11.mp3")
    up = p > .3
    img = bino_view(t, .9, look_up=up)
    if up:   # он смотрит прямо в бинокль
        if p > .7:
            img = Image.blend(img, Image.new("RGB", (W, H), (60, 0, 0)), .15)
    hud(img, 320)
    return shake(img, t, 6 if .3 < p < .4 else 0)


def s12(t, L, cue):
    img = Image.new("RGB", (W, H), (8, 8, 12))
    d = ImageDraw.Draw(img)
    f1, f3 = F(44, FONT_SUB), F(54, FONT_SUB)
    d.text(((W - f1.getlength("365 ДНЕЙ")) / 2, 470), "365 ДНЕЙ", font=f1, fill=RED)
    d.text(((W - f3.getlength("4 СЕРИЯ — ЗАВТРА")) / 2, 540), "4 СЕРИЯ — ЗАВТРА", font=f3, fill=WHITE)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s02")[0] + .05, span("s10")[0] + .05, span("s11")[0] + span("s11")[1] * .35])
