#!/usr/bin/env python3
"""ElevenLabs voiceover with a local cache and a spend gate. Standard library only.

Usage:
  tts.py "<text>" | <script.txt>  -o <out.wav>  [--lang bn|en] [--voice ID] [--model eleven_v4]
         [--speed 1.0] [--stability 0.5] [--similarity 0.75] [--style 0]
         [--prev "<text before>"] [--next "<text after>"] [--yes]
  tts.py --list-voices          free call: lists the voices in the account
  tts.py --list-models          free call: lists the account's TTS models and whether each speaks bn / en

Without --yes nothing is sent: it prints how many characters (= credits, roughly) the call would use
and exits 2. Show that to the user, and re-run with --yes only after they approve.
Same text + voice + model + settings = cache hit (~/.cache/video-studio/tts), no credits spent.

Writes <out.wav> (48 kHz mono) and <out>.words.json [{"text", "start", "end"}] built from ElevenLabs'
character timestamps, so captions need no Whisper pass (better than Whisper for Bengali).
Key: $ELEVENLABS_API_KEY, else ~/.config/video-studio/.env. The key is never printed.
"""
import argparse, base64, datetime, hashlib, json, os, shutil, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io"
ENV_FILE = Path.home() / ".config" / "video-studio" / ".env"
CACHE = Path(os.environ.get("VIDEO_STUDIO_TTS_CACHE", Path.home() / ".cache" / "video-studio" / "tts"))
NO_LANG_CODE = ("eleven_multilingual_v2", "eleven_flash_v2", "eleven_turbo_v2")  # reject or ignore language_code


def env(name):
    if os.environ.get(name):
        return os.environ[name]
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            k, _, v = line.strip().partition("=")
            v = v.strip().strip('"').strip("'")
            if k.strip() == name and v and v != "your_api_key_here":
                return v
    return None


def api_key():
    k = env("ELEVENLABS_API_KEY")
    if not k:
        sys.exit(f"No ElevenLabs key. Ask the user to put ELEVENLABS_API_KEY=... in {ENV_FILE} themselves "
                 "(never paste it in chat).")
    return k


def request(method, path, key, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        sys.exit(f"ElevenLabs HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"ElevenLabs unreachable: {e.reason}")


def list_voices():
    data = request("GET", "/v1/voices", api_key())
    for v in data.get("voices", []):
        labels = ", ".join(f"{k}={x}" for k, x in (v.get("labels") or {}).items())
        print(f"{v['voice_id']}  {v.get('name', '')}  [{v.get('category', '')}]  {labels}")


def words_from_alignment(al):
    words, cur, st, en = [], "", 0.0, 0.0
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append({"text": cur, "start": round(st, 3), "end": round(en, 3)})
            cur = ""
            continue
        if not cur:
            st = s
        cur += ch
        en = e
    if cur:
        words.append({"text": cur, "start": round(st, 3), "end": round(en, 3)})
    # v3/v4 audio tags ([warmly], [sighs] ...) come back in the alignment but are not spoken
    return [w for w in words if not (w["text"].startswith("[") and w["text"].endswith("]"))]


def ffmpeg():
    return shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"


def list_models():
    """Free call. Voice models change often; check this at the start of each project and pick the best one."""
    for m in request("GET", "/v1/models", api_key()):
        if not m.get("can_do_text_to_speech"):
            continue
        langs = {l.get("language_id") for l in m.get("languages", [])}
        print(f"{m['model_id']:<28} bn={'yes' if 'bn' in langs else 'no ':<4} en={'yes' if 'en' in langs else 'no ':<4} "
              f"{len(langs):>3} langs  {m.get('name', '')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?", help="text, or a path to a .txt file")
    ap.add_argument("-o", "--out", help="output .wav")
    ap.add_argument("--lang", default="bn", help="ISO 639-1 code: bn, en, ... (default bn)")
    ap.add_argument("--voice")
    ap.add_argument("--model", default=env("ELEVENLABS_MODEL") or "eleven_v4")
    ap.add_argument("--speed", type=float)
    ap.add_argument("--stability", type=float)
    ap.add_argument("--similarity", type=float)
    ap.add_argument("--style", type=float)
    ap.add_argument("--prev", help="text spoken just before (continuity across scenes)")
    ap.add_argument("--next", help="text spoken just after")
    ap.add_argument("--yes", action="store_true", help="the user approved spending credits")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--list-models", action="store_true")
    a = ap.parse_args()

    if a.list_voices:
        return list_voices()
    if a.list_models:
        return list_models()
    if not a.text or not a.out:
        ap.error("text and -o are required")

    text = Path(a.text).read_text(encoding="utf-8") if a.text.endswith(".txt") and Path(a.text).is_file() else a.text
    text = text.strip()
    voice = a.voice or env(f"ELEVENLABS_VOICE_{a.lang.upper()}") or env("ELEVENLABS_VOICE")
    if not voice:
        sys.exit(f"No voice id. Run `tts.py --list-voices`, then set ELEVENLABS_VOICE_{a.lang.upper()}=<id> in {ENV_FILE}.")

    settings = {k: v for k, v in (("speed", a.speed), ("stability", a.stability),
                                   ("similarity_boost", a.similarity), ("style", a.style)) if v is not None}
    body = {"text": text, "model_id": a.model}
    if not a.model.startswith(NO_LANG_CODE):
        body["language_code"] = a.lang
    if settings:
        body["voice_settings"] = settings
    if a.prev:
        body["previous_text"] = a.prev
    if a.next:
        body["next_text"] = a.next

    key = hashlib.sha256(json.dumps({"voice": voice, **body}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    mp3, meta = CACHE / f"{key}.mp3", CACHE / f"{key}.json"
    out = Path(a.out).expanduser()
    words_out = out.with_suffix(".words.json")

    if mp3.is_file() and meta.is_file():
        print(f"cache hit ({key}): 0 credits")
    else:
        print(f"model={a.model} lang={a.lang} voice={voice} chars={len(text)}")
        if not a.yes:
            print(f"DRY RUN: this call would use about {len(text)} credits. Nothing was sent. "
                  "Get the user's approval, then re-run with --yes.")
            sys.exit(2)
        res = request("POST", f"/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128", api_key(), body)
        CACHE.mkdir(parents=True, exist_ok=True)
        mp3.write_bytes(base64.b64decode(res["audio_base64"]))
        meta.write_text(json.dumps({"voice": voice, "model": a.model, "lang": a.lang, "chars": len(text), "text": text,
                                    "alignment": res.get("alignment") or res.get("normalized_alignment")},
                                   ensure_ascii=False), encoding="utf-8")
        with open(CACHE / "spend.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{len(text)} chars\t{a.model}\t{a.lang}\t{out}\n")
        print(f"generated ({key}): {len(text)} chars spent")

    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(out)], check=True)
    al = json.loads(meta.read_text(encoding="utf-8")).get("alignment")
    if al:
        words_out.write_text(json.dumps(words_from_alignment(al), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {out}" + (f"\n-> {words_out}" if al else "\n(no timestamps returned; transcribe the wav for captions)"))


if __name__ == "__main__":
    main()
