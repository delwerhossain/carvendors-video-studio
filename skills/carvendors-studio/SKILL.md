---
name: carvendors-studio
description: >-
  CarVendors Video Studio v4 — the team's one skill for CarVendors.co.uk videos (B&F Cars Northampton as
  featured dealer). Main job: re-edit the ~200 old @bnf_cars TikTok videos (Google Drive, folders 1-200) into
  polished, rebranded CarVendors Reels / TikTok / YouTube Shorts in bulk, cheaply: attention hook (played in
  full) → one transition → the whole original video → outro, fixed logo badge, old text kept/covered/removed,
  premium text on key beats, music, loudness, QA, shared hook-usage ledger. Works on Mac and Windows. Use for
  any CarVendors / B&F video request: "edit video 7", "plan 1-20", "render the ready ones", "which hooks were
  used", new ads, voiceovers, captions. Do not use this brand for other clients.
---

# CarVendors Video Studio v4

Talk to the user in short, simple Bangla. Everything in the videos is UK English.
`$CS` = this skill folder (`~/.claude/skills/carvendors-studio`, Windows `%USERPROFILE%\.claude\skills\carvendors-studio`).
`$PY` = the skill's Python: Mac `~/.cache/carvendors-studio/venv/bin/python`, Windows
`%USERPROFILE%\.cache\carvendors-studio\venv\Scripts\python.exe` (made by the install; has numpy + scipy).

## 0. Rules that never bend
1. **No invented facts.** Price, mileage, engine, year, "new arrival", "sold", finance, economy, plates only
   with evidence. Old TikTok text and comments are not evidence.
2. **Real stays real.** Real footage and real showroom photos only; no AI-made cars, people, showrooms, signs.
3. **Brand:** CarVendors.co.uk is the main brand; "Featured dealer: B&F Cars" is secondary. CarVendors helps
   people find/connect with cars; it does not sell the car. Both are our companies.
4. **Full video, balanced length:** keep the WHOLE source in order (no scene cuts). Add one hook and one outro.
   Total ≈ source + 3-7 s. Trim only black/frozen/duplicate frames.
5. **Cheap by design:** use the fast lane (`batch.py` + `build.py`). Do not hand-write composition HTML, do not
   re-analyse hooks (the shared catalog has them), look at ONE contact sheet per video. Ask only when blocked.
6. **Never** print or copy API keys (`~/.config/video-studio/.env`). Never overwrite an export (`_v2`, `_v3`…).
7. Unsure where something is or what the user means → check `$PY $CS/tools/paths.py show` and the
   CarVendors Drive folder (`paths.py get carvendors` — it holds all context: sources, logo, showroom photos,
   banners, customer reviews, text-style previews), then ask **one** short question.

## 1. Where things are (automatic, Mac + Windows)
`$PY $CS/tools/paths.py show` finds this PC's Google Drive "My Drive" and reads the team config
`My Drive/Projects/CarVendors/_studio/config.json` (paths relative to My Drive + team defaults). No setup when
Drive is running. Overrides for one PC: `paths.py set <key> <path>` / `paths.py drive <My Drive path>`.
Keys: `car_sources` (folders 1-200 with video.mp4, comments.txt, sometimes Voice/), `hooks`, `bgm`, `sfx`,
`fonts`, `logos`, `showroom_pics`, `text_refs`, `outros`, `exports` (finished videos for upload), `studio`
(shared catalog + ledger), `projects_root` (local job folders, `~/Projects/videos`).

## 2. The bulk loop (default)
```
$PY $CS/tools/batch.py plan 1-20      # job dirs ~/Projects/videos/bnf-vNNN + draft job.json + contact sheet + text boxes
  → for each video: look at work/qa/contact.jpg, edit job.json (§3), set "ready": true
$PY $CS/tools/batch.py render 1-20    # builds + renders every ready job, exports to Drive, writes the hook ledger
$PY $CS/tools/batch.py status 1-200
```
One video by hand: `$PY $CS/tools/build.py <job.json>` (check only) → optional
`npx hyperframes snapshot <job>/work/hf --at <t>` → `build.py <job.json> --render`.
Work in batches of 10-20; after each batch look at the frame sheets (`output/*_frames.jpg`) before the next.

## 3. What to decide per video (the only AI work)
From the contact sheet + `source_info` + `text_hint` in job.json:
- **slug**: short model name, e.g. `mitsubishi-asx`.
- **Text look: follow `references/text-style.md` exactly** (the preview images in `text_refs`): white
  Montserrat Black text, ONE accent = brand red `#E8202A` pills/tags, white cards with charcoal text, green only
  for tiny dots/ticks, logo clean top-centre. Never charcoal/black boxes, pills or badges on footage.
- **Old text** (each `text_hint` box, `src` = source px, `canvas` = 1080x1920 px), cheapest good option:
  keep (harmless, readable, on-brand, e.g. a plain model name) → **cover** with `covers[]` (`text-cover`, style
  `card` = white card + red kicker tag, on `canvas` coords, ALWAYS with a line, e.g. kicker "FEATURED" +
  "Spotted at B&F Cars") when it shows prices, "TikTok", other businesses, rude or unverified claims →
  **remove** (`remove[]` = `src` box, inpaint) only if a cover would hide the car. Never an empty cover.
- **Overlays** (0-3, key beats only, never over the car's face/badge/wheels): `label-card` on the first shot ·
  `punch-text` ("Iconic Abarth / [Style]", "Perfect for / [City Driving]", "Sporty / [Interior]") on detail or
  interior shots · `hero-model` (big "ABARTH / 595") when the sky is empty · `detail-line` "In the / details."
  on a close-up. Pill = brand red always. On white cloud / bright windscreens: move the text or `lineBg`
  0.35-0.5 (soft glow, no box). Times are seconds from the start of the main video.
- **hook**: leave `"auto"` (least-used, not used in the last N edits). `"car_hook": true` for the Car Hooks
  folder. A named hook: `{"file": "Car Hooks/Car Flip.mp4", "in": 0, "out": 3.2}` — whole action, cut only
  dead time after the payoff. `transition`: `cut` (default) · `whip` · `flash` · `zoom` — exactly one.
- **voice**: only if `ready_voiceover` exists and the user wants it; transcribe and check facts first.
Everything else (logo badge, music, outro, grade) comes from team defaults; override only for a reason.

Full field list: docstring of `tools/build.py`. Example: `examples/job-v002.json`.

## 4. Shared hooks, outro, music (same on every PC via Drive)
- `$PY $CS/tools/hooks.py list|stats|pick <id>|sheet <name>|scan` — catalog of all hooks (length, action peak,
  suggested in/out, preview strip) and usage counts from `_studio/ledger/*.json`. Run `scan` after adding hooks.
- **Outro**: put the team outro video in the `outros` folder and set `defaults.outro_video` in
  `_studio/config.json`; every new build uses it. Until then: real showroom photo outro (`defaults.outro_photo`).
- **Music**: `defaults.music` list in the config (library tracks, licence checked, credit line in the post).
  Logo: `defaults.logo` (`logo-badge`, `clean` style, top-centre — the reference look).

## 5. Before saying a video is done
`build.py` reports `hyperframes check` — it must say "Check passed" (fix contrast by position or `lineBg`).
Look at the frame sheet: old text gone or covered, no text on the car, logo readable, hook → main cut clean.
Report in Bangla: output path(s), hook used, what was covered/removed, any blocker. Give UK-English post copy
when asked (include the music credit line for NCS tracks).

## 6. Read more only when needed
- `references/text-style.md` — THE text look (palette, type, the seven elements, placement). Read before overlays.
- `references/components.md` — every component's variables (label-card, punch-text, text-cover, logo-badge,
  hero-model, detail-line, shape-text, verified-feature, caption-line, localized-contrast, outro-real-showroom).
- `references/design.md` — full design system, colour, type presets (PUNCH / CINEMATIC), old-text ladder,
  human-editor finish, colour grading, brand/claims.
- `references/audio.md` — voice (ElevenLabs `tools/tts.py`, model chosen per video, pre-approved for this work),
  music/SFX, loudness. `references/quality.md` — quality gates and history.
- New ads from scratch (story + AI scenes + voice): plan with the user first; same rules, `build.py` for assembly.
