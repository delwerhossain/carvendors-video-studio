#!/usr/bin/env python3
"""Fast lane: build one CarVendors edit from a small job.json (Mac + Windows).

  build.py <job.json> [--render] [--force]

Always: [attention hook, played in full] → one transition → [the WHOLE source video] → [outro].
Plus: fixed logo badge, old-text covers, optional overlays, music (+ voice ducking), light grain, `hyperframes check`.
--render also renders, masters to -14 LUFS, writes <job>/output/<id>_<slug>_carvendors_vN.mp4 + a frame sheet,
copies the final to the shared exports folder and records hook/outro/music in the shared ledger (hook counts).

Missing fields come from the team config on Drive (_studio/config.json → defaults): logo, transition, grade,
music, outro. "hook": "auto" (or no hook key) = least-used hook from the shared catalog (hooks.py pick).

job.json (times of covers/overlays are seconds from the START OF THE MAIN VIDEO; "dur": "all" = to its end):
{
  "id": "v002", "slug": "mitsubishi-asx", "folder": 2,        # car_sources/<folder>/video.mp4 (or "source": path)
  "hook": "auto",                                            # or {"file": "Car Hooks/Car Flip.mp4", "in": 0, "out": 3.2}; null = no hook
  "remove": [[76,704,428,108]],                              # old text boxes to inpaint (source px); [] / omitted = none
  "covers": [{"at": 0, "dur": "all", "x": 135, "y": 1305, "w": 810, "h": 230, "text": "Spotted at B&F Cars", "kicker": "FEATURED"}],
  "overlays": [{"component": "label-card", "at": 0.2, "dur": 2.6, "vars": {"title": "Mitsubishi ASX", "sub": "Compact SUV."}}],
  "logo": {"corner": "top-left", "style": "dark"},           # optional (config default); false = none
  "transition": "cut", "grade": "", "music": {...}, "outro": {...}, "voice": null, "keep_source_audio": false
}
"""
import datetime, hashlib, json, os, platform, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CS = HERE.parent
sys.path.insert(0, str(HERE))
import paths  # noqa: E402

PY = sys.executable


def tool(name):
    t = shutil.which(name) or shutil.which(name + ".cmd")
    if not t:
        sys.exit(f"{name} not found on PATH (run the team install)")
    return t


def sh(cmd, **kw):
    cmd = [str(c) for c in cmd]
    print("  $", " ".join(cmd)[:180], flush=True)
    return subprocess.run(cmd, check=True, **kw)


def need(key):
    p = paths.get(key)
    if not p or not p.exists():
        sys.exit(f"path '{key}' missing — python tools/paths.py show")
    return p


def under(p, key):
    p = Path(os.path.expanduser(str(p)))
    return p if p.is_absolute() else need(key) / p


def dur(f):
    r = subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip())


def has_audio(f):
    r = subprocess.run([tool("ffprobe"), "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def cached(out, key, force, make):
    stamp = out.with_name(out.name + ".key")
    if not force and out.exists() and stamp.exists() and stamp.read_text() == key:
        print(f"  cached: {out.name}"); return
    make(); stamp.write_text(key)


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not args:
        sys.exit(__doc__)
    force, render = "--force" in sys.argv, "--render" in sys.argv
    job_file = Path(args[0]).resolve()
    J = json.loads(job_file.read_text(encoding="utf-8"))
    D = paths.shared_config()[1].get("defaults", {})
    jid, slug = J["id"], J.get("slug", "video")

    if J.get("job_dir"):
        P = Path(os.path.expanduser(J["job_dir"]))
    elif job_file.name == "job.json" and job_file.parent.name.startswith("bnf-"):
        P = job_file.parent                      # planned by batch.py: build in place
    else:
        P = need("projects_root") / f"bnf-{jid}"
    for d in ("input", "work/footage", "work/qa", "output"):
        (P / d).mkdir(parents=True, exist_ok=True)
    if job_file != P / "job.json":
        shutil.copy(job_file, P / "job.json")
    print(f"job: {P}")

    # ---------- source → clean master (cached) ----------
    src = Path(os.path.expanduser(J["source"])) if J.get("source") else need("car_sources") / str(J["folder"]) / "video.mp4"
    local_src = P / "input" / f"{jid}.mp4"
    if not local_src.exists():
        shutil.copy(src, local_src)
    if (src.parent / "comments.txt").exists() and not (P / "input/comments.txt").exists():
        shutil.copy(src.parent / "comments.txt", P / "input/comments.txt")
    boxes = J.get("remove") or (J.get("clean") or {}).get("boxes") or []
    grade = J.get("grade", (J.get("clean") or {}).get("grade", D.get("grade", "")))
    master = P / "work/footage" / f"{jid}_1080.mp4"
    def make_master():
        cmd = [PY, HERE / "clean.py", local_src, master] + (["--grade", grade] if grade else [])
        for b in boxes:
            cmd += ["--box"] + [int(v) for v in b]
        sh(cmd)
    cached(master, json.dumps([str(local_src), boxes, grade]), force, make_master)
    M = round(dur(master), 3)

    # ---------- hook (whole action) ----------
    hk = J.get("hook", "auto")
    if hk == "auto":
        import hooks
        hk = hooks.pick(jid, car=bool(J.get("car_hook")))
        J["hook"] = hk
        (P / "job.json").write_text(json.dumps(J, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  hook picked: {hk['file']} (used {hk['uses_so_far']}x before)")
    H, hook_mp4, hook_vol = 0.0, None, 0
    if hk:
        hsrc = under(hk["file"], "hooks")
        hin, hout = float(hk.get("in", 0)), float(hk.get("out", dur(hsrc)))
        hook_mp4 = P / "work/footage/hook.mp4"
        cached(hook_mp4, json.dumps([str(hsrc), hin, hout]), force, lambda: sh([tool("ffmpeg"), "-v", "error", "-y", "-ss", hin, "-to", hout, "-i", hsrc,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", hook_mp4]))
        H = round(dur(hook_mp4), 3)
        hook_vol = float(hk.get("volume", 0.8)) if has_audio(hook_mp4) else 0

    # ---------- outro: team outro video (config) or real showroom photo ----------
    outro = J.get("outro", {})
    if outro is not False:
        outro = dict(outro or {})
        if not outro.get("video") and not outro.get("photo"):
            if D.get("outro_video"):
                outro["video"] = D["outro_video"]
            else:
                outro["photo"] = D.get("outro_photo", "front-side-view.png")
    O, outro_mp4 = 0.0, None
    if outro and outro.get("video"):
        osrc = under(outro["video"], "outros")
        outro_mp4 = P / "work/footage/outro.mp4"
        cached(outro_mp4, str(osrc), force, lambda: sh([tool("ffmpeg"), "-v", "error", "-y", "-i", osrc, "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", outro_mp4]))
        O = round(dur(outro_mp4), 3)
    elif outro:
        O = float(outro.get("dur", 3.0))
    T = round(H + M + O, 3)

    # ---------- HyperFrames project ----------
    hf = P / "work" / "hf"
    if not (hf / "hyperframes.json").exists():
        sh([tool("npx"), "--yes", "hyperframes", "init", str(hf), "--non-interactive", "--example=blank"], cwd=P / "work", capture_output=True)
    for sub in ("fonts", "brand"):
        shutil.copytree(CS / "assets" / sub, hf / "assets" / sub, dirs_exist_ok=True)
    for sub in ("footage", "audio", "showroom"):
        (hf / "assets" / sub).mkdir(parents=True, exist_ok=True)
    shutil.copy(master, hf / "assets/footage/main.mp4")
    if hook_mp4:
        shutil.copy(hook_mp4, hf / "assets/footage/hook.mp4")
    if outro_mp4:
        shutil.copy(outro_mp4, hf / "assets/footage/outro.mp4")
    photo = None
    if outro and outro.get("photo") and not outro_mp4:
        photo = under(outro["photo"], "showroom_pics")
        shutil.copy(photo, hf / "assets/showroom" / photo.name)
    music = J.get("music") or ({"file": D["music"][int(hashlib.md5(jid.encode()).hexdigest(), 16) % len(D["music"])], "start": 30} if D.get("music") else None)
    if music:
        shutil.copy(under(music["file"], "bgm"), hf / ("assets/audio/music" + Path(music["file"]).suffix))
    voice, vf = J.get("voice"), None
    if voice:
        vf = Path(os.path.expanduser(voice["file"]))
        vf = vf if vf.is_absolute() else P / voice["file"]
        shutil.copy(vf, hf / ("assets/audio/voice" + vf.suffix))
    if (hf / "compositions").exists():
        for f in (hf / "compositions").glob("*.html"):
            f.unlink()

    tr = J.get("transition", D.get("transition", "cut"))
    keep_src = bool(J.get("keep_source_audio")) and has_audio(master)
    el, js = [], []
    if hook_mp4:
        a_attr = f'data-has-audio="true" data-volume="{hook_vol}"' if hook_vol else "muted"
        el.append(f'<div class="kb" id="kb-hook"><div class="pz" id="pz-hook"><video id="v-hook" class="clip" src="assets/footage/hook.mp4" playsinline {a_attr} data-start="0" data-duration="{H}" data-track-index="0"></video></div></div>')
    el.append(f'<div class="kb" id="kb-main"><div class="pz" id="pz-main"><video id="v-main" class="clip" src="assets/footage/main.mp4" playsinline muted data-start="{H}" data-duration="{M}" data-track-index="1"></video></div></div>')
    if outro_mp4:
        el.append(f'<div class="kb" id="kb-outro"><div class="pz"><video id="v-outro" class="clip" src="assets/footage/outro.mp4" playsinline data-has-audio="true" data-volume="1" data-start="{H + M}" data-duration="{O}" data-track-index="2"></video></div></div>')
    if J.get("grain", True):
        el.append('<div id="grain"></div>')
    el.append("<!-- CV:INSERT -->")
    js.append(f'tl.fromTo("#kb-main",{{scale:1}},{{scale:1.035,duration:{M},ease:"none",immediateRender:false}},{H});')
    if hook_mp4:
        if tr == "flash":
            el.append('<div id="flash"></div>')
            js.append(f'tl.fromTo("#flash",{{opacity:0}},{{opacity:0.85,duration:0.04,ease:"none",immediateRender:false}},{H-0.04}).to("#flash",{{opacity:0,duration:0.22}},{H});')
        elif tr == "whip":
            js.append(f'tl.fromTo("#pz-hook",{{x:0,filter:"blur(0px)"}},{{x:-760,filter:"blur(20px)",duration:0.2,ease:"power3.in",immediateRender:false}},{H-0.2});')
            js.append(f'tl.fromTo("#pz-main",{{x:760,filter:"blur(20px)"}},{{x:0,filter:"blur(0px)",duration:0.26,ease:"power3.out",immediateRender:false}},{H});')
        elif tr == "zoom":
            js.append(f'tl.fromTo("#pz-hook",{{scale:1,filter:"blur(0px)"}},{{scale:1.25,filter:"blur(14px)",duration:0.2,ease:"power2.in",immediateRender:false}},{H-0.2});')
            js.append(f'tl.fromTo("#pz-main",{{scale:1.25,filter:"blur(14px)"}},{{scale:1,filter:"blur(0px)",duration:0.4,ease:"expo.out",immediateRender:false}},{H});')
        else:
            js.append(f'tl.fromTo("#pz-main",{{scale:1.07}},{{scale:1,duration:0.42,ease:"expo.out",immediateRender:false}},{H});')
    if keep_src:
        el.append(f'<audio id="srcaudio" src="assets/footage/main.mp4" data-start="{H}" data-duration="{M}" data-track-index="9" data-volume="1"></audio>')
    if music:
        mv, dv = float(music.get("volume", 0.6)), float(music.get("duck_volume", 0.14))
        mend = H + M + (0 if outro_mp4 else O)      # an outro video brings its own sound
        pts = [{"t": 0, "v": mv * 0.6}, {"t": max(H - 0.05, 0.01), "v": mv * 0.7}, {"t": H + 0.05, "v": mv}]
        if voice:
            va = H + float(voice.get("at", 0.3)); vd = dur(vf)
            pts += [{"t": va - 0.3, "v": mv}, {"t": va, "v": dv}, {"t": va + vd, "v": dv}, {"t": va + vd + 0.4, "v": mv}]
        pts += [{"t": mend - 1.0, "v": mv}, {"t": mend, "v": 0}]
        lane = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": sorted(pts, key=lambda p: p["t"])}]})
        el.append(f'<audio id="music" src="assets/audio/music{Path(music["file"]).suffix}" data-start="0" data-duration="{mend}" data-media-start="{float(music.get("start", 0))}" data-track-index="10" data-automation=\'{lane}\'></audio>')
    if voice:
        el.append(f'<audio id="voice" src="assets/audio/voice{vf.suffix}" data-start="{H + float(voice.get("at", 0.3))}" data-track-index="11" data-volume="1"></audio>')

    nl = "\n      "
    (hf / "index.html").write_text(f'''<!doctype html>
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
    <!-- generated by carvendors-studio/tools/build.py from job.json — edit the JSON and re-run -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1080" data-height="1920">
      {nl.join(el)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {nl.join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
''', encoding="utf-8")

    # ---------- components ----------
    mount = [PY, HERE / "mount.py", "add", hf]
    span = lambda o: M - float(o["at"]) if o.get("dur", "all") == "all" else float(o["dur"])
    for i, c in enumerate(J.get("covers", []), 1):
        v = {k: c[k] for k in c if k not in ("at", "dur")}
        v.setdefault("reveal", "none" if float(c["at"]) == 0 else "wipe")
        sh(mount + ["text-cover", f"cover{i}", "--start", round(H + float(c["at"]), 3), "--dur", round(span(c), 3), "--track", 6, "--vars", json.dumps(v)], capture_output=True)
    for i, o in enumerate(J.get("overlays", []), 1):
        sh(mount + [o["component"], f"ov{i}-{o['component']}", "--start", round(H + float(o["at"]), 3), "--dur", round(span(o), 3), "--track", 7, "--vars", json.dumps(o.get("vars", {}))], capture_output=True)
    logo = J.get("logo", D.get("logo", {}))
    if logo is not False:
        sh(mount + ["logo-badge", "badge", "--start", H, "--dur", M, "--track", 8, "--vars", json.dumps(logo if isinstance(logo, dict) else {})], capture_output=True)
    if photo:
        sh(mount + ["outro-real-showroom", "outro", "--start", H + M, "--dur", O, "--track", 9,
                    "--vars", json.dumps({"src": f"../assets/showroom/{photo.name}", "focus": outro.get("focus", D.get("outro_focus", "50% 50%"))})], capture_output=True)

    r = subprocess.run([tool("npx"), "hyperframes", "check"], cwd=hf, capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if any(k in l for k in ("✗", "Check", "text checks"))))
    print(f"length: hook {H}s + main {M}s + outro {O}s = {T}s")
    if not render:
        print(f"next: npx hyperframes snapshot \"{hf}\" --at {H+0.4:.1f},{H+M/2:.1f}  →  build.py job.json --render")
        return

    raw = hf / "renders" / f"{jid}-raw.mp4"
    sh([tool("npx"), "hyperframes", "render", ".", "-o", raw, "-q", "delivery"], cwd=hf, capture_output=True)
    n = 1
    while (P / "output" / f"{jid}_{slug}_carvendors_v{n}.mp4").exists():
        n += 1
    out = P / "output" / f"{jid}_{slug}_carvendors_v{n}.mp4"
    m = subprocess.run([tool("ffmpeg"), "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    d = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
          f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,aresample=48000")
    sh([tool("ffmpeg"), "-v", "error", "-y", "-i", raw, "-c:v", "copy", "-af", ln, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
    sheet = P / "output" / f"{jid}_{slug}_v{n}_frames.jpg"
    tiles = []
    for i, t in enumerate([0.3, H + 0.3, H + M * 0.33, H + M * 0.66, H + M - 0.3, T - 0.5]):
        f = P / "work/qa" / f"final_{i}.jpg"
        subprocess.run([tool("ffmpeg"), "-v", "error", "-y", "-ss", f"{max(t, 0):.2f}", "-i", str(out), "-frames:v", "1", "-vf", "scale=-2:640", str(f)])
        tiles.append(f)
    subprocess.run([tool("ffmpeg"), "-v", "error", "-y"] + sum([["-i", str(t)] for t in tiles], []) + ["-filter_complex", f"hstack={len(tiles)}", str(sheet)])
    print(f"OUTPUT {out}\nFRAMES {sheet}")

    # ---------- shared export + ledger (Drive) ----------
    exp = paths.get("exports")
    if exp:
        exp.mkdir(parents=True, exist_ok=True)
        shutil.copy(out, exp / out.name)
        print(f"EXPORT {exp / out.name}")
    st = paths.get("studio")
    if st:
        (st / "ledger").mkdir(parents=True, exist_ok=True)
        rec = {"id": jid, "slug": slug, "folder": J.get("folder"), "date": datetime.datetime.now().isoformat(timespec="seconds"),
               "editor": platform.node(), "version": n, "hook": ({"file": hk["file"], "in": hk.get("in"), "out": hk.get("out")} if hk else None),
               "transition": tr, "outro": (outro.get("video") or outro.get("photo")) if outro else None,
               "music": music["file"] if music else None, "length": T, "output": out.name}
        (st / "ledger" / f"{jid}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"LEDGER {st / 'ledger' / (jid + '.json')}")


if __name__ == "__main__":
    main()
