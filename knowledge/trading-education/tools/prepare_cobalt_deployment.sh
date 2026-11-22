#!/usr/bin/env bash
# Deploy the upstream cobalt Docker Compose example to an operator-controlled host.
# This script does not open a public port or download media.
set -euo pipefail
: "${COBALT_API_URL:?Set COBALT_API_URL to your actual instance URL (e.g. https://media.example.org/)}"
case "$COBALT_API_URL" in https://*|http://localhost:*|http://127.0.0.1:*) ;; *) echo "Use HTTPS for remote deployment" >&2; exit 2;; esac
command -v docker >/dev/null || { echo "Docker missing" >&2; exit 2; }
docker compose version >/dev/null || { echo "Docker Compose plugin missing" >&2; exit 2; }
command -v git >/dev/null || { echo "Git missing" >&2; exit 2; }
dest="${COBALT_DEPLOY_DIR:-./cobalt-instance}"
mkdir -p "$dest"
if [ ! -d "$dest/upstream/.git" ]; then
  git clone --depth 1 https://github.com/imputnet/cobalt.git "$dest/upstream"
else
  git -C "$dest/upstream" pull --ff-only
fi
sample="$dest/upstream/docs/examples/docker-compose.example.yml"
[ -f "$sample" ] || { echo "Upstream compose example missing: $sample" >&2; exit 3; }
# Do not rewrite upstream settings or guess env var names: operator must configure
# API_URL and protection/reverse proxy per upstream instructions before startup.
cp -n "$sample" "$dest/docker-compose.yml" || true
echo "Official compose template copied to $dest/docker-compose.yml"
echo "Set your instance URL to $COBALT_API_URL in the compose configuration."
echo "Review exposed ports, authentication, proxy, and secrets before running:"
echo "  cd '$dest' && docker compose config && docker compose up -d"
