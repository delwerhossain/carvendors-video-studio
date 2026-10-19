#!/usr/bin/env bash
# Pull the latest version and refresh the two skills (keeps your paths.json, keys and projects untouched).
set -euo pipefail
cd "$(dirname "$0")"
git pull --ff-only
bash install.sh --skills
