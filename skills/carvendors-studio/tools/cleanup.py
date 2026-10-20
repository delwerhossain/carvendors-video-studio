#!/usr/bin/env python3
"""Free disk space in video job folders, keep finals. Mac + Windows.

  cleanup.py [ROOT ...] [--apply] [--keep-all-versions]

Default ROOT: ~/Projects/videos. Without --apply only prints what would go (dry run).

KEEPS (per job folder):
  - output/: the newest version of each video (highest _vN, or any *_final*) + its frame sheet / .srt / post copy
  - recipe files to re-render: job.json, brief.md, *.md, work/hf/index.html, work/hf/compositions/,
    voice/ (VO lines, music beds, SFX — small and cost credits), anything named *final*
DELETES (all re-creatable from Drive sources or by re-running build.py):
  - older output versions (_v1.._v(N-1)) and their frame sheets (unless --keep-all-versions)
  - input/ media copies in fast-lane jobs (job.json present; originals stay on Drive). Hand-made
    projects keep input/ (may hold the only copy of reviews / AI scenes)
  - output/*_raw.* when the mastered file exists, work/footage/ masters, work/hf/assets/ media,
    work/hf/renders/, snapshots (snaps*/, .hyperframes/), work/qa/ frames, node_modules/, __pycache__/
  - loose *.wav / *.mp4 / *.png / *.jpg under work/ that are not in the keep list
Never touches: folders outside ROOT, Google Drive, ~/.claude, ~/.config, the hook catalog or ledger.
"""
import re, shutil, sys
from pathlib import Path

MEDIA = {".mp4", ".mov", ".m4v", ".webm", ".wav", ".mp3", ".m4a", ".aac", ".png", ".jpg", ".jpeg", ".gif", ".exr"}
JUNK_DIRS = {"renders", ".hyperframes", "node_modules", "__pycache__"}
VER = re.compile(r"^(.*)_v(\d+)(_frames)?\.(mp4|jpg|png|srt|txt)$")


def size(p):
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def plan_job(job, keep_all):
    drop = []
    out = job / "output"
    if out.is_dir() and not keep_all:
        best = {}
        for f in out.iterdir():
            m = VER.match(f.name)
            if m and "final" not in f.name:
                best[m.group(1)] = max(best.get(m.group(1), 0), int(m.group(2)))
        for f in out.iterdir():
            m = VER.match(f.name)
            if m and "final" not in f.name and int(m.group(2)) < best[m.group(1)]:
                drop.append(f)
    if out.is_dir():   # *_raw.* duplicates of a mastered file
        names = {f.name for f in out.iterdir()}
        drop += [f for f in out.iterdir() if "_raw." in f.name and f.name.replace("_raw.", ".") in names]
    inp = job / "input"
    if inp.is_dir() and (job / "job.json").exists():   # fast-lane jobs only: their sources live on Drive
        drop += [f for f in inp.rglob("*") if f.is_file() and f.suffix.lower() in MEDIA]
    work = job / "work"
    if work.is_dir():
        for d in work.rglob("*"):
            if d.is_dir() and (d.name in JUNK_DIRS or d.name.startswith("snaps")):
                drop.append(d)
        for sub in ("footage", "qa", "hf/assets", "glass-lab/assets", "analysis"):
            p = work / sub
            if p.is_dir():
                drop += [f for f in p.rglob("*") if f.is_file() and f.suffix.lower() in MEDIA]
        drop += [f for f in work.rglob("*") if f.is_file() and f.suffix.lower() in MEDIA and "final" not in f.name]
    keep_roots = [job / "voice"]
    uniq, seen = [], set()
    for p in drop:
        if any(k in p.parents or p == k for k in keep_roots) or "final" in p.name.lower():
            continue
        if any(par in seen for par in p.parents) or p in seen:
            continue
        seen.add(p); uniq.append(p)
    return uniq


def jobs(root):
    for d in sorted(root.iterdir()):
        if d.is_dir() and ((d / "work").exists() or (d / "output").exists() or (d / "input").exists()):
            yield d


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply, keep_all = "--apply" in sys.argv, "--keep-all-versions" in sys.argv
    roots = [Path(a).expanduser() for a in args] or [Path.home() / "Projects" / "videos"]
    total = 0
    for root in roots:
        if not root.is_dir():
            continue
        for job in jobs(root):
            items = [p for p in plan_job(job, keep_all) if p.exists()]
            s = sum(size(p) for p in items)
            if not s:
                continue
            total += s
            print(f"{s / 1e6:8.1f} MB  {job.name}  ({len(items)} items)")
            if apply:
                for p in items:
                    shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
    print(f"{'freed' if apply else 'would free'}: {total / 1e6:.1f} MB" + ("" if apply else "   (run with --apply)"))


if __name__ == "__main__":
    main()
