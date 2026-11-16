"""Всплывающая реклама в готовую серию (хромакей зелёной плашки).
python3 add_popup.py <серия.mp4> <выход.mp4> <старт_сек> [сдвиг_вверх_px=250] [режим=freeze] [громкость_рекламы=0.9]
freeze — как в примере: после фразы мультик замирает (стоп-кадр, рассказ на паузе), поверх идёт плашка со своим звуком,
         потом история продолжается. Серия становится длиннее на длину плашки.
speed  — мультик идёт под плашкой, кусок ускорен в 1.1 раза (старый вариант)."""
import os, sys, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.join(HERE, "..", "ad", "klassvpn_popup_vertical_green.mp4")
BADGE = os.environ.get("AD_BADGE", os.path.join(HERE, "..", "ad", "klassvpn_badge.png"))   # значок на всё видео ("" — без него)
VOICE = os.environ.get("AD_VOICE", os.path.join(HERE, "..", "ad", "klassvpn_voice_fit.mp3"))   # озвучка рекламы ("" — без голоса)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


src, out, T = sys.argv[1], sys.argv[2], float(sys.argv[3])
shift = int(sys.argv[4]) if len(sys.argv) > 4 else 250
mode = sys.argv[5] if len(sys.argv) > 5 else "freeze"
vol = float(sys.argv[6]) if len(sys.argv) > 6 else 0.9
D = dur(AD)
k = 1.1
T2 = T + D * k          # конец ускоряемого куска в исходнике (режим speed)

fc_freeze = (
    f"[0:v]trim=0:{T},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={D}[vb0];"
    f"[0:v]trim={T},setpts=PTS-STARTPTS[v3];"
    f"[0:a]atrim=0:{T},asetpts=PTS-STARTPTS,apad=pad_dur={D}[a1];"
    f"[0:a]atrim={T},asetpts=PTS-STARTPTS[a3];"
    f"[1:v]scale=720:1280,chromakey=0x00d700:0.18:0.08,setpts=PTS-STARTPTS+{T}/TB[ad];"
    f"[vb0][ad]overlay=0:-{shift}:eof_action=pass:enable='between(t,{T},{T + D})'[v1];"
    + (f"[1:a]volume={vol * .45},adelay={int(T * 1000)}|{int(T * 1000)}[ada];"
       f"[2:a]volume=1.5,adelay={int(T * 1000) + 250}|{int(T * 1000) + 250}[vo];"
       f"[a1][ada][vo]amix=inputs=3:normalize=0:duration=first[a1m];"
       if VOICE else
       f"[1:a]volume={vol},adelay={int(T * 1000)}|{int(T * 1000)}[ada];"
       f"[a1][ada]amix=inputs=2:normalize=0:duration=first[a1m];")
    + f"[v1][a1m][v3][a3]concat=n=2:v=1:a=1[v][a0];[a0]alimiter=limit=0.95[a]"
)

fc = (
    f"[0:v]trim=0:{T},setpts=PTS-STARTPTS[v1];"
    f"[0:v]trim={T}:{T2},setpts=(PTS-STARTPTS)/{k}[v2];"
    f"[0:v]trim={T2},setpts=PTS-STARTPTS[v3];"
    f"[0:a]atrim=0:{T},asetpts=PTS-STARTPTS[a1];"
    f"[0:a]atrim={T}:{T2},asetpts=PTS-STARTPTS,atempo={k}[a2];"
    f"[0:a]atrim={T2},asetpts=PTS-STARTPTS[a3];"
    f"[v1][a1][v2][a2][v3][a3]concat=n=3:v=1:a=1[vb][ab];"
    # плашка: убрать зелёный, поднять вверх, показать с момента T
    f"[1:v]scale=720:1280,chromakey=0x00d700:0.18:0.08,setpts=PTS-STARTPTS+{T}/TB[ad];"
    f"[vb][ad]overlay=0:-{shift}:eof_action=pass:enable='between(t,{T},{T + D})'[v];"
    f"[1:a]volume={vol},adelay={int(T * 1000)}|{int(T * 1000)}[ada];"
    f"[ab][ada]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]"
)
if mode == "freeze":
    fc = fc_freeze
if BADGE:   # значок-плашка справа под шкалами, на всё видео
    n_in = 3 if (VOICE and mode == "freeze") else 2
    fc = fc.replace("[v1][a1m][v3][a3]concat=n=2:v=1:a=1[v][a0]", "[v1][a1m][v3][a3]concat=n=2:v=1:a=1[vc][a0]") \
           .replace("[vb][ad]overlay=0:-{}:eof_action=pass".format(shift), "[vb][ad]overlay=0:-{}:eof_action=pass".format(shift))
    if "[vc]" in fc:
        fc += f";[vc][{n_in}:v]overlay=W-w-25:133[v]"
    else:
        fc = fc.replace("[v];", "[vc];", 1) + f";[vc][{n_in}:v]overlay=W-w-25:133[v]"
extra = (["-i", VOICE] if (VOICE and mode == "freeze") else []) + (["-i", BADGE] if BADGE else [])
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", AD] + extra + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                       "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                       "-movflags", "+faststart", out])
print("готово:", out, f"{dur(out):.2f} c (было {dur(src):.2f})")
