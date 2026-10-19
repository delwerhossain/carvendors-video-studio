# Audio, voice, captions (detail)

## 8. Audio, captions, voice — credit-efficient

### 8.1 Decision tree
1. Listen to the source (Whisper transcript + level). TikTok songs are always removed (rights unknown).
2. Real presenter speech that works → keep and clean; never replace or clone a real person.
3. Ready `Voice/` voiceover → prefer it; **transcribe it and check every fact against the footage** (v001's VO
   said plate "F3 MWN" while the car reads F3 MWW — that phrase was cut from the audio rather than re-voiced).
4. No usable VO → write short, natural UK English (10–25 s) from verified/visible facts.
5. Voice generation: ElevenLabs via `tts.py`, **model chosen per video** (`--list-models`, A/B one short line
   on 2–3 candidates, log the winner in `brief.md`). Same voice for a whole batch. Cache = voice + model +
   text + settings; never re-synthesise for render iterations. No local TTS unless it clearly wins and the
   user agrees (Whisper is the only standard local model).
6. Missing key/tool → continue truthfully without VO, or ask for the one missing thing. Never fake TTS.

### 8.2 Sync and captions
Shot pacing follows the VO; each key phrase gets its matching real footage. Timings from `.words.json` (tts.py)
or Whisper. Captions: spell-checked UK English, 1–2 lines, semantic chunks (`caption-line`, `mount.py --words`).
If a caption and a big headline would overlap, keep the caption and drop the headline.

### 8.3 Music, SFX, loudness
- **Music:** library first — `All Resources/Background Music/Royalty Free Music/` (NCS, Audio Library, YT BG
  Music, Corporate…). Check each track's licence (many "no copyright" tracks still require a credit line in the
  post — add it). Instrumental under speech. ElevenLabs `music.py` only if nothing fits (`voice/music-bed-01.mp3`
  from v001 is already available and reusable).
- **SFX:** library first — `All Resources/Sound Effects/` (whoosh, cinematic whoosh, camera, punch, app click,
  riser…); `sfx.py` only for a missing sound. Max one accent per beat, matched to a visible event.
- **Mix by measurement, not fixed gains:** measure VO and bed loudness (`ffmpeg -af loudnorm=print_format=json`);
  set the bed ≈15–20 LU under the VO while speech plays, lift it in gaps and on the ending; use a
  `data-automation` volume lane; carve with `/hyperframes-audio` `carve.mjs` when available. Hook audio only if
  cleared, limited (sources can peak above 0 dBFS).
- **Master:** two-pass `loudnorm` to I −14 LUFS with a TP target of −2.0 dBTP (AAC encoding adds ~0.5 dB;
  v001 landed at −1.38 with a −1.5 target), AAC 48 kHz 192 kbps, video stream copied. Verify the final file.

