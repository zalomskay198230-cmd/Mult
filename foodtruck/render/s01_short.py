"""«ФУДТРАК С НУЛЯ». Серия 1 — короткая версия (~25 с) с резким началом, без рекламы.
Порядок: хлам (сразу событие) → «40 000 ₽ за это» → календарь 1998 → вопрос про ремонт.
Берёт готовые 3D-кадры (render3d/frames_s01) и озвучку tts/s01_40.
Запуск: python3 s01_short.py ../tts/s01_40 ../seriya01_short.mp4"""
import os, sys, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01_40"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("ft_s01", os.path.join(HERE, "s01_3d.py"))
A = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(A)          # кадры 3D, интерфейс стрима, штампы, карточка вопроса
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01_40"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01_short.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB
from PIL import Image, ImageDraw

W, H, F, pill = A.W, A.H, A.F, A.pill
YEL, RED, WHITE, GREEN = A.YEL, A.RED, A.WHITE, A.GREEN

LINES = {
    "05": "Открываю дверь — а там ^хлам^. До потолка. Шины, коробки, старый матрас. *Вах*.",
    "02": "*Сорок* *тысяч* рублей. Девяносто восьмого года. Без одной ^фары^. Вах, *красавец*.",
    "06": "Прежний хозяин, похоже, здесь *жил*. Даже календарь на стене — девяносто ^восьмого^ года.",
    "07": "С чего начинаем *ремонт*? *Пол*, *плита* или *окно*?",
    "08": "Пишите в *комментариях*, дорогие. Как скажете — так и сделаю.",
}
PLAN = [("n1", [("05", 0.0)], 0.1), ("n2", [("02", 0.05)], 0.1), ("n3", [("06", 0.05)], 0.1),
        ("n4", [("07", 0.05)], 0.05), ("n5", [("08", 0.0)], 0.5)]
setup(LINES, PLAN)


def big_top(img, txt, y=190, col=YEL, size=64):
    f = F(size, FONT_SUB)
    while f.getlength(txt) > W - 60:
        size -= 4; f = F(size, FONT_SUB)
    ImageDraw.Draw(img).text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col, stroke_width=7, stroke_fill=(14, 12, 16))


def n1(t, L, cue):   # сразу событие: хлам до потолка
    img = A.frame3d("s05", min(t + 1.2, 6.0))   # с момента, где дверь уже открыта
    big_top(img, "40 000 ₽ ЗА ЭТО?!")
    A.stamp(img, "ХЛАМ!", t, .35, RED, 330, -6)
    A.stream_ui(img, t)
    return shake(img, t, 6 if .35 < t < .45 else 0)


def n2(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    img = A.frame3d("s02", t)
    pill(img, "−40 000 ₽", W / 2, 200, (150, 30, 36), WHITE, 40)
    if p > .45:
        pill(img, "1998 · без фары", W / 2, 280, (20, 22, 30), YEL, 28)
    if p > .75:
        A.stamp(img, "ВАХ!", t, cue["02"] + dur("02.mp3") * .75, YEL, 360)
    A.stream_ui(img, t)
    return img


def n3(t, L, cue):
    return A.s06(t, L, {"06": cue["06"]})


def n4(t, L, cue):
    img = A.frame3d("s07", t)
    img = A.vote_cards(img, A.fade_in(t, .05))
    A.stream_ui(img, t)
    return img


def n5(t, L, cue):
    img = A.frame3d("s08", t)
    img = A.vote_cards(img)
    d = ImageDraw.Draw(img)
    pop = 1 + .05 * math.sin(t * 8)
    fp = F(int(32 * pop), FONT_SUB)
    txt = "ПИШИ В КОММЕНТАРИЯХ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 24, 680, W / 2 + fp.getlength(txt) / 2 + 24, 744], radius=30, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 692), txt, font=fp, fill=(20, 20, 24))
    pill(img, "1 ЛАЙК = 10 ₽ в кассу", W / 2, 770, (214, 30, 40), WHITE, 26)
    A.stream_ui(img, t)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN}, hits=[span("n1")[0] + .35])
