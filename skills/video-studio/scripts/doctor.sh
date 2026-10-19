#!/usr/bin/env bash
# Health check for the whole video workflow. Read-only. Prints OK / MISSING lines and never prints secrets.
export PATH="$HOME/.cache/claude-shorts/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
SK="$HOME/.claude/skills/claude-shorts"; VS="$HOME/.claude/skills/video-studio"
PY="$HOME/.cache/claude-shorts/venv/bin/python"; ENVF="$HOME/.config/video-studio/.env"
fail=0
ok()  { echo "OK       $1"; }
bad() { echo "MISSING  $1"; fail=1; }

for t in ffmpeg ffprobe whisper-cli node npx uvx git; do command -v "$t" >/dev/null && ok "$t" || bad "$t"; done
[ -d "$SK/.git" ] && ok "claude-shorts ($(git -C "$SK" log -1 --format=%h))" || bad "claude-shorts repo"
[ -x "$PY" ] && "$PY" "$SK/scripts/check_setup.py" >/dev/null 2>&1 && ok "claude-shorts check_setup" || bad "claude-shorts check_setup (run: bash $SK/setup.sh)"
grep -q CLAUDE_SHORTS_LANG "$SK/scripts/transcribe.py" 2>/dev/null && grep -q "local patch" "$SK/scripts/captions.py" \
  && ok "Bengali patch applied" || bad "Bengali patch (run: bash $VS/scripts/update_tools.sh)"
"$PY" -c "from PIL import features; assert features.check('raqm')" 2>/dev/null && ok "Bengali text shaping (raqm)" || bad "raqm (run: brew install fribidi)"
for f in HindSiliguri-Bold.ttf Galada-Regular.ttf; do [ -f "$HOME/.config/claude-shorts/fonts/$f" ] && ok "font $f" || bad "font $f"; done
m="$HOME/.cache/claude-shorts/ggml-large-v3.bin"
[ "$(stat -f %z "$m" 2>/dev/null)" = 3095033483 ] && ok "Whisper large-v3 model" || bad "Whisper large-v3 model"
[ -f "$HOME/.cache/hyperframes/whisper/models/ggml-large-v3.bin" ] && ok "model shared with HyperFrames" || bad "HyperFrames model link (ln $m ~/.cache/hyperframes/whisper/models/)"
claude plugin list 2>/dev/null | grep -A3 "hyperframes@hyperframes" | grep -q enabled && ok "HyperFrames plugin" || bad "HyperFrames plugin"
if [ -f "$ENVF" ] && grep -Eq '^ELEVENLABS_API_KEY=.+' "$ENVF" && ! grep -q '^ELEVENLABS_API_KEY=your_api_key_here' "$ENVF"; then ok "ElevenLabs key set"; else echo "NOT SET  ElevenLabs key (user adds it to $ENVF)"; fi
grep -Eq '^ELEVENLABS_VOICE_(BN|EN)?=.+' "$ENVF" 2>/dev/null && ok "ElevenLabs voice id set" || echo "NOT SET  ElevenLabs voice id (tts.py --list-voices)"
exit $fail
