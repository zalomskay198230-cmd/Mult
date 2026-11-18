"""«ФУДТРАК С НУЛЯ». Серия 1 (~40 с) в игрушечном 3D: кадры из Blender (render3d/ft3d.py) + интерфейс стрима поверх.
1) TIMELINE=../render3d/tl_s01.json python3 s01_3d.py ../tts/s01_40 x      — таймлайн для Blender
2) blender -b -P ../render3d/ft3d.py -- scenes ../render3d/tl_s01.json ../render3d/frames_s01 [samples] [scale]
3) python3 s01_3d.py ../tts/s01_40 ../seriya01.mp4                          — сборка
4) реклама: python3 ../../den365/render/add_popup.py ../seriya01.mp4 ../seriya01_reklama.mp4 <сек> 250 freeze 0.9"""
import os, sys, math, random, json
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
D365 = os.path.join(ROOT, "den365", "render")
sys.path.insert(0, os.path.join(ROOT, "vakhta", "render"))
sys.path.insert(0, D365)
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(ROOT, "den365", "tts", "s01_golos"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("d365_s01", os.path.join(D365, "seriya01.py"))
E1 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(E1)          # субтитры капсом с цветными словами, плашки
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01_40"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01.mp4"
from toonlib import setup, run, span, dur, shake, FONT_SUB, FONT_B
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = toonlib.W, toonlib.H
pill, fade_in, ease, F = E1.pill, E1.fade_in, E1.ease, E1.F
YEL, RED, WHITE, GREEN, BLUE = E1.YEL, E1.RED, E1.WHITE, E1.GREEN, E1.BLUE
FR = os.path.join(HERE, "..", "render3d", "frames_s01")

LINES = {
    "01": "Слушай, меня ^уволили^ из кафе в понедельник. А во вторник я купил *фургон*. На все деньги, брат.",
    "02": "*Сорок* *тысяч* рублей. Девяносто восьмого года. Без одной ^фары^. Вах, *красавец*.",
    "03": "Поэтому теперь всё решаете *вы*, дорогие.",
    "04": "Каждый ваш *лайк* — *десять* *рублей* в кассу. Лайкнул — помог. Клянусь, всё на кухню пойдёт.",
    "05": "Открываю дверь — а там ^хлам^. До потолка. Шины, коробки, старый матрас. *Вах*.",
    "06": "Прежний хозяин, похоже, здесь *жил*. Даже календарь на стене — девяносто ^восьмого^ года.",
    "07": "С чего начинаем *ремонт*? *Пол*, *плита* или *окно*?",
    "08": "Пишите в *комментариях*, дорогие. Как скажете — так и сделаю.",
}
PLAN = [(f"s{k}", [(k, 0.05)], 0.15) for k in LINES]
PLAN[0] = ("s01", [("01", 0.05)], 0.15)
PLAN[-1] = ("s08", [("08", 0.05)], .9)
setup(LINES, PLAN)

if os.environ.get("TIMELINE"):   # таймлайн для Blender: длины сцен и когда герой говорит (для рта)
    out = {"scenes": [{"name": n, "length": l, "talk": [[s, s + d] for s, c, d in sc]} for n, st, l, sc in toonlib.scenes]}
    json.dump(out, open(os.environ["TIMELINE"], "w"), indent=1)
    print("timeline", os.environ["TIMELINE"], f"{toonlib.TOTAL:.1f} c")
    sys.exit()

_cache = {}


def frame3d(name, t):
    f = int(t * 12)
    while f >= 0:
        p = os.path.join(FR, f"{name}_{f:04d}.png")
        if os.path.exists(p):
            break
        f -= 1
    if p not in _cache:
        if len(_cache) > 8:
            _cache.clear()
        _cache[p] = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    return _cache[p].copy()


NICKS = ["ashot_77", "lena.k", "vova_grill", "nastya", "dimon", "kot_v_sapogah", "marat05", "olya_m"]
MSGS = ["вах фургон", "лайк брат", "шаурму давай", "матрас на выброс", "пельмени топ", "где фара?", "бургеры!!!",
        "начни с пола", "держи лайк", "плиту чини!!", "красавец фургон", "тимур красава"]


PAIRED = False   # True — ник и сообщение идут парами (реальные комментарии)


def stream_ui(img, t, cash=0):
    d = ImageDraw.Draw(img)
    on = int(t * 2) % 2 == 0
    d.rounded_rectangle([30, 44, 196, 86], radius=10, fill=(214, 30, 40))
    d.ellipse([46, 57, 62, 73], fill=WHITE if on else (255, 170, 170))
    d.text((72, 53), "В ЭФИРЕ", font=F(22, FONT_SUB), fill=WHITE)
    v = 1180 + int(t * 23) % 300
    lay = img.crop((30, 94, 196, 126)).point(lambda q: q * .4); img.paste(lay, (30, 94))
    d.text((42, 99), f"зрители {v}", font=F(18), fill=(230, 230, 236))
    x0 = W - 30 - 300   # касса в стиле шкал; под ней встанет значок рекламы
    lay = img.crop((x0, 40, x0 + 300, 124)).point(lambda q: q * .4); img.paste(lay, (x0, 40))
    d.rounded_rectangle([x0, 40, x0 + 300, 124], radius=14, outline=(110, 150, 210), width=3)
    d.text((x0 + 150 - F(20).getlength("КАССА") / 2, 48), "КАССА", font=F(20), fill=(200, 216, 240))
    txt = f"{cash:,} ₽".replace(",", " ")
    d.text((x0 + 150 - F(42, FONT_SUB).getlength(txt) / 2, 70), txt, font=F(42, FONT_SUB), fill=YEL)
    base = int(t * 1.4)   # лента комментариев
    for i in range(3):
        j = base + i
        nick = NICKS[j % len(NICKS)]
        msg = MSGS[j % len(MSGS)] if PAIRED else MSGS[(j * 5) % len(MSGS)]
        y = 1150 + i * 34
        fn, fm = F(19, FONT_SUB), F(19)
        w = fn.getlength(nick + ": ") + fm.getlength(msg) + 24
        lay = img.crop((24, y - 4, int(24 + w), y + 27)).point(lambda q: q * .45); img.paste(lay, (24, y - 4))
        d.text((36, y), nick + ":", font=fn, fill=(160, 205, 255))
        d.text((36 + fn.getlength(nick + ": "), y), msg, font=fm, fill=(240, 240, 244))


def stamp(img, txt, t, t0, col=RED, y=300, rot=-8, size=64):
    """штамп «БАЦ!» как в референсе"""
    if t < t0:
        return
    k = min(1, (t - t0) / .15)
    f = F(int(size * (1.6 - .6 * k)), FONT_SUB)
    w = int(f.getlength(txt)) + 40
    lay = Image.new("RGBA", (w, size * 2), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((20, 10), txt, font=f, fill=col + (255,), stroke_width=6, stroke_fill=(20, 16, 18, 255))
    lay = lay.rotate(rot, expand=True)
    img.paste(lay, (int(W / 2 - lay.width / 2), y), lay)


def money_rain(img, t, t0, n=24):
    if t < t0:
        return
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for i in range(n):
        x0, sp, ph = rnd.uniform(0, W), rnd.uniform(260, 420), rnd.uniform(0, 1.5)
        y = -80 + (t - t0 + ph) * sp
        if y > H:
            continue
        a = (t * 3 + i) % 6.28
        w_, h_ = 70 * abs(math.cos(a)) + 12, 34
        d.rectangle([x0 - w_ / 2, y - h_ / 2, x0 + w_ / 2, y + h_ / 2], fill=(110, 180, 90), outline=(60, 110, 50), width=2)


def vote_cards(img, a=1.0):
    """одна карточка: с чего начинаем ремонт"""
    lay = img.copy()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([60, 250, W - 60, 640], radius=24, fill=(16, 18, 26), outline=(110, 150, 210), width=4)
    f0 = F(40, FONT_SUB)
    d.text(((W - f0.getlength("РЕМОНТ: С ЧЕГО?")) / 2, 274), "РЕМОНТ: С ЧЕГО?", font=f0, fill=WHITE)
    for i, (txt, col) in enumerate((("ПОЛ", (170, 120, 70)), ("ПЛИТА", (120, 124, 132)), ("ОКНО", (90, 150, 220)))):
        y = 346 + i * 92
        d.ellipse([110, y, 176, y + 66], fill=col)
        d.text((143 - F(38, FONT_SUB).getlength(str(i + 1)) / 2, y + 9), str(i + 1), font=F(38, FONT_SUB), fill=WHITE)
        d.text((200, y + 8), txt, font=F(46, FONT_SUB), fill=WHITE)
    return Image.blend(img, lay, a)


# ---------- сцены ----------
def s01(t, L, cue):
    p = (t - cue["01"]) / dur("01.mp3")
    img = frame3d("s01", t)
    pill(img, "ПН: УВОЛЕН" if p < .45 else "ВТ: КУПИЛ ФУРГОН", W / 2, 200, (150, 30, 36) if p < .45 else (30, 110, 60), WHITE, 34)
    stamp(img, "УВОЛЕН!", t, .4, RED, 300) if p < .45 else None
    stream_ui(img, t)
    return img


def s02(t, L, cue):
    p = (t - cue["02"]) / dur("02.mp3")
    img = frame3d("s02", t)
    pill(img, "−40 000 ₽", W / 2, 200, (150, 30, 36), WHITE, 40)
    if p > .45:
        pill(img, "1998 · без фары", W / 2, 280, (20, 22, 30), YEL, 28)
    if p > .75:
        stamp(img, "ВАХ!", t, cue["02"] + dur("02.mp3") * .75, YEL, 360)
    stream_ui(img, t)
    return img


def s03(t, L, cue):
    img = frame3d("s03", t)
    pill(img, "РЕШАЕТЕ ВЫ", W / 2, 210, (20, 22, 30), YEL, 46)
    stream_ui(img, t)
    return img


def s04(t, L, cue):
    p = (t - cue["04"]) / dur("04.mp3")
    img = frame3d("s04", t)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 300
    r = 64 * (1 + .08 * abs(math.sin(t * 6)))
    d.ellipse([cx - r, cy - r * .7, cx, cy + r * .3], fill=(240, 50, 70))
    d.ellipse([cx, cy - r * .7, cx + r, cy + r * .3], fill=(240, 50, 70))
    d.polygon([(cx - r * .97, cy - r * .05), (cx + r * .97, cy - r * .05), (cx, cy + r * .95)], fill=(240, 50, 70))
    f = F(50, FONT_SUB)
    d.text((cx - f.getlength("1 ЛАЙК = 10 ₽") / 2, 400), "1 ЛАЙК = 10 ₽", font=f, fill=WHITE, stroke_width=5, stroke_fill=(14, 12, 16))
    for i in range(6):
        k = ((t * .9) + i / 6) % 1
        x = cx + (W - 180 - cx) * k + 30 * math.sin(i * 2 + t * 3)
        y = cy - (cy - 90) * k
        d.text((x, y), "+10 ₽", font=F(26, FONT_SUB), fill=GREEN, stroke_width=3, stroke_fill=(14, 12, 16))
    if p > .45:
        pill(img, "ЛАЙКНУЛ — ПОМОГ", W / 2, 500, (214, 30, 40), WHITE, 32)
    stream_ui(img, t)
    return img


def s05(t, L, cue):
    p = (t - cue["05"]) / dur("05.mp3")
    img = frame3d("s05", t)
    if p > .2:
        stamp(img, "ХЛАМ!", t, cue["05"] + dur("05.mp3") * .2, RED, 260, -6)
    if p > .5:
        pill(img, "шины · коробки · матрас", W / 2, 420, (20, 22, 30), WHITE, 28)
    stream_ui(img, t)
    return shake(img, t, 4 if .2 < p < .26 else 0)


def s06(t, L, cue):
    p = (t - cue["06"]) / dur("06.mp3")
    img = frame3d("s06", t)
    if p > .55:   # год на календаре
        f = F(150, FONT_SUB)
        ImageDraw.Draw(img).text(((W - f.getlength("1998")) / 2, 250), "1998", font=f, fill=(200, 40, 40), stroke_width=6, stroke_fill=(250, 246, 236))
        if p > .7:
            d = ImageDraw.Draw(img)
            for i, (qx, qy) in enumerate(((90, 520), (600, 480))):
                if int(t * 3 + i) % 3:
                    d.text((qx, qy), "?", font=F(90, FONT_SUB), fill=YEL, stroke_width=5, stroke_fill=(14, 12, 16))
    stream_ui(img, t)
    return img


def s07(t, L, cue):
    img = frame3d("s07", t)
    img = vote_cards(img, fade_in(t, .05))
    stream_ui(img, t)
    return img


def s08(t, L, cue):
    img = frame3d("s08", t)
    img = vote_cards(img)
    d = ImageDraw.Draw(img)
    pop = 1 + .05 * math.sin(t * 8)
    fp = F(int(32 * pop), FONT_SUB)
    txt = "ПИШИ В КОММЕНТАРИЯХ"
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 24, 780, W / 2 + fp.getlength(txt) / 2 + 24, 844], radius=30, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 792), txt, font=fp, fill=(20, 20, 24))
    stream_ui(img, t)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN},
        hits=[span("s01")[0] + .4, span("s05")[0] + span("s05")[1] * .2])
