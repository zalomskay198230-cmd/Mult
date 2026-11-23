"""«НОЧНАЯ СМЕНА». Серия 2 — ФИНАЛ (зрители выбрали «бежать»). Холодный старт: выход заперт снаружи.
Развязка: под простынёй сторож, «ты шестой», утром на пятой каталке — герой.
Запуск: python3 seriya02.py ../tts/s02f ../seriya02.mp4"""
import os, sys, math, random, importlib.util
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
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter
from flatworld import SD, chibi, OUT

W, H, K, F = M.W, M.H, M.K, M.F
RED, YEL, WHITE = M.RED, M.YEL, M.WHITE
VOTE = ("БЕЖАТЬ К ВЫХОДУ", .64)

LINES = {
    "01": "Выход ^заперт^. Снаружи.",
    "02": "Минуту назад. Вы выбрали — *бежать*.",
    "03": "Рву по коридору. Сзади — ^скрип^ колёс. Не оглядываюсь.",
    "04": "Пост сторожа. Стул ^пустой^. Чай ещё *тёплый*.",
    "05": "Дёргаю дверь выхода. ^Заперто^. Ключ торчит — с *той* стороны.",
    "06": "Скрип затихает. Прямо за ^спиной^.",
    "07": "Под простынёй на каталке шевелится ^рука^. На ней — часы *сторожа*.",
    "08": "Срываю *простыню*. Под ней — ^сторож^. Глаза ^открыты^.",
    "09": "«Ты считал до *пяти*? — шепчет он. — Значит, ты ^шестой^».",
    "10": "Утром смену принимал *новый* стажёр. А на *пятой* каталке лежал ^я^. С биркой.",
    "11": "*Подпишись* — скоро новая история.",
}
PLAN = [(f"r{k}", [(k, 0.04)], 0.12) for k in LINES]
PLAN[0] = ("r01", [("01", 0.0)], 0.1)
PLAN[7] = ("r08", [("08", 0.05)], 0.2)
PLAN[8] = ("r09", [("09", 0.05)], 0.6)
PLAN[-1] = ("r11", [("11", 0.05)], 1.0)
setup(LINES, PLAN)
T0 = (2, 15, 12)


def timer(img, t, off=0):
    M.timer(img, t, (T0[0], T0[1], T0[2] + off))


def vote_bar(img, t, a=1.0):
    d = ImageDraw.Draw(img)
    lab, pct = VOTE
    k = min(1, t / 1.0)
    v = .2 + (pct - .2) * k
    x0, y0, x1 = 40, 110, W - 40
    d.rounded_rectangle([x0, y0, x1, y0 + 44], radius=10, fill=(20, 24, 28), outline=(200, 210, 210), width=2)
    d.rounded_rectangle([x0 + 4, y0 + 4, x0 + 4 + (x1 - x0 - 8) * v, y0 + 40], radius=8, fill=(214, 90, 60))
    d.text((x0 + 16, y0 + 10), lab, font=F(20, FONT_SUB), fill=WHITE)
    d.text((x1 - 70, y0 + 10), f"{int(v * 100)}%", font=F(22, FONT_SUB), fill=WHITE)


def exit_door(t, pull=0.0, key=False, light=.8):
    """дверь выхода крупно: зелёная табличка, окошко"""
    img = Image.new("RGB", (W * K, H * K))
    d = SD(img, 0, 0, K)
    c = lambda v: tuple(int(q * light) for q in v)
    d.rectangle([0, 0, W, H], fill=c((120, 146, 140)))
    for y in range(0, H, 64):
        d.line([(0, y), (W, y)], fill=c((104, 130, 124)), width=2)
    d.rectangle([150, 150, 570, 230], fill=(30, 170, 90), outline=(10, 60, 30), width=4)   # «ВЫХОД»
    f = F(54, FONT_SUB)
    d.text((360 - f.getlength("ВЫХОД") / 2, 160), "ВЫХОД", font=f, fill=WHITE)
    d.rectangle([140, 280, 580, 1200], fill=c((88, 98, 104)), outline=(26, 30, 32), width=8)
    d.rectangle([290, 380, 430, 560], fill=(10, 16, 22), outline=(26, 30, 32), width=6)   # окошко
    if key:   # ключ снаружи — виден сквозь стекло
        d.ellipse([336, 450, 376, 490], outline=(200, 170, 70), width=6)
        d.rectangle([370, 464, 420, 474], fill=(200, 170, 70))
    hx = 470 - 30 * pull
    d.rectangle([hx, 720, hx + 100, 760], fill=(176, 182, 188), outline=(30, 30, 30), width=3)
    img = M.done(img)
    return img


def guard_post(t, light=.85):
    img = Image.new("RGB", (W * K, H * K))
    d = SD(img, 0, 0, K)
    c = lambda v: tuple(int(q * light) for q in v)
    d.rectangle([0, 0, W, H], fill=c((116, 140, 134)))
    for y in range(0, H, 64):
        d.line([(0, y), (W, y)], fill=c((100, 124, 118)), width=2)
    d.rectangle([0, 1000, W, H], fill=c((84, 92, 90)))
    d.rectangle([60, 760, 660, 800], fill=c((130, 96, 66)), outline=OUT, width=3)   # стол
    for lx in (90, 620):
        d.rectangle([lx, 800, lx + 18, 1000], fill=c((110, 80, 56)))
    d.rectangle([120, 640, 300, 760], fill=c((40, 44, 48)), outline=OUT, width=3)   # мониторчик
    d.rectangle([134, 654, 286, 746], fill=(30, 90, 60) if int(t * 4) % 2 else (20, 60, 40))
    d.rounded_rectangle([420, 690, 480, 760], radius=8, fill=(236, 236, 232), outline=OUT, width=3)   # кружка
    d.arc([470, 708, 500, 740], 270, 90, fill=OUT, width=4)
    d.ellipse([520, 712, 640, 760], fill=(40, 52, 80), outline=OUT, width=3)   # фуражка
    d.rectangle([560, 690, 600, 716], fill=(40, 52, 80), outline=OUT, width=3)
    d.rectangle([300, 860, 440, 900], fill=c((60, 60, 66)), outline=OUT, width=3)   # пустой стул
    d.rectangle([300, 740, 440, 860], fill=c((70, 70, 76)), outline=OUT, width=3)
    for lx in (310, 420):
        d.line([(lx, 900), (lx, 1000)], fill=c((50, 50, 54)), width=6)
    d.rectangle([520, 300, 680, 520], fill=(10, 16, 26), outline=OUT, width=6)   # окно поста
    img = M.done(img)
    img = M.mist(img, t, 450, 660, .7)   # пар от чая
    return img


# ---------- сцены ----------
def r01(t, L, cue):   # холодный старт
    img = exit_door(t, pull=abs(math.sin(t * 14)), key=False)
    v_hand = ImageDraw.Draw(img)
    M.big(img, "ЗАПЕРТО", 600, RED, 110)
    timer(img, t, 34)
    return shake(img, t, 6)


def r02(t, L, cue):
    img, d = M.corridor(light=.3)
    M.gurney(d, 360, 760, .45, light=.5)
    chibi(d, "intern", 360, 1240, 2.2, t, "shock", 0)
    img = M.done(img)
    big = ImageDraw.Draw(img)
    M.big(img, "МИНУТУ НАЗАД", 300, WHITE, 64)
    vote_bar(img, t)
    timer(img, t, 0)
    return img


def r03(t, L, cue):   # бег: каталка едет сзади
    p = (t - cue["03"]) / dur("03.mp3")
    img, d = M.corridor(light=.35)
    M.gurney(d, 360, 640 + 200 * M.ease(p), .3 + .45 * M.ease(p), light=.55)
    chibi(d, "intern", 360 + 30 * math.sin(t * 12), 1240, 2.2, t, "shock", 0, walk=True)
    img = M.done(img)
    if p > .3:
        M.tag(img, "СКРИП…", 110, (20, 22, 24), (220, 220, 220), 28)
    timer(img, t, 3)
    return shake(img, t, 3)


def r04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = guard_post(t)
    if p > .3:
        M.tag(img, "ПУСТО", 110, (150, 30, 30), WHITE, 30)
    if p > .65:
        M.tag(img, "ЧАЙ ТЁПЛЫЙ", 180, (20, 22, 24), YEL, 26)
    timer(img, t, 9)
    return img


def r05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = exit_door(t, pull=abs(math.sin(t * 14)) if p < .5 else 0, key=p > .55)
    img = toonlib.zoom(img, 1 + (.7 * M.ease((p - .55) / .45) if p > .55 else 0), .5, .37)
    if p > .3:
        M.big(img, "ЗАПЕРТО", 600, RED, 110) if p < .55 else M.tag(img, "КЛЮЧ — СНАРУЖИ", 120, (20, 22, 24), YEL, 30)
    timer(img, t, 14)
    return shake(img, t, 5 if p < .5 else 0)


def r06(t, L, cue):   # тишина: каталка вплотную
    p = (t - cue["06"]) / dur("06.mp3")
    img = exit_door(t, light=.5)
    d = SD(img, 0, 0, 1)
    M.gurney(d, 360, 1400, 1.9, light=.6)
    if p > .5:
        img = Image.blend(img, Image.new("RGB", (W, H)), .25)
        M.tag(img, "ТИШИНА", 120, (20, 22, 24), (220, 220, 220), 30)
    timer(img, t, 19)
    return img


def r07(t, L, cue):   # рука из-под простыни, часы сторожа
    p = (t - cue["07"]) / dur("07.mp3")
    img = Image.new("RGB", (W * K, H * K), (10, 12, 14))
    d = SD(img, 0, 0, K)
    d.polygon([(0, 560), (720, 520), (720, 1000), (0, 1040)], fill=(206, 212, 212))   # простыня крупно
    for i in range(7):
        d.line([(40 + i * 100, 560), (80 + i * 90, 1020)], fill=(180, 188, 188), width=6)
    k = M.ease(min(1, p / .6))
    hx = 520 - 120 * k
    d.polygon([(720, 820), (hx + 60, 800), (hx, 812), (hx - 30, 840), (hx, 870), (hx + 60, 880), (720, 880)], fill=(150, 170, 160), outline=OUT, width=4)
    for i in range(4):   # пальцы шевелятся
        a = math.sin(t * 6 + i) * 8
        d.line([(hx + 4, 820 + i * 14), (hx - 50, 812 + i * 18 + a)], fill=(150, 170, 160), width=14)
    if p > .55:   # часы на запястье
        d.rectangle([hx + 110, 800, hx + 150, 886], fill=(60, 40, 30))
        d.ellipse([hx + 100, 818, hx + 160, 868], fill=(220, 200, 140), outline=OUT, width=4)
        d.line([(hx + 130, 843), (hx + 130, 826)], fill=OUT, width=3)
        d.line([(hx + 130, 843), (hx + 144, 848)], fill=OUT, width=3)
    img = M.done(img)
    M.flashlight(img, 360, 1280, 420, 760, 200, 60)
    if p > .6:
        M.big(img, "ЧАСЫ СТОРОЖА", 240, RED, 78)
    timer(img, t, 24)
    return shake(img, t, 3 if p > .2 else 0)


def guard_face(t, eyes_open=True, close=1.0, light=.8, lips=0.0):
    """лицо сторожа на каталке (вид сверху), простыня откинута"""
    img = Image.new("RGB", (W * K, H * K), (8, 10, 12))
    d = SD(img, 0, 0, K)
    c = lambda v: tuple(int(q * light) for q in v)
    s_ = close
    cx, cy = 360, 640
    d.rectangle([60, cy + 220 * s_, 660, H], fill=c((210, 216, 216)))   # простыня
    d.ellipse([cx - 210 * s_, cy - 250 * s_, cx + 210 * s_, cy + 250 * s_], fill=c((196, 206, 200)), outline=OUT, width=6)
    d.chord([cx - 214 * s_, cy - 260 * s_, cx + 214 * s_, cy - 40 * s_], 180, 360, fill=c((170, 170, 176)))   # седые волосы
    d.chord([cx - 170 * s_, cy + 60 * s_, cx + 170 * s_, cy + 280 * s_], 0, 180, fill=c((180, 180, 186)))    # борода
    for sx in (-1, 1):
        ex = cx + sx * 80 * s_
        if eyes_open:
            d.ellipse([ex - 44 * s_, cy - 60 * s_, ex + 44 * s_, cy + 4 * s_], fill=(236, 236, 230), outline=OUT, width=4)
            d.ellipse([ex - 14 * s_, cy - 42 * s_, ex + 14 * s_, cy - 14 * s_], fill=(10, 10, 12))
        else:
            d.line([(ex - 40 * s_, cy - 28 * s_), (ex + 40 * s_, cy - 28 * s_)], fill=OUT, width=6)
    mo = 8 + 30 * lips
    d.ellipse([cx - 50 * s_, cy + 120 * s_ - mo, cx + 50 * s_, cy + 120 * s_ + mo], fill=(60, 30, 30), outline=OUT, width=4)
    return M.done(img)


def r08(t, L, cue):
    p = (t - cue["08"]) / dur("08.mp3")
    if p < .35:   # простыня ещё на нём — слетает
        img = Image.new("RGB", (W, H), (8, 10, 12))
        d = SD(img, 0, 0, 1)
        k = M.ease(p / .35)
        M.gurney(d, 360, 1100 - 600 * k, 2.2, light=.7)
    else:
        lit = 1.0 if int(t * 9) % 3 else .35   # свет мигает
        img = guard_face(t, eyes_open=p > .7, close=1.0, light=.8 * lit)
        if p > .7:
            M.big(img, "ГЛАЗА ОТКРЫТЫ", 180, RED, 70)
    timer(img, t, 31)
    return shake(img, t, 7 if .33 < p < .42 or .7 < p < .76 else 0)


def r09(t, L, cue):
    p = (t - cue["09"]) / dur("09.mp3")
    img = guard_face(t, eyes_open=True, close=1.0 + .5 * M.ease(t / L), light=.75,
                     lips=abs(math.sin(t * 11)) if p < .9 else 0)
    img = toonlib.zoom(img, 1.3, .5, .62)
    if p > .6:
        M.big(img, "ТЫ — ШЕСТОЙ", 180, RED, 96)
    timer(img, t, 36)
    return img


def r10(t, L, cue):   # утро: новый стажёр, пятая каталка, бирка
    p = (t - cue["10"]) / dur("10.mp3")
    if p < .55:
        img, d = M.corridor(light=1.15)
        M.draw_gurneys(d, empty5=False)
        chibi(d, "son", 470, 1180, 2.0, t, "smile", -1, walk=True)
        img = M.done(img)
        M.tag(img, "УТРО · 08:00", 110, (20, 22, 24), WHITE, 28)
    else:
        img = Image.new("RGB", (W, H))
        k = M.ease((p - .55) / .45)
        img = Image.new("RGB", (W, H), (226, 232, 232))
        d = ImageDraw.Draw(img)
        d.polygon([(0, 500), (720, 460), (720, 1100), (0, 1140)], fill=(232, 236, 236), outline=(150, 160, 160))   # простыня
        d.polygon([(720, 820), (520, 790), (470, 840), (520, 900), (720, 900)], fill=(200, 210, 204), outline=(30, 30, 30))   # стопа
        tag = Image.new("RGBA", (330, 180), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rounded_rectangle([0, 0, 329, 179], radius=14, fill=(236, 228, 196, 255), outline=(120, 100, 70, 255), width=4)
        td.text((24, 18), "№ 5", font=F(32, FONT_SUB), fill=(60, 50, 40))
        td.text((24, 70), "КОВАЛЁВ Д.", font=F(40, FONT_SUB), fill=(170, 30, 30))
        td.text((24, 126), "стажёр", font=F(26), fill=(80, 70, 60))
        tag = tag.rotate(-6, expand=True)
        d.line([(520, 860), (430, 740)], fill=(180, 170, 140), width=4)
        img.paste(tag, (170, 560), tag)
        img = toonlib.zoom(img, 1 + .35 * k, .45, .5)
    M.timer(img, t, (8, 0, 0))
    return img


def r11(t, L, cue):
    img = Image.new("RGB", (W, H), (6, 6, 8))
    d = ImageDraw.Draw(img)
    f1, f2 = F(70, FONT_SUB), F(90, FONT_SUB)
    d.text(((W - f1.getlength("НОЧНАЯ СМЕНА")) / 2, 440), "НОЧНАЯ СМЕНА", font=f1, fill=WHITE)
    d.text(((W - f2.getlength("КОНЕЦ")) / 2, 530), "КОНЕЦ", font=f2, fill=RED)
    pop = 1 + .05 * math.sin(t * 8)
    fp = F(int(36 * pop), FONT_SUB)
    d.rounded_rectangle([W / 2 - fp.getlength("ПОДПИШИСЬ") / 2 - 26, 680, W / 2 + fp.getlength("ПОДПИШИСЬ") / 2 + 26, 748], radius=32, fill=YEL)
    d.text((W / 2 - fp.getlength("ПОДПИШИСЬ") / 2, 692), "ПОДПИШИСЬ", font=fp, fill=(20, 20, 24))
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=[span("r03")[0] + .3 + i * .45 for i in range(6)],
        hits=[span("r01")[0] + .05, span("r06")[0] + span("r06")[1] * .5, span("r07")[0] + span("r07")[1] * .6,
              span("r08")[0] + span("r08")[1] * .35, span("r09")[0] + span("r09")[1] * .6])
