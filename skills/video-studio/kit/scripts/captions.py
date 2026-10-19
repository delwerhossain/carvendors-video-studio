#!/usr/bin/env python3
"""British Road caption track for a HyperFrames project (one track, word-by-word, active word on a yellow plate).

Usage: captions.py <config.json>

config.json:
{
  "project": "/path/to/hf",                  // HyperFrames project root
  "duration": 30,                            // root data-duration
  "out": "compositions/captions.html",       // optional
  "segments": [
    {"kind": "words", "file": "assets/audio/v01.words.json", "offset": 0.5},             // tts.py output
    {"kind": "review", "transcript": "../work/tr/transcript.json",                        // claude-shorts transcribe.py
     "in": 0.0, "out": 9.65, "start": 12.0, "fix": {"Carvandas": "CarVendors"}}
  ]
}
Paths are relative to the project. Review captions keep the speaker's words: only "fix" spellings change and
fillers (uh, um, erm) are not displayed. "B and F" is shown as "B&F". Chunks: up to 4 words / 23 characters,
broken at sentence ends, long commas and pauses over 0.45 s; a lone short word folds into the previous chunk.
Host: <div id="g-captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
       data-start="0" data-duration="<duration>" data-track-index="4" data-track-kind="captions" ...></div>
"""
import json, re, sys
from pathlib import Path

FILLERS = {"uh", "uh,", "um", "um,", "erm", "erm,"}


def load_words(cfg, root):
    words = []
    for seg in cfg["segments"]:
        if seg["kind"] == "words":
            for w in json.loads((root / seg["file"]).read_text(encoding="utf-8")):
                if not (w["text"].startswith("[") and w["text"].endswith("]")):
                    words.append([w["text"], w["start"] + seg["offset"], w["end"] + seg["offset"], id(seg)])
        elif seg["kind"] == "review":
            tr = json.loads((root / seg["transcript"]).read_text(encoding="utf-8"))
            fix = seg.get("fix", {})
            for w in (x for c in tr["chunks"] for x in c["words"]):
                if seg["in"] - 0.05 <= w["start"] and w["end"] <= seg["out"] + 0.05:
                    t = fix.get(w["w"], w["w"])
                    if t.lower() not in FILLERS:
                        words.append([t, w["start"] - seg["in"] + seg["start"], w["end"] - seg["in"] + seg["start"], id(seg)])
    words.sort(key=lambda w: w[1])
    merged, i = [], 0
    while i < len(words):
        if i + 2 < len(words) and [w[0] for w in words[i:i + 3]] == ["B", "and", "F"]:
            merged.append(["B&F", words[i][1], words[i + 2][2], words[i][3]]); i += 3
        else:
            merged.append(words[i]); i += 1
    for w in merged:
        w[0] = w[0].replace("...", "…")
    return merged


def chunk(words):
    groups, cur = [], []
    for j, w in enumerate(words):
        cur.append(w)
        nxt = words[j + 1] if j + 1 < len(words) else None
        chars = sum(len(x[0]) + 1 for x in cur)
        nchars = chars + (len(nxt[0]) + 1 if nxt else 0)
        gap = (nxt[1] - w[2]) if nxt else 9
        if (not nxt or nxt[3] != w[3] or gap > 0.45 or len(cur) >= 4 or nchars > 23
                or re.search(r"[.?!…]$", w[0]) or (w[0].endswith(",") and chars >= 10)):
            groups.append(cur); cur = []
    out = []
    for g in groups:
        if out and len(g) == 1 and len(g[0][0]) <= 6 and g[0][1] - out[-1][-1][2] < 0.45 \
                and sum(len(x[0]) + 1 for x in out[-1] + g) <= 28 and out[-1][-1][3] == g[0][3]:
            out[-1] = out[-1] + g
        else:
            out.append(g)
    return out


HTML = """<!doctype html>
<html>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>
        #root { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
        #cap-band { position: absolute; left: 70px; right: 70px; top: 1250px; height: 170px; }
        .cap-group { position: absolute; left: 0; right: 0; top: 0; display: flex; justify-content: center; opacity: 0; }
        .cap-line { display: block; max-width: 940px; text-align: center; font-family: "Montserrat", sans-serif; font-weight: 800;
          font-size: 64px; line-height: 1.18; color: #ffffff; text-shadow: 0 3px 0 #111311, 0 0 22px rgb(0 0 0 / 65%); }
        .cap-w { display: inline-block; margin: 0 0.02em; padding: 0 0.12em; border-radius: 10px; }
      </style>
      <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
        <div id="cap-band"></div>
      </div>
      <script>
        const GROUPS = __DATA__;
        const band = document.getElementById("cap-band");
        const tl = gsap.timeline({ paused: true });
        GROUPS.forEach(function (g, gi) {
          const el = document.createElement("div"); el.className = "cap-group"; el.id = "cap-g" + gi;
          const line = document.createElement("div"); line.className = "cap-line"; line.id = "cap-l" + gi;
          g.w.forEach(function (w, wi) {
            const s = document.createElement("span"); s.className = "cap-w"; s.id = "cap-g" + gi + "-w" + wi; s.textContent = w[0]; line.appendChild(s);
          });
          el.appendChild(line); band.appendChild(el);
          tl.set(el, { opacity: 1 }, g.s);
          tl.fromTo(line, { y: 14, scale: 0.94 }, { y: 0, scale: 1, duration: 0.16, ease: "back.out(2)" }, g.s);
          g.w.forEach(function (w, wi) {
            const sel = "#cap-g" + gi + "-w" + wi;
            tl.set(sel, { backgroundColor: "#f7d117", color: "#111311", textShadow: "none" }, w[1]);
            tl.set(sel, { backgroundColor: "rgba(0,0,0,0)", color: "#ffffff", textShadow: "0 3px 0 #111311, 0 0 22px rgba(0,0,0,0.65)" }, Math.min(w[2], g.e));
          });
          tl.set(el, { opacity: 0 }, g.e);
        });
        window.__timelines["captions"] = tl;
      </script>
    </template>
  </body>
</html>
"""


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    root = Path(cfg["project"]).expanduser()
    dur = float(cfg["duration"])
    groups = chunk(load_words(cfg, root))
    data = []
    for i, g in enumerate(groups):
        s = max(0, g[0][1] - 0.05)
        nxt = groups[i + 1][0][1] - 0.05 if i + 1 < len(groups) else dur
        e = min(nxt, g[-1][2] + 0.4, dur)
        data.append({"s": round(s, 3), "e": round(e, 3), "w": [[x[0], round(x[1], 3), round(x[2], 3)] for x in g]})
    out = root / cfg.get("out", "compositions/captions.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print(f"{len(data)} caption chunks -> {out}")
    for g in data:
        print(f"  {g['s']:6.2f}-{g['e']:6.2f}  " + " ".join(w[0] for w in g["w"]))


if __name__ == "__main__":
    main()
