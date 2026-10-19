# CarVendors Studio — motion components (HyperFrames, 1080x1920)

Eight small, restrained pieces for the premium "human editor" CarVendors look: big white type in real
negative space, almost no boxes, no glass, no glow, no bounce. Each is a templated HyperFrames
sub-composition in `components/`, driven by declared variables, mounted once per use with `tools/mount.py`.
Full variable list, defaults and timing sit in the header comment of each file (`python3 tools/mount.py list`).

| Component | Use it for | Do NOT use it when |
|---|---|---|
| `hero-model` | First hero shot: small spaced make line + huge model number in sky/plain wall | No clean negative space above the car; the number would touch the car body |
| `detail-line` | Tight real close-up: "In the / details." + tiny green full stop | The text would cover the detail the shot is about; educational videos (use a factual line) |
| `shape-text` | One alternate-angle shot: white line + keyword on a small accent pill | More than once or twice per video; the accent would clash with the car colour |
| `localized-contrast` | Soft charcoal scrim under text on busy/bright footage, or to calm a footage blemish | Whole-frame darkening, "vignette" looks, or behind text that already reads |
| `logo-top` | Real CarVendors mark + "Featured dealer: B&F Cars", every shot before the outro | The outro (it has its own logo); a shot whose top is covered by a person/subject |
| `verified-feature` | At most two short, verified or plainly visible facts with thin ticks | Unverified claims (engine, insurance, economy, finance, price); on the same shot as another headline |
| `caption-line` | Voiceover captions, semantic chunks, 1-2 lines on a subtle charcoal backing | Karaoke/word-pop styling; when there is no voice (do not caption silent shots) |
| `outro-real-showroom` | End card on a REAL showroom photo with logo, CTA and dealer credit | No real photo available (do not fake one; use a clean authentic clip or a plain charcoal card) |

One headline system per shot: `hero-model` OR `detail-line` OR `shape-text` OR `verified-feature`.
`logo-top` and `caption-line` may run alongside.

## Install into a HyperFrames project

1. Copy `assets/fonts/` (Manrope-Regular.ttf, Manrope-Bold.ttf, Oswald.ttf + OFL-Oswald.txt) and
   `assets/brand/` (cv-icon-light.png, cv-wordmark-light.png, cv-logo-light.png) into `<project>/assets/`.
   Components load them as `../assets/...` from `compositions/`.
2. Put `<!-- CV:INSERT -->` inside the root `<div data-composition-id=...>` of `index.html`, after the footage.
3. Make hosts fill the canvas: `#root > div[data-composition-src] { position:absolute; inset:0; pointer-events:none; }`.
4. Mount each beat, then `npx hyperframes check` (lint + layout + contrast) and snapshots.

```bash
CS=~/.claude/skills/carvendors-studio
python3 $CS/tools/mount.py add <hf> hero-model hero --start 0 --dur 2.8 --vars '{"make":"ABARTH","model":"595","x":570,"y":250,"size":235}'
python3 $CS/tools/mount.py add <hf> localized-contrast hero-veil --start 0 --dur 2.8 --below hero --vars '{"x":200,"y":318,"w":740,"h":226,"opacity":0.46,"shape":"soft-rect"}'
python3 $CS/tools/mount.py add <hf> caption-line captions --start 0 --dur 30 --track 9 --words voice/s01.words.json
```

- Every use needs its own instance id (timelines bind by composition id). Re-running `add` with the same id
  replaces that instance (good for re-timing).
- **Paint order is DOM order**, not track number. A scrim must come before its text: use `--below <id>`.
- `--words` builds caption chunks from a tts.py / transcript word list (max 6 words / 30 chars per chunk).
- Fonts used: Manrope 400/700 and Oswald 700 (variable font). Never synthesise bold or italic.

## Position convention (all text components)

- `x` is the **anchor**, `align` says which edge it is: `left` = left edge at x, `center` = centre at x,
  `right` = right edge at x. `y` is always the top of the block. (logo-top: `position` top-left / top-center.)
- Alignment is done with GSAP `xPercent`, never with measured widths: a clip that starts later is
  `display:none` when its script runs, so any `offsetWidth` reads 0. (This was the cause of right/centre
  blocks landing at the wrong place in an earlier version; fixed.) Text widths that must be known (detail-line
  fit, caption line breaks) come from canvas text metrics.
- Ink edges are optically aligned: side bearings of the real glyphs are measured, and the tracked make line
  drops its trailing letter-space, so "ABARTH" and "595" line up on the left, centre or right.
- Safe text guide: x 80-870, y 230-1500. Logo may sit at y ~110-200 (check the platform top bar).

## Legibility

- First move the text to cleaner space, then use `scrim` (0-0.55, built into each text component; a feathered
  charcoal ellipse sized to the text block), then `localized-contrast` for an area or a linear fall-off.
  Never a full-frame darken, never a big panel.
- `logo-top` credit line is small text (needs 4.5:1). Default scrim 0.32; raise to 0.38-0.45 over
  overcast/white sky.
- `verified-feature` `backing:true` (charcoal 45 % per row) only on genuinely busy footage.
- Captions keep their ~55 % backing; that is what makes them readable over gravel and paint.

## Motion (defaults)

| Piece | Entrance | Exit |
|---|---|---|
| hero-model | make line 320 ms, 12 px rise; number +60 ms, 20 px rise out of a bottom-up clip mask, expo.out | 200 ms fade + 8 px lift |
| detail-line | each line 280 ms, 16 px rise in a clip mask, 70 ms stagger | 180 ms |
| shape-text | lead 280 ms, 14 px; pill +120 ms scaleX wipe 260 ms; keyword +120 ms slide 160 ms | 180 ms |
| verified-feature | rows 260 ms, 12 px, 90 ms apart; tick draws 200 ms | 180 ms |
| logo-top | 300 ms fade + 8 px settle, credit +60 ms; stays | optional 200 ms |
| caption-line | per chunk 160 ms, 6 px rise | 100 ms fade ending at chunk end |
| localized-contrast | 200 ms fade | 180 ms |
| outro-real-showroom | photo 4-6 % push over the slot; logo / CTA / credit at +0.25 / +0.50 / +0.75 s, 320 ms each | none (last card) |

Exits are tied to the host `data-duration`: the slot length is the on-screen time. Hold headlines 1.5 s+.

## Layout tips

- Find the negative space first (sky, plain wall, dark window, clean gravel). Text never crosses the bonnet,
  grille, headlights, wheels, badges or plate.
- hero-model: 210-235 px for a 3-digit number; centre it over the sky gap or align it to a building edge.
- detail-line: 84-92 px, left at 80 when the close-up leaves the left side clear.
- shape-text: tilt -3 only when the shot is static enough; default 0.
- Captions: bottom 1480, centred; a long sentence breaks into two balanced lines automatically.
- outro: pick `focus` so the photo's busiest part is above y ~1000; `shade` 0.65-0.72 under the copy.
- The B&F footage has an inpainted smudge at x 273-867, y 352-507 on every shot (the removed TikTok
  sticker). Centre the shot's headline over it and add a scrim / `localized-contrast` soft-rect to calm the
  rest; see `test/mount-test.sh`.

## Test project

`test/` — 12 s, five shots from `v001_1080.mp4` (hero, headlight, side, rear, outro). Re-mount everything with
`test/mount-test.sh`; render: `npx hyperframes render test -o test/renders/test.mp4 -q looks`.
Result: `test/renders/test.mp4`, frames in `test/renders/frames/`. `check`: 0 lint / layout / motion findings,
18/18 contrast checks pass.

## Known limits

- The smudge is softened, not removed: a darker soft band remains visible beside "595" and beside the
  headlines in the other shots. A permanent fix belongs in the footage (better inpaint) or in a crop.
- In the outro test photo, the real CarVendors sign shows above the overlay logo (two logos in frame).
  Pick a crop (`focus`) or photo without signage when one exists.
- The showroom photo is landscape (1672x941), so `cover` upscales it ~2x and it looks slightly soft.
- logo-top `top-center` centres the whole lockup box, including a credit line that is wider than the wordmark,
  so the mark itself sits ~20 px left of x.
- GSAP comes from the jsDelivr CDN (HyperFrames default); fonts and images are local.

## logo-badge (v3.3 — fixed default brand mark)
Authentic CarVendors logo on its own background (dark charcoal badge with the light logo, or a white badge with
the dark logo), optional "Featured dealer: B&F Cars" line inside. Mount once over the whole main video; the
fast lane does it automatically (`"logo": {"corner": "top-left", "style": "dark"}`). Corners: top-left,
top-right, top-center, bottom-left. Use this instead of logo-top for bulk work: it is readable on any footage.

## text-cover (v3.3 — cover old baked-in text with a designed box)
Solid rounded box (dark / white / accent) laid exactly over an old TikTok text box (source box × 1.875 + ~10 px)
for as long as that text is on screen, with an optional new line (`|` = line break) and kicker. `reveal: none`
when the old text is visible from the first frame (the fast lane sets this when `at` = 0). Cheaper and cleaner
than inpainting; use inpainting only when a box would cover the car. Variables: x, y, w, h, text, kicker,
style, accent, opacity (keep 1 so old text cannot show through), size, align, radius, reveal, delay, exit.

## punch-text (v3.3 — reference "Iconic Abarth / [Style]" look)
Heavy white line (Montserrat Black, optional real Black Italic) + one keyword on a bright rounded pill, whole
group tilted (default −4°), soft drop shadow. Vars: line1, word, x, y, align (left/center/right = anchor edge),
size, italic, tilt, pill, pillText, lineBg (charcoal backing behind line 1 for white cloud/bright walls),
shadow, delay, exit. 1-3 per video, on the key beats.

## label-card (v3.3 — reference "Abarth 595 / Small Car. Big Personality." look)
White rounded card with a Montserrat Black charcoal title, a short subtitle, an optional coloured tag on the top
edge and up to two green-tick lines under the card. Vars: title, sub, tag, tagColor, x, y, align, size, tilt,
ticks ("a|b"), delay, exit. Tags/ticks must be true. Good on the first main shot or placed over old text.
