# Quality gates and delivery (detail)

## 10. Quality gates
| Check | Pass |
|---|---|
| Authenticity | Real footage/photos only, or disclosed |
| Claims | Price, model/year, engine, stock, plate, promos verified or omitted |
| Old TikTok text | Not readable anywhere; no visible smear at phone size (zoom crops checked) |
| Brand | Authentic CarVendors mark; correct featured-dealer wording |
| Hook → hero | One clear transition onto the strongest real angle |
| Typography | One headline system per shot; ≤2 families; sharp glyphs |
| Contrast | Readable over the whole overlay duration; `check` passes |
| Coverage | No text on headlights, bonnet, wheels, steering wheel, badges or faces |
| Human finish | §5.9 holds: varied rhythm, restraint, no AI tells |
| Safe zones | Right rail/bottom clear; CTA ≥2 s |
| Audio | Speech clear on a phone speaker, no clipping, rights checked, −14 LUFS / ≤ −1.5 dBTP |
| Export | 1080×1920, H.264, synced AAC, no corrupt frames, correct duration |

Frame QA minimum: first frame, first frame after the hook, middle of every scene, brightest text frame,
fastest-motion frame, final CTA frame — all from the rendered MP4, viewed at phone scale.

## 11. Delivery (in Bangla to the user)
1. Final MP4 path(s). 2. Contact sheet from the actual render. 3. One-line summary: hook, transition, overlay
system, evidence for claims, how the old TikTok text was handled. 4. Audio: original / ready VO / ElevenLabs
(model + new paid calls) / library track + its credit line. 5. Post copy (UK English) for TikTok, Instagram,
Facebook, YouTube Shorts with hashtags. 6. Blockers stated exactly; never claim unfinished work.

CTA copy (only if true): `Discover more at CarVendors.co.uk.` · `Find your next car with CarVendors.` ·
`Featured dealer: B&F Cars, Northampton.`


## 13. Compatibility and history
- v3.3 (2026-10-19): full-length policy, hook played in full + one transition, fixed `logo-badge`,
  `text-cover` as the default for old text, cost-ordered old-text ladder, fast lane `build.py` + job.json,
  per-computer paths (`paths.py`), texture re-grain in inpainting, light colour grading rule, PUNCH preset
  from the reference images (`punch-text`, `label-card`, Montserrat Black), `logo-badge` clean style.
- Supersedes the 2026-10-16 "Glass Editorial" look for this series: big glass cards, the persistent glass status
  pill and red keyword blocks are retired. the old glass example (video-studio skill, owner's PC only) stays as a technical reference (shot
  re-cut, drift/punch wrappers, audio lanes, end-card mechanics), not as a look to copy.
- v3.0/v3.1 behaviour kept: multi-PC paths, `video.mp4` + `comments.txt` + optional `Voice/`, real showroom
  end cards, `brief.md` decision log, HyperFrames automation. White intro card = optional rescue layout.
- Priority in conflicts: the user's specific brief and verified footage → safety, truth and asset rights →
  this design system → legacy components.
