---
name: video-studio
description: >-
  The user's own video production workflow on this Mac: ads, Reels, Shorts and TikToks, customer-review
  videos, product videos, voiceovers in Bengali and English. Use for ANY video task: starting a new video
  project, editing a raw clip, cutting retakes, captions/subtitles, ElevenLabs voiceover or TTS, background
  music, motion graphics, rendering with HyperFrames or claude-shorts. Load this BEFORE the claude-shorts or
  hyperframes skills; it decides which one to use and the rules both must follow.
---

# Video studio

The user makes marketing videos (often ads with real customer reviews) in **Bengali and English**. This skill
is the single source of truth for how to make them. Talk to the user in simple Bengali, one question at a
time, and show progress (a transcript, a cut list, a preview frame) instead of describing it.

`$VS` = `~/.claude/skills/video-studio`. Run `bash $VS/scripts/doctor.sh` once at the start of a session that
will render anything; fix any MISSING line before starting.

## Tools on this Mac

| Tool | What it does here |
|---|---|
| claude-shorts skill (`~/.claude/skills/claude-shorts`) | Raw vertical talking-head clip → cut retakes and dead air, word-by-word captions, music, -14 LUFS, thumbnail, title |
| HyperFrames plugin (`/hyperframes`) | Builds video from HTML: motion graphics, product/ad videos, explainers, designed overlays, slideshows. Renders in Chrome, so Bengali text always renders correctly |
| Whisper large-v3 (`~/.cache/claude-shorts/ggml-large-v3.bin`, hard-linked into `~/.cache/hyperframes/whisper/models/`) | Local speech-to-text. Never download another copy |
| `$VS/scripts/tts.py` | The ONLY way to make ElevenLabs voiceovers (Bengali + English, cached, spend-gated) |
| `$VS/scripts/to_hf_transcript.py` | Turns claude-shorts or `tts.py` word timings into HyperFrames `transcript.json` |
| `$VS/scripts/music.py`, `$VS/scripts/sfx.py` | ElevenLabs music beds and sound effects (cached, logged). One bed is reused across a whole series |
| `$VS/scripts/clean_master.sh` (+ `sticker_fill.py`) | TikTok source → clean 1080x1920 30 fps master with baked-in text boxes inpainted out |
| `$VS/scripts/batch_scan.py` | Bulk jobs: manifest.csv + 3-frame thumbs per clip, status tracking |
| FFmpeg 9 | All local audio/video processing |

**Local models: exactly one.** Whisper large-v3 is the only local model in the standard setup (speech-to-text,
with word timings). All voice generation (text-to-speech) goes to ElevenLabs `eleven_v4` via `tts.py`. No local
model today does both STT and TTS with usable Bengali, word timings and a commercial licence, so a second local
model is not installed by default (Kokoro / Indic Parler in "Free local voiceover" below are optional extras).

## Pick the theme first

| Job | Theme | Files |
|---|---|---|
| CarVendors's own story ads (AI dramatisation, real reviews, "new to the UK" style) | **British Road** | `$VS/kit/` (frame.md, playbook.md, kit.py) |
| B&F Cars TikTok re-edit series for CarVendors socials (car showcase / info clips) | **Premium Minimal Cinematic (v3.2)** | **load the `carvendors-studio` skill** (`~/.claude/skills/carvendors-studio/SKILL.md`, components + mount.py there) |
A video never mixes the two. 2026-10-19: the B&F series moved from "Glass Editorial" to the v3.2 minimal
cinematic look in `carvendors-studio` (big white type in negative space, rare car-colour accent, no big glass
cards, human-editor finish). `$VS/glass/` remains only as a technical reference (example-v001 mechanics).

## Brand kit: CarVendors "British Road" (CarVendors story ads)

User decision 2026-10-14: CarVendors story ads use the British Road theme (2026-10-16: the B&F TikTok re-edit series uses Glass Editorial instead, see above). Before planning any video read
`$VS/kit/frame.md` (theme tokens and rules) and `$VS/kit/playbook.md` (lengths, hooks, rhythm, captions,
motion library, compliance, QA). `$VS/kit/swipe-file.md` holds the analysed UK car ads it was built from.
- New HyperFrames project: `python3 $VS/kit/scripts/kit.py install <hf>`; put `<!-- KIT:INSERT -->` inside
  the root in `index.html`, then add each graphic with
  `python3 $VS/kit/scripts/kit.py add <hf> <component> <unique-id> --start S --dur D --vars '{...}'`.
  `kit.py list` shows the components (sign-hook, plate-stack, info-panel, location-sign, name-plate,
  lane-bg, sign-wipe, end-card) and their variables. Every use needs its own id: one shared file mounted
  twice does not animate both copies (tested).
- Captions: `python3 $VS/kit/scripts/captions.py <config.json>` (docstring shows the config). Mount the
  output once as the captions track.
- A beat that no component covers: build it in the frame.md language, then add it to `kit/components/`
  with the `__ID__` / `__DUR__` placeholders and list it in playbook.md § 6.
- Working demo of every component: `$VS/kit/demo/` (`kit-demo.mp4`).
- Retired look (do not reuse): navy + neon green glass cards from the first CarVendors preview.

## Pick the tool

| The user has / wants | Use |
|---|---|
| A raw phone clip of someone talking, to tidy into a Short/Reel | claude-shorts |
| Customer review clips to keep as they are, plus captions | claude-shorts (one clip) or HyperFrames `/embedded-captions` |
| An ad built from product shots, text, reviews and a voiceover | HyperFrames (`/product-launch-video` or `/general-video`) |
| Animated title, logo sting, stat, lower-third, end card | HyperFrames `/motion-graphics` |
| Talking-head video with designed graphics on top | claude-shorts for the cut, then HyperFrames `/talking-head-recut` |
| Explainer with no face on screen | HyperFrames `/faceless-explainer` + `tts.py` |

Combine them freely: claude-shorts output (`output/*.mp4`) is a normal clip HyperFrames can place in a scene.

## Every new video starts here

1. `bash $VS/scripts/new_project.sh <english-slug> <bn|en|both>`. Projects live in `~/Projects/videos/`
   (override with `$VIDEO_PROJECTS_ROOT`). It creates `input/ work/ voice/ output/`, `brief.md` and a project
   `CLAUDE.md`. Work inside that folder.
2. Fill `brief.md` with the user, one question at a time: goal, platform/format, language, length, call to
   action, which assets they have. Skip what the files already answer (probe clips with ffprobe).
3. Copy the user's files into `input/` (never move or edit originals). Then pick the tool from the table.
4. Log every decision the user makes (chosen voice, cut list approved, title locked) under `## Decisions`.

## Bulk editing (many existing clips)

Full process: `~/Projects/videos/VIDEO_TEAM_CONTEXT.md` § 6. In short: one project, copy clips to `input/`,
`python3 $VS/scripts/batch_scan.py <project>/input <project> --batch-size 10` (manifest.csv + 3-frame thumb
per clip; re-run keeps status/notes), classify each clip (`type` + plan in `notes`), pilot one clip per type
until approved and lock the recipe in `brief.md`, then work one batch at a time (status todo → edited →
approved/redo). `--status <project>` shows progress; the manifest is the memory between sessions.

## Bengali (bn) rules

- **Transcribing with claude-shorts:** prefix every `transcribe.py` call with `CLAUDE_SHORTS_LANG=bn`.
  Without it Whisper writes Bengali speech in English letters.
- **Captions with claude-shorts:** copy `$VS/assets/bn-caption-settings.json` to `<workdir>/settings.json`
  before `captions.py` and `thumbnail.py`. It switches to Hind Siliguri (text) + Galada (script hero), which
  carry Bengali and Latin, and turns tracking off. English-only projects skip this.
- **Captions with HyperFrames:** do NOT use `hyperframes transcribe` for Bengali: it glues every Bengali
  word into one entry (tested). Transcribe with claude-shorts instead
  (`CLAUDE_SHORTS_LANG=bn "$PY" ~/.claude/skills/claude-shorts/scripts/transcribe.py <clip> work/tr`), then
  `python3 $VS/scripts/to_hf_transcript.py work/tr/transcript.json <hf-project>/transcript.json`.
  For a voiceover use its `.words.json` the same way (`--offset <s>` if it starts later in the video).
  English can use `npx hyperframes transcribe <file> --model large-v3 --language en` directly.
- Whisper's Bengali is usable, not exact (test: "প্রোডাক্টটা" came back "প্রদাক্তাটা"). Always show the
  user the clean Bengali transcript with your fixes in bold and get a yes before captions.
- For voiceovers, caption timing comes from `tts.py`'s `.words.json`, not Whisper (exact text, exact timing).
  Verified 2026-10-14 with a real `eleven_v4` Bengali call: word timings came back correct.
- The account has cloned Bengali voices (`language=bn` in `--list-voices`); Fardin-bn
  (`M6HBGx22m6z23EGuruYz`) was the user's pick for the first test.
- `$PY` = `~/.cache/claude-shorts/venv/bin/python` (use it for every claude-shorts script).

## Voiceover (ElevenLabs) rules

- Write the script per scene in `brief.md`. Generate one file per scene so changing one line re-generates one
  scene, not the whole ad.
- Always dry-run first: `python3 $VS/scripts/tts.py "<text>" -o voice/s01.wav --lang bn`. Tell the user the
  character count (≈ credits) and the voice, wait for a clear yes, then re-run with `--yes`. Each approval
  covers only the calls you listed.
- Exception (user decision 2026-10-16): for the B&F TikTok re-edit series the user pre-approved ElevenLabs
  credits (voice, music, SFX). Still dry-run to see the cost, then run with `--yes` without asking and report
  what was spent. Keep spend low: reuse source speech, cached lines and the shared music bed first.
- **Voice model is chosen per video, never fixed** (user decision 2026-10-17). Pick whichever model sounds best
  for that video's language, voice and style. At the start of each project run `tts.py --list-models` (free;
  shows which models speak bn/en today). On 2026-10-17 Bengali: `eleven_v4`, `eleven_v4_turbo`, `eleven_v3`,
  `eleven_v3_conversational`; English: those plus `eleven_multilingual_v2` (very steady long narration),
  `eleven_turbo_v2_5` / `eleven_flash_v2_5` (fast, drafts). For a new voice or style, render the same 1-2
  sentence line on 2-3 candidate models (`--model <id>`), compare (or let the user pick), use the winner and
  log model + voice + settings under `## Decisions`. Starting point when unsure: `eleven_v4`. A newer model that
  sounds better replaces the old choice; a local model is used only if it clearly wins and the user agrees.
  If a model returns no character timestamps, take caption timings from Whisper on the wav instead.
  Do not use HyperFrames' built-in ElevenLabs path: it is hard-coded to `eleven_multilingual_v2` (no Bengali).
  Feed `tts.py`'s wav into HyperFrames as audio.
- Pass `--prev`/`--next` with the neighbouring scene lines for natural flow between scenes.
- Emotion (v4): audio tags in the text, e.g. `[excited]`, `[warmly]`, `[sighs]`, `[laughs]`, `[whispers]`, plus
  ellipses for pauses and CAPS for emphasis. Tags are not spoken but count as characters. Split by speaker
  (one call per voice) and join with short gaps. Working example:
  `~/Projects/video-test/local-tts-test/elevenlabs-v4-emotional/run.sh` (dry run; `--yes` to spend).
- Kokoro emotion: direction lines `[am_michael 1.1] text` / `[pause 0.4]` (see `local_tts.py` docstring).
- Voices: `tts.py --list-voices` (free). Defaults live in `~/.config/video-studio/.env` as
  `ELEVENLABS_VOICE_BN` and `ELEVENLABS_VOICE_EN`.
- Spending history: `~/.cache/video-studio/tts/spend.log`. Same text + voice + settings is a free cache hit.
- If HyperFrames' preflight asks about HeyGen sign-in for voices, tell the user voiceovers come from ElevenLabs
  via `tts.py`; use HeyGen only if they choose it.

## Free local voiceover (ONLY when the user explicitly asks for local / free)

User decision 2026-10-14: voiceovers use ElevenLabs (`tts.py`) by default. Do not use or suggest the local
models below unless the user asks for them in that conversation.

`$LPY` = `~/.cache/video-studio/parler-venv/bin/python` (private env: PyTorch + Parler-TTS + Kokoro).
- English: `$LPY $VS/scripts/local_tts.py <text|file.txt> -o voice/s01.wav --engine kokoro --voice am_michael`
  (54 voices: `af_*`/`am_*` US, `bf_*`/`bm_*` UK). Tested: 23 s of ad copy in 7 s, Whisper read it back exactly.
- Bengali or Bengali-English mix: `$LPY $VS/scripts/local_tts.py <text|file.txt> -o voice/s01.wav`
  (Indic Parler-TTS; `--desc` sets the voice style, keep `--seed` fixed for one consistent voice).
  Needs a one-time Hugging Face login that accepted https://huggingface.co/ai4bharat/indic-parler-tts
  (`~/.cache/video-studio/parler-venv/bin/hf auth login`, done by the user). Model 3.8 GB, cached after.
- Write numbers as words in the script. Local voices have no word timings: transcribe the wav for captions.
- Hugging Face tokens: the user runs `hf auth login` themselves; never accept a token in chat or write it.

## Real customer reviews

- Never re-voice, re-word, speed up, or AI-"clean" a real customer's voice. Allowed: trimming before/after
  their words, loudness normalisation, and noise reduction only after the user hears a before/after.
- Captions for a review must match what the customer said; fix only spelling.

## Secrets

- The ElevenLabs key lives only in `~/.config/video-studio/.env` (mode 600, folder 700). The user adds it
  themselves by replacing `your_api_key_here`. `~/.claude/settings.json` denies Read/Edit on that file, so
  only `tts.py` (run via Bash) ever reads it. After the user adds it, verify with
  `python3 $VS/scripts/tts.py --list-voices` (free call).
- Never print, echo, cat or log that file or the key, never copy it into a project, never commit it.
  Check presence with `doctor.sh` only. If the key is missing, ask the user to add it; never ask them to
  paste it in chat.

## Before showing any result

- `ffprobe` the export: resolution matches the brief, duration as expected, audio present.
- Look at 2-3 frames yourself (captions readable, nothing cut off, Bengali conjuncts intact).
- Loudness -14 LUFS for social platforms.
- Final files go in `output/` with a clear name; never overwrite an earlier export.

## Maintenance

- Update both tools: `bash $VS/scripts/update_tools.sh`. It pulls claude-shorts, re-applies
  `patches/claude-shorts-local.patch` (the Bengali fixes), updates the HyperFrames plugin and runs `doctor.sh`.
  If the patch fails, re-port it (same intent) and save the new `git diff` over the patch file.
- Optional extras not installed on purpose: Kokoro (local TTS, no Bengali), MusicGen (needs PyTorch).
  Install only if the user asks.
