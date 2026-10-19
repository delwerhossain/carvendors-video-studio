# CarVendors × B&F Cars Northampton — video production context

Hand-off file for any session that makes ads or social videos for CarVendors. Read it fully before planning.
Last updated 2026-10-14. Talk to the user in simple Bengali; all public ad copy is British English.

## 1. The business (what the videos must say)
- **CarVendors** (carvendors.co.uk) is a free car-finding / sourcing / connection service, not a dealer.
  The customer says their budget, needs and how they will use the car; the team searches its vendor network and
  the wider market, suggests suitable options and connects them with the vendor. The customer decides.
- **B&F Cars Northampton** (bnfcarsnorthampton.co.uk, "B & F Northampton Ltd") is the group's own established
  used-car dealer in Northampton: physical forecourt, real stock, real customers, about 600 Google reviews
  (re-check the live number before quoting it). In marketing it is the trust bridge for CarVendors.
- Spell it **B&F Cars Northampton** on screen; narration says "B and F Cars Northampton".
- Core message: *You don't need to be a car expert. Tell us what you need; we help with the search.*
  "Free" means the help is free (no consultation or sourcing fee, no obligation to buy), never a free car.
- Audience: people new to the UK, Bangladeshi / Pakistani / Indian / Nepali communities, families, budget buyers.
  Any budget (about £1,000 to £10,000+). Respectful, never discriminatory.
- Language edge: advisers speak English, Bengali, Hindi and Urdu.
- Launch area: Northampton first (then Leicester LE1-LE5, Luton LU1-LU4).
- Goal: genuine phone leads, not views. CTA: **Request a free callback** · **0330 113 1668** · carvendors.co.uk.
- Full business context: `2026-10-14-carvendors-new-to-uk-ad/input/context.md` and `context.docx`.

## 2. Non-negotiable rules
- AI or acted scenes carry a small "Dramatisation" label. Never present an AI person as a real customer.
- Real testimonials only, the customer's own words and voice (level changes only; spelling fixes in captions).
- Never imply CarVendors owns or sells the car. CarVendors finds and connects; B&F sells.
- Avoid: "cheapest", "guaranteed", "best in UK", "100% perfect", fake urgency, finance offers without full APR
  wording, misleading "free car". The old local logo file says "CHEAPEST POSSIBLE RELIABLE CARS": never use it.

## 3. Look and editing (decided: British Road theme)
- The video-studio skill holds the kit: `~/.claude/skills/video-studio/kit/`
  - `frame.md` theme tokens: route-sign green #00703C panels, plate yellow #F7D117 labels, motorway blue #1D4F91
    info panels, asphalt #1C2023 backgrounds, Montserrat 800 + Oswald 700.
  - `playbook.md` editing rules: 15 / 30 / 60 s structures, hook in 0-3 s, proof by 8-12 s, shots 1.5-3 s,
    captions 2-4 words at 0.6-0.9 s, motion library, sound, CTA, UK compliance, QA checklist.
  - `swipe-file.md` analysed live UK car ads (Motorway, carwow, cinch, Cazoo).
  - `components/` sign-hook, plate-stack, info-panel, location-sign, name-plate, lane-bg, sign-wipe, end-card.
  - `scripts/kit.py` (install / add / list) and `scripts/captions.py` (caption track); `demo/kit-demo.mp4`.
- Retired look: navy + neon green glass cards and network-node graphics from the first preview. Do not reuse.
- Default deliverable: a 30 s 9:16 ad plus a 15 s cut, 2-3 hook variants each. Then 4:5, 1:1, 16:9 versions.

## 4. Tools and how to run them
- Start: load the `video-studio` skill, then `bash ~/.claude/skills/video-studio/scripts/doctor.sh`.
- New project: `bash ~/.claude/skills/video-studio/scripts/new_project.sh <english-slug> en`, then inside it
  `npx --yes hyperframes@0.8.154 init <project>/hf --non-interactive --example=blank --skill=general-video`,
  `python3 ~/.claude/skills/video-studio/kit/scripts/kit.py install <project>/hf`, add `<!-- KIT:INSERT -->`
  inside the root div of `index.html`, then `kit.py add ...` per graphic (one unique id per use).
- Narration: `python3 ~/.claude/skills/video-studio/scripts/tts.py <text|file> -o voice/sNN.wav --lang en --voice <id>`
  (ElevenLabs `eleven_v4`, dry run first, show the character count, spend only after the user says yes,
  `--prev/--next` for flow, audio tags like `[warmly]` for emotion). Voice used so far: George
  `JBFqnCBsd6RMkjVDRZzb` (warm British storyteller). For ads a younger conversational British voice may fit
  better: list free with `tts.py --list-voices` and let the user pick.
- Music: `python3 ~/.claude/skills/video-studio/scripts/music.py "<prompt>" -o work/music/bed.mp3 --seconds N`
  (same spend gate; credit cost is measured after). Carve it under voice with
  `node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music` after grouping voice
  tracks with `data-audio-group="voiceover"`.
- Review transcripts: `~/.cache/claude-shorts/venv/bin/python ~/.claude/skills/claude-shorts/scripts/transcribe.py <clip> <workdir>`.
- Checks: `npx --yes hyperframes@0.8.154 lint`; full check needs
  `npx --yes hyperframes@0.8.154 check --timeout 120000 --at <scene midpoints>`; look at
  `npx --yes hyperframes@0.8.154 snapshot --at ... --no-end -o <dir>` contact sheets before showing anything.
- Render: `npx --yes hyperframes@0.8.154 render --fps 30 -o <out>_raw.mp4`, then master to -14 LUFS with
  `bash 2026-10-14-carvendors-new-to-uk-ad/work/master.sh <raw.mp4> <final.mp4>`.
- Local TTS models exist but the user decided: ElevenLabs by default; local only if the user asks.
- Image generation: Codex/GPT is not connected (the codex MCP config points to a Windows path). Write prompts
  for the user to run in ChatGPT, or ask them to fix the Codex config.

## 5. Assets already available
Project: `~/Projects/videos/2026-10-14-carvendors-new-to-uk-ad/`
- `input/main-video/` AI dramatisation, 6 clips × 8 s, 1080x1920 24 fps: Scene 1 leaving home (Northampton
  street), Scene 2 café browsing, Scene 3 parts 1-2 confused scrolling, Scene 4 evening notebook (he wears a grey
  jumper here), Scene 5 picks up phone and calls (says "I need some help." at about 5.8-6.7 s). Phone screens
  show nonsense AI text; keep phone close-ups under 1 s.
- `input/review/` 7 reviews. **Only `Client Review 1.mp4` (Tatiana) is usable**: she bought her first car through
  "CarVendors garage" when she had just moved to the UK. Reviews 2, 3, 5, 6 name "Syston Autos" (another garage);
  review 4 names no business. Do not use those without the user confirming.
  Upright 1080x1920 copy: `hf/assets/video/tatiana.mp4`; word timings: `work/tatiana/transcript.json`.
  Best lines: 0.0-9.5 s "Hi guys, my name is Tatiana… where I bought my first car when I just moved in the UK",
  23.3-33.1 s "they give me exactly the vehicle which I wanted… very supportive, honest and professional".
  Her audio needs +2.5 dB (segment A) / +5 dB (segment B) to match narration.
- `input/office-showrooms/` 7 real B&F forecourt photos (CarVendors signage, Tesla, Mercedes, Range Rover).
- `input/poster-ads/` 8 square CarVendors poster ads (contain text; use as style reference only).
- `input/brand/` + `~/.claude/skills/video-studio/kit/brand/`: CarVendors logo (dark, light, icon), B&F logo.
- `voice/` 11 George narration lines (eleven_v4) with word timings; `work/music/bed_v1.mp3` 90 s instrumental.
- Previous cut: `output/carvendors-new-to-uk_preview-v2.mp4` (86.5 s, old look, approved content but retired style).
- Theme samples: `theme-samples/frames/contact-sheet.jpg` (A British Road was chosen).
- Missing and most valuable: real phone footage at B&F (walkarounds, staff talking, key handover, customers).

## 6. Video ideas backlog (pick, adapt, or ask the user)
1. "New to the UK?" 30 s: question hook → overwhelm → call CarVendors → B&F → Tatiana line → CTA. (assets ready)
2. "Tell us your budget" 15 s: plate-stack of needs → "we search" → CTA. (assets ready)
3. Tatiana testimonial 20 s: her first line as the hook, name plate, one B-roll cut, CTA. (assets ready)
4. "How CarVendors works in 3 steps" 20 s: info panels Tell us → We search → You decide. (graphics only)
5. "Euro 6, ULEZ, road tax… confused?" 25 s education hook → "ask us" CTA. (graphics + AI scene 3)
6. Bengali / Hindi / Urdu versions of idea 1 or 2 for community targeting (eleven_v4 Bengali works; the account
   has cloned Bengali voices, e.g. Fardin-bn `M6HBGx22m6z23EGuruYz`).
7. Real adviser intro (needs footage): a B&F/CarVendors adviser says "Tell me your budget, I'll do the searching".
8. Forecourt walkaround (needs footage): one car, mileage, why it suits a family, "found through CarVendors".

## 7. Lessons learned (avoid repeating)
- One HyperFrames sub-composition file mounted twice does not animate both copies: give every use its own file
  and id (`kit.py add` does this). Registry blocks that use `getElementById` break when duplicated.
- Pin `hyperframes@0.8.154` in npx calls: `hyperframes@latest` briefly pointed to an unpublished version.
- The default `check` timed out on an 86 s video: pass `--timeout 120000 --at ...`.
- In this shell (zsh), `"$VAR"` holding a whole command does not split: write a bash script for multi-step builds.
- Keep caption band (y 1230-1420) and top hook zone (y 180-700) separate; never put a panel over a face.
- ElevenLabs alignment returns audio tags as words: `tts.py` now strips them from `.words.json`.
