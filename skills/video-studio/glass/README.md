# glass-lab — CarVendors x B&F motion components (HyperFrames, 1080x1920)

Six reusable pieces for the B&F TikTok re-edit look (brief: `input/reference/master-editing-context.md`, sections 3-6).
Each one is a templated HyperFrames sub-composition in `components/`, set by text variables, mounted one copy per use with `tools/mount.py`.

| Component | What it is | Main variables |
|---|---|---|
| `glass-card` | Neutral frosted glass card with one short line | `text`, `x`, `y`, `size`, `fill`, `delay`, `blurIn`, `exit` |
| `glass-checklist` | Same glass, 1-3 rows with round ticks that draw on | `items` ("A\|B\|C"), `x`, `y`, `size`, `stagger`, `delay`, `exit` |
| `headline` | Big Manrope Bold headline, per-line mask reveal | `line1`, `line2`, `size`, `x`, `y`, `italic`, `dot`, `green`, `delay`, `stagger`, `exit` |
| `red-keyword` | Keyword on a small red block, optional white lead word | `word`, `lead`, `layout` (stack/inline), `size`, `x`, `y`, `red`, `delay`, `exit` |
| `logo-header` | CarVendors icon + wordmark + "Featured dealer: B&F Cars" | `dealer`, `mode` (image/text), `x`, `y`, `scale`, `delay`, `exit` |
| `caption-line` | Voiceover caption track, active word slightly brighter/heavier | `chunks` (JSON), `x`, `bottom`, `maxW`, `size`, `align` |

The full parameter list, defaults and timing sit in the header comment of each file.
`python3 tools/mount.py list` prints every variable and its default.

## Mount a component

```bash
python3 tools/mount.py add <hf-project> <component> <instance-id> --start S --dur D [--track N] [--vars '{json}'] [--vars-file f.json]
```

- It writes `compositions/<instance-id>.html` (fills `__ID__` and `__DUR__`) and puts the host `<div>` into `index.html` before the `<!-- GLASS:INSERT -->` marker. Without the marker it prints the host line to paste.
- Every use needs its own instance id. One shared file mounted twice does not animate both copies.
- Running `add` again with the same id replaces that instance (handy for re-timing).
- Captions straight from a `tts.py` voiceover: `--words voice/s01.words.json [--words-offset 1.5]` builds the `chunks` variable (max 6 words / 30 characters, breaks at sentence ends and pauses over 0.45 s).
- Text can also be changed later in Studio: every variable is declared, so the host's `data-variable-values` is editable.

## Install into another HyperFrames project

1. Copy `assets/fonts/` (Manrope-Bold.ttf, SourceSans3-SemiBold.ttf) and `assets/brand/` (cv-icon-light.png, cv-wordmark-light.png) into `<project>/assets/`. Components load them with `../assets/...` from `compositions/`.
2. Put `<!-- GLASS:INSERT -->` inside the root `<div data-composition-id=...>` of `index.html`.
3. Make sub-composition hosts fill the canvas: `#root > div[data-composition-src] { position:absolute; inset:0; pointer-events:none; }`.
4. Run `mount.py add` for each beat, then `npx hyperframes lint` and `check`.

## Timing (defaults)

| Piece | Entrance | Exit |
|---|---|---|
| glass-card | 280 ms, 16 px rise + opacity, power3.out, backdrop blur ramps 0 → 28 px with it | 200 ms fade + 8 px lift, power2.in, ends 20 ms before the slot |
| glass-checklist | card as above; rows from +120 ms, 120 ms apart, 260 ms, 14 px rise; tick draws 300 ms from +100 ms | same as card |
| headline | each line 480 ms out of its mask (yPercent 130 → 0), expo.out, lines 90 ms apart | 220 ms fade + 10 px lift |
| red-keyword | lead word 450 ms mask rise; red block scaleX 0 → 1 from the left, 340 ms expo.out; word slides in +120 ms, 360 ms | 200 ms fade |
| logo-header | 450 ms, 12 px rise + opacity; dealer line +80 ms | none (stays for the slot) |
| caption-line | each chunk 180 ms, 8 px rise; active word 80 ms in, 140 ms out | 120 ms fade ending at the chunk end |

`delay` moves an entrance inside its slot. The exit is tied to the host's `data-duration`, so the slot length is the on-screen time.

## Layout used in the test (safe zone x 72-900, y 300-1240)

- logo-header: x 72, y 150 (above the safe line on purpose; check it against the platform top bar).
- headline / red-keyword: x 72, y 560. glass-checklist: y 600. glass-card: y 905 (under the headline).
- caption-line: left-aligned at x 72, bottom 1240.
- The source footage has a baked-in white "Abarth 595 🦂" sticker at about y 364-487, so all copy starts below it.

## Test composition

- `index.html`: 8 s, v001.mp4 full-frame (576x1024 → 1080x1920 with object-fit: cover, muted), logo whole time, headline "Match found." 0.5-3 s, glass-card 1-3 s, red-keyword "Sporty" 3-5 s, checklist 5-8 s, captions throughout. Caption timing is test data in `tools/test-captions.json`.
- Render (draft): `renders/glass-lab-test.mp4` (1080x1920, 30 fps, 8.0 s, h264).
- Frames taken from the rendered mp4: `renders/frames/render-1.2.png`, `render-4.2.png`, `render-6.4.png`.

## Backdrop blur in the rendered video: confirmed

Real `backdrop-filter: blur(28px) saturate(1.15)` survives the local render (screenshot capture, hardware GPU, HyperFrames 0.8.164). In the rendered frames, the door handle and badge under the checklist and the mirror under the glass card are blurred inside the card and sharp outside it. Red bodywork turns the glass red. It also works inside sub-compositions and with the tweened blur ramp, so no fallback was needed.

If a future renderer drops it (for example the layered-composite path used for HDR media or shader transitions), the fallback is a second copy of the same `<video>` with `filter: blur(28px) saturate(1.15)`, clipped to the card with `clip-path: inset(... round 24px)`, with the same `src`/`data-start` so the frames stay in sync. Re-test with a render plus a frame grab before trusting it.

## Known limits

- Never fade, filter, mask or clip-path a **parent** of a glass card. That parent becomes the backdrop root, and the blur disappears until the fade ends. The components animate the card element itself.
- `check` reports **2 contrast errors and 2 warnings** in the test. They are white captions over bright gravel (0.4 s, 5.8 s) and the dealer line over white cloud (4 s). The audit ignores text-shadow. On mobile the text is readable, but over very bright ground move the caption up or onto a darker area. Do not darken the glass to fix it (the brief rules that out).
- The oblique headline is a synthesised slant (no Manrope Italic file). Ship a real italic font if a true italic is needed.
- "Heavier" active caption word = 0.9 px white stroke, because only the SemiBold file is installed.
- Green full stop uses the logo's real green `#7AC943` (sampled from cv-logo-light.png), not `#3EC93A`. Change it with the `green` variable.
- GSAP loads from the jsDelivr CDN, like every HyperFrames scaffold. Fonts and images are local.
- The headline fits each line to `maxW` (it never wraps). Keep it 2-5 words, max 2 lines.

## Moved into the video-studio skill (2026-10-17)

This set now lives at `~/.claude/skills/video-studio/glass/` (mount with `python3 ~/.claude/skills/video-studio/glass/tools/mount.py add <hf> ...`).
- `series-brief-bnf.md` — the B&F TikTok series brief (look, glass material values, type, motion, audio, accuracy rules). Read it before editing any video in that series.
- `reference-look.png` — the target look.
- `example-v001/` — the approved first edit (Abarth 595): `index.html` holds the shot re-cut, Ken Burns + punch-ins, the dynamic glass status pill that covers the removed TikTok sticker, the featured-dealer badge, the dark end card with the showroom photo and logo lockup, flash frames and the audio/SFX mix. Copy it as the starting point for the next video.
- logo-header: the dealer line now sits on a small glass chip (`brightness(0.58)`) so it passes the contrast check over white cloud.
