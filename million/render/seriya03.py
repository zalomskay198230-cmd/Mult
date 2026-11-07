"""ВЕРНУТЬ МИЛЛИОН. Серия 3 — заключительная. Гибрид: 3D-фоны (frames_bg, сцены e3_*) + 2D-персонажи.
Запуск: python3 seriya03.py ../tts/s03 ../seriya03.mp4
Хуки (PRAVILA.md): ответ на опрос с первой секунды, «А вот и подвох», «А потом выяснилось вот что»,
«И вот цена вопроса», «А в итоге получилось это»."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
TTS3 = sys.argv[1] if len(sys.argv) > 1 else "../tts/s03"
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)
import toonlib
toonlib.TTS = os.path.join(HERE, "..", "tts", "s01")
import seriya01 as E
toonlib.TTS = TTS3
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import denis_rig as DR
import person

LINES = {
    "01": "Кто ответил «два» — вы угадали. На пороге стояла хозяйка квартиры.",
    "02": "Артём снял её на одни сутки. Для фото с ключами. Он здесь ни дня не жил.",
    "03": "А вот и подвох: заказ оформили не с его номера.",
    "04": "Я позвонил по номеру из заказа. Трубку взял Артём. Голос дрожал.",
    "05a": "Дэн, меня самого развели. Я вложил всё, что занял. А квартира — это было их условие. Фото для рекламы канала.",
    "06": "А потом выяснилось вот что: хозяин канала каждый вечер заказывает ужин. На один и тот же адрес.",
    "07": "А я — курьер. Я дождался этого заказа и взял его.",
    "08": "Дверь открыл парень лет двадцати. За ним — три ноутбука. И наш канал на экранах.",
    "09": "Я не стал драться. Я просто включил камеру. А Артём — полицию.",
    "10": "Через месяц деньги начали возвращать. Шестьсот тысяч из миллиона. Мамины двести — до копейки.",
    "11": "И вот цена вопроса: четыреста тысяч. И друг, которого я чуть не потерял.",
    "12": "А в итоге получилось это: до миллиона я не дошёл. Но мама теперь берёт трубку с первого гудка. И я тоже.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[-1] = ("s12", [("12", 0.1)], 3.4)
setup(LINES, PLAN)

FR = os.path.join(HERE, "..", "render3d", "frames_bg")
NIGHT = {"s04", "s05a", "s06", "s07", "s08", "s09", "s10"}
GY = 1250
F, RED, GREEN = E.F, E.RED, E.GREEN
_cache = {}


def bg(name, t):
    f = int(t * 12)
    path = None
    while f >= 0:
        p = os.path.join(FR, f"e3_{name}_{f:04d}.png")
        if os.path.exists(p):
            path = p
            break
        f -= 1
    if path not in _cache:
        if len(_cache) > 30:
            _cache.clear()
        im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
        _cache[path] = ImageEnhance.Brightness(im).enhance(1.35 if name in NIGHT else 1.05)
    return _cache[path].copy()


def char(img, fig, name, tint=True, shadow=True):
    a = fig.getchannel("A")
    bb = a.getbbox()
    if bb and shadow:
        x0, y0, x1, y1 = bb
        sh = Image.new("L", (W, H), 0)
        cx, w = (x0 + x1) / 2, (x1 - x0) * .55
        ImageDraw.Draw(sh).ellipse([cx - w, y1 - 16, cx + w, y1 + 18], fill=150)
        img.paste(Image.new("RGB", (W, H)), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    if tint and name in NIGHT:
        R, G, B = fig.convert("RGB").split()
        fig = Image.merge("RGBA", (R.point(lambda v: int(v * .84)), G.point(lambda v: int(v * .88)), B, a))
    img.paste(fig, (0, 0), fig)
    return img


def pers(who, x, s, expr="neutral", look=(0, 0), t=0.0):
    fig, _ = person.figure((W, H), x, GY - 962 * s, s, who, expr, look, blink=(t % 3.3) < .1)
    return fig


def counter(img, bal):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([360, 26, 700, 108], radius=16, fill=(16, 18, 22), outline=(80, 84, 96), width=2)
    d.text((378, 34), "БАЛАНС", font=F(18), fill=(150, 154, 166))
    d.text((378, 56), E.rub(bal), font=F(34, FONT_SUB), fill=RED if bal < 10000 else (240, 200, 80) if bal < 1_000_000 else GREEN)
    d.text((570, 34), "ЦЕЛЬ", font=F(18), fill=(150, 154, 166))
    d.text((570, 62), "1 000 000", font=F(24, FONT_SUB), fill=GREEN)


def label(img, txt, y=150):
    d = ImageDraw.Draw(img)
    f = F(36, FONT_SUB)
    d.rounded_rectangle([40, y, 64 + f.getlength(txt), y + 58], radius=12, fill=(20, 22, 30))
    d.text((52, y + 8), txt, font=f, fill=(240, 240, 244))


def panel(img, fn, t, L, pos=(400, 150), w=290, t0=0.0, tilt=-4):
    if t < t0:
        return img
    k = 1 - (1 - min(1, (t - t0) / .25)) ** 3
    ph = fn(t, L).crop(E.PANEL_BOX)
    h = int(w * ph.height / ph.width)
    sc = .6 + .4 * k
    ph = ph.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width, ph.height], radius=int(36 * sc), fill=255)
    ph.putalpha(m)
    ph = ph.rotate(tilt + 6 * (1 - k), expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", ph.size, (0, 0, 0, 0))
    shadow.putalpha(ph.getchannel("A").point(lambda v: int(v * .5)))
    x, y = int(pos[0] + w * (1 - sc) / 2), int(pos[1] + h * (1 - sc) / 2)
    base = img.convert("RGBA")
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)), (x + 12, y + 18))
    base.alpha_composite(ph, (x, y))
    return base.convert("RGB")


def no_zoom(fn, *a):
    g = fn.__globals__
    z, sh = g["zoom"], g["shake"]
    g["zoom"] = lambda im, *x, **k: im
    g["shake"] = lambda im, *x, **k: im
    try:
        return fn(*a)
    finally:
        g["zoom"], g["shake"] = z, sh


# ---------- экраны телефона ----------
def ui_post(t, L):
    img = no_zoom(E.old_s10, 9, 1)
    d = ImageDraw.Draw(img)
    f = F(52, FONT_SUB)
    st = Image.new("RGBA", (420, 110), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([4, 4, 416, 106], radius=12, outline=(230, 50, 50), width=8)
    sd.text((24, 22), "СНЯТО НА СУТКИ", font=F(40, FONT_SUB), fill=(230, 50, 50))
    st = st.rotate(14, expand=True)
    img.paste(st, (150, 420), st)
    return img


def ui_order(t, L):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    d.text((E.PX0 + 40, E.PY0 + 100), "Заказ №4471", font=F(36), fill=(240, 240, 244))
    rows = [("Адрес", "ЖК «Северный парк», кв. 147"), ("Получатель", "Артём"), ("Телефон заказчика", "+7 9•• ••• 14 47")]
    for i, (a, b) in enumerate(rows):
        y = E.PY0 + 190 + i * 130
        d.text((E.PX0 + 40, y), a, font=F(24, E.F_REG), fill=(140, 146, 160))
        d.text((E.PX0 + 40, y + 34), b, font=F(32 if i < 2 else 40, FONT_B if i < 2 else FONT_SUB), fill=(240, 240, 244) if i < 2 else (255, 110, 100))
    d.rounded_rectangle([E.PX0 + 30, E.PY0 + 590, E.PX1 - 30, E.PY0 + 690], radius=20, fill=(60, 20, 22))
    d.text((E.PX0 + 56, E.PY0 + 616), "≠ номер Артёма", font=F(40, FONT_SUB), fill=(255, 120, 110))
    return img


def ui_call(t, L):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    f = F(44, FONT_SUB)
    name = "Неизвестный" if t < 1.6 else "Артём"
    d.text((360 - f.getlength(name) / 2, E.PY0 + 300), name, font=f, fill=(240, 240, 244))
    d.text((360 - F(30, E.F_REG).getlength("+7 9•• ••• 14 47") / 2, E.PY0 + 370), "+7 9•• ••• 14 47", font=F(30, E.F_REG), fill=(160, 166, 180))
    d.text((360 - F(30).getlength("00:0" + str(int(t))) / 2, E.PY0 + 430), "00:0" + str(min(9, int(t))), font=F(30), fill=E.GREEN)
    return img


def ui_history(t, L):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    d.text((E.PX0 + 40, E.PY0 + 100), "Заказы адреса", font=F(36), fill=(240, 240, 244))
    for i, dd in enumerate(("пн 21:00", "вт 21:02", "ср 20:58", "чт 21:01", "пт 21:00")):
        y = E.PY0 + 180 + i * 96
        if t > .3 + i * .25:
            d.rounded_rectangle([E.PX0 + 30, y, E.PX1 - 30, y + 80], radius=16, fill=(32, 34, 42))
            d.text((E.PX0 + 50, y + 10), "Ужин · Заречная 5, кв. 12", font=F(24), fill=(220, 222, 230))
            d.text((E.PX0 + 50, y + 44), dd, font=F(22, E.F_REG), fill=(236, 172, 44))
    return img


def ui_order_kid(t, L):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    d.rounded_rectangle([E.PX0 + 30, E.PY0 + 90, E.PX1 - 30, E.PY0 + 150], radius=16, fill=(236, 172, 44))
    d.text((E.PX0 + 50, E.PY0 + 100), "ЗАКАЗ ПРИНЯТ", font=F(34, FONT_SUB), fill=(20, 20, 24))
    d.text((E.PX0 + 40, E.PY0 + 210), "Заречная 5, кв. 12", font=F(36), fill=(240, 240, 244))
    d.text((E.PX0 + 40, E.PY0 + 270), "Ужин · 21:00", font=F(30, E.F_REG), fill=(160, 166, 180))
    return img


def ui_refund(t, L):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    d.text((E.PX0 + 40, E.PY0 + 100), "Мой банк", font=F(34), fill=(200, 204, 214))
    k = min(1, t / (L * .6))
    k = k * k * (3 - 2 * k)
    d.text((E.PX0 + 40, E.PY0 + 170), E.rub(int(347 + 600_000 * k)), font=F(70, FONT_SUB), fill=E.GREEN)
    rows = [("Возврат · дело №118", "+600 000 ₽"), ("Маме · возврат", "+200 000 ₽")]
    for i, (a, b) in enumerate(rows):
        if t > .6 + i * 1.6:
            y = E.PY0 + 320 + i * 110
            d.rounded_rectangle([E.PX0 + 30, y, E.PX1 - 30, y + 90], radius=18, fill=(26, 44, 34))
            d.text((E.PX0 + 52, y + 26), a, font=F(26, E.F_REG), fill=(200, 204, 214))
            d.text((E.PX1 - 52 - F(28).getlength(b), y + 24), b, font=F(28), fill=E.GREEN)
    return img


# ---------- сцены ----------
def s01(t, L, cue):   # хук: ответ на опрос + хозяйка на пороге
    img = bg("s01", t)
    img = char(img, pers("host", 430, .78, "neutral", (-.6, 0), t), "s01", tint=False)
    img = char(img, DR.front((W, H), 170, 1300, .86, t, ("down", "down"), "idle", "shock" if t < 1.5 else "tense", (.8, 0), courier=True), "s01", tint=False)
    d = ImageDraw.Draw(img)
    f = F(64, FONT_SUB)
    for i, n in enumerate("123"):   # итоги опроса из комментариев
        x, y = 150 + i * 160, 170
        win = n == "2"
        d.rounded_rectangle([x, y, x + 120, y + 120], radius=24, fill=(40, 170, 100) if win else (40, 42, 52),
                            outline=(255, 255, 255) if win else (90, 92, 104), width=5 if win else 2)
        d.text((x + 60 - f.getlength(n) / 2, y + 20), n, font=f, fill=(255, 255, 255))
        if win and t > .5:
            d.text((x + 76, y - 34), "✓", font=F(60), fill=(80, 230, 140))
    return img


def s02(t, L, cue):
    img = bg("s02", t)
    img = char(img, pers("host", 470, .78, "neutral", (-.6, 0), t), "s02", tint=False)
    img = char(img, DR.front((W, H), 170, 1300, .86, t, ("down", "down"), "idle", "tense", (.8, 0), courier=True), "s02", tint=False)
    return panel(img, ui_post, t, L, pos=(300, 120), w=280, t0=.3)


def s03(t, L, cue):
    img = bg("s03", t)
    img = char(img, DR.front((W, H), 200, 1300, .86, t, ("down", "phone"), "idle", "tense", (.6, -.6), phone_hand="r", courier=True), "s03", tint=False)
    return panel(img, ui_order, t, L, pos=(390, 130), w=300, t0=.2)


def s04(t, L, cue):
    img = bg("s04", t)
    img = char(img, DR.front((W, H), 220, GY, .82, t, ("down", "ear"), "idle", "worried", (0, 0), phone_hand="r", courier=True), "s04")
    return panel(img, ui_call, t, L, pos=(430, 150), w=260)


def s05a(t, L, cue):   # Артём говорит
    img = bg("s05a", t)
    img = char(img, pers("artem", 330, .86, "sad", (0, .4), t), "s05a")
    label(img, "АРТЁМ · по телефону")
    return zoom(img, 1.0 + .06 * t / L, .45, .35)


def s06(t, L, cue):
    img = bg("s06", t)
    img = char(img, pers("artem", 470, .76, "worried", (-.6, 0), t), "s06")
    img = char(img, DR.front((W, H), 200, GY, .8, t, ("down", "phone"), "idle", "tense", (.6, -.6), phone_hand="r", courier=True), "s06")
    return panel(img, ui_history, t, L, pos=(380, 110), w=290)


def s07(t, L, cue):
    img = bg("s07", t)
    img = char(img, DR.side((W, H), 280, GY - 40, .72, t, "run", "tense", courier=True), "s07")
    E.rain(img, t, n=60)
    return panel(img, ui_order_kid, t, L, pos=(430, 150), w=250, t0=.3)


def monitors(img, t):
    d = ImageDraw.Draw(img)
    for x, y in ((150, 480), (330, 470), (510, 480)):
        d.text((x, y), "$TOKEN", font=F(22, FONT_SUB), fill=(200, 230, 255))


def s08(t, L, cue):
    img = bg("s08", t)
    monitors(img, t)
    img = char(img, pers("kid", 470, .8, "shock" if t > 1.4 else "neutral", (-.6, 0), t), "s08", tint=False)
    img = char(img, DR.front((W, H), 170, 1300, .86, t, ("down", "down"), "idle", "tense", (.8, 0), courier=True), "s08")
    return zoom(img, 1.0 + .08 * t / L, .55, .45)


def s09(t, L, cue):
    img = bg("s09", t)
    monitors(img, t)
    img = char(img, pers("kid", 480, .8, "shock", (-.6, 0), t), "s09", tint=False)
    img = char(img, DR.front((W, H), 190, 1300, .86, t, ("down", "phone"), "idle", "tense", (.8, -.2), phone_hand="r", courier=True), "s09")
    d = ImageDraw.Draw(img)
    if int(t * 2) % 2 == 0:
        d.ellipse([40, 160, 76, 196], fill=(240, 40, 40))
    d.text((90, 158), "REC", font=F(40, FONT_SUB), fill=(240, 240, 244))
    p = (t - cue["09"]) / dur("09.mp3")
    if p > .6:   # мигалки полиции
        col = (40, 60, 255) if int(t * 6) % 2 else (255, 40, 50)
        lay = Image.new("RGB", (W, H), col)
        img = Image.blend(img, lay, .16)
    return img


def s10(t, L, cue):
    img = bg("s10", t)
    img = char(img, DR.front((W, H), 220, GY, .82, t, ("down", "phone"), "idle", "smile" if t > 2 else "neutral", (.6, -.6), phone_hand="r"), "s10")
    img = panel(img, ui_refund, t, L, pos=(390, 120), w=300)
    k = min(1, t / (L * .6))
    counter(img, int(347 + 600_000 * (k * k * (3 - 2 * k))))
    return img


def s11(t, L, cue):
    img = bg("s11", t)
    img = char(img, pers("artem", 480, .8, "sad", (-.8, 0), t), "s11", tint=False)
    img = char(img, DR.front((W, H), 220, GY, .82, t, ("down", "out"), "idle", "neutral", (.8, 0)), "s11", tint=False)
    d = ImageDraw.Draw(img)
    p = (t - cue["11"]) / dur("11.mp3")
    f = F(60, FONT_SUB)
    if p > .15:
        d.text((W / 2 - f.getlength("−400 000 ₽") / 2, 230), "−400 000 ₽", font=f, fill=(200, 200, 206), stroke_width=4, stroke_fill=INK)
    if p > .55:
        d.text((W / 2 - f.getlength("+ друг") / 2, 320), "+ друг", font=f, fill=(250, 210, 90), stroke_width=4, stroke_fill=INK)
    counter(img, 600_347)
    return img


def s12(t, L, cue):
    vo_end = cue["12"] + dur("12.mp3")
    img = bg("s12", t)
    p = (t - cue["12"]) / dur("12.mp3")
    img = char(img, pers("mama", 500, .78, "smile" if p > .4 else "neutral", (-.6, 0), t), "s12", tint=False)
    img = char(img, DR.front((W, H), 210, GY, .82, t, ("down", "down"), "idle", "smile", (.8, 0)), "s12", tint=False)
    counter(img, 600_347)
    if t > vo_end + .5:
        a = min(1, (t - vo_end - .5) / .4)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f1, f2, f3 = F(88, FONT_SUB), F(46, FONT_SUB), F(38, FONT_SUB)
            for j, (line, f, col) in enumerate((("ВЕРНУТЬ", f1, YELLOW), ("МИЛЛИОН", f1, YELLOW), ("конец", f2, (240, 240, 244)))):
                dd.text(((W - f.getlength(line)) / 2, 360 + j * 100), line, font=f, fill=col, stroke_width=4, stroke_fill=(58, 50, 14))
            if t > vo_end + 1.6:   # вопрос зрителям — для комментариев
                for j, line in enumerate(("Простили бы Артёма?", "1 — да     2 — нет")):
                    dd.text(((W - f3.getlength(line)) / 2, 760 + j * 60), line, font=f3, fill=(240, 240, 244))
    return img


if __name__ == "__main__":
    if os.environ.get("TIMELINE"):
        import json
        out = {"scenes": [{"name": "e3_" + n, "start": st, "length": l, "cue_start": sc[0][0], "cue_dur": sc[0][2]} for n, st, l, sc in scenes]}
        json.dump(out, open(os.environ["TIMELINE"], "w"), indent=1)
        print("timeline saved", round(toonlib.TOTAL, 1))
        sys.exit()
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .5, span("s03")[0] + .2, span("s08")[0] + 1.4, span("s09")[0] + dur("09.mp3") * .6])
