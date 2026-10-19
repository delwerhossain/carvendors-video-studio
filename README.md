# CarVendors Video Studio (v4)

One Claude Code skill (`skills/carvendors-studio`) that re-edits the old @bnf_cars TikTok videos into
CarVendors.co.uk Reels / TikTok / Shorts in bulk — Mac and Windows, shared resources on Google Drive.

Each video: **attention hook (full action) → one transition → the whole original video → outro**, fixed
CarVendors logo badge, old TikTok text kept / covered / removed, premium text beats, music, −14 LUFS master.
The AI fills one small `job.json` per video; Python tools do the rest.

## Install
- **Mac:** `git clone https://github.com/delwerhossain/carvendors-video-studio.git && cd carvendors-video-studio && bash install.sh`
- **Windows (PowerShell):** `git clone …` then `powershell -ExecutionPolicy Bypass -File install.ps1`

Google Drive for desktop must be running: the skill finds "My Drive" and reads the team config at
`My Drive/Projects/CarVendors/_studio/config.json`. No paths to type.

## Update
`bash update.sh` (Mac) · `powershell -ExecutionPolicy Bypass -File update.ps1` (Windows)

## Use (Claude Code, opened in ~/Projects/videos)
"plan videos 1-20" → "render 1-20" → finished files in Drive `Projects/CarVendors/CarVendors Edited/`.
See `workspace/TEAM_GUIDE.md`. Tools (run with the skill Python, see SKILL.md):

| Tool | Does |
|---|---|
| `tools/batch.py plan / render / status` | bulk loop over folders 1-200 |
| `tools/build.py job.json [--render]` | one video: clean master, hook, full video, outro, logo, covers, text, music, check, render, export, ledger |
| `tools/hooks.py list / stats / pick / scan` | shared hook catalog and usage counts |
| `tools/paths.py show / set / drive` | where everything is on this PC |
| `tools/clean.py` | upscale + light grade + inpaint old text |
| `tools/tts.py`, `music.py`, `sfx.py` | ElevenLabs voice / music / SFX (own key) |
| `tools/doctor.py` | health check |

Never commit keys, media or per-PC config.
