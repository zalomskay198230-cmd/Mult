"""Звуковой дизайн для «Ночной смены»: голос с эхом кафельной комнаты + гул ламп + сердцебиение + скрип каталки + удары.
Таймлайн берётся из скрипта серии (toonlib.scenes/cues), видео пересобирается с новой дорожкой.
python3 sound.py <скрипт_серии.py> <tts_dir> <видео_без_звука_или_с_любым.mp4> <выход.mp4> <конфиг_json>
конфиг: {"heart": [["сцена_от", "сцена_до"]], "creak": [["сцена", доля_от, доля_до]], "hits": [["сцена", доля]], "dark": ["сцена", ...]}"""
import os, sys, json, subprocess, importlib.util, math
import numpy as np

SR = 44100
script, tts, src, out, cfg = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], json.loads(sys.argv[5])
sys.argv = [script, tts, "x.mp4"]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
spec = importlib.util.spec_from_file_location("ep", script)
ep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ep)
import toonlib

T = toonlib.TOTAL
N = int(T * SR) + SR
mix = np.zeros(N, np.float32)
span = {n: (s, l) for n, s, l, _ in toonlib.scenes}
rng = np.random.default_rng(3)


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.float32).copy()


def add(sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    mix[i:j] += sig[:j - i] * gain


# --- реверберация «кафель»: затухающий шум 0.6 с + ранние отражения
ir_len = int(.6 * SR)
ir = rng.normal(0, 1, ir_len).astype(np.float32) * np.exp(-np.arange(ir_len) / SR * 9).astype(np.float32)
for d_, g in ((.017, .5), (.029, .35), (.043, .25)):
    ir[int(d_ * SR)] += g
ir[0] = 1.0
ir /= np.abs(ir).sum() / 6


def reverb(x, wet=.28):
    n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:n].astype(np.float32)
    y = y / (np.abs(y).max() + 1e-9) * np.abs(x).max()
    out_ = np.zeros(n, np.float32)
    out_[:len(x)] += x * (1 - wet)
    out_ += y * wet
    return out_


# --- голос
for start, clip, d in toonlib.cues:
    add(reverb(load(os.path.join(tts, clip + ".mp3"))), start, 1.35)

# --- гул ламп (100/200 Гц) + тихий шум помещения; в «тёмных» сценах лампы молчат
t = np.arange(N) / SR
hum = (.018 * np.sin(2 * np.pi * 100 * t) + .008 * np.sin(2 * np.pi * 200 * t) + .004 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
hum *= (1 + .25 * np.sin(2 * np.pi * .3 * t)).astype(np.float32)
room = np.convolve(rng.normal(0, .012, N).astype(np.float32), np.ones(40, np.float32) / 40, "same")
env = np.ones(N, np.float32)
for sc in cfg.get("dark", []):
    s, l = span[sc]
    env[int(s * SR):int((s + l) * SR)] = 0
env = np.convolve(env, np.ones(2000, np.float32) / 2000, "same")
mix += hum * env + room

# --- низкий дрон для напряжения
mix += (.03 * np.sin(2 * np.pi * 41 * t) * (.6 + .4 * np.sin(2 * np.pi * .07 * t))).astype(np.float32)


def beat():
    n = int(.18 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 28)).astype(np.float32)


# --- сердцебиение: ускоряется от 70 до 130 уд/мин
for a, b in cfg.get("heart", []):
    t0, t1 = span[a][0], span[b][0] + span[b][1]
    x = t0
    while x < t1:
        k = (x - t0) / max(1e-3, t1 - t0)
        bpm = 70 + 60 * k
        add(beat(), x, .55 + .35 * k)
        add(beat(), x + .16, .35 + .25 * k)
        x += 60 / bpm


# --- скрип колёс каталки
def creak():
    n = int(.45 * SR)
    tt = np.arange(n) / SR
    f = 700 + 260 * np.sin(2 * np.pi * 9 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (.16 * np.sin(ph) * np.sin(np.pi * tt / tt[-1]) ** 2).astype(np.float32)


for sc, a, b in cfg.get("creak", []):
    s, l = span[sc]
    x = s + l * a
    while x < s + l * b:
        add(creak(), x, 1.0)
        x += .55

# --- удары (испуг)
def hit():
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    return (.9 * np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 7)) * tt) * np.exp(-tt * 2.2)
            + .25 * rng.normal(0, 1, n) * np.exp(-tt * 18)).astype(np.float32)


for sc, a in cfg.get("hits", []):
    s, l = span[sc]
    add(hit(), s + l * a, 1.0)

# --- в конце тихо гаснем
fade = int(1.2 * SR)
end = int(T * SR)
mix[end - fade:end] *= np.linspace(1, 0, fade).astype(np.float32)
mix = mix[:end]
mix = np.tanh(mix * 1.1) * .95
wav = out + ".f32"
mix.astype(np.float32).tofile(wav)
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", src, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", wav,
                       "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", out])
os.remove(wav)
print("звук готов:", out)
