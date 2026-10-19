# CarVendors Video Studio — team guide (v4)

**Goal now:** re-edit the ~200 old @bnf_cars TikTok videos (Drive: `Projects/CarVendors/@bnf_cars-All Tiktok Video/1…200`)
into CarVendors videos for our other accounts. Each video = **attention hook (full action) → one transition →
the whole original video → outro**, CarVendors logo badge, old TikTok text kept / covered / removed, 1-3 premium
text beats, music, −14 LUFS. Cheap and fast: the AI only fills a small `job.json` per video.

## Daily use (Claude Code in `~/Projects/videos`)
- "plan videos 21-40" → job folders + contact sheets + draft job.json for each.
- The AI looks at each contact sheet and fills the job (model name, old text, 1-3 text beats) → "ready".
- "render 21-40" → finished videos land in Drive `Projects/CarVendors/CarVendors Edited/`.
- "hook stats" → how often each hook was used and in which videos (shared for the whole team).
- Split the work by number ranges (e.g. Rahim 1-50, Karim 51-100) so two people never edit the same video.

## Shared on Drive (same on every PC)
- `Projects/CarVendors/_studio/config.json` — team defaults: logo, music list, outro, transition, grade.
- `Projects/CarVendors/_studio/hooks/catalog.json` — all hooks measured once. After adding hooks: `hooks.py scan`.
- `Projects/CarVendors/_studio/ledger/` — one file per finished video (hook, outro, music, who, when).
- `Video Editing Component/All Resources/Outro/` — drop the team outro video here, then set
  `defaults.outro_video` in config.json. Until then the outro is the real showroom photo.

## Install / update
Mac: `bash install.sh` · Windows: `powershell -ExecutionPolicy Bypass -File install.ps1`
Update: `bash update.sh` / `update.ps1`. Google Drive for desktop must be running.

## Rules
No invented facts (price, "new arrival", sold, specs) · real footage and real showroom photos only ·
CarVendors main brand, "Featured dealer: B&F Cars" secondary · own ElevenLabs key, never shared ·
check music licence (NCS: add the credit line in the post) · prefer hooks we have rights to.
