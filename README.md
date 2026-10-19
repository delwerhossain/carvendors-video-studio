# CarVendors Video Studio

Claude Code skills and tools the CarVendors / B&F team uses to re-edit the B&F Cars TikTok videos (and make new
ads) for CarVendors.co.uk's Reels, TikTok and YouTube Shorts — premium, human-looking, fast in bulk.

| Folder | What |
|---|---|
| `skills/carvendors-studio/` | The CarVendors edit skill (v3.3): rules (`SKILL.md`), components, `tools/build.py` (fast lane), `tools/paths.py`, `tools/mount.py` |
| `skills/video-studio/` | General video tools: `clean_master.sh` (remove old text + upscale), `tts.py` (ElevenLabs, per-video model), `music.py`, `sfx.py`, `batch_scan.py`, `doctor.sh`, British Road kit |
| `workspace/` | `AGENTS.md`, `CLAUDE.md`, team context and business context copied to `~/Projects/videos/` |
| `examples/job-v002.json` | A complete fast-lane job |

## Install (Mac, once)
```bash
git clone <this repo> ~/carvendors-video-studio && cd ~/carvendors-video-studio && bash install.sh
```
Then: put **your own** ElevenLabs key in `~/.config/video-studio/.env`, and fix any `MISSING` resource path
(hooks, music, SFX, fonts, logo, showroom photos, the TikTok video folder) once:
```bash
python3 ~/.claude/skills/carvendors-studio/tools/paths.py set car_sources "/path/to/@bnf_cars-All Tiktok Video"
```
Paths are saved per computer; you never give them again.

## Update
```bash
cd ~/carvendors-video-studio && bash update.sh
```

## Use
Open Claude Code (Claude or GLM) in `~/Projects/videos` and ask, e.g. *"edit video 7"*. The agent writes a
`job.json` and runs `build.py`. Each video: hook (full action) → one transition → the whole original video →
outro, fixed logo badge, old TikTok text kept / covered / removed as needed, premium text on key beats.

## Rules that matter
No invented facts (prices, "new arrival", sold status, specs) · real footage and real showroom photos only ·
CarVendors is the main brand, B&F Cars is "Featured dealer" · never commit keys, media or `paths.json`.
