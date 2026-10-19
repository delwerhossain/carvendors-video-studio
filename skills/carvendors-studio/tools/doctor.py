#!/usr/bin/env python3
"""Health check for carvendors-studio on this computer (Mac or Windows). Read-only; never prints secrets."""
import os, shutil, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import paths  # noqa: E402

bad = 0
def line(ok, name, hint=""):
    global bad
    bad += 0 if ok else 1
    print(f"{'OK     ' if ok else 'MISSING'} {name}" + ("" if ok else f"   → {hint}"))

for t, hint in [("ffmpeg", "Mac: brew install ffmpeg · Windows: winget install Gyan.FFmpeg"), ("ffprobe", "comes with ffmpeg"),
                ("node", "Mac: brew install node · Windows: winget install OpenJS.NodeJS.LTS"), ("npx", "comes with node")]:
    line(bool(shutil.which(t) or shutil.which(t + ".cmd")), t, hint)
try:
    import numpy, scipy  # noqa
    line(True, "numpy + scipy (skill Python)")
except ImportError:
    line(False, "numpy + scipy", "run the install script (it makes the skill venv)")
md = paths.my_drive()
line(bool(md), f"Google Drive My Drive ({md})", "start Google Drive for desktop, or: paths.py drive <path>")
_, _, p = paths.resolve_all()
for k in ("car_sources", "hooks", "bgm", "logos", "showroom_pics", "studio"):
    line(bool(p.get(k)) and Path(p[k]).exists(), f"path {k}", f"paths.py set {k} <folder>")
st = paths.get("studio")
line(bool(st) and (st / "hooks" / "catalog.json").exists(), "hook catalog", "tools/hooks.py scan")
env = Path.home() / ".config" / "video-studio" / ".env"
has_key = env.exists() and any(l.startswith("ELEVENLABS_API_KEY=") and "your_api_key_here" not in l and len(l.strip()) > 25
                              for l in env.read_text(encoding="utf-8", errors="ignore").splitlines())
print(f"{'OK     ' if has_key else 'OPTIONAL'} ElevenLabs key (only for new voiceovers / music / SFX)")
print("all good" if not bad else f"{bad} item(s) to fix")
sys.exit(1 if bad else 0)
