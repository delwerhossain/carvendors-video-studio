#!/usr/bin/env python3
"""Convert word timings into HyperFrames' transcript.json ([{"text", "start", "end", "id"}]).

Usage: to_hf_transcript.py <input.json> <out transcript.json> [--offset SECONDS]

Input is either claude-shorts' transcript.json ({"chunks": [{"words": [{"w", "start", "end"}]}]})
or tts.py's .words.json ([{"text", "start", "end"}]). Use this for Bengali: `hyperframes transcribe`
glues Bengali words into one entry, so it cannot drive word-level captions.
--offset shifts every word (e.g. a voiceover that starts 2.5 s into the video).
"""
import json, sys


def main():
    args = sys.argv[1:]
    offset = 0.0
    if "--offset" in args:
        i = args.index("--offset"); offset = float(args[i + 1]); del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    data = json.load(open(args[0], encoding="utf-8"))
    if isinstance(data, dict) and "chunks" in data:
        raw = [(w["w"], w["start"], w["end"]) for c in data["chunks"] for w in c.get("words", [])]
    else:
        raw = [(w["text"], w["start"], w["end"]) for w in data]
    out = [{"text": t.strip(), "start": round(s + offset, 3), "end": round(e + offset, 3), "id": f"w{i}"}
           for i, (t, s, e) in enumerate(x for x in raw if x[0].strip())]
    json.dump(out, open(args[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(out)} words -> {args[1]}")


if __name__ == "__main__":
    main()
