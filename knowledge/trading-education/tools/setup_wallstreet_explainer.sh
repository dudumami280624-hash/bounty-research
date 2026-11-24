#!/usr/bin/env bash
set -euo pipefail
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
git clone --depth 1 https://github.com/HeyChengC/wallstreet-explainer.git "$ROOT/upstream"
cd "$ROOT/upstream"
git rev-parse HEAD
test -f LICENSE
command -v ffmpeg
npm install --no-audit --no-fund
npx playwright install chromium
node scripts/new_film.mjs "$ROOT/demo" --demo
node scripts/render.mjs --dir "$ROOT/demo" --check
# No third-party footage, publishing, or paid APIs.
