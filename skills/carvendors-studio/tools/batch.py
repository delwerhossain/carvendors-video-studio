#!/usr/bin/env python3
"""Bulk re-edit of the B&F TikTok folder (1-200) with the least AI work per video.

  batch.py plan 1-20           for each folder: job dir + draft job.json (hook auto, defaults) + contact sheet
                               + auto-detected static text boxes (hint) → prints the list of contact sheets to look at
  batch.py render 1-20         build.py --render every job in the range whose job.json has "ready": true
  batch.py status [1-200]      planned / ready / rendered (from the shared ledger) per folder

Per video the agent only: looks at ONE contact sheet (work/qa/contact.jpg), then edits job.json:
slug, keep/cover/remove old text (hint: "text_hint" boxes in source px and 1080x1920 px), 1-3 overlays,
"ready": true. Everything else (hook choice, logo, music, outro, transition, grade) comes from the team config.
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import paths  # noqa: E402

PY = sys.executable


def rng(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def job_dir(n):
    return paths.get("projects_root") / f"bnf-v{n:03d}"


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type", "-of", "json", str(f)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    return float(d.get("format", {}).get("duration", 0) or 0), v.get("width"), v.get("height")


def text_hint(f, dur, w, h):
    """Static bright text (TikTok captions/stickers) present in most sampled frames → bounding boxes."""
    try:
        import numpy as np
    except ImportError:
        return []
    n = 10
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", f"fps={n / max(dur, 0.5):.4f},format=rgb24", "-frames:v", str(n),
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    k = len(raw) // (w * h * 3)
    if k < 3:
        return []
    a = np.frombuffer(raw[:k * w * h * 3], np.uint8).reshape(k, h, w, 3).astype(np.int16)
    white = (a.min(3) > 228) & ((a.max(3) - a.min(3)) < 22)
    static = white.mean(0) > 0.8
    rows = np.nonzero(static.sum(1) > 6)[0]
    boxes, start = [], None
    for i, y in enumerate(rows):
        if start is None:
            start = y
        if i == len(rows) - 1 or rows[i + 1] - y > 34:
            ys = slice(start, y + 1)
            xs = np.nonzero(static[ys].sum(0) > 0)[0]
            if len(xs) and (y - start) > 8:
                bx, by, bw, bh = int(xs.min()) - 6, int(start) - 6, int(xs.max() - xs.min()) + 12, int(y - start) + 12
                boxes.append({"src": [max(bx, 0), max(by, 0), bw, bh],
                              "canvas": [round(bx * 1080 / w) - 8, round(by * 1920 / h) - 8, round(bw * 1080 / w) + 16, round(bh * 1920 / h) + 16]})
            start = None
    return boxes


def plan(nums):
    src_root = paths.get("car_sources")
    for n in nums:
        src = src_root / str(n) / "video.mp4"
        if not src.exists():
            print(f"{n:>4}  no video.mp4"); continue
        P = job_dir(n); (P / "work/qa").mkdir(parents=True, exist_ok=True)
        jf = P / "job.json"
        dur, w, h = probe(src)
        contact = P / "work/qa/contact.jpg"
        if not contact.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"fps={10 / max(dur, 0.5):.4f},scale=-2:480,tile=10x1",
                            "-frames:v", "1", str(contact)])
        comments = (src.parent / "comments.txt").read_text(encoding="utf-8", errors="ignore").strip() if (src.parent / "comments.txt").exists() else ""
        voice = sorted((src.parent / "Voice").glob("*")) if (src.parent / "Voice").exists() else []
        if not jf.exists():
            J = {"id": f"v{n:03d}", "slug": f"f{n}", "folder": n, "ready": False, "hook": "auto",
                 "source_info": {"duration": round(dur, 2), "size": [w, h], "comments": comments[:300],
                                 "ready_voiceover": [v.name for v in voice]},
                 "text_hint": text_hint(src, dur, w, h),
                 "remove": [], "covers": [], "overlays": []}
            jf.write_text(json.dumps(J, indent=2, ensure_ascii=False), encoding="utf-8")
        J = json.loads(jf.read_text(encoding="utf-8"))
        print(f"{n:>4}  {dur:5.1f}s  text boxes: {len(J.get('text_hint', []))}  voice: {len(voice)}  {contact}")


def render(nums):
    for n in nums:
        jf = job_dir(n) / "job.json"
        if not jf.exists():
            print(f"{n:>4}  not planned"); continue
        J = json.loads(jf.read_text(encoding="utf-8"))
        if not J.get("ready"):
            print(f"{n:>4}  skipped (ready=false)"); continue
        print(f"\n===== {n} =====")
        r = subprocess.run([PY, HERE / "build.py", str(jf), "--render"], text=True, capture_output=True)
        keep = [l for l in r.stdout.splitlines() if l.startswith(("OUTPUT", "FRAMES", "EXPORT", "LEDGER", "length", "  hook picked", "  ✗", "◇"))]
        print("\n".join(keep) or r.stdout[-800:])
        if r.returncode:
            print(r.stderr[-1200:])


def status(nums):
    st = paths.get("studio")
    led = {json.loads(f.read_text(encoding="utf-8")).get("folder"): f for f in (st / "ledger").glob("*.json")} if st else {}
    for n in nums:
        jf = job_dir(n) / "job.json"
        s = "rendered" if n in led else ("ready" if jf.exists() and json.loads(jf.read_text(encoding="utf-8")).get("ready") else ("planned" if jf.exists() else "-"))
        print(f"{n:>4}  {s}")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    nums = rng(a[1]) if len(a) > 1 else list(range(1, 201))
    {"plan": plan, "render": render, "status": status}.get(a[0], lambda _: sys.exit(__doc__))(nums)


if __name__ == "__main__":
    main()
