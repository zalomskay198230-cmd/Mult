"""«365 ДНЕЙ». Серия 4 (зрители выбрали «поговорить»). Ставка → «вы выбрали» → серия → короткий титр.
Озвучка — пользователя (tts/s04_golos). Реклама вставляется потом: add_popup.py (стоп-кадр после фразы 4).
Запуск: python3 seriya04.py ../tts/s04_golos ../seriya04.mp4"""
import os, sys, math, random
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s03_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s03", os.path.join(HERE, "seriya03.py"))
E3 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E3)
sys.argv[:] = _argv
E2, E1 = E3.E2, E3.E1
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s04_golos"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya04.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter
from flatworld import world, chibi, GR, OUT, dk

W, H = toonlib.W, toonlib.H
V, hud, pill, bubble, dark_card, fade_in, ease, F = E1.V, E1.hud, E1.pill, E1.bubble, E1.dark_card, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE
ROOF_Y = E3.ROOF_Y

LINES = {
    "01": "До конца света — *триста* *двадцать* дней. Денег — ^ноль^. А сосед знает, что я за ним ^следил^.",
    "02": "Вы выбрали — *поговорить*.",
    "03": "Я спустился с крыши и пошёл к нему. *Сам*. Без лопаты.",
    "04": "Он ждал у забора. Его зовут *Михалыч*. Он *сварщик*.",
    "05": "Мы показали друг другу *телефоны*. Одинаковые сообщения. Один и тот же *день*.",
    "06": "Только моё пришло с *моего* номера. А его — с *его*.",
    "07": "Правило четвёртое: не знаешь, кто ^враг^, — найди того, кто боится так же, как *ты*.",
    "08": "У Михалыча есть *цемент*, но нет ^стали^. У меня — *контейнер*, но нет ^цемента^.",
    "09": "Мы пожали руки. Денег всё ещё ^ноль^. Но теперь нас *двое*.",
    "10": "А потом он показал *наверх*. На крышу моего гаража.",
    "11": "Там стояла ^чёрная^ ^коробка^. С антенной. И она *мигала*.",
    "12": "Пятая серия — *завтра*.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.3) for k in LINES]
PLAN[0] = ("s01", [("01", 0.1)], 0.15)
PLAN[1] = ("s02", [("02", 0.05)], 0.25)
PLAN[-2] = ("s11", [("11", 0.05)], 0.5)
PLAN[-1] = ("s12", [("12", 0.0)], 0.15)
setup(LINES, PLAN)

FENCE_X = 1205
NB_STAND = 1262
ME_STAND = 1150
WRLD = dict(day=False, lights=False, dug=1.0, cont=True, nb="open")


def two_phones(img, left, right, la="МОЙ НОМЕР", ra="ЕГО НОМЕР", hl=False, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    for i, (who, msg) in enumerate(((la, left), (ra, right))):
        x0 = 50 + i * 330
        x1, y0, y1 = x0 + 290, 360, 820
        d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(20, 20, 24), outline=(70, 70, 76), width=5)
        d.rounded_rectangle([x0 + 14, y0 + 20, x1 - 14, y1 - 20], radius=18, fill=(240, 240, 244))
        d.text((x0 + 32, y0 + 40), who, font=F(22, FONT_SUB), fill=RED if hl else (60, 60, 66))
        if hl:
            d.rounded_rectangle([x0 + 24, y0 + 32, x0 + 40 + F(22, FONT_SUB).getlength(who), y0 + 70], radius=8, outline=RED, width=3)
        f = F(21)
        h = 30 * len(msg) + 26
        d.rounded_rectangle([x0 + 26, y0 + 92, x1 - 26, y0 + 92 + h], radius=14, fill=(222, 224, 232))
        for j, l in enumerate(msg):
            d.text((x0 + 40, y0 + 104 + j * 30), l, font=f, fill=(24, 24, 28))
    return Image.blend(img, lay, a)


MSG = ["Через 365 дней —", "конец.", "Строй бункер."]


def black_box(d, x, y, t, s=1.0):
    d.rounded_rectangle([x - 30 * s, y - 40 * s, x + 30 * s, y], radius=4 * s, fill=(20, 20, 24), outline=OUT, width=2 * s)
    d.line([x + 14 * s, y - 40 * s, x + 24 * s, y - 100 * s], fill=(40, 40, 44), width=3 * s)
    d.ellipse([x + 20 * s, y - 106 * s, x + 28 * s, y - 98 * s], fill=(60, 60, 64))
    if int(t * 2.5) % 2 == 0:
        d.ellipse([x - 8 * s, y - 30 * s, x + 4 * s, y - 18 * s], fill=(255, 40, 40))


# ---------- сцены ----------
def s01(t, L, cue):
    v = V(world(**WRLD), (1180, 800, 1.5))
    chibi(v.d, "me", 1040, ROOF_Y, 1.0, t, "shock", 1)
    chibi(v.d, "neigh", NB_STAND, GR - 4, 1.0, t, "neutral", -1)
    img = v.out()
    p = (t - cue["01"]) / dur("01.mp3")
    if p < .6:
        return E3.big_hud(img, 320, min(1, t / .15))
    if p < .72:
        img = E3.big_hud(img, 320, 1 - (p - .6) / .12)
    hud(img, 320)
    sx, sy = v.screen(NB_STAND, GR - 150)
    pill(img, "он знает", sx, sy - 70, (140, 30, 30), WHITE, 28, anchor=(sx, sy))
    return img


def s02(t, L, cue):
    img = V(world(**WRLD), (1180, 800, 1.5)).out()
    hud(img, 320)
    img = E3.choice_banner(img, t, "ПОГОВОРИТЬ", L + .5, "вариант №1 из комментариев")
    return img


def s03(t, L, cue):
    p = ease(t / (L * .85))
    v = V(world(**WRLD), (1100, 780, 1.6), (1180, 820, 1.6), t / L)
    if p < .4:   # спускается по лестнице гаража
        y = ROOF_Y + (GR - 4 - ROOF_Y) * (p / .4)
        chibi(v.d, "me", 1132, y, 1.0, t, "neutral", 1, arm="up")
    else:
        x = 1132 + (ME_STAND - 1132) * ((p - .4) / .6)
        chibi(v.d, "me", x, GR - 4, 1.0, t, "neutral", 1, walk=p < 1)
    chibi(v.d, "neigh", NB_STAND, GR - 4, 1.0, t, "neutral", -1)
    img = v.out()
    if (t - cue["03"]) / dur("03.mp3") > .6:
        pill(img, "без лопаты", W / 2, 240, (20, 22, 30), YEL, 28)
    hud(img, 320)
    return img


def s04(t, L, cue):
    v = V(world(**WRLD), (1205, 820, 2.0))
    chibi(v.d, "me", ME_STAND, GR - 4, 1.0, t, "neutral", 1)
    chibi(v.d, "neigh", NB_STAND, GR - 4, 1.0, t, "neutral", -1)
    img = v.out()
    sx, sy = v.screen(NB_STAND, GR - 160)
    if (t - cue["04"]) / dur("04.mp3") > .35:
        pill(img, "МИХАЛЫЧ · сварщик", sx, sy - 80, (20, 22, 30), YEL, 26, anchor=(sx, sy))
    hud(img, 320)
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = V(world(**WRLD), (1205, 820, 2.0)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .4)
    img = two_phones(img, MSG, MSG if p > .4 else [], a=fade_in(t, .05))
    if p > .75:
        pill(img, "один и тот же день", W / 2, 860, (30, 60, 110), WHITE, 26)
    hud(img, 320)
    return img


def s06(t, L, cue):
    img = V(world(**WRLD), (1205, 820, 2.0)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .4)
    img = two_phones(img, MSG, MSG, "С МОЕГО НОМЕРА", "С ЕГО НОМЕРА", hl=True)
    hud(img, 320)
    return img


def s07(t, L, cue):
    p = (t - cue["07"]) / dur("07.mp3")
    img = V(world(**WRLD), (1205, 820, 1.7)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .35)
    rows = []
    if p > .3:
        rows.append(("НЕ ЗНАЕШЬ ВРАГА", "", 1.0, RED))
    if p > .6:
        rows.append(("НАЙДИ ТОГО, КТО БОИТСЯ", "", 1.0, BLUE))
    dark_card(img, "ПРАВИЛО №4", rows, 220, fade_in(t, .05))
    hud(img, 320)
    return img


def s08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    img = V(world(**WRLD), (1205, 820, 1.7)).out()
    img = Image.blend(img, Image.new("RGB", (W, H)), .35)
    rows = [("МИХАЛЫЧ: ЦЕМЕНТ", "есть", 1.0, GREEN), ("МИХАЛЫЧ: СТАЛЬ", "нет", 0.0, RED)]
    if p > .5:
        rows += [("Я: КОНТЕЙНЕР", "есть", 1.0, GREEN), ("Я: ЦЕМЕНТ", "нет", 0.0, RED)]
    dark_card(img, "ЧТО У НАС ЕСТЬ", rows, 220, fade_in(t, .05))
    hud(img, 320)
    return img


def s09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    v = V(world(**WRLD), (1205, 820, 2.0))
    shake_hands = p < .4
    chibi(v.d, "me", ME_STAND + 30, GR - 4, 1.0, t, "smile" if p > .5 else "neutral", 1)
    chibi(v.d, "neigh", NB_STAND - 20, GR - 4, 1.0, t, "smile" if p > .5 else "neutral", -1)
    if shake_hands:
        v.d.ellipse([1200 - 10, GR - 50, 1200 + 10, GR - 34], fill=(230, 186, 150), outline=OUT, width=2)
    img = v.out()
    if p > .65:
        pill(img, "НАС ДВОЕ", W / 2, 240, (30, 80, 50), WHITE, 34)
    hud(img, 320)
    return img


def s10(t, L, cue):
    k = ease(t / L)
    v = V(world(**WRLD), (1205, 820, 2.0), (1060, ROOF_Y + 60, 2.0), t / L)
    chibi(v.d, "me", ME_STAND + 30, GR - 4, 1.0, t, "neutral", -1)
    chibi(v.d, "neigh", NB_STAND - 20, GR - 4, 1.0, t, "neutral", -1, arm="up")
    black_box(v.d, 1000, ROOF_Y, t, 1.0)
    img = v.out()
    hud(img, 320)
    return img


def s11(t, L, cue):
    p = (t - cue["11"]) / dur("11.mp3")
    z = 2.0 + 1.2 * ease(t / L)
    v = V(world(**WRLD), (1000, ROOF_Y - 40, z))
    black_box(v.d, 1000, ROOF_Y, t, 1.0)
    if int(t * 2.5) % 2 == 0:
        v.glow(998, ROOF_Y - 24, 20, (255, 40, 40), .8)
    img = v.out()
    if p > .45:
        sx, sy = v.screen(1000, ROOF_Y - 40)
        pill(img, "антенна", sx + 120, sy - 220, (20, 22, 30), WHITE, 26, anchor=(sx + 40, sy - 100))
    hud(img, 320)
    return img


def s12(t, L, cue):
    img = Image.new("RGB", (W, H), (8, 8, 12))
    d = ImageDraw.Draw(img)
    f1, f3 = F(44, FONT_SUB), F(54, FONT_SUB)
    d.text(((W - f1.getlength("365 ДНЕЙ")) / 2, 470), "365 ДНЕЙ", font=f1, fill=RED)
    d.text(((W - f3.getlength("5 СЕРИЯ — ЗАВТРА")) / 2, 540), "5 СЕРИЯ — ЗАВТРА", font=f3, fill=WHITE)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s02")[0] + .05, span("s11")[0] + span("s11")[1] * .3])
