---
name: CarVendors British Road
version: 1
colors:
  road-green: "#00703C"      # UK primary-route sign green: hero panels, CTA panels
  sign-white: "#FFFFFF"      # sign borders, text on green/blue
  plate-yellow: "#F7D117"    # UK rear number plate: labels, active caption word, phone number
  plate-white: "#F4F4F0"     # UK front number plate: name tags, light chips
  ink: "#111311"             # plate text, plate borders, hard shadows
  motorway-blue: "#1D4F91"   # info panels only (facts, "how it works"); never the hero
  asphalt: "#1C2023"         # graphics-only backgrounds
  kerb-grey: "#8C9399"       # secondary text on asphalt
  cv-green: "#00C831"        # CarVendors logo green: tiny accents only (ticks, logo context)
typography:
  display: { family: "Montserrat", weight: 800, use: "sign text, headlines, captions" }
  plate:   { family: "Oswald", weight: 700, transform: uppercase, tracking: "0.05em", use: "plates, labels, numbers, phone" }
  meta:    { family: "Montserrat", weight: 600, use: "sub-lines" }
  sizes_9x16: { hook: "92-110px", sign-sub: "40-46px", plate: "52-64px", caption: "60-66px", label: "26-30px" }
spacing:
  gutter: 70px
  safe-top: 150px
  safe-bottom: 1540px        # nothing important below this y on 1080x1920
  caption-band: "1230-1420px"
components:
  sign-panel: "road-green fill, radius 34px, 18px outer pad, 6px sign-white inner border at radius 22px, white text, optional white arrow glyph"
  plate-chip: "plate-yellow fill, 4px ink border, radius 12px, Oswald 700 uppercase ink text"
  front-plate: "plate-white fill, 4px ink border, radius 12px, Oswald 700 ink text (names, places)"
  info-panel: "motorway-blue fill, same border recipe as sign-panel"
  caption: "Montserrat 800 white, hard 3px ink drop + soft dark glow, active word sits in a plate-chip"
  logo-card: "CarVendors dark logo on sign-white card, radius 26px"
---

# CarVendors British Road

## Overview
A British, practical, trustworthy look built from things every UK driver already reads: green route signs,
yellow number plates, blue motorway info panels and tarmac. It says "cars, UK, we know the road" without a
single glowing tech graphic. The CarVendors green appears only inside the logo and tiny ticks.

## The Frame
- 9:16 master (1080x1920). Real footage fills the frame; graphics sit on top as signs and plates.
- Hook text lives top-centre (y 180-700) in a sign panel. Captions live in the caption band (y 1230-1420).
- Keep 0-150 px and 1540-1920 px free of key content (platform UI).
- Graphics-only scenes use asphalt with an animated dashed white lane line as the moving background layer.

## Composition Rules
- One sign panel per beat. Plates come in stacks of 1-3, left-aligned at the gutter.
- Footage first: never cover a face with a panel; move the panel, not the face.
- A fact is a blue info panel; a question or promise is a green sign; a value or number is a yellow plate.
- Logo: dark logo on a white card, top-centre on CTA frames; never on footage without its card.

## Motion
- Signs slide in like they are passing the camera: x or y 60-120 px with `power3.out`, 0.35-0.5 s.
- Plates drop and settle: y -40 → 0 with `back.out(2)`, staggered 0.08-0.12 s.
- Transitions: sign wipe (a green panel crosses the frame, 0.35 s), whip cut on a word, short white flash for proof.
  No neon glows, no lens-flare light leaks over faces.
- Ambient: lane dashes scroll, plates breathe ±2 % scale; nothing static for longer than 2 s.

## Do / Don't
- Do: real B&F footage, real customers, phone-shot honesty, "Dramatisation" label on AI scenes.
- Do: spell the dealer "B&F Cars Northampton"; phone 0330 113 1668; site carvendors.co.uk.
- Don't: glassmorphism, neon on navy, gradient text, "cheapest", "guaranteed", fake urgency, finance claims
  without the legally required APR wording, implying CarVendors owns or sells the car.
