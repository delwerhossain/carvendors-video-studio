#!/usr/bin/env python3
"""Scan a folder of videos for bulk editing: one manifest row + one preview strip per video.

Usage:
  batch_scan.py <videos-dir> <project-dir> [--batch-size 10]    scan (safe to re-run: keeps status/notes)
  batch_scan.py --status <project-dir>                          counts per status and per batch

Writes <project-dir>/work/batch/manifest.csv and <project-dir>/work/batch/thumbs/<id>.jpg (3 frames at
15/50/85 % side by side, so an agent can look at one image per video before deciding the edit).
Columns: id, batch, file, duration_s, width, height, fps, orientation, audio, mean_db, status, type, notes.
  status: todo -> pilot -> edited -> approved | redo | skip   (the agent and the reviewer update it)
  type:   talking / review / car-showcase / already-edited / other   (the agent fills it after looking)
  audio:  none | silent (mean below -50 dB) | yes
Standard library + ffmpeg/ffprobe only. Never modifies the source videos.
"""
import argparse, csv, json, re, shutil, subprocess, sys
from collections import Counter
from pathlib import Path

EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
COLS = ["id", "batch", "file", "duration_s", "width", "height", "fps", "orientation", "audio", "mean_db",
        "status", "type", "notes"]
KEEP = ("status", "type", "notes")


def tool(name):
    return shutil.which(name) or f"/opt/homebrew/bin/{name}"


def probe(f):
    out = subprocess.run([tool("ffprobe"), "-v", "error", "-print_format", "json", "-show_streams",
                          "-show_format", str(f)], capture_output=True, text=True)
    if out.returncode:
        return None
    d = json.loads(out.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        return None
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    rot = str(v.get("tags", {}).get("rotate", "")) or next(
        (str(int(sd.get("rotation", 0))) for sd in v.get("side_data_list", []) if "rotation" in sd), "")
    if rot.lstrip("-") in ("90", "270"):
        w, h = h, w
    num, _, den = v.get("avg_frame_rate", "0/1").partition("/")
    fps = round(float(num) / float(den), 2) if den and float(den) else 0
    return {"duration_s": round(float(d.get("format", {}).get("duration", 0) or 0), 2), "width": w,
            "height": h, "fps": fps, "has_audio": a is not None}


def mean_db(f):
    r = subprocess.run([tool("ffmpeg"), "-v", "info", "-nostats", "-i", str(f), "-vn", "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume:\s*(-?[\d.]+|-inf) dB", r.stderr)
    return None if not m or m.group(1) == "-inf" else float(m.group(1))


def strip(f, dur, out):
    ts = [max(0.0, dur * p) for p in (0.15, 0.5, 0.85)]
    cmd = [tool("ffmpeg"), "-y", "-v", "error"]
    for t in ts:
        cmd += ["-ss", f"{t:.2f}", "-i", str(f)]
    cmd += ["-filter_complex", "[0:v]scale=-2:360[a];[1:v]scale=-2:360[b];[2:v]scale=-2:360[c];[a][b][c]hstack=3",
            "-frames:v", "1", "-q:v", "4", str(out)]
    subprocess.run(cmd, capture_output=True)


def scan(a):
    src, proj = Path(a.videos).expanduser().resolve(), Path(a.project).expanduser().resolve()
    bdir = proj / "work" / "batch"
    (bdir / "thumbs").mkdir(parents=True, exist_ok=True)
    man = bdir / "manifest.csv"
    old = {}
    if man.exists():
        with man.open(newline="", encoding="utf-8") as fh:
            old = {r["file"]: r for r in csv.DictReader(fh)}
    files = sorted(p for p in src.rglob("*") if p.suffix.lower() in EXT and not p.name.startswith("."))
    rows, bad = [], []
    for i, f in enumerate(files, 1):
        rel = str(f.relative_to(src))
        vid = f"v{i:03d}"
        p = probe(f)
        if not p:
            bad.append(rel)
            continue
        db = mean_db(f) if p["has_audio"] else None
        audio = "none" if not p["has_audio"] else ("silent" if db is None or db < -50 else "yes")
        orient = "vertical" if p["height"] > p["width"] else ("square" if p["height"] == p["width"] else "horizontal")
        row = {"id": vid, "batch": (i - 1) // a.batch_size + 1, "file": rel, "duration_s": p["duration_s"],
               "width": p["width"], "height": p["height"], "fps": p["fps"], "orientation": orient,
               "audio": audio, "mean_db": "" if db is None else db, "status": "todo", "type": "", "notes": ""}
        for k in KEEP:
            if rel in old and old[rel].get(k):
                row[k] = old[rel][k]
        thumb = bdir / "thumbs" / f"{vid}.jpg"
        if not thumb.exists():
            strip(f, p["duration_s"], thumb)
        rows.append(row)
        print(f"{vid}  {p['duration_s']:>6}s  {p['width']}x{p['height']}  audio={audio:<6}  {rel}", flush=True)
    with man.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} videos -> {man}")
    print(f"{(len(rows) + a.batch_size - 1) // a.batch_size} batches of {a.batch_size}; thumbs in {bdir / 'thumbs'}")
    if bad:
        print(f"unreadable ({len(bad)}): " + ", ".join(bad))


def status(proj):
    man = Path(proj).expanduser() / "work" / "batch" / "manifest.csv"
    if not man.exists():
        sys.exit(f"no manifest at {man}; run a scan first")
    with man.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    print("status:", dict(Counter(r["status"] for r in rows)))
    print("type:  ", dict(Counter(r["type"] or "(not set)" for r in rows)))
    by = {}
    for r in rows:
        by.setdefault(int(r["batch"]), Counter())[r["status"]] += 1
    for b in sorted(by):
        print(f"batch {b:>3}: " + ", ".join(f"{k}={v}" for k, v in sorted(by[b].items())))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="?")
    ap.add_argument("project", nargs="?")
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--status", metavar="PROJECT")
    a = ap.parse_args()
    if a.status:
        return status(a.status)
    if not (a.videos and a.project):
        ap.error("need <videos-dir> <project-dir> (or --status <project-dir>)")
    scan(a)


if __name__ == "__main__":
    main()
