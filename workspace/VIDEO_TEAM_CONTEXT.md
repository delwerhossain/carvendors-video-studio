# CarVendors Video Studio: Team Context (v2)

> **Update 19 Oct 2026:** the B&F TikTok series now uses the `carvendors-studio` skill v3.3 (fast lane
> `build.py` + job.json, full-length edits, logo badge, PUNCH text style). Where this file says "Glass
> Editorial", follow `skills/carvendors-studio/SKILL.md` instead.

**Updated: 17 October 2026.** Replaces v1 (15 Oct). Voice model rule added (section 2.3). Give this file to every teammate and to the AI agent they
work with. Read it together with `CARVENDORS_CONTEXT.md` (business facts) in the same folder.

---

## 0. Quick start (new PC, about 30-45 minutes, mostly downloads)

1. Unzip `carvendors-video-setup.zip` anywhere and run `bash install-mac.sh` (Mac). Windows: section 5.3.
2. Put your **own** ElevenLabs key in `~/.config/video-studio/.env` (replace `your_api_key_here`). Never paste
   keys in chat, email or files.
3. Run `bash ~/.claude/skills/video-studio/scripts/doctor.sh`. Every line should say OK.
4. Open Claude Code (with Claude or with GLM, section 5.4) inside `~/Projects/videos/` and describe the video.
   The agent reads `CLAUDE.md` / `AGENTS.md` there, then this file, then the `video-studio` skill.

---

## 1. How the system works

The AI is the **director**: it plans, decides and runs tools. All real work (cutting, cleaning, graphics,
captions, voice, mixing, rendering) is done by local tools and small scripts on the PC. So the AI model can be
swapped (Claude, GLM, others) and the result stays the same, because the rules, brand themes and tools are
files on disk, not knowledge inside one model.

Pipeline in one line:
**source footage / AI scenes → clean master (FFmpeg) → story + timings (Whisper / ElevenLabs word times) →
HyperFrames composition (HTML + GSAP motion, glass/brand components) → render → loudness master → QA → output/**

---

## 2. The stack: what we use, and when

| Job | Tool | Local or cloud | When to use it |
|---|---|---|---|
| Director | Claude Code running Claude or GLM (section 5.4) | cloud model | Always. It must be able to run shell commands and **look at images** (QA is visual). |
| Editing, motion graphics, rendering | **HyperFrames** (HTML → video, renders in Chrome) + GSAP | local | Every final video. Gives After-Effects-style motion: mask reveals, glass cards, camera push-ins, whip pans, flashes. |
| Footage processing | **FFmpeg** | local | Upscale, re-time to 30 fps, cut, loudness master (-14 LUFS), frame grabs. |
| Talking-head clean-up | **claude-shorts** skill | local | Raw phone clip of a person talking: cut dead air/retakes, word captions. |
| TikTok text removal | `clean_master.sh` + `sticker_fill.py` | local | B&F TikTok sources: inpaint the baked-in text box, upscale 576x1024 → 1080x1920. |
| **Speech → text** | **Whisper large-v3** (whisper.cpp, 3 GB) | **local, the only local model** | Transcribing source audio, finding word timings for captions, checking what a voiceover really says. Free. |
| **Text → speech (all voices)** | **ElevenLabs via `tts.py`, best model per video** (section 2.3) | cloud, paid | Every voiceover that is used in a video (Bengali or English). Returns exact word timings, so captions need no Whisper pass. |
| Music bed | ElevenLabs Music via `music.py` | cloud, paid | One instrumental bed per series, reused across all its videos (cached). |
| Sound effects | ElevenLabs Sound Effects via `sfx.py` | cloud, paid | Whoosh, impact, tick, shutter, riser. Generated once, cached, reused. |
| AI video scenes (optional) | Google Gemini Omni `gemini-omni-1.1-flash` (or Flow with Google AI Pro, by hand) | cloud, paid | Only when real footage is missing. Needs a **paid** Gemini API tier (free tier = 0 quota). Always labelled "Dramatisation". |
| Bulk tracking | `batch_scan.py` | local | Many source clips: manifest.csv + 3-frame thumbnail per clip + status. |

### 2.1 Why only one local model

We want the lightest possible PC setup. We checked the "one model does both speech-to-text and text-to-speech"
idea (speech-in/speech-out "omni" models, and Meta SeamlessM4T). As of October 2026 (research, not a local test)
none fits: their Bengali voices are weak, they do not give per-word timings for captions, they need 15-30 GB of
RAM/VRAM, and SeamlessM4T's licence is non-commercial. So the optimised setup is:

- **1 local model: Whisper large-v3** for speech-to-text (3 GB, runs on CPU/Apple GPU, no PyTorch).
- **All text-to-speech on ElevenLabs** (better quality than any local model, and it returns word timings).

Optional extras, only if the team lead asks for free/offline voice: Kokoro (English, 0.3 GB) and Indic Parler-TTS
(Bengali, 3.8 GB + PyTorch). They are not installed by the standard setup.

### 2.2 Credits: how to keep ElevenLabs spend low

1. Reuse first: real speech in the source, voiceovers already made, the cache (same text + voice + settings =
   free), the series music bed and the SFX set.
2. Generate one file per line/scene, never a whole video at once, so one change re-generates one line.
3. Every paid script dry-runs without `--yes` and prints the cost. Spend log: `~/.cache/video-studio/tts/spend.log`.
4. Approval: normal projects need a person's yes before `--yes`. The **B&F TikTok series is pre-approved**
   (voice, music, SFX): run, then report what was spent.
5. Music/SFX calls do not move the account's character counter; check real cost on the ElevenLabs Usage page.

### 2.3 Voice model: chosen per video, never fixed
Do not lock the team to one voice model. For every video, use whichever model gives the best result for that
language, voice and style (user decision, 17 Oct 2026).
1. Start of each project: `python3 ~/.claude/skills/video-studio/scripts/tts.py --list-models` (free). It shows
   which models speak Bengali / English today; ElevenLabs adds and retires models often.
2. Candidates on 17 Oct 2026:

   | Language | Models that can do it | Notes |
   |---|---|---|
   | Bengali | `eleven_v4`, `eleven_v4_turbo`, `eleven_v3`, `eleven_v3_conversational` | v4 = most expressive (audio tags like `[warmly]`); v3 conversational = natural talk; turbo = faster |
   | English (British) | the four above + `eleven_multilingual_v2` | multilingual v2 is very steady for long calm narration |
   | English drafts | `eleven_turbo_v2_5`, `eleven_flash_v2_5` | fast and cheap; for timing tests, not for final |
3. New voice or new style: render the same 1-2 sentence line on 2-3 candidates (`--model <id>`), listen, pick
   the winner (or let the team lead pick), then write the model, voice and settings in `brief.md` under
   `## Decisions`. Keep that choice for the whole video so the voice stays consistent.
4. Unsure? Start with `eleven_v4`. A newer model that sounds better replaces the old choice.
5. A local voice model is used only if it clearly beats ElevenLabs for that video and the team lead agrees
   (the standard setup keeps Whisper as the only local model).
6. If a model returns no word timestamps, get caption timings by running Whisper on the generated wav.

---

## 3. Themes: which look for which video

| Video type | Theme | Where it lives |
|---|---|---|
| CarVendors's own story ads (AI dramatisation, real customer reviews, problem → CarVendors solution) | **British Road** | `~/.claude/skills/video-studio/kit/` (`frame.md`, `playbook.md`, components via `kit.py`) |
| **B&F Cars TikTok re-edit series** (car showcase or info clips re-posted on CarVendors's Meta/YouTube) | **Glass Editorial** | `~/.claude/skills/video-studio/glass/` (`series-brief-bnf.md`, components via `mount.py`, `example-v001/`) |

Never mix the two in one video. Retired look (do not reuse): navy + neon green glass from the first preview.

### 3.1 British Road (story ads)
UK route-sign green panels (`#00703C`) for hooks/promises, yellow number-plate chips (`#F7D117`) for values,
blue motorway panels (`#1D4F91`) for facts, tarmac backgrounds. Montserrat 800 + Oswald 700. Components:
sign-hook, plate-stack, info-panel, location-sign, name-plate, lane-bg, sign-wipe, end-card. Full rules:
`kit/frame.md` and `kit/playbook.md` (lengths, 3-second hook, proof by second 8-12, captions, CTA, compliance).

### 3.2 Glass Editorial (B&F TikTok series)
Premium UK automotive editorial. Brand hierarchy: **CarVendors.co.uk is the main brand, B&F Cars is "Featured
dealer"** (both are our group). Full brief: `glass/series-brief-bnf.md`. Key values:
- **Glass material:** white fill 4-9 %, `backdrop-filter: blur(28-30px) saturate(1.15)`, 1.5 px white border at
  ~25 %, radius 24 px (pills 44 px), no black fill, no outer shadow. Scene colour must bleed through (red car →
  reddish glass). Where white text sits over bright sky/white walls, add `brightness(0.84)` to the backdrop
  filter (keeps the colour bleed, passes contrast). Blur only inside cards, never the whole frame.
- **Type:** Manrope Bold for headlines (2-5 words, max 2 lines, mask reveal, optional green full stop
  `#7AC943`); Source Sans 3 SemiBold for cards and captions. UK English only on screen.
- **Red keyword** `#E3262F` block for one or two words ("Sporty", "free"), never a red theme.
- **Safe text area** on 1080x1920: x 72-900, y 300-1240. Logo header may sit at y 150.
- **Motion:** 200-500 ms, expo/power3 ease-out, 12-20 px rises, mask reveals; no bounce, no flashy loops.
- **Components** (`glass/components/`): glass-card, glass-checklist, headline, red-keyword, logo-header,
  caption-line. Mount: `python3 ~/.claude/skills/video-studio/glass/tools/mount.py add <hf> <component> <unique-id> --start S --dur D --vars '{...}'`
  (`mount.py list` shows variables; `--words file.json --words-offset S` builds captions).
- **Signature pieces in `example-v001/index.html`** (copy them): the dynamic glass status pill that covers the
  removed TikTok text and changes its line with the story, the featured-dealer badge (B&F logo on a white
  card), the dark end card (showroom photo in a rounded frame, logo lockup, `carvendors.co.uk` pill, B&F badge).

---

## 4. End-to-end workflows

### 4.1 Workflow A: a new story ad (British Road)
1. `bash ~/.claude/skills/video-studio/scripts/new_project.sh <slug> <bn|en|both>`.
2. Pick **one customer type and the problem CarVendors solves for them**; every ad is a new concept (new to
   the UK, first car, busy parent, tight budget, nervous about dealers, too many listings...). List concepts
   already used in `~/Projects/videos/*/brief.md` and choose a different angle.
3. Story → scene table in `brief.md` (time, visual, narration). Get approval.
4. Visuals: real B&F footage and real customers first; AI scenes only where needed, short, "Dramatisation".
5. Voice: `tts.py` per scene (dry-run → approval → `--yes`), word timings from its `.words.json`.
6. HyperFrames with British Road components + `kit/scripts/captions.py`; render; QA; deliver to `output/`.

### 4.2 Workflow B: one B&F TikTok re-edit (Glass Editorial). This is the recipe used for video 1.
Source folder: `My Drive/@bnf_cars-All Tiktok Video/<n>/` with `video.mp4` (576x1024, baked-in TikTok text,
TikTok song), `comments.txt`, sometimes `Voice/` with a ready voiceover.
1. **Project:** `new_project.sh bnf-tiktok-v<nnn>-<car> en`; copy source, voice, hook clips, logos, showroom
   photos into `input/`.
2. **Look at it:** frame sheet (8-10 frames) + local Whisper on the audio. Decide type: showcase / info /
   presenter. Note baked-in text, prices, "new arrival" claims (never trusted, never repeated).
3. **Clean master:** find the text box on a source frame (x y w h in source pixels), then
   `clean_master.sh input/source/v.mp4 work/footage/v_1080.mp4 X Y W H` (≈ 25 s for a 30 s clip).
   A soft smudge may remain: plan a glass pill/card over it (box + 8 px each side, in 1080x1920 terms).
4. **Shots:** detect cuts (`select='gt(scene,0.25)'`), list clean ranges (skip the source's own fades).
5. **Voice:** use the ready voiceover if it exists. Transcribe it with Whisper and check every fact against
   the footage (video 1: the voice said plate "F3 MWN", the real plate is F3 MWW, so that phrase was cut out of
   the audio instead of re-voicing). New lines: write a short UK English script (10-20 s), `tts.py` per line.
6. **Structure (≈ 30-35 s):** hook clip 1-1.5 s (impact on the cut) → product beats re-cut to the voice, one
   shot per idea, 1.3-3 s each → proof/dealer beat → whip pan → end card 6-9 s → hold 2 s.
7. **Build:** copy `glass/example-v001/` as the starting composition, swap media, retime from the word
   timings, change text. Ken Burns drift on every shot, 0.4 s settle punch on cuts, zoom-blur landing after the
   hook, camera punch + light flash on the "match"/proof word.
8. **Audio:** drop the TikTok song. Voice at 1.0; series music bed under it (~0.16 before the bed's full
   section, ~0.07 after, rise to ~0.24 after the last word so its button ending closes the video); hook clip
   sound ~0.5; SFX at most one per second (impact on hook cut, tick on checklist, whoosh on cards/whip,
   shutter on the proof word).
9. **Check + render:** `npx hyperframes lint` → `npx hyperframes check` (must pass) → snapshots at key times →
   `npx hyperframes render . -o renders/<name>-raw.mp4 -q delivery` (33 s took about 1 min on an M3 Pro).
10. **Master:** two-pass `loudnorm` to I -14 LUFS, TP -1.5 dBTP, video stream copied; AAC 192k 48 kHz.
11. **QA (section 7)** on frames pulled from the final mp4, then deliver `output/v<nnn>_<car>_carvendors_v1.mp4`
    and a frame sheet; log decisions in `brief.md`.

### 4.3 Workflow C: bulk (≈ 196 TikToks)
1. One project per batch; copy sources into `input/`.
2. `batch_scan.py <project>/input <project> --batch-size 10` → `work/batch/manifest.csv` + thumbs.
3. Classify each clip (`type` + one-line plan in `notes`): showcase / info / presenter / already-edited / skip.
4. Pilot one clip per type with Workflow B until approved; lock the recipe in `brief.md`.
5. Batches of 10 (20 if limits allow): build → check → render → QA → status `edited`; reviewer marks
   `approved` / `redo`. `batch_scan.py --status <project>` shows progress. One fresh AI session per batch.
6. Never start the next batch while `redo` items are open. Never overwrite an export (`_v2`, `_v3`...).

---

## 5. Setting up a new PC

### 5.1 What gets installed (`install-mac.sh` does all of it, safe to re-run)
| Item | Why | Size |
|---|---|---|
| Homebrew: ffmpeg, node, git, python, cairo, fribidi, whisper-cpp, yt-dlp; Google Chrome | tools + HyperFrames rendering | ~1.5 GB |
| `~/.claude/skills/video-studio/` | rulebook, scripts, British Road kit, Glass Editorial kit | 21 MB |
| `~/.claude/skills/claude-shorts/` (+ our Bengali patch) + its Python venv (pillow, cairosvg, yt-dlp, numpy, scipy) | talking-head editor, Whisper wrapper, text removal | ~200 MB |
| **Whisper large-v3** `~/.cache/claude-shorts/ggml-large-v3.bin` (hard-linked for HyperFrames) | the one local model | 3 GB |
| HyperFrames (Claude Code plugin + `npx hyperframes` CLI + its skills) | editing/rendering | ~300 MB |
| Bengali caption fonts (Hind Siliguri, Galada) in `~/.config/claude-shorts/fonts/` | Bengali captions | 0.5 MB |
| `~/.config/video-studio/.env` (ElevenLabs) and `google.env` (Gemini) templates, private (600) | keys, added by the person | — |
| `~/Projects/videos/` with `CLAUDE.md`, `AGENTS.md`, this file, `CARVENDORS_CONTEXT.md` | workspace | — |

Hardware: Apple Silicon Mac with 16 GB RAM is comfortable; 8 GB works but transcribe one clip at a time.

### 5.2 Keys and safety
- ElevenLabs: each person uses their own key in `~/.config/video-studio/.env` (`ELEVENLABS_API_KEY=`).
  Check it with `python3 ~/.claude/skills/video-studio/scripts/tts.py --list-voices` (free).
- Gemini (only if AI scenes are needed): `GEMINI_API_KEY=` in `~/.config/video-studio/google.env`; the Google
  project needs billing enabled, otherwise video models return "limit 0".
- Add to `~/.claude/settings.json` → `permissions.deny`: `"Read(~/.config/video-studio/.env)"`,
  `"Edit(~/.config/video-studio/.env)"`, `"Read(~/.config/video-studio/google.env)"` so no agent can read keys.
- Never print, copy or commit key files. A key that was pasted into a chat should be rotated.

### 5.3 Windows (not tested by us)
Install with winget: `winget install Gyan.FFmpeg OpenJS.NodeJS Git.Git Python.Python.3.12 Google.Chrome`.
Copy the bundle's `video-studio` folder to `%USERPROFILE%\.claude\skills\video-studio`, clone claude-shorts to
`%USERPROFILE%\.claude\skills\claude-shorts` and run its `setup.ps1` (installs Whisper and the model), then
`git apply` our patch from `video-studio\patches\`, and `pip install numpy scipy` into its venv. Our `.sh`
helpers need Git Bash. HyperFrames: `npx hyperframes skills update general-video`. WSL2 + the Mac script is
the more predictable route if anything fails.

### 5.4 Which AI agent
- **Claude Code + Claude** (reference setup): skills load automatically.
- **Claude Code + GLM:** keep Claude Code as the tool and point it at Z.ai's Anthropic-compatible endpoint
  (`ANTHROPIC_BASE_URL` + the GLM key as `ANTHROPIC_AUTH_TOKEN`; check Z.ai's current docs for the exact URL and
  model names). Everything in this file works the same. Use a GLM model with vision for QA.
- **Other agents (Codex, opencode, Cursor...):** they read `~/Projects/videos/AGENTS.md`, which points to this
  file and to `SKILL.md`, `kit/*.md`, `glass/README.md` and `glass/series-brief-bnf.md` as plain files.

---

## 6. Hard rules

- Truth: no price, mileage, spec, finance, insurance, stock, condition or "sold" claim without a verified
  source. Old TikTok text ("Only £5,450", "New arrival") is never repeated. Check voiceovers against footage.
- CarVendors finds and connects; B&F Cars Northampton (same group) sells. Never imply CarVendors sells the car.
  Spell "B&F Cars Northampton" (spoken "B and F"), phone 0330 113 1668, site carvendors.co.uk.
- Real customers: never re-voice, re-word, speed up or AI-clean them; captions match their words.
- AI or acted people carry "Dramatisation" and are never presented as real customers.
- No "cheapest", "guaranteed", "best in UK", fake urgency, finance without full APR wording.
- Music: never ship TikTok trending songs (copyright claims on Meta/YouTube). Use our ElevenLabs beds.
- Third-party clips (e.g. pattern-interrupt hooks) only when we own them or have the rights.
- Secrets: section 5.2.

## 7. QA before anyone sees a video
- [ ] `npx hyperframes check` passes; contrast findings fixed (move/size first, glass brightness second).
- [ ] Frames pulled from the **rendered mp4** (not just snapshots): text readable at phone size, nothing in
      the right rail/bottom UI, no card over a face or the car's key detail, old TikTok text fully covered.
- [ ] Whisper on the final audio: every word present, in the right place.
- [ ] ffprobe: 1080x1920, 30 fps, expected length, AAC 48 kHz; loudness about -14 LUFS, true peak ≤ -1 dBTP.
- [ ] CTA on screen ≥ 2 s; brand hierarchy CarVendors > Featured dealer B&F.

## 8. Things we learned the hard way
- A glass card's **parent** must not animate opacity/filter/mask/clip-path, or the blur disappears.
- Real `backdrop-filter` blur **does** survive HyperFrames renders (verified on the rendered mp4).
- Every component use needs its own id; one file mounted twice animates only once.
- `<video data-start>` must not sit inside another element that has `data-start`; time one of them.
- zsh traps in shell commands: write `${VAR}` not `$VAR[...]` or `$VAR:l...` (zsh treats them as modifiers).
- Source TikTok fades: cut inside the clean ranges, not on the fade frames.
- Background agents can stop on a network drop; what they wrote to disk stays, resume them instead of
  restarting. Paid scripts are cached, so a retry does not pay twice.

## 9. How long things take (M3 Pro)
| Step | Time |
|---|---|
| First video of a new series (design + components) | ~1 hour |
| Each next video in the same series, from the template | ~15-25 min |
| Clean master (30 s source) | ~25 s |
| Render 33 s 1080x1920 delivery | ~1 min 10 s |
| New PC setup | ~30-45 min (downloads) |

## 10. Command cheat sheet
```
bash    ~/.claude/skills/video-studio/scripts/doctor.sh                               # health check
bash    ~/.claude/skills/video-studio/scripts/new_project.sh <slug> en                # new job folder
bash    ~/.claude/skills/video-studio/scripts/clean_master.sh <in> <out> X Y W H      # remove TikTok text + upscale
python3 ~/.claude/skills/video-studio/scripts/batch_scan.py <in> <proj>               # bulk manifest + thumbs
python3 ~/.claude/skills/video-studio/scripts/tts.py --list-models                       # which voice models speak bn/en (free)
python3 ~/.claude/skills/video-studio/scripts/tts.py "<text>" -o voice/s01.wav --lang en --model <id>   # voice (dry run)
python3 ~/.claude/skills/video-studio/scripts/music.py "<prompt>" -o voice/bed.mp3 --seconds 45
python3 ~/.claude/skills/video-studio/scripts/sfx.py   "<prompt>" -o voice/sfx/x.mp3 --seconds 0.6
python3 ~/.claude/skills/video-studio/glass/tools/mount.py list                       # glass components
python3 ~/.claude/skills/video-studio/kit/scripts/kit.py list                         # British Road components
npx hyperframes lint | check | snapshot . --at 1,5,10 | render . -o renders/x.mp4 -q delivery
```
