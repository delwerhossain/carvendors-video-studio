# Changelog

## 3.3.0 — 2026-10-19
- Fast lane: `skills/carvendors-studio/tools/build.py job.json [--render]` builds a whole edit from a small JSON
  (clean master, hook played in full → one transition → FULL source video → outro, fixed logo badge, old-text
  covers, overlays, music/voice, check, render, −14 LUFS master, frame sheet). Cuts token use per video.
- Full-length policy: never cut source scenes; add one hook and one outro only.
- New components: `logo-badge` (fixed logo with background; dark / light / clean), `text-cover` (premium box over
  old TikTok text with a new line), `punch-text` and `label-card` (reference look: heavy Montserrat Black, bright
  tilted pill, white label card).
- Old-text ladder by cost: keep → cover with text-cover → inpaint (texture re-grain) → reframe/drop.
- Per-computer resource paths (`tools/paths.py detect|set|show`), saved in `~/.config/carvendors-studio/paths.json`.
- Light colour grading only when a shot needs it; voice model chosen per video.

## 3.2.0 — 2026-10-19
- carvendors-studio skill created from the team's v3.1 brief, wired to the real tools; minimal cinematic components.
