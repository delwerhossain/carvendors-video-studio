#!/usr/bin/env bash
# CarVendors Video Studio: setup / update for a Mac (Apple Silicon or Intel). Safe to re-run.
# Usage: bash install.sh            full setup (tools + skills + workspace + paths)
#        bash install.sh --skills  only refresh the two skills from this repo (used by update.sh)
# Installs: Homebrew tools, Chrome, the video-studio skill (themes + scripts), claude-shorts (+ Bengali patch),
# Whisper large-v3 (the ONLY local model, 3 GB), HyperFrames, Bengali fonts, private key templates, workspace.
# Voices come from ElevenLabs (cloud); no local TTS model is installed.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
if [ "${1:-}" = "--skills" ]; then
  mkdir -p "$HOME/.claude/skills"
  for s in video-studio carvendors-studio; do rsync -a --exclude '__pycache__' --exclude '.DS_Store' "$HERE/skills/$s/" "$HOME/.claude/skills/$s/"; done
  chmod +x "$HOME"/.claude/skills/video-studio/scripts/*.sh
  echo "skills updated to $(cat "$HERE/VERSION")"; exit 0
fi
SKILLS="$HOME/.claude/skills"; VS="$SKILLS/video-studio"; SK="$SKILLS/claude-shorts"
step() { printf '\n== %s\n' "$1"; }

step "1/8 Homebrew + system tools"
if ! command -v brew >/dev/null; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)" && break; done
fi
if ! command -v brew >/dev/null; then
  echo "Installing Homebrew (macOS may ask for your password)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)" && break; done
fi
for pkg in ffmpeg node git python cairo fribidi whisper-cpp yt-dlp rsync; do
  brew list "$pkg" >/dev/null 2>&1 || brew install "$pkg"
done
[ -d "/Applications/Google Chrome.app" ] || brew install --cask google-chrome

step "2/8 skills: video-studio (tools) + carvendors-studio (CarVendors edits)"
mkdir -p "$SKILLS"
for s in video-studio carvendors-studio; do rsync -a --exclude '__pycache__' --exclude '.DS_Store' "$HERE/skills/$s/" "$SKILLS/$s/"; done
chmod +x "$VS"/scripts/*.sh

step "3/8 claude-shorts + Whisper large-v3 (3 GB download on first run)"
if [ ! -d "$SK/.git" ]; then git clone https://github.com/Ansub/claude-shorts "$SK"; fi
bash "$SK/setup.sh"
PATCH="$VS/patches/claude-shorts-local.patch"
if git -C "$SK" apply --check "$PATCH" 2>/dev/null; then
  git -C "$SK" apply "$PATCH" && echo "Bengali patch applied"
elif grep -q CLAUDE_SHORTS_LANG "$SK/scripts/transcribe.py"; then
  echo "Bengali patch already applied"
else
  echo "WARNING: Bengali patch did not apply (upstream changed). Ask the agent to re-port it (see SKILL.md, Maintenance)."
fi
"$HOME/.cache/claude-shorts/venv/bin/python" -m pip install --quiet numpy scipy

step "4/8 Bengali caption fonts + shared Whisper model"
mkdir -p "$HOME/.config/claude-shorts/fonts"
cp -n "$HERE/fonts/"* "$HOME/.config/claude-shorts/fonts/" 2>/dev/null || true
mkdir -p "$HOME/.cache/hyperframes/whisper/models"
M="$HOME/.cache/claude-shorts/ggml-large-v3.bin"
[ -e "$HOME/.cache/hyperframes/whisper/models/ggml-large-v3.bin" ] || ln "$M" "$HOME/.cache/hyperframes/whisper/models/ggml-large-v3.bin"

step "5/8 HyperFrames (renderer + skills)"
if command -v claude >/dev/null; then
  claude plugin marketplace add heygen-com/hyperframes >/dev/null 2>&1 || true
  claude plugin install hyperframes@hyperframes >/dev/null 2>&1 || true
  claude plugin list 2>/dev/null | grep -q "hyperframes@hyperframes" && echo "HyperFrames plugin installed" \
    || echo "Install the HyperFrames plugin inside Claude Code: /plugin marketplace add heygen-com/hyperframes"
else
  echo "Claude Code not found: install it from https://claude.com/claude-code, then re-run this script."
fi
(cd "$HOME" && npx --yes hyperframes@latest skills update general-video) || echo "WARNING: hyperframes skills update failed; re-run later."

step "6/8 private key files (you add the keys yourself)"
mkdir -p "$HOME/.config/video-studio"; chmod 700 "$HOME/.config/video-studio"
ENVF="$HOME/.config/video-studio/.env"
if [ ! -f "$ENVF" ]; then
  printf 'ELEVENLABS_API_KEY=your_api_key_here\nELEVENLABS_VOICE_EN=JBFqnCBsd6RMkjVDRZzb\nELEVENLABS_VOICE_BN=\n' > "$ENVF"
fi
GENV="$HOME/.config/video-studio/google.env"
[ -f "$GENV" ] || printf 'GEMINI_API_KEY=\n' > "$GENV"
chmod 600 "$ENVF" "$GENV"

step "7/8 workspace ~/Projects/videos"
mkdir -p "$HOME/Projects/videos"
for f in CLAUDE.md AGENTS.md VIDEO_TEAM_CONTEXT.md CARVENDORS_CONTEXT.md; do
  cp "$HERE/workspace/$f" "$HOME/Projects/videos/$f"
done

step "8/8 health check + this computer's resource paths"
bash "$VS/scripts/doctor.sh" || true
python3 "$SKILLS/carvendors-studio/tools/paths.py" detect || true
cat <<'EOF'

Next:
  1. Open ~/.config/video-studio/.env in a text editor and replace your_api_key_here with YOUR ElevenLabs key.
     Then check it:  python3 ~/.claude/skills/video-studio/scripts/tts.py --list-voices
  2. In ~/.claude/settings.json add to permissions.deny:
       "Read(~/.config/video-studio/.env)", "Edit(~/.config/video-studio/.env)", "Read(~/.config/video-studio/google.env)"
  3. Any MISSING path above: python3 ~/.claude/skills/carvendors-studio/tools/paths.py set <key> "<folder>"
  4. Open Claude Code in ~/Projects/videos and say e.g. "edit video 5" (it uses the carvendors-studio skill).
EOF
