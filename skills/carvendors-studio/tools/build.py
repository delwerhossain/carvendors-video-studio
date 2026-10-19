#!/usr/bin/env python3
"""Fast lane: build a whole CarVendors edit from one small job.json (the agent only fills the JSON).

  build.py <job.json> [--render] [--force]

Structure it always produces (no scene of the source is cut):
  [hook, played in full: in→out]  →  transition  →  [main source video, FULL length]  →  [outro]
  + fixed logo badge over the main video, old-text covers, optional overlays, music/voice, light grain.

job.json (all paths may be absolute, or names resolved with paths.py; times of covers/overlays are
seconds from the START OF THE MAIN VIDEO; "dur": "all" = until the main video ends):
{
  "id": "v002", "slug": "mitsubishi-asx",
  "folder": 2,                              # car_sources/<folder>/video.mp4  (or "source": "/path/video.mp4")
  "job_dir": null,                          # default: <projects_root>/<date>-bnf-<id>-<slug>
  "clean": {"boxes": [[76,704,428,108]],    # old text to REMOVE (source px); [] = keep all old text
            "grade": "eq=contrast=1.05:saturation=1.07:gamma=0.98"},   # "" = no grade
  "hook": {"file": "Soccer-Tire.mp4", "in": 0, "out": 5.75, "volume": 0.8},   # file in the hooks folder; whole action
  "transition": "cut",                      # cut | flash | whip | zoom  (exactly one, on the hook's last frame)
  "logo": {"corner": "top-left", "style": "dark", "credit": true},   # or false to omit
  "covers": [{"at": 0, "dur": "all", "x": 130, "y": 1310, "w": 820, "h": 230, "text": "", "style": "dark"}],
  "overlays": [{"component": "hero-model", "at": 0.2, "dur": 2.6, "vars": {"make": "MITSUBISHI", "model": "ASX", "x": 870, "y": 235, "align": "right", "size": 175, "scrim": 0.4}}],
  "music": {"file": "Royalty Free Music/NCS/Syn_Cole_-_Feel_Good_[NCS_Release].mp3", "start": 44.96, "volume": 0.6},
  "voice": null,                            # {"file": "voice/vo.wav", "at": 0.3} → music ducks to duck_volume
  "keep_source_audio": false,               # true only for real speech/engine sound worth keeping
  "outro": {"photo": "front-side-view.png", "dur": 3.0, "focus": "72% 50%"},   # file in showroom_pics; or false
  "grain": true
}
Re-running is cheap: the cleaned master and hook transcode are cached by their inputs (use --force to redo).
"""
import hashlib, json, os, shutil, subprocess, sys, datetime
from pathlib import Path

CS = Path(__file__).resolve().parent.parent
VS = Path.home() / ".claude" / "skills" / "video-studio"
PY = sys.executable


def sh(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:200], flush=True)
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def path_of(key):
    r = subprocess.run([PY, CS / "tools" / "paths.py", "get", key], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"path '{key}' not set: run  python3 {CS}/tools/paths.py detect  (or set {key} <path>)")
    return Path(r.stdout.strip())


def resolve(p, key=None):
    p = Path(os.path.expanduser(str(p)))
    if p.is_absolute():
        return p
    return path_of(key) / p if key else p


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout.strip())


def has_audio(f):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(f)],
                               capture_output=True, text=True).stdout.strip())


def cached(out, key, force, make):
    stamp = out.with_suffix(out.suffix + ".key")
    if not force and out.exists() and stamp.exists() and stamp.read_text() == key:
        print(f"  cached: {out.name}")
        return
    make()
    stamp.write_text(key)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        sys.exit(__doc__)
    force, render = "--force" in sys.argv, "--render" in sys.argv
    job_file = Path(a[0]).resolve()
    J = json.loads(job_file.read_text())
    jid, slug = J["id"], J.get("slug", "video")

    # ---------- job folder ----------
    if J.get("job_dir"):
        P = Path(os.path.expanduser(J["job_dir"]))
    else:
        P = path_of("projects_root") / f"{datetime.date.today():%Y-%m-%d}-bnf-{jid}-{slug}"
    if not (P / "brief.md").exists():
        P.mkdir(parents=True, exist_ok=True)
        (P / "brief.md").write_text(f"# {jid} {slug}\n\nBuilt with carvendors-studio fast lane (job.json).\n\n## Decisions\n")
    for d in ("input/source", "input/hooks", "work/footage", "work/qa", "output"):
        (P / d).mkdir(parents=True, exist_ok=True)
    shutil.copy(job_file, P / "job.json") if job_file != P / "job.json" else None
    print(f"job: {P}")

    # ---------- source + clean master ----------
    src = Path(os.path.expanduser(J["source"])) if J.get("source") else path_of("car_sources") / str(J["folder"]) / "video.mp4"
    local_src = P / "input/source" / f"{jid}.mp4"
    if not local_src.exists():
        shutil.copy(src, local_src)
    folder = src.parent
    for extra in ("comments.txt",):
        if (folder / extra).exists() and not (P / "input/source" / extra).exists():
            shutil.copy(folder / extra, P / "input/source" / extra)
    clean = J.get("clean") or {}
    boxes = [int(v) for b in clean.get("boxes", []) for v in b]
    grade = clean.get("grade", "")
    master = P / "work/footage" / f"{jid}_1080.mp4"
    def make_master():
        env = dict(os.environ, GRADE=grade) if grade else dict(os.environ)
        sh(["bash", VS / "scripts" / "clean_master.sh", local_src, master] + (boxes or ["none"]), env=env)
    cached(master, json.dumps([str(local_src), boxes, grade]), force, make_master)
    M = round(dur(master), 3)

    # ---------- hook (played in full between in/out) ----------
    H, hook_mp4, hook_vol = 0.0, None, 0
    if J.get("hook"):
        hk = J["hook"]
        hsrc = resolve(hk["file"], "hooks")
        hin, hout = float(hk.get("in", 0)), float(hk.get("out", dur(hsrc)))
        hook_mp4 = P / "work/footage" / "hook.mp4"
        def make_hook():
            sh(["ffmpeg", "-v", "error", "-y", "-ss", hin, "-to", hout, "-i", hsrc, "-vf",
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30", "-c:v", "libx264", "-crf", "16",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", hook_mp4])
        cached(hook_mp4, json.dumps([str(hsrc), hin, hout]), force, make_hook)
        H = round(dur(hook_mp4), 3)
        hook_vol = float(hk.get("volume", 0.8)) if has_audio(hook_mp4) else 0

    # ---------- outro ----------
    O, outro = 0.0, J.get("outro")
    if outro:
        O = float(outro.get("dur", 3.0))
    T = round(H + M + O, 3)

    # ---------- HyperFrames project ----------
    hf = P / "work" / "hf"
    if not (hf / "hyperframes.json").exists():
        sh(["npx", "hyperframes", "init", str(hf), "--non-interactive", "--example=blank"], cwd=P / "work", capture_output=True)
    for sub in ("fonts", "brand"):
        shutil.copytree(CS / "assets" / sub, hf / "assets" / sub, dirs_exist_ok=True)
    (hf / "assets" / "footage").mkdir(parents=True, exist_ok=True)
    (hf / "assets" / "audio").mkdir(parents=True, exist_ok=True)
    shutil.copy(master, hf / "assets/footage/main.mp4")
    if hook_mp4:
        shutil.copy(hook_mp4, hf / "assets/footage/hook.mp4")
    if outro:
        photo = resolve(outro["photo"], "showroom_pics")
        (hf / "assets/showroom").mkdir(parents=True, exist_ok=True)
        shutil.copy(photo, hf / "assets/showroom" / photo.name)
    music = J.get("music")
    if music:
        shutil.copy(resolve(music["file"], "bgm"), hf / ("assets/audio/music" + Path(music["file"]).suffix))
    voice = J.get("voice")
    if voice:
        vf = resolve(voice["file"])
        vf = vf if vf.is_absolute() and vf.exists() else P / voice["file"]
        shutil.copy(vf, hf / ("assets/audio/voice" + vf.suffix))
    for f in (hf / "compositions").glob("*.html") if (hf / "compositions").exists() else []:
        f.unlink()   # rebuilt from job.json every time

    # ---------- index.html ----------
    tr = J.get("transition", "cut")
    keep_src = bool(J.get("keep_source_audio")) and has_audio(master)
    el, js = [], []
    if hook_mp4:
        el.append(f'<div class="kb" id="kb-hook"><div class="pz" id="pz-hook"><video id="v-hook" class="clip" src="assets/footage/hook.mp4" playsinline'
                  f' {"data-has-audio=\"true\" data-volume=\"%s\"" % hook_vol if hook_vol else "muted"} data-start="0" data-duration="{H}" data-track-index="0"></video></div></div>')
    el.append(f'<div class="kb" id="kb-main"><div class="pz" id="pz-main"><video id="v-main" class="clip" src="assets/footage/main.mp4" playsinline muted'
              f' data-start="{H}" data-duration="{M}" data-track-index="1"></video></div></div>')
    if J.get("grain", True):
        el.append('<div id="grain"></div>')
    el.append("<!-- CV:INSERT -->")
    # gentle continuous drift on the main video (cheap, feels shot-aware enough for static tripod clips)
    js.append(f'tl.fromTo("#kb-main",{{scale:1}},{{scale:1.035,duration:{M},ease:"none",immediateRender:false}},{H});')
    if hook_mp4:
        if tr == "cut":
            js.append(f'tl.fromTo("#pz-main",{{scale:1.07}},{{scale:1,duration:0.42,ease:"expo.out",immediateRender:false}},{H});')
        elif tr == "flash":
            el.append('<div id="flash"></div>')
            js.append(f'tl.fromTo("#flash",{{opacity:0}},{{opacity:0.85,duration:0.04,ease:"none",immediateRender:false}},{H-0.04}).to("#flash",{{opacity:0,duration:0.22}},{H});')
        elif tr == "whip":
            js.append(f'tl.fromTo("#pz-hook",{{x:0,filter:"blur(0px)"}},{{x:-760,filter:"blur(20px)",duration:0.2,ease:"power3.in",immediateRender:false}},{H-0.2});')
            js.append(f'tl.fromTo("#pz-main",{{x:760,filter:"blur(20px)"}},{{x:0,filter:"blur(0px)",duration:0.26,ease:"power3.out",immediateRender:false}},{H});')
        elif tr == "zoom":
            js.append(f'tl.fromTo("#pz-hook",{{scale:1,filter:"blur(0px)"}},{{scale:1.25,filter:"blur(14px)",duration:0.2,ease:"power2.in",immediateRender:false}},{H-0.2});')
            js.append(f'tl.fromTo("#pz-main",{{scale:1.25,filter:"blur(14px)"}},{{scale:1,filter:"blur(0px)",duration:0.4,ease:"expo.out",immediateRender:false}},{H});')
    audio = []
    if keep_src:
        el.append(f'<audio id="srcaudio" src="assets/footage/main.mp4" data-start="{H}" data-duration="{M}" data-track-index="9" data-volume="1"></audio>')
    if music:
        mv = float(music.get("volume", 0.6)); dv = float(music.get("duck_volume", 0.14))
        pts = [{"t": 0, "v": mv * 0.6}, {"t": max(H - 0.05, 0.01), "v": mv * 0.7}, {"t": H + 0.05, "v": mv}]
        if voice:
            va = H + float(voice.get("at", 0.3)); vd = dur(hf / ("assets/audio/voice" + Path(vf).suffix))
            pts += [{"t": va - 0.3, "v": mv}, {"t": va, "v": dv}, {"t": va + vd, "v": dv}, {"t": va + vd + 0.4, "v": mv}]
        pts += [{"t": T - 1.2, "v": mv}, {"t": T, "v": 0}]
        lane = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": sorted(pts, key=lambda p: p["t"])}]})
        el.append(f'<audio id="music" src="assets/audio/music{Path(music["file"]).suffix}" data-start="0" data-duration="{T}" data-media-start="{float(music.get("start", 0))}" data-track-index="10" data-automation=\'{lane}\'></audio>')
    if voice:
        el.append(f'<audio id="voice" src="assets/audio/voice{Path(vf).suffix}" data-start="{H + float(voice.get("at", 0.3))}" data-track-index="11" data-volume="1"></audio>')

    html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #root > div[data-composition-src] {{ position: absolute; inset: 0; pointer-events: none; }}
      .kb {{ position: absolute; inset: 0; overflow: hidden; will-change: transform; }}
      .pz {{ position: absolute; inset: 0; will-change: transform; }}
      .pz video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; z-index: 50; }}
      #grain {{ position: absolute; inset: -20px; pointer-events: none; opacity: 0.035; mix-blend-mode: overlay;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' seed='7'/></filter><rect width='160' height='160' filter='url(%23n)'/></svg>"); }}
    </style>
  </head>
  <body>
    <!-- generated by carvendors-studio/tools/build.py from job.json; edit the JSON and re-run instead of this file -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1080" data-height="1920">
      {chr(10).join("      " + e for e in el).strip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).strip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    (hf / "index.html").write_text(html)

    # ---------- mount components ----------
    mount = [PY, CS / "tools" / "mount.py", "add", hf]
    def end_of(o):
        return M - float(o["at"]) if o.get("dur", "all") == "all" else float(o["dur"])
    for i, c in enumerate(J.get("covers", []), 1):
        v = {k: c[k] for k in c if k not in ("at", "dur")}
        v.setdefault("reveal", "none" if float(c["at"]) == 0 else "wipe")
        sh(mount + ["text-cover", f"cover{i}", "--start", round(H + float(c["at"]), 3), "--dur", round(end_of(c), 3), "--track", 6, "--vars", json.dumps(v)])
    for i, o in enumerate(J.get("overlays", []), 1):
        sh(mount + [o["component"], f"ov{i}-{o['component']}", "--start", round(H + float(o["at"]), 3), "--dur", round(end_of(o), 3), "--track", 7, "--vars", json.dumps(o.get("vars", {}))])
    if J.get("logo", True):
        lg = J.get("logo") if isinstance(J.get("logo"), dict) else {}
        sh(mount + ["logo-badge", "badge", "--start", H, "--dur", M, "--track", 8, "--vars", json.dumps(lg)])
    if outro:
        photo = resolve(outro["photo"], "showroom_pics")
        sh(mount + ["outro-real-showroom", "outro", "--start", H + M, "--dur", O, "--track", 9,
                    "--vars", json.dumps({"src": f"../assets/showroom/{photo.name}", "focus": outro.get("focus", "50% 50%")})])

    # ---------- check ----------
    r = subprocess.run(["npx", "hyperframes", "check"], cwd=hf, capture_output=True, text=True)
    tail = "\n".join(l for l in r.stdout.splitlines() if any(k in l for k in ("✗", "Check", "text checks", "error(s)")))
    print(tail)
    print(f"\nlength: hook {H}s + main {M}s + outro {O}s = {T}s")
    if not render:
        print(f"next: npx hyperframes snapshot {hf} --at ... ; then  build.py {job_file} --render")
        return
    raw = hf / "renders" / f"{jid}-raw.mp4"
    sh(["npx", "hyperframes", "render", ".", "-o", raw, "-q", "delivery"], cwd=hf, capture_output=True)
    n = 1
    while (P / "output" / f"{jid}_{slug}_carvendors_v{n}.mp4").exists():
        n += 1
    out = P / "output" / f"{jid}_{slug}_carvendors_v{n}.mp4"
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    d = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
          f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,aresample=48000")
    sh(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c:v", "copy", "-af", ln, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
    sheet = P / "output" / f"{jid}_{slug}_v{n}_frames.jpg"
    times = [0.3, H + 0.3, H + M * 0.33, H + M * 0.66, H + M - 0.3, T - 0.5]
    tiles = []
    for i, t in enumerate(times):
        f = P / "work/qa" / f"final_{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(t, 0):.2f}", "-i", out, "-frames:v", "1", "-vf", "scale=-2:640", f])
        tiles.append(f)
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + sum([["-i", t] for t in tiles], []) + ["-filter_complex", f"hstack={len(tiles)}", sheet])
    print(f"\nOUTPUT {out}\nFRAMES {sheet}")


if __name__ == "__main__":
    main()
