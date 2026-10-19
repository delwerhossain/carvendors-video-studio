#!/usr/bin/env python3
"""Where everything is, on this computer (Mac or Windows). Zero setup when Google Drive for desktop is running.

  paths.py show                 every path + OK / MISSING
  paths.py get <key>            one absolute path (exit 1 if missing) — used by the other tools
  paths.py set <key> <path>     local override for this computer only (a folder that lives elsewhere here)
  paths.py drive <path>         tell this computer where "My Drive" is (only if auto-detect fails)

How it resolves: it finds this computer's Google Drive "My Drive" folder (Mac: ~/Library/CloudStorage/
GoogleDrive-*/My Drive; Windows: <letter>:\\My Drive, %USERPROFILE%\\My Drive, …), then reads the team's shared
config  <My Drive>/Projects/CarVendors/_studio/config.json  whose paths are RELATIVE to My Drive. So the whole
team shares one config on Drive; a change there reaches every PC. Local overrides live in
~/.config/carvendors-studio/paths.json and win over the shared config.
"""
import json, os, string, sys
from pathlib import Path

LOCAL = Path.home() / ".config" / "carvendors-studio" / "paths.json"
SHARED_REL = "Projects/CarVendors/_studio/config.json"
DEFAULT_REL = {   # used if the shared config does not exist yet
    "carvendors": "Projects/CarVendors",
    "car_sources": "Projects/CarVendors/@bnf_cars-All Tiktok Video",
    "logos": "Projects/CarVendors/Logo",
    "showroom_pics": "Projects/CarVendors/Showroom Pic",
    "text_refs": "Projects/CarVendors/video-text-img -preveiw",
    "studio": "Projects/CarVendors/_studio",
    "resources": "Video Editing Component/All Resources",
    "hooks": "Video Editing Component/All Resources/All Hooks",
    "bgm": "Video Editing Component/All Resources/Background Music",
    "sfx": "Video Editing Component/All Resources/Sound Effects",
    "fonts": "Video Editing Component/All Resources/Font",
    "outros": "Video Editing Component/All Resources/Outro",
    "exports": "Projects/CarVendors/CarVendors Edited",
}


def load_local():
    try:
        return json.loads(LOCAL.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_local(d):
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def my_drive():
    loc = load_local()
    if loc.get("my_drive") and Path(loc["my_drive"]).exists():
        return Path(loc["my_drive"])
    cands = []
    home = Path.home()
    cs = home / "Library" / "CloudStorage"
    if cs.exists():
        cands += [p / "My Drive" for p in sorted(cs.glob("GoogleDrive-*"))]
    cands += [home / "My Drive", home / "Google Drive" / "My Drive", home / "Google Drive"]
    if os.name == "nt":
        cands += [Path(f"{c}:\\") / "My Drive" for c in string.ascii_uppercase[3:]]
    for c in cands:
        if (c / SHARED_REL).exists() or (c / "Projects" / "CarVendors").exists():
            return c
    return None


def shared_config():
    md = my_drive()
    if md and (md / SHARED_REL).exists():
        try:
            return md, json.loads((md / SHARED_REL).read_text(encoding="utf-8"))
        except Exception:
            pass
    return md, {"paths": DEFAULT_REL}


def resolve_all():
    md, cfg = shared_config()
    out = {}
    for k, rel in {**DEFAULT_REL, **cfg.get("paths", {})}.items():
        out[k] = str(md / rel) if md else None
    out["projects_root"] = str(Path.home() / "Projects" / "videos")
    for k, v in load_local().items():
        if k != "my_drive":
            out[k] = v
    return md, cfg, out


def get(key):
    _, _, p = resolve_all()
    v = p.get(key)
    return Path(v) if v else None


def main():
    a = sys.argv[1:]
    if not a or a[0] == "show":
        md, cfg, p = resolve_all()
        print(f"My Drive: {md or 'NOT FOUND — run: paths.py drive <path to My Drive>'}")
        for k, v in p.items():
            ok = v and Path(v).exists()
            print(f"{'OK     ' if ok else 'MISSING'} {k:<14} {v}")
        return
    if a[0] == "get" and len(a) == 2:
        v = get(a[1])
        if not v or not v.exists():
            sys.exit(1)
        print(v); return
    if a[0] == "set" and len(a) == 3:
        p = Path(os.path.expanduser(a[2]))
        if not p.exists():
            sys.exit(f"does not exist: {p}")
        d = load_local(); d[a[1]] = str(p); save_local(d); return main_show()
    if a[0] == "drive" and len(a) == 2:
        p = Path(os.path.expanduser(a[1]))
        if not (p / "Projects" / "CarVendors").exists():
            sys.exit(f"no Projects/CarVendors inside {p}")
        d = load_local(); d["my_drive"] = str(p); save_local(d); return main_show()
    sys.exit(__doc__)


def main_show():
    sys.argv = [sys.argv[0], "show"]; main()


if __name__ == "__main__":
    main()
