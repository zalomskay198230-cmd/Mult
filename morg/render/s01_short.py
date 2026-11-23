"""«НОЧНАЯ СМЕНА». Серия 1 — короткая версия (~35 с) с холодным стартом: каталка едет из темноты → «минутой ранее» → история.
В конце — призыв переслать другу. Озвучка — та же (tts/s01). Запуск: python3 s01_short.py ../tts/s01 ../seriya01_short.mp4"""
import os, sys, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("morg_s01", os.path.join(HERE, "seriya01.py"))
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01_short.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB
from PIL import Image, ImageDraw

W, H, F = M.W, M.H, M.F
RED, YEL, WHITE = M.RED, M.YEL, M.WHITE
L_ = M.LINES
LINES = {k: L_[k] for k in ("11", "01", "04", "05", "06", "08", "09", "10", "12")}
PLAN = [("c11", [("11", 0.0)], 0.1), ("flash", [], 0.7),
        ("m01", [("01", 0.0)], 0.1), ("m04", [("04", 0.0)], 0.1), ("m05", [("05", 0.0)], 0.05),
        ("m06", [("06", 0.0)], 0.05), ("m08", [("08", 0.0)], 0.05), ("m09", [("09", 0.0)], 0.4),
        ("m10", [("10", 0.05)], 0.3), ("end", [("12", 0.05)], 1.0)]
setup(LINES, PLAN)


def c11(t, L, cue):   # холодный старт: каталка из темноты
    c = {"11": cue["11"] - dur("11.mp3") * .55}   # каталка уже близко с первого кадра
    img = M.m11(t, L, c)
    M.big(img, "ОНА ЕДЕТ КО МНЕ", 200, RED, 74)
    return img


def flash(t, L, cue):
    img = Image.new("RGB", (W, H), (6, 6, 8))
    M.big(img, "МИНУТОЙ", 520, WHITE, 90)
    M.big(img, "РАНЕЕ", 630, WHITE, 90)
    return shake(img, t, 4 if t < .15 else 0)


def end(t, L, cue):
    img = Image.new("RGB", (W, H), (10, 14, 18))
    d = ImageDraw.Draw(img)
    f = F(34, FONT_SUB)
    d.text(((W - f.getlength("ЧТО ДЕЛАТЬ?")) / 2, 250), "ЧТО ДЕЛАТЬ?", font=f, fill=WHITE)
    img = M.choice_card(img, 40, "Бежать к выходу\nчерез коридор", "run", min(1, t / .3))
    img = M.choice_card(img, 380, "Запереться\nв боксе №3", "door", min(1, max(0, t - .3) / .3))
    p = (t - cue["12"]) / dur("12.mp3")
    if p > .85:
        M.big(img, "РЕШАЙ", 800, RED, 80)
    d = ImageDraw.Draw(img)
    fp = F(30, FONT_SUB)
    txt = "ОТПРАВЬ ДРУГУ — ОН БЫ ЗАШЁЛ?"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 22, 940, W / 2 + fp.getlength(txt) / 2 + 22, 998], radius=28, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 951), txt, font=fp, fill=(20, 20, 24))
    M.timer(img, t, (2, 15, 9))
    return img


funcs = {"c11": c11, "flash": flash, "end": end}
for n in ("m01", "m04", "m05", "m06", "m08", "m09", "m10"):
    funcs[n] = getattr(M, n)

if __name__ == "__main__":
    run(funcs, knocks=[span("c11")[0] + .2 + i * .45 for i in range(4)],
        hits=[span("flash")[0] + .02, span("m09")[0] + span("m09")[1] * .35, span("m10")[0] + span("m10")[1] * .3])
