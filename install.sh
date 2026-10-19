#!/usr/bin/env bash
# CarVendors Video Studio — install / update on a Mac. Safe to re-run.
#   bash install.sh           full install (tools + skill + Python env + workspace + check)
#   bash install.sh --skill   only copy the skill from this repo (used by update.sh)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SKILL="$HOME/.claude/skills/carvendors-studio"
VENV="$HOME/.cache/carvendors-studio/venv"
copy_skill() {
  mkdir -p "$HOME/.claude/skills"
  rsync -a --delete --exclude '__pycache__' --exclude '.DS_Store' "$HERE/skills/carvendors-studio/" "$SKILL/"
  echo "skill installed: $(cat "$HERE/VERSION")"
}
if [ "${1:-}" = "--skill" ]; then copy_skill; exit 0; fi

echo "== 1/5 tools (Homebrew: ffmpeg, node, python, rsync)"
if ! command -v brew >/dev/null; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)" && break; done
fi
if ! command -v brew >/dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)" && break; done
fi
for p in ffmpeg node python rsync; do brew list "$p" >/dev/null 2>&1 || brew install "$p"; done
[ -d "/Applications/Google Chrome.app" ] || brew install --cask google-chrome

echo "== 2/5 skill"
copy_skill

echo "== 3/5 Python env for the skill (numpy + scipy)"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --quiet --upgrade pip numpy scipy

echo "== 4/5 keys file + workspace"
mkdir -p "$HOME/.config/video-studio"; chmod 700 "$HOME/.config/video-studio"
ENVF="$HOME/.config/video-studio/.env"
[ -f "$ENVF" ] || printf 'ELEVENLABS_API_KEY=your_api_key_here\nELEVENLABS_VOICE_EN=JBFqnCBsd6RMkjVDRZzb\n' > "$ENVF"
chmod 600 "$ENVF"
mkdir -p "$HOME/Projects/videos"
for f in AGENTS.md CLAUDE.md TEAM_GUIDE.md CARVENDORS_CONTEXT.md; do cp "$HERE/workspace/$f" "$HOME/Projects/videos/$f"; done
(cd "$HOME/Projects/videos" && npx --yes hyperframes@latest --version >/dev/null 2>&1) || true

echo "== 5/5 check"
"$VENV/bin/python" "$SKILL/tools/doctor.py" || true
cat <<'EOF'

Done. Next:
  • Google Drive for desktop must be running (the skill finds "My Drive" by itself).
    If doctor says MISSING for Drive:  ~/.cache/carvendors-studio/venv/bin/python ~/.claude/skills/carvendors-studio/tools/paths.py drive "/path/to/My Drive"
  • Only for new voiceovers: put YOUR ElevenLabs key in ~/.config/video-studio/.env
  • Open Claude Code in ~/Projects/videos and say: "plan videos 1-10" or "edit video 7".
EOF
