"""ВЕРНУТЬ МИЛЛИОН. Серия 2 — «План». Гибрид: 3D-фоны (render3d/frames_bg, сцены e2_*) + 2D-персонажи.
Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4
Хуки по PRAVILA.md: «Нет, ну вы это видели?», «А это оказалось не так просто», «Самое интересное — впереди»,
«Простите, а за что?», «Вот это сейчас поворот», финал-обрыв."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
TTS2 = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
sys.path.insert(0, HERE)   # свой seriya01 (не «Вахты»)
import toonlib
toonlib.TTS = os.path.join(HERE, "..", "tts", "s01")   # seriya01 строит свой таймлайн при импорте
import seriya01 as E
toonlib.TTS = TTS2
from toonlib import *
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import denis_rig as DR
import person

LINES = {
    "01": "Нет, ну вы это видели? Я — курьер. В доме человека, который украл мой миллион.",
    "02": "Первый пункт плана: попасть в его ЖК. Туда не пускают никого. Кроме доставки.",
    "03": "Я устроился за один вечер. Куртка, сумка, приложение. Заказы по триста рублей.",
    "04": "А это оказалось не так просто. Охрана пускает курьера только с заказом на этот дом.",
    "05": "Три дня я возил чужую еду. И ждал заказ в его ЖК. Самое интересное — впереди.",
    "06": "А потом снова позвонила мама. Тогда, в день перевода, она хотела меня предупредить. В этот раз я взял.",
    "07m": "Денис, Артём у меня тоже занял. Двести тысяч. Сказал — на неделю. Это было месяц назад.",
    "08": "Простите, а за что? Мама копила эти деньги пять лет.",
    "09": "И тут пискнуло приложение. Новый заказ. ЖК «Северный парк». Квартира сто сорок семь.",
    "10": "Получатель — Артём. Вот это сейчас поворот.",
    "11": "Седьмой этаж. Я позвонил в дверь. Она открылась.",
    "12": "А на пороге стоял не Артём.",
}
PLAN = [(f"s{k}", [(k, 0.05 if k != "01" else 0.0)], 0.25) for k in LINES]
PLAN[-1] = ("s12", [("12", 0.3)], 2.6)
setup(LINES, PLAN)

FR = os.path.join(HERE, "..", "render3d", "frames_bg")
NIGHT = {"s01", "s02", "s03", "s04", "s05", "s06", "s07m", "s08", "s09", "s10"}
GY = 1250
_cache = {}
F, RED, GREEN, BLUE, YELLOWC = E.F, E.RED, E.GREEN, E.BLUE, YELLOW
BAL = {"s01": 347, "s02": 347, "s03": 347, "s04": 347, "s05": None, "s06": 1247, "s07m": 1247, "s08": 1247,
       "s09": 1247, "s10": 1247, "s11": 1247, "s12": 1247}


def bg(name, t):
    f = int(t * 12)
    path = None
    while f >= 0:
        p = os.path.join(FR, f"e2_{name}_{f:04d}.png")
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


def char(img, fig, name, tint=True):
    a = fig.getchannel("A")
    bb = a.getbbox()
    if bb:
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


def counter(img, bal):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([380, 26, 700, 108], radius=16, fill=(16, 18, 22), outline=(80, 84, 96), width=2)
    d.text((398, 34), "БАЛАНС", font=F(18), fill=(150, 154, 166))
    d.text((398, 56), E.rub(bal), font=F(34, FONT_SUB), fill=RED if bal < 10000 else (240, 200, 80))
    d.text((560, 34), "ЦЕЛЬ", font=F(18), fill=(150, 154, 166))
    d.text((560, 62), "1 000 000", font=F(26, FONT_SUB), fill=GREEN)


def day(img, txt):
    E.day_plate(img, txt)


# ---------- экраны телефона ----------
def ui_plan(t, L, cue=None):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img)
    d.text((E.PX0 + 40, E.PY0 + 100), "Заметки", font=F(26, E.F_REG), fill=(230, 170, 30))
    d.text((E.PX0 + 40, E.PY0 + 160), "ПЛАН", font=F(54, FONT_SUB), fill=(20, 20, 24))
    rows = [("1. Устроиться курьером", True), ("     в его ЖК", True), ("2. Узнать, кто", False), ("3. Забрать своё", False)]
    for i, (row, vis) in enumerate(rows):
        d.text((E.PX0 + 40, E.PY0 + 250 + i * 80), row, font=F(36), fill=(20, 20, 24) if vis else (20, 20, 24))
    blur = img.crop((E.PX0 + 90, E.PY0 + 400, E.PX1 - 20, E.PY0 + 560)).filter(ImageFilter.GaussianBlur(12))
    img.paste(blur, (E.PX0 + 90, E.PY0 + 400))
    d = ImageDraw.Draw(img)
    d.rectangle([E.PX0 + 36, E.PY0 + 300, E.PX1 - 40, E.PY0 + 304], fill=(240, 200, 60))
    return img


def ui_order(t, L, cue=None, addr="ул. Лесная, 12 · кв. 8", who="Ольга", price="+300 ₽", hl=False):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    d.rounded_rectangle([E.PX0 + 30, E.PY0 + 90, E.PX1 - 30, E.PY0 + 150], radius=16, fill=(236, 172, 44))
    d.text((E.PX0 + 50, E.PY0 + 100), "НОВЫЙ ЗАКАЗ", font=F(34, FONT_SUB), fill=(20, 20, 24))
    d.text((E.PX0 + 40, E.PY0 + 200), "Адрес", font=F(24, E.F_REG), fill=(140, 146, 160))
    d.text((E.PX0 + 40, E.PY0 + 232), addr, font=F(32), fill=(240, 240, 244))
    d.text((E.PX0 + 40, E.PY0 + 310), "Получатель", font=F(24, E.F_REG), fill=(140, 146, 160))
    col = (255, 90, 80) if hl else (240, 240, 244)
    fn = F(52 if hl else 34, FONT_SUB if hl else FONT_B)
    d.text((E.PX0 + 40, E.PY0 + 342), who, font=fn, fill=col)
    d.text((E.PX0 + 40, E.PY0 + 440), "Оплата", font=F(24, E.F_REG), fill=(140, 146, 160))
    d.text((E.PX0 + 40, E.PY0 + 472), price, font=F(44, FONT_SUB), fill=GREEN)
    d.rounded_rectangle([E.PX0 + 40, E.PY1 - 200, E.PX1 - 40, E.PY1 - 90], radius=30, fill=GREEN)
    d.text(((E.PX0 + E.PX1) / 2 - F(38, FONT_SUB).getlength("Принять") / 2, E.PY1 - 172), "Принять", font=F(38, FONT_SUB), fill=(255, 255, 255))
    return img


def ui_order_artem(t, L, cue=None):
    return ui_order(t, L, addr="ЖК «Северный парк» · кв. 147", who="Артём", price="+420 ₽", hl=True)


def ui_gate(t, L, cue=None):
    img = Image.new("RGB", (W, H), (30, 30, 36))
    d = E.phone(img, dark=True)
    d.text((E.PX0 + 40, E.PY0 + 120), "Пропуск курьера", font=F(36), fill=(240, 240, 244))
    d.ellipse([260, E.PY0 + 260, 460, E.PY0 + 460], fill=(120, 30, 30))
    d.line([310, E.PY0 + 310, 410, E.PY0 + 410], fill=(255, 120, 110), width=16)
    d.line([410, E.PY0 + 310, 310, E.PY0 + 410], fill=(255, 120, 110), width=16)
    d.text((E.PX0 + 50, E.PY0 + 520), "Нет активного заказа", font=F(34, FONT_SUB), fill=(255, 120, 110))
    d.text((E.PX0 + 50, E.PY0 + 570), "на этот адрес", font=F(34, FONT_SUB), fill=(255, 120, 110))
    return img


def ui_mama(t, L, cue=None):
    return E.old_s07(t, L, {"07": -99})


def panel(img, fn, t, L, cue=None, pos=(400, 150), w=290, t0=0.0, tilt=-4):
    if fn in (E.old_s07,):
        return E.panel(img, fn, t, L, cue, pos=pos, w=w, t0=t0, tilt=tilt)
    if t < t0:
        return img
    k = 1 - (1 - min(1, (t - t0) / .25)) ** 3
    ph = fn(t, L, cue).crop(E.PANEL_BOX)
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


# ---------- сцены ----------
def s01(t, L, cue):   # хук: Денис-курьер идёт вдоль забора ЖК
    img = bg("s01", t)
    img = char(img, DR.side((W, H), 300, GY, .78, t, "walk", "tense", courier=True), "s01")
    d = ImageDraw.Draw(img)
    f = F(40, FONT_SUB)
    if t > .6:
        d.rounded_rectangle([60, 150, 80 + f.getlength("ЖК «СЕВЕРНЫЙ ПАРК»"), 210], radius=12, fill=(20, 22, 30))
        d.text((70, 158), "ЖК «СЕВЕРНЫЙ ПАРК»", font=f, fill=(240, 240, 244))
    counter(img, 347)
    return img


def s02(t, L, cue):
    img = bg("s02", t)
    img = char(img, DR.front((W, H), 200, GY, .8, t, ("down", "phone"), "idle", "tense", (.6, -.4), phone_hand="r", courier=True), "s02")
    img = panel(img, ui_plan, t, L, pos=(420, 150), w=270, t0=.4)
    counter(img, 347)
    return img


def s03(t, L, cue):
    img = bg("s03", t)
    img = char(img, DR.side((W, H), 260, GY, .78, t, "walk", "neutral", courier=True), "s03")
    img = panel(img, ui_order, t, L, pos=(420, 150), w=270, t0=1.5)
    day(img, "ДЕНЬ 2 ВОЗВРАТА")
    counter(img, 347)
    return img


def s04(t, L, cue):
    img = bg("s04", t)
    p = (t - cue["04"]) / dur("04.mp3")
    img = char(img, DR.front((W, H), 220, GY, .8, t, ("down", "phone"), "idle", "worried" if p > .3 else "tense", (.6, -.2),
                             phone_hand="r", courier=True, head_tilt=math.sin(t * 4) * .4 if p > .5 else 0), "s04")
    img = panel(img, ui_gate, t, L, pos=(430, 160), w=260, t0=.6)
    counter(img, 347)
    return img


def s05(t, L, cue):   # монтаж: бег с заказами, счётчик растёт
    img = bg("s05", t)
    img = char(img, DR.side((W, H), 280, GY - 40, .72, t, "run", "tense", courier=True), "s05")
    E.rain(img, t, n=60)
    k = min(1, t / (L * .85))
    bal = int(347 + 900 * k)
    for i, (lbl, tt) in enumerate((("ДЕНЬ 3", 0), ("ДЕНЬ 4", L * .33), ("ДЕНЬ 5", L * .66))):
        if tt <= t < tt + L * .33:
            day(img, lbl + " ВОЗВРАТА")
    d = ImageDraw.Draw(img)
    if (t * 3) % 1 < .35 and t > .3:   # всплывающие «+300 ₽»
        d.text((420, 420 - 60 * ((t * 3) % 1)), "+300 ₽", font=F(54, FONT_SUB), fill=GREEN, stroke_width=4, stroke_fill=INK)
    counter(img, bal)
    return shake(img, t, 3)


def s06(t, L, cue):
    img = bg("s06", t)
    p = (t - cue["06"]) / dur("06.mp3")
    picked = p > .8
    img = char(img, DR.front((W, H), 220, GY, .8, t, ("down", "ear" if picked else "phone"), "worried", (.6, -.6),
                             phone_hand="r", courier=True), "s06")
    if not picked:
        img = panel(img, E.old_s07, t, L, {"07": -99}, pos=(430, 150), w=260)
    counter(img, 1247)
    return img


def s07m(t, L, cue):   # мама в своей комнате, держит трубку
    img = bg("s07m", t)
    fig, _ = person.figure((W, H), 330, 1250 - 962 * .84, .84, "mama", "worried", (0, 0), blink=(t % 3.3) < .1)
    img = char(img, fig, "s07m")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 140, 300, 200], radius=12, fill=(20, 22, 30))
    d.text((56, 148), "МАМА · сейчас", font=F(34, FONT_SUB), fill=(240, 240, 244))
    counter(img, 1247)
    return zoom(img, 1.0 + .06 * t / L, .45, .4)


def s08(t, L, cue):
    img = bg("s08", t)
    img = char(img, DR.front((W, H), 300, GY, .82, t, ("head", "head"), "idle", "sad", (0, 0), courier=True), "s08")
    d = ImageDraw.Draw(img)
    p = (t - cue["08"]) / dur("08.mp3")
    if p > .45:
        txt = "−200 000 ₽ маминых"
        d.text((W / 2 - F(48, FONT_SUB).getlength(txt) / 2, 300), txt, font=F(48, FONT_SUB), fill=RED, stroke_width=4, stroke_fill=INK)
    counter(img, 1247)
    return shake(img, t, 4 if p < .2 else 0)


def s09(t, L, cue):
    img = bg("s09", t)
    img = char(img, DR.front((W, H), 220, GY, .8, t, ("down", "phone"), "idle", "neutral" if t < 1 else "tense", (.6, -.6),
                             phone_hand="r", courier=True), "s09")
    img = panel(img, ui_order_artem, t, L, pos=(420, 150), w=280, t0=.5)
    counter(img, 1247)
    return shake(img, t, 5 if .5 < t < .8 else 0)


def s10(t, L, cue):   # крупно: «Получатель — Артём»
    img = bg("s10", t)
    img = char(img, DR.front((W, H), 200, 1560, 1.15, t, ("down", "phone"), "idle", "shock", (.6, -.6), phone_hand="r", courier=True), "s10")
    img = panel(img, ui_order_artem, t, L, pos=(350, 120), w=340, tilt=-2)
    counter(img, 1247)
    return zoom(img, 1.0 + .12 * t / L, .7, .35)


def s11(t, L, cue):
    img = bg("s11", t)
    img = char(img, DR.side((W, H), 300, GY, .8, t, "walk", "tense", courier=True), "s11", tint=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 150, 260, 214], radius=12, fill=(20, 22, 30))
    d.text((56, 156), "ЭТАЖ 7", font=F(40, FONT_SUB), fill=(240, 240, 244))
    counter(img, 1247)
    return img


def s12(t, L, cue):   # дверь открыта, в проёме — чужой силуэт
    vo_end = cue["12"] + dur("12.mp3")
    img = bg("s12", t)
    d = ImageDraw.Draw(img)
    f = F(36, FONT_SUB)
    d.rounded_rectangle([300, 300, 400, 350], radius=8, fill=(210, 180, 100), outline=INK, width=3)
    d.text((350 - f.getlength("147") / 2, 304), "147", font=f, fill=INK)
    # силуэт в проёме (контровой свет) — кто это, узнаем в серии 3
    k = min(1, max(0, (t - cue["12"]) / .6))
    if k > 0:
        sil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sil)
        cx, base = 420, 1000
        sd.ellipse([cx - 52, base - 560, cx + 52, base - 440], fill=(10, 10, 14, int(255 * k)))
        sd.rounded_rectangle([cx - 90, base - 450, cx + 90, base - 180], radius=40, fill=(10, 10, 14, int(255 * k)))
        sd.polygon([(cx - 70, base - 190), (cx + 70, base - 190), (cx + 50, base), (cx - 50, base)], fill=(10, 10, 14, int(255 * k)))
        sd.ellipse([cx - 64, base - 600, cx + 64, base - 470], fill=(10, 10, 14, int(255 * k)))   # объём волос
        img = Image.alpha_composite(img.convert("RGBA"), sil.filter(ImageFilter.GaussianBlur(1))).convert("RGB")
    img = char(img, DR.front((W, H), 150, 1300, .86, t, ("down", "down"), "idle", "shock" if k > .3 else "tense", (.8, 0), courier=True), "s12", tint=False)
    counter(img, 1247)
    img = zoom(img, 1.0 + .15 * min(1, t / max(1, vo_end)), .55, .45)
    if t > vo_end + .5:
        a = min(1, (t - vo_end - .5) / .3)
        img = Image.blend(img, Image.new("RGB", (W, H)), a)
        if a >= 1:
            dd = ImageDraw.Draw(img)
            f3 = F(60, FONT_SUB)
            for j, line in enumerate(("серия 3", "скоро")):
                dd.text(((W - f3.getlength(line)) / 2, 520 + j * 80), line, font=f3, fill=YELLOW, stroke_width=4, stroke_fill=(58, 50, 14))
    return img


if __name__ == "__main__":
    if os.environ.get("TIMELINE"):   # таймлайн для Blender
        import json
        out = {"scenes": [{"name": "e2_" + n, "start": st, "length": l, "cue_start": sc[0][0], "cue_dur": sc[0][2]} for n, st, l, sc in scenes]}
        json.dump(out, open(os.environ["TIMELINE"], "w"), indent=1)
        print("timeline saved", round(TOTAL, 1))
        sys.exit()
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .2, span("s04")[0] + .6, span("s08")[0] + .1, span("s09")[0] + .5, span("s10")[0] + .1,
              span("s12")[0] + .3])
