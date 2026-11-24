#!/usr/bin/env bash
set -euo pipefail
root="${1:?provide external checkout directory}"
if [[ ! -d "$root/.git" ]]; then git clone --depth 1 https://github.com/HeyChengC/wallstreet-explainer.git "$root"; fi
cd "$root"
git rev-parse HEAD
command -v ffmpeg
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install
npx playwright install chromium
film=$(mktemp -d)/demo
node scripts/new_film.mjs "$film" --demo
node scripts/render.mjs --dir "$film" --check
