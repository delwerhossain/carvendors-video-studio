#!/usr/bin/env python3
"""Team hook library: one shared catalog + usage ledger on Google Drive (same on every PC).

  hooks.py scan [--force]          measure every hook once (length, action peak, suggested in/out, preview strip)
                                   → <studio>/hooks/catalog.json + hooks/sheets/<n>.jpg. Only new/changed files are scanned.
  hooks.py list [--car]            catalog with usage counts (car = the "Car Hooks" folder)
  hooks.py pick <video-id> [--car] least-used hook that is not in the last N edits (N = config defaults.hook_cooldown)
  hooks.py stats                   how often each hook was used and in which videos
  hooks.py sheet <name>            path of a hook's preview strip (look at it before choosing in/out by eye)

Usage is read from <studio>/ledger/*.json, which build.py writes when it renders a video (one file per video,
so two people editing at the same time never overwrite each other).
Suggested in/out: whole clip, ending ~0.4 s after the loudest moment (the impact/payoff) — the hook is played in
full; only dead time after the payoff is dropped. Check the strip if the audio has no clear peak.
"""
import hashlib, json, math, os, struct, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import paths  # noqa: E402

VIDEO = {".mp4", ".mov", ".m4v"}


def studio():
    s = paths.get("studio")
    if not s:
        sys.exit("shared _studio folder not found (Google Drive running? paths.py show)")
    return s


def cfg():
    return paths.shared_config()[1]


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                        "-of", "json", str(f)], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = any(s.get("codec_type") == "audio" for s in d.get("streams", []))
    return float(d.get("format", {}).get("duration", 0) or 0), v.get("width"), v.get("height"), a


def peak(f, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    if not raw:
        return None, None
    s = struct.unpack("<%dh" % (len(raw) // 2), raw)
    win = 800
    rms = []
    for i in range(0, len(s), win):
        seg = s[i:i + win]
        rms.append(math.sqrt(sum(x * x for x in seg) / max(len(seg), 1)) or 1)
    db = [20 * math.log10(r / 32768) for r in rms]
    i = max(range(len(db)), key=lambda k: db[k])
    med = sorted(db)[len(db) // 2]
    return round(i * 0.1, 2), round(db[i] - med, 1)


def scan(force=False):
    st, hooks = studio(), paths.get("hooks")
    cat_f = st / "hooks" / "catalog.json"
    cat = json.loads(cat_f.read_text(encoding="utf-8")) if cat_f.exists() and not force else {}
    files = sorted(p for p in hooks.rglob("*") if p.suffix.lower() in VIDEO and not p.name.startswith("."))
    (st / "hooks" / "sheets").mkdir(parents=True, exist_ok=True)
    for f in files:
        rel = f.relative_to(hooks).as_posix()
        key = f"{f.stat().st_size}"
        if rel in cat and cat[rel].get("key") == key:
            continue
        dur, w, h, has_a = probe(f)
        pk, strength = peak(f, dur) if has_a else (None, None)
        out = round(min(dur, pk + 0.4), 2) if pk is not None and strength and strength > 12 and pk >= 0.6 * dur else round(dur, 2)
        n = len(cat) + 1
        sheet = st / "hooks" / "sheets" / (hashlib.md5(rel.encode()).hexdigest()[:10] + ".jpg")
        fps = 8 / max(dur, 0.1)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", f"fps={fps:.4f},scale=-2:240,tile=8x1", "-frames:v", "1", str(sheet)])
        cat[rel] = {"name": f.stem, "file": rel, "category": "car" if "car" in f.parent.name.lower() else "general",
                    "duration": round(dur, 2), "size": [w, h], "audio": has_a, "peak": pk, "peak_strength": strength,
                    "in": 0.0, "out": out, "sheet": sheet.name, "key": key, "tags": []}
        print(f"  {rel:<55} {dur:5.2f}s  peak {pk}  out {out}")
    for rel in list(cat):
        if not (hooks / rel).exists():
            del cat[rel]
    cat_f.write_text(json.dumps(cat, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(cat)} hooks in {cat_f}")


def catalog():
    f = studio() / "hooks" / "catalog.json"
    if not f.exists():
        scan()
    return json.loads(f.read_text(encoding="utf-8"))


def ledger():
    d = studio() / "ledger"
    out = []
    for f in d.glob("*.json"):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return sorted(out, key=lambda e: e.get("date", ""))


def usage():
    use = {}
    for e in ledger():
        h = (e.get("hook") or {}).get("file")
        if h:
            use.setdefault(h, []).append(e.get("id"))
    return use


def pick(vid, car=False):
    cat, use, led = catalog(), usage(), ledger()
    cool = int(cfg().get("defaults", {}).get("hook_cooldown", 15))
    recent = {(e.get("hook") or {}).get("file") for e in led[-cool:]}
    pool = [h for h in cat.values() if (h["category"] == "car") == car] or list(cat.values())
    fresh = [h for h in pool if h["file"] not in recent] or pool
    seed = lambda h: hashlib.md5((vid + h["file"]).encode()).hexdigest()
    best = sorted(fresh, key=lambda h: (len(use.get(h["file"], [])), seed(h)))[0]
    return {"file": best["file"], "in": best["in"], "out": best["out"], "uses_so_far": len(use.get(best["file"], []))}


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "scan":
        return scan("--force" in a)
    if a[0] == "list":
        use = usage()
        for h in sorted(catalog().values(), key=lambda h: (h["category"], h["name"])):
            if "--car" in a and h["category"] != "car":
                continue
            print(f"{len(use.get(h['file'], [])):>3}x  {h['category']:<7} {h['duration']:5.2f}s  in {h['in']:<4} out {h['out']:<5} {h['file']}")
        return
    if a[0] == "pick" and len(a) >= 2:
        return print(json.dumps(pick(a[1], "--car" in a)))
    if a[0] == "stats":
        for f, ids in sorted(usage().items(), key=lambda x: -len(x[1])):
            print(f"{len(ids):>3}x  {f}  ← {', '.join(ids)}")
        return
    if a[0] == "sheet" and len(a) >= 2:
        q = " ".join(a[1:]).lower()
        h = next((h for h in catalog().values() if q in h["file"].lower()), None)
        return print(studio() / "hooks" / "sheets" / h["sheet"] if h else "not found")
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
