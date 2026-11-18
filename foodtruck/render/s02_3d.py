"""«ФУДТРАК С НУЛЯ». Серия 2 (~27 с): зрители выбрали «окно». Холодный старт с кульминации (ключ в окне).
1) TIMELINE=../render3d/tl_s02.json python3 s02_3d.py ../tts/s02 x
2) blender -b -P ../render3d/ft3d.py -- scenes ../render3d/tl_s02.json ../render3d/frames_s02 24 .75
3) python3 s02_3d.py ../tts/s02 ../seriya02.mp4
4) реклама поверх перемотки (без стоп-кадра): add_popup.py ... speed"""
import os, sys, math, json, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
import toonlib

_tl = os.environ.pop("TIMELINE", None)   # чтобы подгружаемый скрипт серии 1 не перехватил запрос таймлайна
_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01_40"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("ft_s01", os.path.join(HERE, "s01_3d.py"))
A = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(A)          # интерфейс стрима, штампы, плашки, субтитры
sys.argv[:] = _argv
if _tl:
    os.environ["TIMELINE"] = _tl
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB
from PIL import Image, ImageDraw

W, H, F, pill = A.W, A.H, A.F, A.pill
YEL, RED, WHITE, GREEN = A.YEL, A.RED, A.WHITE, A.GREEN
A.FR = os.path.join(HERE, "..", "render3d", "frames_s02")

LINES = {
    "01": "Слушай… в окне был спрятан ^ключ^!",
    "02": "Вы выбрали — *окно*. Лайков тринадцать — но я решил: каждый лайк теперь *тысяча*! В кассе *тринадцать* *тысяч*.",
    "03": "Стекло мутное, рама ^гнилая^. Снимаю — а она ^трещит^.",
    "04": "Новое стекло — *две* *тысячи*. Герметик — *триста*.",
    "05": "А в старой раме, под резинкой, — ^ключ^. Маленький. С биркой «*семь*».",
    "06": "От чего он? Пишите *версии* в комментариях.",
}
PLAN = [("k1", [("01", 0.0)], 0.1), ("k2", [("02", 0.05)], 0.1), ("k3", [("03", 0.0)], 0.05),
        ("k4", [("04", 0.0)], 0.1), ("k5", [("05", 0.05)], 0.1), ("k6", [("06", 0.0)], 0.6)]
setup(LINES, PLAN)

if os.environ.get("TIMELINE"):
    out = {"scenes": [{"name": n, "length": l, "talk": [[s, s + d] for s, c, d in sc]} for n, st, l, sc in toonlib.scenes]}
    json.dump(out, open(os.environ["TIMELINE"], "w"), indent=1)
    print("timeline", f"{toonlib.TOTAL:.1f} c")
    sys.exit()

A.MSGS[:] = ["окно топ", "вах ключ", "держи лайк", "тысяча за лайк!!", "это от ящика?", "ключ от сейфа", "лайк брат",
             "от гаража", "рецепт 7?", "тимур красава", "стекло класс", "ставлю лайк"]
CASH = {"k1": 0}


def cash_at(name, t, cue):
    """касса по сюжету: 0 → +13 000 → −2 000 → −300"""
    if name == "k1":
        return 0
    if name == "k2":
        p = (t - cue["02"]) / dur("02.mp3")
        return 0 if p < .75 else min(13000, int((p - .75) / .15 * 13000))
    if name in ("k3",):
        return 13000
    if name == "k4":
        p = (t - cue["04"]) / dur("04.mp3")
        return 13000 if p < .2 else (11000 if p < .6 else 10700)
    return 10700


def big_top(img, txt, y=190, col=YEL, size=70):
    f = F(size, FONT_SUB)
    while f.getlength(txt) > W - 60:
        size -= 4; f = F(size, FONT_SUB)
    ImageDraw.Draw(img).text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col, stroke_width=7, stroke_fill=(14, 12, 16))


def vote_bars(img, t, a=1.0):
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([50, 150, W - 50, 420], radius=18, fill=(16, 18, 26), outline=(110, 150, 210), width=3)
    d.text((80, 168), "ИТОГИ ГОЛОСОВАНИЯ", font=F(28, FONT_SUB), fill=WHITE)
    k = min(1, t / .8)
    for i, (lab, v, col) in enumerate((("ОКНО", .54, GREEN), ("ПОЛ", .31, (170, 120, 70)), ("ПЛИТА", .15, (120, 124, 132)))):
        y = 222 + i * 64
        d.text((80, y), lab, font=F(26, FONT_SUB), fill=WHITE)
        d.rounded_rectangle([220, y + 4, W - 140, y + 32], radius=10, fill=(40, 44, 56))
        d.rounded_rectangle([220, y + 4, 220 + (W - 360) * v * k, y + 32], radius=10, fill=col)
        d.text((W - 124, y), f"{int(v * 100 * k)}%", font=F(26, FONT_SUB), fill=col)
    return Image.blend(img, lay, a)


def k1(t, L, cue):
    img = A.frame3d("k1", t)
    big_top(img, "КЛЮЧ В ОКНЕ?!")
    A.stamp(img, "ВАХ!", t, .25, RED, 330, 8)
    A.stream_ui(img, t, 0)
    return shake(img, t, 6 if .25 < t < .35 else 0)


def k2(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    img = A.frame3d("k2", t)
    if p < .5:
        img = vote_bars(img, t)
    else:
        A.stamp(img, "1 ЛАЙК = 1 000 ₽!", t, cue["02"] + dur("02.mp3") * .5, YEL, 230, -5, 54)
    c = cash_at("k2", t, cue)
    A.stream_ui(img, t, c)
    if p > .75:
        A.money_rain(img, t, cue["02"] + dur("02.mp3") * .75, 30)
        pill(img, "+13 000 ₽", W - 180, 140, (30, 110, 60), WHITE, 30)
    return img


def k3(t, L, cue):
    p = t / L
    img = A.frame3d("k3", t)
    pill(img, "▶▶ ×16", W - 120, 150, (20, 22, 30), WHITE, 26)
    d = ImageDraw.Draw(img)
    if p > .3:   # щепки
        rnd = random.Random(int(t * 12))
        for _ in range(14):
            x, y = rnd.uniform(200, 600), rnd.uniform(400, 900)
            d.polygon([(x, y), (x + 14, y + 4), (x + 4, y + 12)], fill=(150, 100, 60))
        A.stamp(img, "ТРЕСК!", t, L * .3, RED, 280, 6)
    A.stream_ui(img, t, 13000)
    return shake(img, t, 4 if .3 < p < .6 else 0)


def k4(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = A.frame3d("k4", t)
    if p > .15:
        pill(img, "стекло −2 000 ₽", W / 2, 230, (150, 30, 36), WHITE, 32)
    if p > .55:
        pill(img, "герметик −300 ₽", W / 2, 300, (150, 30, 36), WHITE, 32)
    A.stream_ui(img, t, cash_at("k4", t, cue))
    return img


def k5(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = A.frame3d("k5", t)
    if p > .4:
        A.stamp(img, "КЛЮЧ!", t, cue["05"] + dur("05.mp3") * .4, YEL, 250, -6)
    if p > .7:
        pill(img, "бирка «7»", W / 2, 400, (20, 22, 30), YEL, 34)
    A.stream_ui(img, t, 10700)
    return shake(img, t, 5 if .4 < p < .46 else 0)


def k6(t, L, cue):
    img = A.frame3d("k6", t)
    big_top(img, "ОТ ЧЕГО КЛЮЧ?", 200, WHITE, 66)
    d = ImageDraw.Draw(img)
    pop = 1 + .05 * math.sin(t * 8)
    fp = F(int(32 * pop), FONT_SUB)
    txt = "ПИШИ ВЕРСИИ В КОММЕНТАРИЯХ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 24, 300, W / 2 + fp.getlength(txt) / 2 + 24, 364], radius=30, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 312), txt, font=fp, fill=(20, 20, 24))
    A.stream_ui(img, t, 10700)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN}, hits=[span("k1")[0] + .25, span("k5")[0] + span("k5")[1] * .4])
