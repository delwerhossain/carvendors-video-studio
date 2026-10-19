#!/usr/bin/env bash
# Create a video project with the standard layout and print its path.
# Usage: new_project.sh <english-slug> [bn|en|both]   e.g. new_project.sh skin-cream-review-ad bn
set -euo pipefail
ROOT="${VIDEO_PROJECTS_ROOT:-$HOME/Projects/videos}"
[ $# -ge 1 ] || { echo "usage: new_project.sh <english-slug> [bn|en|both]"; exit 1; }
slug=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')
lang="${2:-bn}"
case "$lang" in bn|en|both) ;; *) echo "language must be bn, en or both"; exit 1 ;; esac
dir="$ROOT/$(date +%Y-%m-%d)-${slug:-video}"
[ -e "$dir" ] && { echo "already exists: $dir"; exit 1; }
mkdir -p "$dir"/{input,work,voice,output}

cat > "$dir/CLAUDE.md" <<EOF
# Video project: ${slug:-video}

Load the \`video-studio\` skill first and follow it for every step. Narration language: $lang.

- \`input/\` original clips, customer reviews, images, logo, music. Never modify or overwrite.
- \`work/\` scratch files (claude-shorts workdir, HyperFrames project).
- \`voice/\` voiceovers from \`tts.py\` (one file per scene).
- \`output/\` finished videos, thumbnail, title and description.
- \`brief.md\` the brief and every decision. Keep it updated.
EOF

cat > "$dir/brief.md" <<EOF
# Brief

- Goal:
- Platform and format: (Reels / Shorts / TikTok 1080x1920, Facebook feed 1080x1350, YouTube 1920x1080)
- Language: $lang
- Length:
- Audience:
- Key message and call to action:
- Assets in input/: (customer review clips, product shots, logo, music)
- Voice: (ElevenLabs voice id, tone, speed)

## Decisions
EOF

printf '.env\n.env.*\nwork/\n.DS_Store\n' > "$dir/.gitignore"
echo "$dir"
