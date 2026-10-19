#!/usr/bin/env bash
# Clean master for a TikTok source: remove baked-in text box(es), 30 fps CFR, upscale to 1080x1920, no audio.
# Usage: clean_master.sh <in.mp4> <out.mp4> X Y W H [X Y W H ...]   (boxes in SOURCE pixels; find them on a frame)
#        clean_master.sh <in.mp4> <out.mp4> none                      (no text to remove: just upscale)
# Optional light grade: GRADE="eq=contrast=1.04:saturation=1.06:gamma=0.98" clean_master.sh ... (applied before upscale).
# Uses the claude-shorts venv Python (numpy + scipy installed by the team setup).
set -euo pipefail
IN=$1; OUT=$2; shift 2
PY=${PY:-$HOME/.cache/claude-shorts/venv/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
read -r W H < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$IN" | tr ',' ' ')
ENC=(-vf "${GRADE:+$GRADE,}scale=1080:1920:flags=lanczos,unsharp=5:5:0.6" -c:v libx264 -preset slow -crf 14 -profile:v high -pix_fmt yuv420p -g 30 -movflags +faststart -an)
if [ "${1:-none}" = none ]; then
  ffmpeg -hide_banner -loglevel error -y -i "$IN" -an -vf fps=30 -f yuv4mpegpipe -pix_fmt yuv420p - | ffmpeg -hide_banner -loglevel error -y -i - "${ENC[@]}" "$OUT"
else
  ffmpeg -hide_banner -loglevel error -i "$IN" -an -vf fps=30 -pix_fmt yuv420p -f rawvideo - \
   | "$PY" -I "$HERE/sticker_fill.py" "$W" "$H" "$@" \
   | ffmpeg -hide_banner -loglevel error -y -f rawvideo -pix_fmt yuv420p -s "${W}x${H}" -framerate 30 -i - "${ENC[@]}" "$OUT"
fi
ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration -of compact "$OUT"
