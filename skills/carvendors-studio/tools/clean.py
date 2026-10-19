#!/usr/bin/env python3
"""Clean master for a TikTok source (Mac + Windows): 30 fps CFR, optional light grade, upscale to 1080x1920,
optional removal of baked-in text boxes (harmonic inpaint + texture re-grain), no audio.

  clean.py <in.mp4> <out.mp4> [--box X Y W H ...] [--grade "eq=contrast=1.04:saturation=1.06:gamma=0.98"]

Boxes are in SOURCE pixels (B&F TikToks are 576x1024). Without --box it only re-times, grades and upscales.
Needs ffmpeg/ffprobe on PATH; numpy + scipy only when --box is used.
"""
import argparse, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def size(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--box", nargs=4, type=int, action="append", default=[])
    ap.add_argument("--grade", default="")
    a = ap.parse_args()
    vf = (a.grade + "," if a.grade else "") + "scale=1080:1920:flags=lanczos,unsharp=5:5:0.6"
    enc = ["-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-g", "30", "-movflags", "+faststart", "-an", str(a.out)]
    if not a.box:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", a.inp, "-an", "-vf", "fps=30"] + enc, check=True)
    else:
        sys.path.insert(0, str(HERE))
        import numpy as np
        import sticker_fill as sf
        W, H = size(a.inp)
        M = 4
        fl = []
        for x, y, bw, bh in a.box:
            x0, y0 = max(6, (x - M) // 2 * 2), max(6, (y - M) // 2 * 2)
            x1, y1 = min(W - 7, x + bw + M), min(H - 7, y + bh + M)
            x1 = x1 if (x1 - x0 + 1) % 2 == 0 else x1 + 1
            y1 = y1 if (y1 - y0 + 1) % 2 == 0 else y1 + 1
            fl.append((sf.Filler(x0, x1, y0, y1, 1, H=H, grain=True), sf.Filler(x0 // 2, (x1 - 1) // 2, y0 // 2, (y1 - 1) // 2, 2)))
        dec = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", a.inp, "-an", "-vf", "fps=30",
                                "-pix_fmt", "yuv420p", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
        encp = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p",
                                 "-s", f"{W}x{H}", "-framerate", "30", "-i", "-"] + enc, stdin=subprocess.PIPE)
        ysz, csz = W * H, (W // 2) * (H // 2)
        n = 0
        while True:
            buf = dec.stdout.read(ysz + 2 * csz)
            if len(buf) < ysz + 2 * csz:
                break
            arr = np.frombuffer(buf, np.uint8)
            Y = arr[:ysz].reshape(H, W); U = arr[ysz:ysz + csz].reshape(H // 2, W // 2); V = arr[ysz + csz:].reshape(H // 2, W // 2)
            for LY, LC in fl:
                Y = LY(Y); U = LC(U); V = LC(V)
            encp.stdin.write(Y.tobytes()); encp.stdin.write(U.tobytes()); encp.stdin.write(V.tobytes()); n += 1
        encp.stdin.close(); encp.wait(); dec.wait()
        print(f"clean: {n} frames, {len(fl)} box(es) removed")
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                        "-of", "compact", str(a.out)], capture_output=True, text=True)
    print(r.stdout.strip())


if __name__ == "__main__":
    main()
