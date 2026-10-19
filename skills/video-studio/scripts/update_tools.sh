#!/usr/bin/env bash
# Update claude-shorts and HyperFrames, then re-apply the local Bengali patch and run the health check.
set -uo pipefail
SK="$HOME/.claude/skills/claude-shorts"; VS="$HOME/.claude/skills/video-studio"
PATCH="$VS/patches/claude-shorts-local.patch"

echo "== claude-shorts"
git -C "$SK" checkout -- . && git -C "$SK" pull --ff-only
if git -C "$SK" apply --check "$PATCH" 2>/dev/null; then
  git -C "$SK" apply "$PATCH" && echo "Bengali patch re-applied"
else
  echo "PATCH FAILED: upstream changed transcribe.py or captions.py. Re-port $PATCH by hand (same intent: CLAUDE_SHORTS_LANG + whole-word drawing for non-ASCII), then save the new diff over it."
fi
"$HOME/.cache/claude-shorts/venv/bin/python" -m pip install --quiet --upgrade yt-dlp

echo "== HyperFrames"
claude plugin marketplace update hyperframes 2>&1 | tail -1
claude plugin update hyperframes@hyperframes 2>&1 | tail -1

echo "== health check"
bash "$VS/scripts/doctor.sh"
