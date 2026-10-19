#!/usr/bin/env bash
# Get the latest version of the skill (keeps your keys, Drive paths and job folders untouched).
set -euo pipefail
cd "$(dirname "$0")"
git pull --ff-only
bash install.sh --skill
