#!/usr/bin/env python3
"""CarVendors British Road kit for HyperFrames projects.

  kit.py install <hf-project>
      copy brand logos, fonts and frame.md into the project (never overwrites an existing frame.md)
  kit.py add <hf-project> <component> <instance-id> --start S --dur D [--track N] [--vars '{json}'] [--at 0.2,0.8,1.4]
      write compositions/<instance-id>.html from kit/components/<component>.html and insert its host
      <div> into index.html before the "<!-- KIT:INSERT -->" marker (or print it when there is no marker)
  kit.py list
      show components and their variables

Every use gets its own file and composition id: HyperFrames binds variables and timelines by composition
id, so one shared file mounted twice does not animate both copies (tested 2026-10-14).
"""
import argparse, json, re, shutil, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
COMP = KIT / "components"


def variables(src):
    m = re.search(r"data-composition-variables='(\[.*?\])'", src, re.S)
    return json.loads(m.group(1)) if m else []


def cmd_install(a):
    p = Path(a.project).expanduser()
    (p / "assets" / "brand").mkdir(parents=True, exist_ok=True)
    (p / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (KIT / "brand").iterdir():
        shutil.copy(f, p / "assets" / "brand" / f.name)
    for f in (KIT / "fonts").iterdir():
        shutil.copy(f, p / "assets" / "fonts" / f.name)
    if not (p / "frame.md").exists():
        shutil.copy(KIT / "frame.md", p / "frame.md")
    print(f"kit installed into {p} (brand, fonts, frame.md)")


def cmd_add(a):
    p = Path(a.project).expanduser()
    src_file = COMP / f"{a.component}.html"
    if not src_file.is_file():
        sys.exit(f"no component {a.component}; run kit.py list")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", a.id):
        sys.exit("instance id must be kebab-case, e.g. hook-1")
    src = src_file.read_text(encoding="utf-8")
    at = [float(x) for x in a.at.split(",")] if a.at else [0.15, 0.55, 0.95]
    out = src.replace("__ID__", a.id).replace("__DUR__", repr(float(a.dur))).replace("__AT__", json.dumps(at))
    dest = p / "compositions" / f"{a.id}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    vals = json.loads(a.vars) if a.vars else {}
    known = {v["id"] for v in variables(src)}
    unknown = set(vals) - known
    if unknown:
        sys.exit(f"unknown variables {sorted(unknown)}; {a.component} takes {sorted(known)}")
    vj = json.dumps(vals, ensure_ascii=False).replace("&", "&amp;").replace("'", "&#39;")
    attr = f" data-variable-values='{vj}'" if vals else ""
    host = (f'<div id="h-{a.id}" data-composition-id="{a.id}" data-composition-src="compositions/{a.id}.html"{attr}\n'
            f'        data-start="{a.start}" data-duration="{a.dur}" data-track-index="{a.track}" data-track-kind="graphics" '
            f'data-width="1080" data-height="1920"></div>')
    idx = p / "index.html"
    html = idx.read_text(encoding="utf-8") if idx.exists() else ""
    marker = "<!-- KIT:INSERT -->"
    if marker in html and f'data-composition-id="{a.id}"' not in html:
        idx.write_text(html.replace(marker, host + "\n      " + marker), encoding="utf-8")
        print(f"added {a.component} as {a.id} ({a.start}s +{a.dur}s) -> {dest.name}, host inserted in index.html")
    else:
        print(f"wrote {dest}\nhost:\n      {host}")


def cmd_list(a):
    for f in sorted(COMP.glob("*.html")):
        vs = variables(f.read_text(encoding="utf-8"))
        print(f"{f.stem:15s} " + ", ".join(f"{v['id']}={v['default']!r}" for v in vs))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("install"); s.add_argument("project"); s.set_defaults(fn=cmd_install)
    s = sub.add_parser("add"); s.add_argument("project"); s.add_argument("component"); s.add_argument("id")
    s.add_argument("--start", type=float, required=True); s.add_argument("--dur", type=float, required=True)
    s.add_argument("--track", type=int, default=2); s.add_argument("--vars"); s.add_argument("--at")
    s.set_defaults(fn=cmd_add)
    s = sub.add_parser("list"); s.set_defaults(fn=cmd_list)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
