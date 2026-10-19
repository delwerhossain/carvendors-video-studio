# CarVendors text style — the reference look (MUST follow)

Source of truth: the preview images in the Drive folder `text_refs`
(`Projects/CarVendors/video-text-img -preveiw`, `paths.py get text_refs`). Look at them once per session
before deciding overlays. Every on-screen text must look like it belongs to that set.

## Palette — only these
| Role | Colour | Use |
|---|---|---|
| Text on footage | **white `#FFFFFF`** + soft dark drop shadow | headlines, model names, line 1 of pills |
| The one accent | **brand red `#E8202A`** | keyword pills, tags ("FEATURED", "AT B&F CARS"), red cover box |
| Card | white `#FFFFFF` with **charcoal `#111311` text** | label-card, text-cover `card` |
| Tiny markers | CarVendors green `#7AC943` (logo green), tick green `#2DB84B` | the dot after "details.", tick circles |

**Forbidden (looks cheap / dull — the v002 test failure):** charcoal or black boxes, pills or badges on
footage; grey "chips" behind lines; dark logo badges; two different accent colours in one video; matching the
pill to a black/white/silver car; neon, gradients, glass, outlines, emoji. Charcoal is ONLY a text colour on a
white card. The pill is ALWAYS brand red (on a red car too — it is the brand colour, not the car colour).

## Type
Montserrat Black (900) for every headline, pill word, card title and the big model number; Montserrat
ExtraBold (800) for tags and spaced make lines; real Montserrat Black Italic only for "In the details."-style
lines. Manrope only for the tiny logo credit. Tight tracking (−0.01…−0.035em), line height ~1.0.

## The seven elements (component → how it looks in the references)
1. **Logo** — `logo-badge` style `clean`, `top-center`: real CarVendors logo (green icon + white wordmark),
   "Featured dealer: B&F Cars" under it, no box, soft shadow + feathered glow. On every shot of the main video.
2. **Hero model** — `hero-model` (`font: montserrat`): small spaced make line "ABARTH" (letter-spacing ~0.3em)
   above a huge white "595" (180-235 px) in the open sky above the car. First shot only, when the sky is free.
3. **Detail headline** — `detail-line`: "In the / details." white, heavy (italic face allowed), green dot at the
   end, top-left over a close-up. One per video at most.
4. **Label card** — `label-card`: white rounded card, charcoal Montserrat Black title ("Abarth 595"), short
   subtitle ("Small Car. Big Personality."), small red tag on the top edge (only TRUE words: "FEATURED",
   "AT B&F CARS"; never "NEW ARRIVAL" without proof). Optional ≤2 green-tick lines under it, verified only.
5. **Pill line** — `punch-text`: white line 1 + red pill keyword, group tilted −3…−5°:
   "Iconic Abarth / [Style]", "Perfect for / [City Driving]", "Sporty / [Interior]". 1-3 per video.
6. **Old-text cover** — `text-cover` style `card` (white card, charcoal Black text, red kicker tag) or `red`
   (red box, white Black text). Never `dark`. Always with a line, e.g. kicker "FEATURED" + "Spotted at B&F Cars".
7. **Outro** — real showroom photo or the team outro video; logo + "Explore more at CarVendors.co.uk".

## Placement
Text sits in open sky or on plain areas, top third (y 230-700) or upper-left; never over the grille, headlights,
badge, wheels or a face. One text element per shot (plus the logo). Hold each 1.5-3 s; enter in 250-350 ms
(rise/mask/pill wipe), exit quickly.

## Legibility without boxes
White text needs contrast without a dark box: move it to a darker area (trees, car body, shadowed wall) first;
if it must sit on white cloud or a bright windscreen, give `punch-text` `lineBg` 0.35-0.5 (a feathered shadow
glow, no edges) or use the white `label-card` instead. `hyperframes check` must pass.

## Copy
Short, confident, British, true: "Iconic Abarth / Style", "Built for / Every Day", "Step / Inside",
"Room for / Everyone" (only if visible), "Spotted at B&F Cars". No prices, specs, finance, stock status
unless verified. No questions that sound like clickbait unless the source had that tone.
