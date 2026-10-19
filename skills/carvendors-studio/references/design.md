# Design system, old text, brand and claims (detail)

Read when choosing overlays, colours, positions or how to treat old TikTok text.

## 5. Design system (follows the v3.1 brief)

### 5.1 Composition
- **Car first:** no text over bonnet, grille, headlights, wheels, badges, key details or a speaker's face.
- Find real negative space (sky, plain wall, floor, soft interior) per shot; position per shot, not fixed XY.
- Some shots carry only the car + tiny logo. **One headline system per shot** (`hero-model` OR `shape-text`
  OR `detail-line` OR `verified-feature`). No dense infographics or tall lists on a moving car.

### 5.2 Modes
- **A — Minimal cinematic hero (default first shot):** `logo-top` + `hero-model` (small spaced make line +
  very large model, 140–235 px, fitted to the sky/wall above the car).
- **B — Detail / shape-text:** `detail-line` ("In the / details." + tiny green dot) on a tight real close-up,
  or one `shape-text` line ("Iconic Abarth" + [Style]); small, rare accent pill, optional −3…−4° tilt.
- **C — White intro card:** rescue layout only for cluttered footage; never by default.

### 5.3 Colour
White text; charcoal `#111311` for scrims/backings; authentic logo green (`#7AC943`) only as tiny markers;
accent derived from the actual paint, muted, ≤10–15 % of graphic area. White/silver/black cars → neutral or
tiny green accent. Natural grade; preserve paint; no oversaturation. A red car ≠ red everything.

### 5.4 Typography
Oswald 700 for big numbers/display; Manrope 400/700 for everything else (or Manrope 700 + Source Sans for a
softer car — still two families max). Starting sizes at 1080×1920: hero 140–235 px, title 64–92, heading
46–68, caption 42–56, label 28–36. Line height 0.95–1.12 display, 1.15–1.30 reading. UK English only.

### 5.5 Legibility on moving footage
Test each text region across its whole duration (brightest and busiest frames). Clean sky/wall → plain white.
Busy → `localized-contrast` (charcoal → transparent, 30–55 %, confined to the text). Very busy → small dark
backing on the text only. Never blur the whole frame or the car. Targets: 4.5:1 small text, 3:1 large
(`npx hyperframes check` must pass; fix by position/size/scrim first). Max two short verified tick lines.
If it still fails: move, shorten, delay, change shot, or show nothing.

### 5.6 Safe zones (1080 × 1920 guide)
Text x 80–870, y 230–1500; keep key text out of the bottom ~320 px and the right action rail. Logo upper-left
or upper-centre. Captions above the bottom UI. Safe zone never justifies covering the car.

### 5.7 Motion
Entrances 200–350 ms (opacity + 8–20 px slide or mask rise), exits 120–250 ms, ease-out. Hold key words ≥1–1.5 s.
One animation focus at a time. Glass only on tiny labels (no big glass cards). Graphics leave with their shot.

### 5.8 Old TikTok text — decide per text, cheapest good option first

Old B&F videos carry burned-in text. Treat each text box once for the whole video:
1. **Keep it** when it is harmless, readable and on-brand (e.g. a plain model name "Abarth 595"). Zero cost.
2. **Must go** when it shows prices/finance, mentions TikTok, names another business, is off-brand or rude,
   makes an unverified claim, or clashes with the new design.
3. **Cover with `text-cover` (default for must-go static text):** a premium solid box (dark / white / accent,
   radius ~22) exactly over the old text box (source box × 1.875 + ~10 px) for as long as it is on screen,
   carrying the new line (or empty). `reveal: none` when the old text is visible from the first frame. Cheap,
   reliable, no smears. Rewrite the line in brand voice (e.g. "Any Asian dad…?" → "Dad's next car?").
4. **Inpaint** (`clean.boxes` → `tools/clean.py` (fast lane: `remove[]`), re-grains texture) only when a box would cover the car's key
   detail or the design needs a clean frame (e.g. a hero shot with big type). Zoom-check the result.
5. **Reframe or drop** a moment only if nothing else works.
Text that moves or changes every few seconds (busy text): prefer one cover box sized to the union of its
positions, or inpaint; do not animate one box per caption change.

### 5.8.1 Brand mark and text backgrounds
- **`logo-badge` is the fixed default** brand mark for bulk edits: the authentic logo on its own background
  (dark or white badge) in one corner for the whole main video — always readable, no per-shot work. Choose the
  corner once per batch (top-left unless the source has text there). `logo-top` (no background) is for
  hand-made hero edits only.
- **Text on a background is allowed and often better** (text-cover, verified-feature backing, a small label):
  use it where footage is busy or for a premium label look; keep big hero type (`hero-model`) background-free
  in real negative space. Mix both within a video as the shots demand, never one style everywhere.

### 5.8.2 Two type presets (pick one per video, keep it for the batch where it fits)
- **PUNCH (reference look, default for B&F showcase re-posts):** Montserrat Black / Black Italic / ExtraBold
  (real files in `assets/fonts`) + Manrope for small text. Components: `punch-text` (heavy white line + one
  keyword on a bright pill, group tilted −3…−5°, soft drop shadow), `label-card` (white card, charcoal Black
  title, short subtitle, small coloured tag on the edge, ≤2 ticks), `text-cover` with text, `logo-badge`.
  References: "Iconic Abarth / [Style]", "Perfect for / [City Driving]", "Sporty / [Interior]",
  "Abarth 595 / Small Car. Big Personality." Pill colour: ALWAYS brand red `#E8202A` (see text-style.md; charcoal pills were rejected by the user). Use the real italic face for "In the details."
- **CINEMATIC:** Oswald 700 + Manrope (`hero-model`, `detail-line`, `shape-text`) for calm, premium hero shots.
Legibility rules for PUNCH: on blue sky the white line needs nothing; on white cloud, bright walls or
windscreens give line 1 a charcoal backing (`lineBg` 0.45-0.6) — `check` must pass. `logo-badge` style `clean` top-centre is the default (reference look).
Tags and ticks state only true things ("AT B&F CARS", "FEATURED"); never "NEW ARRIVAL", "SOLD", engine or
economy facts unless verified. **Never leave an empty `text-cover`** — an empty dark box looks crude: always
give it a line (and optional kicker), or inpaint instead.

### 5.9 Human-editor finish (must not look AI-made)
- **Cut on purpose:** cut on music beats and on spoken words (J/L cuts: sound leads the picture by 2–6 frames
  where natural); vary shot lengths (1.2–3.5 s), let one beauty shot breathe 2–3 s with no text.
- **Restraint:** most shots have one small element or none; no element on every shot; no repeating the same
  entrance on every line; no emoji, no stock phrases ("Unleash", "Elevate", "Ultimate"), no "Wait for it…" clichés.
- **Motion that belongs to the footage:** gentle drift that follows the camera's own movement direction; no
  constant zoom-pulse; speed ramps only on a real action moment, at most once.
- **Real sound design:** library SFX (camera, whoosh, punch, click) at low level, matched to an on-screen event;
  room tone under silence; never a whoosh on every cut.
- **Picture:** keep the source's real colour; mild sharpening only (no halos); match all shots' brightness;
  a very light grain (≈2–3 %) can unify upscaled footage; no glow, no light leaks, no AI-style gloss.
- **Voice:** natural British delivery with real pauses; write how a person speaks (short sentences, contractions);
  no hype tone. Captions are plain, readable chunks — no karaoke colour boxes, no bouncing words.
- **Typography craft:** optical alignment to the car/horizon lines, consistent margins, real kerning, no text
  touching edges; two families only; nothing centred by habit.

### 5.10 Colour grading — light, only when it helps
Grade only shots that need it; otherwise leave the footage as shot. Check each shot's frames (and
`ffmpeg -vf signalstats` YAVG/SATAVG): flat, hazy, dull or underexposed shots get a **light** correction;
shots that already look good get none. Correction recipe (start small, compare before/after side by side):
`eq=contrast=1.03-1.06:saturation=1.04-1.08:gamma=0.97-1.0` (plus a touch of `colorbalance` only to remove a
colour cast). Apply via ``job.json` "grade" (fast lane) or `$PY $CS/tools/clean.py in.mp4 out.mp4 --grade "..."`` (before upscale) or per shot in the
composition. Rules: keep the real paint colour and skin tones; match all shots in a video to each other; no
looks/LUT styles, teal-orange, crushed blacks, glow or oversaturation — a viewer should not notice a grade,
only that the video looks clean. Note the grade (or "none") in `brief.md`.

## 6. Story and overlays per shot (Type A example — skip what the footage lacks)

| Scene | Range | Visual | Overlay |
|---|---|---|---|
| External hook (optional) | ~0–3 s | relevant action | none → one transition |
| Hero | ~2–4 s | best front 3/4 | `logo-top` + `hero-model` in negative space |
| Close-up | ~2–3 s | wheel / badge / trim | `detail-line` “In the / details.” |
| Alternate angle | ~2–3 s | side / rear | one `shape-text` (“Made to / stand out”) |
| Interior | ~2–3 s | real interior | small line or nothing |
| Feature (optional) | ~2–3 s | relevant footage | `verified-feature`, ≤2 verified/visible lines |
| Outro / CTA | ≥2 s | real showroom photo/clip | `outro-real-showroom` |

Type B: real question hook → one point per beat with exact captions → takeaway → short CTA. Density rule: a
shot with a big model display gets nothing else except the tiny logo.

## 7. Brand, dealer credit and claims
- CarVendors.co.uk is the main mark; “Featured dealer: B&F Cars” small and readable. B&F is a featured dealer,
  not the only partner. CarVendors helps people discover/connect; it does not sell the car itself.
- Phone `0330 113 1668` only if confirmed as the current CTA; otherwise `CarVendors.co.uk`.
- `SOURCED & SOLD` only with a documented sale; `AVAILABLE NOW` only with confirmed availability; else no
  stock label. "Free UK-wide car finding" needs a current brief; otherwise "Explore more at CarVendors.co.uk" /
  "Find your next car".
- Do not transcribe or enhance plates unless the job needs it and the text is verified from the footage.
- End cards use **real** showroom photos/clips only. `Showroom Pic/` contains some styled or possibly AI-made
  images (e.g. "Golden Hour…", "Modern UK Car Dealership Showcase"); use files from `orginal img ` or ones the
  user confirms as real. Crop out outdated prices/signage.

