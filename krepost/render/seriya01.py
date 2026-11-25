"""«КРЕПОСТЬ». Серия 1: конец света, гараж, сутки до темноты — строим ворота. Плоский стиль (flatworld).
Мат в субтитрах скрыт звёздочками (символ § в тексте → *). Запуск: python3 seriya01.py ../tts/s01 ../seriya01.mp4"""
import os, sys, math, random, importlib.util
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
_sp.loader.exec_module(E1)
_sp2 = importlib.util.spec_from_file_location("bs_s01", os.path.join(ROOT, "bezsveta", "render", "seriya01.py"))
sys.argv[1:3] = [os.path.join(ROOT, "morg", "tts", "s01"), "x.mp4"]
toonlib.TTS = sys.argv[1]
B = importlib.util.module_from_spec(_sp2)
_sp2.loader.exec_module(B)        # красивые карточки выбора
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s01"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya01.mp4"
from toonlib import setup, run, span, dur, shake, glow, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import flatworld as FW
from flatworld import SD, chibi, OUT, world, GR

W, H, F = toonlib.W, toonlib.H, E1.F
YEL, RED, WHITE, GREEN = E1.YEL, E1.RED, E1.WHITE, E1.GREEN
pill, ease, V = E1.pill, E1.ease, E1.V

FW.CHAR["hero"] = dict(skin=(232, 186, 150), hair=(52, 40, 34), top=(90, 98, 84), pants=(50, 54, 64), shoes=(60, 50, 44), style="short", beard=(70, 54, 44))
FW.CHAR["zom"] = dict(skin=(150, 176, 140), hair=(50, 50, 46), top=(70, 70, 76), pants=(46, 46, 52), shoes=(36, 36, 40), style="spiky")

LINES = {
    "01": "Мир закончился ^вчера^. А у меня — *гараж*, *сварка* и сутки до ^темноты^.",
    "02": "Ночью они ^выходят^. Днём — прячутся.",
    "03": "Гараж — железная коробка. Но ворота — ^жесть^, ёб твою м§§§. Их пробьют с первого раза.",
    "04": "Сегодня строю *ворота*. Три листа стали с соседней стройки. Каждый — килограмм *сорок*, с§§а. Сварка. Засов из арматуры.",
    "05": "Восемь часов. Руки ^трясутся^.",
    "06": "Солнце ^садится^.",
    "07": "Первый ^удар^ в ворота. Второй. *Держат*.",
    "08": "Б§§… *держат*.",
    "09": "Завтра — одно из двух: *окна* на втором ярусе — или *колодец* с водой. ^Решай^.",
}
PLAN = [(f"k{k}", [(k, 0.04)], 0.12) for k in LINES]
PLAN[0] = ("k01", [("01", 0.0)], 0.15)
PLAN[6] = ("k07", [("07", 0.05)], 0.3)
PLAN[-1] = ("k09", [("09", 0.05)], 1.0)
setup(LINES, PLAN)

# субтитры: как в den365, но § → * (цензура мата)
F_CAP = ImageFont.truetype(FONT_SUB, 54)


def _tokens(text):
    out = []
    for w in text.split():
        col = YEL if "*" in w else (RED if "^" in w else WHITE)
        out.append((w.replace("*", "").replace("^", "").replace("§", "*").upper(), col))
    return out


def draw_caps(img, t):
    for s, e, text, _ in toonlib.SUBS:
        if not (s <= t < e):
            continue
        toks = _tokens(text)
        lines, cur = [], []
        for tok in toks:
            if F_CAP.getlength(" ".join(w for w, _ in cur + [tok])) > W - 90 and cur:
                lines.append(cur); cur = [tok]
            else:
                cur.append(tok)
        lines.append(cur)
        d = ImageDraw.Draw(img)
        y0 = int(H * .75) - len(lines) * 33
        for i, ln in enumerate(lines):
            x = (W - F_CAP.getlength(" ".join(w for w, _ in ln))) / 2
            for w, col in ln:
                d.text((x, y0 + i * 66), w, font=F_CAP, fill=col, stroke_width=6, stroke_fill=(8, 8, 10))
                x += F_CAP.getlength(w + " ")
        return


toonlib.draw_subs = draw_caps

# ---------- HUD «до темноты» и «построено» ----------
DARK_H = {"k01": 24, "k02": 24, "k03": 23, "k04": 14, "k05": 3, "k06": 0, "k07": 0, "k08": 0, "k09": 0}
BUILT = {"k05": True, "k06": True, "k07": True, "k08": True, "k09": True}


def hud(img, name, t):
    h = DARK_H[name]
    d = ImageDraw.Draw(img)
    for i, (lab, val, col) in enumerate((("ДО ТЕМНОТЫ", f"{h:02d}:00" if h else "НОЧЬ", RED if h < 4 else YEL),
                                         ("ПОСТРОЕНО", "ворота ✓" if BUILT.get(name) or (name == "k04" and t > 6) else "—", GREEN))):
        x0 = 40 + i * 340
        lay = img.crop((x0, 40, x0 + 300, 124)).point(lambda v: v * .4)
        img.paste(lay, (x0, 40))
        d.rounded_rectangle([x0, 40, x0 + 300, 124], radius=14, outline=(110, 150, 210), width=3)
        d.text((x0 + 150 - F(20).getlength(lab) / 2, 48), lab, font=F(20), fill=(200, 216, 240))
        fv = F(38, FONT_SUB)
        d.text((x0 + 150 - fv.getlength(val) / 2, 72), val, font=fv, fill=col)


GX0, GX1, GY0 = 800, 1140, GR - 220   # гараж в мире flatworld
GATE = (832, GR - 160, 990, GR - 2)


def gate(d, kind="tin", dents=0, t=0.0):
    x0, y0, x1, y1 = GATE
    if kind == "tin":   # тонкая жесть, ржавчина, щели
        d.rectangle([x0, y0, x1, y1], fill=(140, 120, 100), outline=OUT, width=3)
        for y in range(int(y0) + 10, int(y1), 22):
            d.line([x0 + 4, y, x1 - 4, y + 3], fill=(110, 92, 76), width=3)
        d.rectangle([x0 + 60, y0 + 40, x0 + 90, y0 + 46], fill=(20, 20, 22))
        d.rectangle([x0 + 100, y0 + 90, x0 + 130, y0 + 95], fill=(20, 20, 22))
    else:               # три листа стали + засов
        for k in range(3):
            d.rectangle([x0 + k * (x1 - x0) / 3, y0, x0 + (k + 1) * (x1 - x0) / 3, y1], fill=(110, 116, 126), outline=OUT, width=3)
            d.line([x0 + (k + 1) * (x1 - x0) / 3, y0, x0 + (k + 1) * (x1 - x0) / 3, y1], fill=(220, 200, 150), width=3)   # сварной шов
        d.rectangle([x0 - 6, (y0 + y1) / 2 - 6, x1 + 6, (y0 + y1) / 2 + 6], fill=(150, 90, 60), outline=OUT, width=2)   # засов
        rnd = random.Random(5)
        for i in range(dents):
            cx, cy = rnd.uniform(x0 + 20, x1 - 20), rnd.uniform(y0 + 20, y1 - 20)
            d.ellipse([cx - 14, cy - 10, cx + 14, cy + 10], fill=(84, 88, 96), outline=OUT, width=2)


def sparks(img, x, y, t, n=26):
    d = ImageDraw.Draw(img)
    rnd = random.Random(int(t * 24))
    for _ in range(n):
        a = rnd.uniform(-math.pi, 0)
        r = rnd.uniform(10, 80)
        d.line([x, y, x + r * math.cos(a), y + r * math.sin(a)], fill=(255, rnd.randint(180, 240), 80), width=3)
    glow(img, (x, y), 40, (255, 220, 150), 1.0)


def zombies(d, t, n=6, y=GR - 4, x0=1250, spread=60, s=.9, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + i * spread + rnd.uniform(-10, 10) + 8 * math.sin(t * 2 + i)
        chibi(d, "zom", x, y, s, t + i, "angry", -1, walk=True)


# ---------- сцены ----------
def k01(t, L, cue):   # холодный старт: закат, пустой город, гараж
    v = V(world(day=False, lights=False), (900, 700, 1.0), (980, 760, 1.5), t / L)
    gate(v.d, "tin")
    chibi(v.d, "hero", 760, GR - 4, 1.0, t, "neutral", 1)
    img = v.out()
    img = Image.blend(img, Image.new("RGB", (W, H), (200, 90, 40)), .18)
    E1.big = B.M.big
    B.M.big(img, "КОНЕЦ СВЕТА", 180, RED, 92)
    hud(img, "k01", t)
    return img


def k02(t, L, cue):   # ночью — они
    p = (t - cue["02"]) / dur("02.mp3")
    night = p < .55
    v = V(world(day=not night, lights=False), (1250, 800, 1.3))
    if night:
        zombies(v.d, t, 7, x0=1050, spread=70)
    img = v.out()
    if night:
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 20)), .35)
        pill(img, "НОЧЬЮ", W / 2, 180, (150, 30, 30), WHITE, 34)
    else:
        pill(img, "ДНЁМ — ПУСТО", W / 2, 180, (20, 22, 30), WHITE, 34)
    hud(img, "k02", t)
    return img


def k03(t, L, cue):   # жестяные ворота крупно
    v = V(world(day=True, lights=False), (911, GR - 80, 3.0))
    gate(v.d, "tin")
    img = v.out()
    p = (t - cue["03"]) / dur("03.mp3")
    if p > .3:
        B.M.big(img, "ЖЕСТЬ", 200, RED, 110)
    hud(img, "k03", t)
    return img


def k04(t, L, cue):   # стройка: тащит листы, варит
    p = (t - cue["04"]) / dur("04.mp3")
    if p < .45:   # тащит лист со стройки
        v = V(world(day=True, lights=False, nb="hidden"), (1180, 820, 1.7))
        x = 1380 - 260 * (p / .45)
        chibi(v.d, "hero", x, GR - 4, 1.0, t, "angry", -1, walk=True, arm="up")
        v.d.rectangle([x - 70, GR - 150, x + 70, GR - 120], fill=(130, 136, 146), outline=OUT, width=3)
        img = v.out()
        pill(img, "3 ЛИСТА · по 40 кг", W / 2, 180, (20, 22, 30), YEL, 30)
    else:         # варит ворота
        v = V(world(day=True, lights=False), (900, GR - 90, 2.4))
        gate(v.d, "steel")
        chibi(v.d, "hero", 1040, GR - 4, 1.0, t, "angry", -1, arm="shovel")
        img = v.out()
        sx, sy = v.screen(990, GR - 80 - 40 * math.sin(t * 2))
        sparks(img, sx, sy, t)
        pill(img, "СВАРКА", W / 2, 180, (20, 22, 30), YEL, 34)
    hud(img, "k04", t + p * 8)
    return img


def k05(t, L, cue):   # устал
    v = V(world(day=True, lights=False), (900, GR - 60, 2.6))
    gate(v.d, "steel")
    chibi(v.d, "hero", 920, GR - 4, 1.0, t, "sad", 0)
    img = v.out()
    img = Image.blend(img, Image.new("RGB", (W, H), (220, 110, 50)), .15)
    img = shake(img, t, 1.5)
    pill(img, "8 ЧАСОВ", W / 2, 180, (20, 22, 30), WHITE, 34)
    hud(img, "k05", t)
    return img


def k06(t, L, cue):   # закат
    k = t / L
    v = V(world(day=False, lights=False), (980, 700, 1.2))
    gate(v.d, "steel")
    zombies(v.d, t, 5, x0=1300, spread=60, s=.8)
    img = v.out()
    img = Image.blend(img, Image.new("RGB", (W, H), (10, 10, 30)), .3 + .4 * k)
    hud(img, "k06", t)
    return img


def k07(t, L, cue):   # удары в ворота изнутри
    p = (t - cue["07"]) / dur("07.mp3")
    hits = sum(p > q for q in (.05, .35))
    img = Image.new("RGB", (W * 2, H * 2), (30, 30, 36))
    d = SD(img, 0, 0, 2)
    d.rectangle([0, 0, W, H], fill=(36, 36, 42))
    for k in range(3):   # ворота изнутри крупно
        d.rectangle([60 + k * 200, 200, 260 + k * 200, 1100], fill=(96, 100, 110), outline=OUT, width=6)
    d.rectangle([40, 640, 680, 680], fill=(150, 90, 60), outline=OUT, width=4)
    rnd = random.Random(3)
    for i in range(hits * 2):
        cx, cy = rnd.uniform(140, 580), rnd.uniform(300, 1000)
        d.ellipse([cx - 40, cy - 30, cx + 40, cy + 30], fill=(130, 134, 144), outline=OUT, width=4)
    img = img.resize((W, H), Image.LANCZOS)
    glow(img, (360, 1240), 200, (255, 180, 90), .3)   # лампа в гараже
    if hits:
        B.M.big(img, "БАМ!", 160, RED, 110)
    if p > .75:
        B.M.big(img, "ДЕРЖАТ", 300, GREEN, 96)
    hud(img, "k07", t)
    return shake(img, t, 12 if any(0 < p - q < .06 for q in (.05, .35)) else 0)


def k08(t, L, cue):   # облегчение
    img = Image.new("RGB", (W * 2, H * 2), (30, 30, 36))
    d = SD(img, 0, 0, 2)
    d.rectangle([0, 0, W, H], fill=(36, 36, 42))
    chibi(d, "hero", 360, 1500, 6.5, t, "smile", 0)
    img = img.resize((W, H), Image.LANCZOS)
    glow(img, (360, 1200), 220, (255, 180, 90), .3)
    hud(img, "k08", t)
    return img


def card_art_k(kind):
    if kind == "windows":
        v = V(world(day=True, lights=False), (970, GR - 160, 2.2))
        d = v.d
        d.rectangle([GX0 + 20, GY0 - 120, GX1 - 20, GY0], fill=(110, 116, 126), outline=OUT, width=4)   # второй ярус
        for x in (GX0 + 60, GX0 + 200):
            d.rectangle([x, GY0 - 90, x + 60, GY0 - 40], fill=(20, 24, 36), outline=OUT, width=4)
            for k in range(4):
                d.line([x + 8 + k * 14, GY0 - 90, x + 8 + k * 14, GY0 - 40], fill=(150, 90, 60), width=4)   # решётка
        gate(d, "steel")
        return v.out()
    v = V(world(day=True, lights=False), (900, GR - 40, 2.4))
    d = v.d
    d.ellipse([720, GR - 30, 880, GR + 30], fill=(90, 90, 96), outline=OUT, width=4)   # колодец
    d.ellipse([740, GR - 20, 860, GR + 20], fill=(30, 60, 100))
    d.line([730, GR - 30, 730, GR - 140], fill=(120, 84, 56), width=8)
    d.line([870, GR - 30, 870, GR - 140], fill=(120, 84, 56), width=8)
    d.line([720, GR - 140, 880, GR - 140], fill=(120, 84, 56), width=8)
    d.rectangle([790, GR - 110, 812, GR - 80], fill=(150, 150, 156), outline=OUT, width=2)   # ведро
    gate(d, "steel")
    return v.out()


def k09(t, L, cue):
    B._cards["win"] = B._cards.get("win") or card_art_k("windows")
    B._cards["well"] = B._cards.get("well") or card_art_k("well")
    bg = V(world(day=False, lights=False), (980, 760, 1.2)).out().filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(bg, Image.new("RGB", (W, H)), .55)
    d = ImageDraw.Draw(img)
    f = F(44, FONT_SUB)
    d.text(((W - f.getlength("ЧТО СТРОИМ ЗАВТРА?")) / 2, 170), "ЧТО СТРОИМ ЗАВТРА?", font=f, fill=WHITE, stroke_width=4, stroke_fill=(8, 8, 10))
    pulse = .5 + .5 * math.sin(t * 4)
    img = B.pretty_card(img, 36, 300, 310, 470, "win", "1", "Окна\nна втором ярусе", (240, 170, 60), min(1, t / .3), pulse)
    img = B.pretty_card(img, 374, 300, 310, 470, "well", "2", "Колодец\nс водой", (90, 150, 230), min(1, max(0, t - .25) / .3), 1 - pulse)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 40, 495, W / 2 + 40, 575], fill=YEL, outline=(10, 10, 14), width=5)
    fi = F(24, FONT_SUB)
    d.text((W / 2 - fi.getlength("ИЛИ") / 2, 520), "ИЛИ", font=fi, fill=(20, 20, 24))
    p = (t - cue["09"]) / dur("09.mp3")
    if p > .7:
        B.M.big(img, "РЕШАЙ", 800, RED, 84)
    hud(img, "k09", t)
    return img


if __name__ == "__main__":
    run({n: globals()[n] for n, *_ in PLAN})
