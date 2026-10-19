#!/usr/bin/env python3
"""Mount a CarVendors Studio motion component into a HyperFrames project.

  mount.py add <hf-project> <component> <instance-id> --start S --dur D [--track N] [--vars '{json}']
               [--vars-file f.json] [--words words.json --words-offset 0] [--below other-id]
      Copies components/<component>.html (found next to this tool: ../components/) to
      <hf-project>/compositions/<instance-id>.html with the __ID__ and __DUR__ placeholders filled in, and
      inserts the host <div> into <hf-project>/index.html just before the "<!-- CV:INSERT -->" marker.
      Without the marker the host line is printed for you to paste. Re-running with the same id replaces it.
      Paint order = DOM order (track numbers do not stack layers): --below <id> inserts the host just
      before h-<id>, e.g. a localized-contrast scrim under its headline.
      --words (caption-line only): a tts.py / to_hf_transcript-style word list
      ([{"text","start","end"}, ...]) is chunked into the "chunks" variable (max 6 words / 30 chars,
      breaks at sentence ends and pauses > 0.45 s). --words-offset shifts it (seconds, host-local).
  mount.py list
      Shows each component and its variables with defaults.

Components: hero-model, detail-line, shape-text, localized-contrast, logo-top, verified-feature,
caption-line, outro-real-showroom (usage: ../COMPONENTS.md).

Every use gets its own file and composition id: HyperFrames binds timelines by composition id, so one
shared file mounted twice does not animate both copies. The components load fonts and brand art from
<hf-project>/assets/fonts and <hf-project>/assets/brand (copy them from ../assets/, see COMPONENTS.md).
"""
import argparse, json, re, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent  # the carvendors-studio folder
COMP = KIT / "components"
MARKER = "<!-- CV:INSERT -->"


def declared(src):
    m = re.search(r"data-composition-variables='(\[.*?\])'", src, re.S)
    return json.loads(m.group(1)) if m else []


def chunk_words(words, offset=0.0, max_words=6, max_chars=30, gap=0.45):
    words = [w for w in words if not (w["text"].startswith("[") and w["text"].endswith("]"))]
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        text = " ".join(x["text"] for x in cur)
        end_sentence = w["text"].rstrip().endswith((".", "?", "!"))
        pause = nxt is not None and nxt["start"] - w["end"] > gap
        too_long = nxt is not None and (len(cur) >= max_words or len(text) + 1 + len(nxt["text"]) > max_chars)
        if nxt is None or end_sentence or pause or too_long:
            chunks.append({
                "s": round(cur[0]["start"] + offset, 3),
                "e": round(cur[-1]["end"] + offset, 3),
                "w": [[x["text"], round(x["start"] + offset, 3)] for x in cur],
            })
            cur = []
    return chunks


def cmd_add(a):
    p = Path(a.project).expanduser().resolve()
    src_file = COMP / f"{a.component}.html"
    if not src_file.is_file():
        sys.exit(f"no component {a.component}; run mount.py list")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", a.id):
        sys.exit("instance id must be kebab-case, e.g. card-1")
    src = src_file.read_text(encoding="utf-8")
    vals = {}
    if a.vars_file:
        vals.update(json.loads(Path(a.vars_file).read_text(encoding="utf-8")))
    if a.vars:
        vals.update(json.loads(a.vars))
    if a.words:
        vals["chunks"] = json.dumps(chunk_words(json.loads(Path(a.words).read_text(encoding="utf-8")),
                                                a.words_offset), ensure_ascii=False)
    if isinstance(vals.get("chunks"), list):
        vals["chunks"] = json.dumps(vals["chunks"], ensure_ascii=False)
    known = {v["id"] for v in declared(src)}
    unknown = set(vals) - known
    if unknown:
        sys.exit(f"unknown variables {sorted(unknown)}; {a.component} takes {sorted(known)}")
    out = src.replace("__ID__", a.id).replace("__DUR__", repr(float(a.dur)))
    dest = p / "compositions" / f"{a.id}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    vj = json.dumps(vals, ensure_ascii=False).replace("&", "&amp;").replace("'", "&#39;")
    attr = f" data-variable-values='{vj}'" if vals else ""
    kind = "captions" if a.component == "caption-line" else "graphics"
    host = (f'<div id="h-{a.id}" data-composition-id="{a.id}" data-composition-src="compositions/{a.id}.html"{attr}\n'
            f'        data-start="{a.start}" data-duration="{a.dur}" data-track-index="{a.track}" '
            f'data-track-kind="{kind}" data-width="1080" data-height="1920"></div>')
    idx = p / "index.html"
    html = idx.read_text(encoding="utf-8") if idx.exists() else ""
    if MARKER in html:
        # replace an existing host for this id (re-mount), else insert before the marker
        pat = re.compile(r'<div id="h-' + re.escape(a.id) + r'".*?</div>\n\s*', re.S)
        html = pat.sub("", html)
        anchor = f'<div id="h-{a.below}"' if a.below else None
        if anchor and anchor in html:
            # stack under another instance (DOM order = paint order), e.g. a scrim under its headline
            html = html.replace(anchor, host + "\n      " + anchor, 1)
        else:
            if anchor:
                print(f"note: no host h-{a.below} yet; inserted at the marker (on top)")
            html = html.replace(MARKER, host + "\n      " + MARKER)
        idx.write_text(html, encoding="utf-8")
        print(f"mounted {a.component} as {a.id} ({a.start}s +{a.dur}s) -> compositions/{dest.name}")
    else:
        print(f"wrote {dest}\npaste this host inside the root:\n      {host}")


def cmd_list(a):
    for f in sorted(COMP.glob("*.html")):
        vs = declared(f.read_text(encoding="utf-8"))
        print(f"{f.stem}")
        for v in vs:
            d = v["default"]
            d = (d[:60] + "...") if isinstance(d, str) and len(d) > 60 else d
            print(f"    {v['id']:10s} {v['type']:8s} {d!r}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("project")
    s.add_argument("component")
    s.add_argument("id")
    s.add_argument("--start", type=float, required=True)
    s.add_argument("--dur", type=float, required=True)
    s.add_argument("--track", type=int, default=2)
    s.add_argument("--below", help="instance id to paint under (inserts the host just before h-<id>)")
    s.add_argument("--vars")
    s.add_argument("--vars-file")
    s.add_argument("--words")
    s.add_argument("--words-offset", type=float, default=0.0)
    s.set_defaults(fn=cmd_add)
    l = sub.add_parser("list")
    l.set_defaults(fn=cmd_list)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
