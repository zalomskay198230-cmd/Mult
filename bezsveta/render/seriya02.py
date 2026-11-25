"""«БЕЗ СВЕТА». Серия 2 (зрители выбрали «идти к свету»). Герой — спрайты из утверждённого листа персонажа
(bezsveta/sprites, вырезаны из geroy_list.jpg), фоны — ночной город из серии 1.
Запуск: python3 seriya02.py ../tts/s02 ../seriya02.mp4"""
import os, sys, math, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "vakhta", "render"))
import toonlib

_argv = sys.argv[:]
sys.argv[1:3] = [os.path.join(HERE, "..", "tts", "s01"), "x.mp4"]
toonlib.TTS = sys.argv[1]
_sp = importlib.util.spec_from_file_location("bs_s01", os.path.join(HERE, "seriya01.py"))
B = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(B)
sys.argv[:] = _argv
toonlib.TTS = sys.argv[1] if len(sys.argv) > 1 else "../tts/s02"
toonlib.OUT = sys.argv[2] if len(sys.argv) > 2 else "../seriya02.mp4"
from toonlib import setup, run, span, dur, shake, glow, FONT_SUB
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
import numpy as np

M = B.M
W, H, F = B.W, B.H, B.F
RED, YEL, WHITE = B.RED, B.YEL, B.WHITE
SPR = os.path.join(HERE, "..", "sprites")
_spr = {}


def sprite(name):
    if name not in _spr:
        _spr[name] = Image.open(os.path.join(SPR, name + ".png")).convert("RGBA")
    return _spr[name]


from flatworld import SD, chibi
FACE = {"e_scared": "shock", "e_whisper": "sad", "e_brave": "angry", "e_calm": "smile", "front": "neutral", "q34": "neutral", "side": "neutral"}


def hero(img, name, cx, bottom, height, t=0.0, tint=None, flip=False, bob=0.0, shake_=0.0, light=None):
    """свой человечек (как в серии 1): крупные планы — большой масштаб, ходьба — ноги шагают"""
    big = img.resize((W * 2, H * 2), Image.BICUBIC)
    d = SD(big, 0, 0, 2)
    s = height / 125.0
    walk = bob > 0
    look = (1 if not flip else -1) if name in ("side", "q34") else 0
    arm = "phone" if name in ("front", "side", "q34") and light is not None else None
    if name == "e_whisper":
        arm = "phone"
    x = cx + (shake_ * math.sin(t * 37) if shake_ else 0)
    chibi(d, "hero", x, bottom, s, t, FACE.get(name, "neutral"), look, walk=walk, arm=arm)
    out = big.resize((W, H), Image.LANCZOS)
    if tint:   # ночной тон только на персонажа не делаем — он и так подсвечен сценой
        pass
    if light:
        glow(out, (cx, bottom - height * .78), height * .35, (255, 200, 130), .5 * light)
    return out


LINES = {
    "01": "Фонарик ^погас^. И я услышал ^шаги^.",
    "02": "Пять минут назад. Вы выбрали — идти к *свету*.",
    "03": "Выхожу из подъезда. Темнота — не видно рук. Фонарик телефона — *двенадцать* процентов.",
    "04": "На улице тихо. ^Слишком^ тихо. Ни машин. Ни собак.",
    "05": "До той многоэтажки — *три* квартала.",
    "06": "На втором квартале — фонарик ^гаснет^.",
    "07": "И в темноте — шаги. ^Не^ ^мои^. Идут в ногу со мной.",
    "08": "Останавливаюсь. Шаги — ^тоже^.",
    "09": "А свет на крыше мигнул. *Три* раза. Будто ^увидел^ меня.",
    "10": "Бежать к *свету* — или вернуться *домой*? ^Решай^. И отправь другу — он бы побежал?",
}
PLAN = [(f"z{k}", [(k, 0.04)], 0.12) for k in LINES]
PLAN[0] = ("z01", [("01", 0.0)], 0.2)
PLAN[7] = ("z08", [("08", 0.05)], 0.7)
PLAN[-1] = ("z10", [("10", 0.05)], 1.0)
setup(LINES, PLAN)
B.HOURS.update({f"z{k}": 12 for k in LINES})


def street(night=1.0, roof=True, seed=7):
    """ночная улица от первого лица: дорога в перспективу, тёмные дома, вдали свет на крыше"""
    img = B.city(lit=0, night=night, roof_light=roof, seed=seed)
    d = ImageDraw.Draw(img)
    d.polygon([(0, H), (W, H), (W * .58, 1000), (W * .42, 1000)], fill=(22, 22, 28))
    for i in range(6):
        k = i / 6
        y = 1000 + (H - 1000) * k ** 1.5
        w = 6 + 30 * k
        d.rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 6 + 20 * k], fill=(60, 60, 64))
    return img


def flashlight_beam(img, cx, cy, tx, ty, spread, a):
    if a <= 0:
        return img
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(cx, cy), (tx - spread, ty), (tx + spread, ty)], fill=int(a))
    img.paste(Image.new("RGB", (W, H), (255, 240, 205)), (0, 0), m.filter(ImageFilter.GaussianBlur(26)))
    return img


def darken(img, k):
    return ImageEnhance.Brightness(img).enhance(k)


def step_text(img, t, t0, n, y=150):
    for i in range(n):
        if t > t0 + i * .5:
            a = min(1, (t - t0 - i * .5) / .1)
            M.big(img, "ШАГ", y + i * 80, (int(220 * a), int(220 * a), int(226 * a)), 64)


# ---------- сцены ----------
def z01(t, L, cue):   # холодный старт: фонарик гаснет, лицо в ужасе
    p = (t - cue["01"]) / dur("01.mp3")
    img = darken(street(), .45)
    on = p < .35 and int(t * 14) % 3
    img = hero(img, "e_scared", W / 2, H + 120, 1000, t, tint=(.55, .6, .85), light=.9 if on else .0, shake_=4)
    if not on:
        img = darken(img, .55)
    if p > .5:
        M.big(img, "ШАГИ", 160, RED, 110)
    B.blackout_timer(img, "z01", t)
    return shake(img, t, 5 if .35 < p < .45 else 0)


def z02(t, L, cue):   # выбор зрителей
    img = darken(B.city(lit=0, night=1.0, roof_light=True), .9)
    img = img.filter(ImageFilter.GaussianBlur(3))
    img = hero(img, "e_brave", W / 2, H + 120, 1000, t, tint=(.62, .68, .95))
    M.big(img, "5 МИНУТ НАЗАД", 190, WHITE, 56)
    d = ImageDraw.Draw(img)
    k = min(1, t / 1.0)
    v = .3 + (.62 - .3) * k
    x0, y0, x1 = 40, 110, W - 40
    d.rounded_rectangle([x0, y0, x1, y0 + 44], radius=10, fill=(20, 24, 28), outline=(200, 210, 210), width=2)
    d.rounded_rectangle([x0 + 4, y0 + 4, x0 + 4 + (x1 - x0 - 8) * v, y0 + 40], radius=8, fill=(240, 170, 60))
    d.text((x0 + 16, y0 + 10), "ИДТИ К СВЕТУ", font=F(20, FONT_SUB), fill=WHITE)
    d.text((x1 - 70, y0 + 10), f"{int(v * 100)}%", font=F(22, FONT_SUB), fill=WHITE)
    B.blackout_timer(img, "z02", t)
    return img


def z03(t, L, cue):   # выходит из подъезда с фонариком
    p = (t - cue["03"]) / dur("03.mp3")
    img = darken(street(), .5)
    d = ImageDraw.Draw(img)
    d.rectangle([60, 560, 300, 1060], fill=(26, 26, 30), outline=(50, 50, 56), width=8)   # дверь подъезда
    d.rectangle([80, 520, 280, 556], fill=(40, 40, 46))
    img = hero(img, "front", 180 + 120 * M.ease(p), 1080, 470, t, tint=(.66, .7, .95), bob=6)
    img = flashlight_beam(img, 230 + 120 * M.ease(p), 820, 420, 1280, 170, 70)
    if p > .55:
        M.tag(img, "🔋 12%".replace("🔋 ", "БАТАРЕЯ "), 160, (150, 30, 30), WHITE, 30)
    B.blackout_timer(img, "z03", t)
    return img


def z04(t, L, cue):   # пустая улица, идёт в профиль
    img = darken(street(), .55)
    x = -100 + (W + 200) * (t / L)
    img = hero(img, "side", x, 1120, 430, t, tint=(.66, .7, .95), bob=8)
    img = flashlight_beam(img, x + 70, 860, x + 330, 1120, 120, 60)
    M.tag(img, "ТИШИНА", 160, (20, 22, 24), (220, 220, 226), 30)
    B.blackout_timer(img, "z04", t)
    return img


def z05(t, L, cue):   # цель: свет на крыше
    img = B.city(lit=0, night=1.0, roof_light=True)
    img = toonlib.zoom(img, 1.3, .78, .3)
    img = hero(img, "q34", 180, H + 60, 620, t, tint=(.66, .7, .95), flip=True)
    M.big(img, "3 КВАРТАЛА", 170, YEL, 76)
    B.blackout_timer(img, "z05", t)
    return img


def z06(t, L, cue):   # фонарик гаснет
    p = (t - cue["06"]) / dur("06.mp3")
    img = darken(street(), .5)
    img = hero(img, "q34", W / 2, 1160, 560, t, tint=(.66, .7, .95))
    flick = 1 if p < .4 else (1 if int(t * 16) % 2 and p < .65 else 0)
    img = flashlight_beam(img, W / 2 + 60, 850, W / 2 + 40, 1280, 160, 70 * flick)
    if p > .65:
        img = darken(img, .18)
        M.big(img, "ТЬМА", 260, RED, 120)
    B.blackout_timer(img, "z06", t)
    return img


def z07(t, L, cue):   # шаги в темноте
    p = (t - cue["07"]) / dur("07.mp3")
    img = darken(street(), .12)
    img = hero(img, "e_whisper", W / 2, H + 120, 1000, t, tint=(.35, .4, .6))
    step_text(img, t, cue["07"] + dur("07.mp3") * .1, 3)
    B.blackout_timer(img, "z07", t)
    return img


def z08(t, L, cue):   # остановился — шаги тоже
    p = (t - cue["08"]) / dur("08.mp3")
    img = darken(street(), .12)
    img = hero(img, "e_scared", W / 2, H + 120, 1000, t, tint=(.35, .4, .6), shake_=3)
    if p > .55:
        M.big(img, "ТИШИНА", 170, WHITE, 90)
    B.blackout_timer(img, "z08", t)
    return img


def z09(t, L, cue):   # свет мигает трижды
    p = (t - cue["09"]) / dur("09.mp3")
    on = not (.3 < p < .75 and int((p - .3) / .075) % 2 == 0)
    img = B.city(lit=0, night=1.0, roof_light=on)
    img = toonlib.zoom(img, 1.4 + .5 * M.ease(p), .78, .28)
    if p > .3:
        n = min(3, 1 + int((p - .3) / .15))
        M.big(img, "МИГ " * n, 760, YEL, 70)
    if p > .8:
        M.big(img, "ОН ВИДИТ МЕНЯ", 180, RED, 72)
    B.blackout_timer(img, "z09", t)
    return img


def card_hero(kind):
    """мини-кадры для выбора: бежать к свету / вернуться домой"""
    if kind == "run":
        img = B.city(lit=0, night=1.0, roof_light=True)
        img = toonlib.zoom(img, 1.5, .78, .3)
        img = hero(img, "side", 360, 1180, 520, 0, tint=(.55, .6, .85))
    else:
        img = B.card_art("home").copy()
        img = hero(img, "e_calm", 360, H + 40, 700, 0, tint=(.75, .6, .5))
    return img


def z10(t, L, cue):
    B._cards["run2"] = B._cards.get("run2") or card_hero("run")
    B._cards["home2"] = B._cards.get("home2") or card_hero("home")
    bg = B.city(lit=0, night=1.0).filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(bg, Image.new("RGB", (W, H)), .55)
    d = ImageDraw.Draw(img)
    f = F(44, FONT_SUB)
    d.text(((W - f.getlength("ЧТО ДЕЛАТЬ?")) / 2, 170), "ЧТО ДЕЛАТЬ?", font=f, fill=WHITE, stroke_width=4, stroke_fill=(8, 8, 10))
    pulse = .5 + .5 * math.sin(t * 4)
    img = B.pretty_card(img, 36, 300, 310, 470, "run2", "1", "Бежать\nк свету", (240, 170, 60), min(1, t / .3), pulse)
    img = B.pretty_card(img, 374, 300, 310, 470, "home2", "2", "Вернуться\nдомой", (90, 150, 230), min(1, max(0, t - .25) / .3), 1 - pulse)
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 40, 495, W / 2 + 40, 575], fill=YEL, outline=(10, 10, 14), width=5)
    fi = F(24, FONT_SUB)
    d.text((W / 2 - fi.getlength("ИЛИ") / 2, 520), "ИЛИ", font=fi, fill=(20, 20, 24))
    p = (t - cue["10"]) / dur("10.mp3")
    if p > .55:
        M.big(img, "РЕШАЙ", 800, RED, 84)
    fp = F(30, FONT_SUB)
    txt = "ОТПРАВЬ ДРУГУ — ОН БЫ ПОБЕЖАЛ?"
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W / 2 - fp.getlength(txt) / 2 - 22, 1110, W / 2 + fp.getlength(txt) / 2 + 22, 1168], radius=28, fill=YEL)
    d.text((W / 2 - fp.getlength(txt) / 2, 1121), txt, font=fp, fill=(20, 20, 24))
    B.blackout_timer(img, "z10", t)
    return img


if __name__ == "__main__":
    s7 = span("z07")[0] + .1
    run({n: globals()[n] for n, *_ in PLAN},
        knocks=[s7 + dur("07.mp3") * .1 + i * .5 for i in range(int(dur("07.mp3") / .5))],
        hits=[span("z01")[0] + span("z01")[1] * .4, span("z06")[0] + span("z06")[1] * .65, span("z09")[0] + span("z09")[1] * .8])
