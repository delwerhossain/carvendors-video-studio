#!/usr/bin/env python3
"""Instrumental background music with ElevenLabs Music, with the same spend gate as tts.py.

Usage: music.py "<prompt>" -o music.mp3 --seconds 90 [--model music_v1] [--yes]

Without --yes nothing is sent. With --yes it reads the account's credit counter before and after, so the
real cost is printed and logged (the API docs do not publish a per-track price).
Result is cached in ~/.cache/video-studio/music by prompt + length + model.
"""
import argparse, datetime, hashlib, importlib.util, json, shutil, sys, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tts", HERE / "tts.py")
tts = importlib.util.module_from_spec(spec); spec.loader.exec_module(tts)
CACHE = Path.home() / ".cache" / "video-studio" / "music"


def used(key):
    return tts.request("GET", "/v1/user/subscription", key).get("character_count")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--seconds", type=float, default=60)
    ap.add_argument("--model", default="music_v1")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    body = {"prompt": a.prompt, "music_length_ms": int(a.seconds * 1000), "model_id": a.model,
            "force_instrumental": True}
    h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:24]
    cached = CACHE / f"{h}.mp3"
    out = Path(a.out).expanduser(); out.parent.mkdir(parents=True, exist_ok=True)
    if cached.is_file():
        shutil.copy(cached, out); print(f"cache hit ({h}): 0 credits -> {out}"); return
    print(f"model={a.model} length={a.seconds:.0f}s prompt={a.prompt!r}")
    if not a.yes:
        print("DRY RUN: nothing sent. Get the user's approval, then re-run with --yes."); sys.exit(2)
    key = tts.api_key()
    before = used(key)
    req = urllib.request.Request(tts.API + "/v1/music?output_format=mp3_44100_128", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:600]}")
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data); shutil.copy(cached, out)
    after = used(key)
    cost = (after - before) if isinstance(after, int) and isinstance(before, int) else "unknown"
    with open(tts.CACHE / "spend.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{cost} credits\t{a.model} music {a.seconds:.0f}s\t{out}\n")
    print(f"generated ({h}): {cost} credits -> {out}")


if __name__ == "__main__":
    main()
