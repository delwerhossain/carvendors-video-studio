#!/usr/bin/env python3
"""Free, offline Bengali/English voiceover with AI4Bharat Indic Parler-TTS (no ElevenLabs credits).

Run with the private env:  ~/.cache/video-studio/parler-venv/bin/python local_tts.py ...
Usage: local_tts.py "<text>" | <script.txt>  -o <out.wav>  [--desc "<voice description>"] [--seed 7]
                    [--pause 0.25] [--cpu]

The text is split into sentences (। ! ? .) and each one is generated with the same description and seed,
so the voice stays consistent and long scripts don't drift; sentences are joined with --pause seconds of
silence. Writes 48 kHz mono wav. Write numbers as words ("বিশ শতাংশ", not "২০%") for clean reading.
First run downloads the model (3.8 GB) to ~/.cache/huggingface; it needs a Hugging Face login that has
accepted the model's terms at https://huggingface.co/ai4bharat/indic-parler-tts.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
MODEL = "ai4bharat/indic-parler-tts"
DEFAULT_DESC = ("Arjun speaks in a clear, warm and expressive voice at a moderate pace, with natural "
                "intonation. The recording is of very high quality, close up, with no background noise.")


def sentences(text):
    parts = re.split(r"(?<=[।!?.])\s+", re.sub(r"\s+", " ", text.strip()))
    return [p for p in parts if p.strip()]


def to_wav48(samples, sr, out):
    import soundfile as sf
    out = Path(out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw.wav"
        sf.write(raw, samples, sr)
        ff = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
        subprocess.run([ff, "-y", "-v", "error", "-i", str(raw), "-ar", "48000", "-ac", "1", str(out)], check=True)
    return out


def kokoro(text, a):
    """English with Kokoro-82M (ONNX, ~/.cache/video-studio/kokoro). Voices: af_* / am_* US, bf_* / bm_* UK.

    Kokoro has no emotion tags, so emotion comes from direction lines (one per line):
      [am_michael 1.1] Order today!      voice + speed (0.5-2.0) for this line
      [pause 0.6]                        silence in seconds
      plain line                         uses --voice / --speed
    Different speeds per line, pauses, punctuation (? ! ...) and a second voice for quotes do the acting.
    """
    import numpy as np
    from kokoro_onnx import Kokoro
    m = Path.home() / ".cache" / "video-studio" / "kokoro"
    t0 = time.time()
    k = Kokoro(str(m / "kokoro-v1.0.onnx"), str(m / "voices-v1.0.bin"))
    sr, parts = 24000, []
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            continue
        d = re.match(r"^\[([^\]]+)\]\s*(.*)$", line)
        voice, speed, say = a.voice, a.speed, line
        if d:
            args, say = d.group(1).split(), d.group(2)
            if args[0] == "pause":
                parts.append(np.zeros(int(sr * float(args[1])), dtype=np.float32))
                continue
            voice = args[0]
            speed = float(args[1]) if len(args) > 1 else a.speed
        if not say:
            continue
        s, sr = k.create(say, voice=voice, speed=speed, lang="en-gb" if voice[0] == "b" else "en-us")
        parts += [s.astype(np.float32), np.zeros(int(sr * 0.12), dtype=np.float32)]
        print(f"{voice} x{speed}: {say}", flush=True)
    samples = np.concatenate(parts)
    out = to_wav48(samples, sr, a.out)
    print(f"{len(samples) / sr:.1f}s audio in {time.time() - t0:.0f}s -> {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--desc", default=DEFAULT_DESC)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--pause", type=float, default=0.25)
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--engine", choices=["parler", "kokoro"], default="parler",
                    help="parler: Bengali, Bengali-English mix (default). kokoro: pure English, more natural")
    ap.add_argument("--voice", default="am_michael", help="kokoro voice, e.g. am_michael, af_heart, bf_emma")
    ap.add_argument("--speed", type=float, default=1.0, help="kokoro speed")
    a = ap.parse_args()
    text = Path(a.text).read_text(encoding="utf-8") if a.text.endswith(".txt") and Path(a.text).is_file() else a.text
    if a.engine == "kokoro":
        return kokoro(text, a)

    import numpy as np, soundfile as sf, torch
    from transformers import AutoTokenizer, set_seed
    from parler_tts import ParlerTTSForConditionalGeneration

    device = "mps" if torch.backends.mps.is_available() and not a.cpu else "cpu"
    t0 = time.time()
    model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL).to(device)
    tok = AutoTokenizer.from_pretrained(MODEL)
    desc_tok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
    sr = model.config.sampling_rate
    print(f"model loaded on {device} in {time.time() - t0:.0f}s", flush=True)

    desc = desc_tok(a.desc, return_tensors="pt").to(device)
    gap = np.zeros(int(sr * a.pause), dtype=np.float32)
    pieces = []
    for i, s in enumerate(sentences(text), 1):
        t1 = time.time()
        set_seed(a.seed)
        prompt = tok(s, return_tensors="pt").to(device)
        with torch.no_grad():
            gen = model.generate(input_ids=desc.input_ids, attention_mask=desc.attention_mask,
                                 prompt_input_ids=prompt.input_ids, prompt_attention_mask=prompt.attention_mask)
        audio = gen.cpu().numpy().squeeze().astype(np.float32)
        pieces += [audio, gap]
        print(f"[{i}] {len(audio) / sr:.1f}s audio in {time.time() - t1:.0f}s: {s}", flush=True)

    out = to_wav48(np.concatenate(pieces[:-1]), sr, a.out)
    print(f"-> {out}  (total {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
