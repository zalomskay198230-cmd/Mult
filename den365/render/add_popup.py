"""Всплывающая реклама поверх готовой серии (хромакей зелёной плашки) + ускорение куска под ней.
python3 add_popup.py <серия.mp4> <выход.mp4> <старт_сек> [сдвиг_вверх_px=340] [ускорение=1.1] [громкость_рекламы=0.5]
Кусок серии длиной (длина_плашки × ускорение) с момента старта ускоряется, поэтому общая длина почти не растёт."""
import os, sys, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.join(HERE, "..", "ad", "klassvpn_popup_vertical_green.mp4")


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


src, out, T = sys.argv[1], sys.argv[2], float(sys.argv[3])
shift = int(sys.argv[4]) if len(sys.argv) > 4 else 340
k = float(sys.argv[5]) if len(sys.argv) > 5 else 1.1
vol = float(sys.argv[6]) if len(sys.argv) > 6 else 0.5
D = dur(AD)
T2 = T + D * k          # конец ускоряемого куска в исходнике

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
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", AD, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                       "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                       "-movflags", "+faststart", out])
print("готово:", out, f"{dur(out):.2f} c (было {dur(src):.2f})")
