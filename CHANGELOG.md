# Changelog

## 4.1.0 — 2026-10-20
- **Text look locked to the team's reference images** (`references/text-style.md`, Drive `video-text-img -preveiw`):
  white Montserrat Black text, ONE accent = brand red `#E8202A` (pills, tags), white cards with charcoal text,
  green only for tiny dots/ticks. Charcoal/black boxes, pills and badges on footage are now forbidden.
- `logo-badge` default: clean (no background), top-centre, tight feathered glow.
- `text-cover` default style `card` (white card + red kicker tag, straight so old text never peeks out); `red` option.
- `hero-model` default font Montserrat Black (the reference "595"); Oswald still available.
- `punch-text` `lineBg` is now a soft glow without edges instead of a dark chip.
- Old-text hints are wider (TikTok emoji after the text are not white). Slightly more vivid default grade.

## 4.0.0 — 2026-10-20
- **One skill**: everything the team needs is in `skills/carvendors-studio` (the separate video-studio skill and
  claude-shorts are no longer installed for the team).
- **Mac + Windows**: all tools in Python (`clean.py` replaces `clean_master.sh`); `install.ps1` / `update.ps1`.
- **Zero-setup paths**: finds Google Drive "My Drive" and reads the shared team config
  `Projects/CarVendors/_studio/config.json` (relative paths + defaults for logo, music, outro, transition, grade).
- **Shared hook library**: `hooks.py` — catalog of all 55 hooks measured once (length, action peak, in/out,
  preview strip) + usage ledger on Drive (`_studio/ledger/<id>.json`); auto-pick of the least-used hook with a
  cool-down; `stats` shows how often and where each hook was used.
- **Bulk loop**: `batch.py plan|render|status` — draft job.json, contact sheet and auto-detected old-text boxes
  per video; renders every ready job; exports to Drive `CarVendors Edited/`.
- **Team outro slot**: drop the outro video in `All Resources/Outro/` and set `defaults.outro_video`.
- Shorter SKILL.md (details moved to `references/`) → fewer tokens per session.

## 3.3.0 — 2026-10-19
Fast lane `build.py`, full-length policy, logo-badge, text-cover, punch-text, label-card, per-PC paths.

## 3.2.0 — 2026-10-19
carvendors-studio created from the team's v3.1 brief.
