#!/usr/bin/env python3
"""Per-computer path setup for carvendors-studio. Run once per PC; afterwards every job reads the saved map.

  paths.py show                 print the saved map and whether each path exists (OK / MISSING)
  paths.py detect               search this computer for the usual folders and save what it finds
  paths.py set <key> <path>     save one path (use when detect cannot find it, or a folder moved)
  paths.py get <key>            print one path (for scripts); exit 1 if unset or missing

Keys: car_sources (folder with numbered video folders 1..N), hooks, bgm, sfx, fonts, logos, showroom_pics,
customer_reviews, projects_root (where job folders are made).
Saved at ~/.config/carvendors-studio/paths.json (per user, per computer; never inside the shared skill).
Detection looks for these folder names under the home folder, Google Drive / CloudStorage, Downloads,
Documents, Desktop and Projects: "@bnf_cars-All Tiktok Video", "All Hooks", "Background Music",
"Sound Effects", "Font", "Logo", "Showroom Pic", "Customer Review CarVendors".
"""
import json, os, sys
from pathlib import Path

CFG = Path.home() / ".config" / "carvendors-studio" / "paths.json"
KEYS = {
    "car_sources": "@bnf_cars-All Tiktok Video",
    "hooks": "All Hooks",
    "bgm": "Background Music",
    "sfx": "Sound Effects",
    "fonts": "Font",
    "logos": "Logo",
    "showroom_pics": "Showroom Pic",
    "customer_reviews": "Customer Review CarVendors",
}
ROOTS = ["Library/CloudStorage", "Google Drive", "Downloads", "Documents", "Desktop", "Projects"]


def load():
    try:
        return json.loads(CFG.read_text())
    except Exception:
        return {}


def save(d):
    CFG.parent.mkdir(parents=True, exist_ok=True)
    CFG.write_text(json.dumps(d, indent=2, ensure_ascii=False))


def find(name, max_depth=7):
    hits = []
    for r in ROOTS:
        base = Path.home() / r
        if not base.exists():
            continue
        for dirpath, dirnames, _ in os.walk(base):
            depth = Path(dirpath).relative_to(base).parts
            if len(depth) >= max_depth:
                dirnames[:] = []
                continue
            dirnames[:] = [x for x in dirnames if not x.startswith(".") and x not in ("node_modules", "Library")]
            if name in dirnames:
                hits.append(str(Path(dirpath) / name))
    return hits


def detect():
    d = load()
    for key, name in KEYS.items():
        if d.get(key) and Path(d[key]).exists():
            continue
        hits = find(name)
        if key == "fonts":
            hits = [h for h in hits if Path(h).parent.name == "All Resources"] or hits
        if len(hits) == 1:
            d[key] = hits[0]
        elif hits:
            print(f"{key}: several matches, choose one with `paths.py set {key} <path>`:")
            for h in hits:
                print("   ", h)
    d.setdefault("projects_root", str(Path.home() / "Projects" / "videos"))
    save(d)
    show()


def show():
    d = load()
    for key in list(KEYS) + ["projects_root"]:
        v = d.get(key)
        state = "OK     " if v and Path(v).exists() else "MISSING"
        print(f"{state} {key:<17} {v or '(not set: paths.py set ' + key + ' <path>)'}")
    print(f"saved in {CFG}")


def main():
    a = sys.argv[1:]
    if not a or a[0] == "show":
        return show()
    if a[0] == "detect":
        return detect()
    if a[0] == "set" and len(a) == 3:
        p = Path(os.path.expanduser(a[2]))
        if not p.exists():
            sys.exit(f"does not exist: {p}")
        d = load(); d[a[1]] = str(p); save(d); return show()
    if a[0] == "get" and len(a) == 2:
        v = load().get(a[1])
        if not v or not Path(v).exists():
            sys.exit(1)
        print(v); return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
