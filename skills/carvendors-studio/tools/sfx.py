#!/usr/bin/env python3
"""Short sound effects with ElevenLabs Sound Effects, with the same spend gate as tts.py / music.py.

Usage: sfx.py "<prompt>" -o whoosh.mp3 --seconds 0.6 [--influence 0.5] [--model eleven_text_to_sound_v2]
              [--loop] [--yes]

Without --yes nothing is sent (exit 2). With --yes it reads the account's credit counter before and after,
so the real cost is printed and logged to ~/.cache/video-studio/tts/spend.log (same log as tts.py/music.py).
Result is cached in ~/.cache/video-studio/sfx by prompt + length + influence + model + loop: the same call
again is a free cache hit.
The API's shortest length is 0.5 s. For a shorter --seconds (e.g. a 0.3 s tick) it asks for 0.5 s and trims
the file locally to the requested length with a 15 ms fade-out (free, done with ffmpeg).
Endpoint: POST /v1/sound-generation {"text", "duration_seconds", "prompt_influence", "model_id", "loop"}.
"""
import argparse, datetime, hashlib, importlib.util, json, shutil, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tts", HERE / "tts.py")
tts = importlib.util.module_from_spec(spec); spec.loader.exec_module(tts)
CACHE = Path.home() / ".cache" / "video-studio" / "sfx"
API_MIN, API_MAX = 0.5, 30.0


def used(key):
    return tts.request("GET", "/v1/user/subscription", key).get("character_count")


def deliver(src, out, seconds):
    """Copy the cached mp3 to out; trim locally when the asked length is below the API minimum."""
    if seconds >= API_MIN:
        shutil.copy(src, out); return
    fade = 0.015
    subprocess.run([tts.ffmpeg(), "-y", "-v", "error", "-i", str(src), "-t", f"{seconds:.3f}",
                    "-af", f"afade=t=out:st={max(0.0, seconds - fade):.3f}:d={fade}",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt")
    ap.add_argument("-o", "--out", required=True, help="output .mp3")
    ap.add_argument("--seconds", type=float, default=1.0, help="length; below 0.5 s is trimmed locally")
    ap.add_argument("--influence", type=float, default=0.5, help="prompt_influence 0-1 (higher = more literal)")
    ap.add_argument("--model", default="eleven_text_to_sound_v2")
    ap.add_argument("--loop", action="store_true", help="ask for a seamless loop (v2 model)")
    ap.add_argument("--yes", action="store_true", help="the user approved spending credits")
    a = ap.parse_args()
    req_s = min(API_MAX, max(API_MIN, a.seconds))
    body = {"text": a.prompt, "duration_seconds": round(req_s, 2), "prompt_influence": a.influence,
            "model_id": a.model}
    if a.loop:
        body["loop"] = True
    h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:24]
    cached = CACHE / f"{h}.mp3"
    out = Path(a.out).expanduser(); out.parent.mkdir(parents=True, exist_ok=True)
    trim = f", trimmed locally to {a.seconds:.2f}s" if a.seconds < API_MIN else ""
    if cached.is_file():
        deliver(cached, out, a.seconds); print(f"cache hit ({h}): 0 credits -> {out}{trim}"); return
    print(f"model={a.model} length={req_s:.2f}s{trim} influence={a.influence} prompt={a.prompt!r}")
    if not a.yes:
        print("DRY RUN: nothing sent. Get the user's approval, then re-run with --yes."); sys.exit(2)
    key = tts.api_key()
    before = used(key)
    req = urllib.request.Request(tts.API + "/v1/sound-generation?output_format=mp3_44100_128", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:600]}")
    except urllib.error.URLError as e:
        sys.exit(f"ElevenLabs unreachable: {e.reason}")
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    deliver(cached, out, a.seconds)
    after = used(key)
    cost = (after - before) if isinstance(after, int) and isinstance(before, int) else "unknown"
    tts.CACHE.mkdir(parents=True, exist_ok=True)
    with open(tts.CACHE / "spend.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{cost} credits\t{a.model} sfx {req_s:.2f}s\t{out}\n")
    print(f"generated ({h}): {cost} credits -> {out}{trim}")


if __name__ == "__main__":
    main()
