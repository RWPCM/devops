#!/usr/bin/env bash
# Rebuilds and restarts the preprod workout_backend release.
#
# Automates the manual steps in devops/docs/PREPROD_CONFIGURATION.md
# section 5 ("Release + launchd agents"): source secrets, build assets,
# build the release, then reload the launchd agent so it picks up the
# new release binary.
#
# NOTE: this does NOT manage launchd-only secrets (values in the plist's
# EnvironmentVariables, e.g. MCP_ADMIN_TOKEN, GRADIUM_API_KEY,
# GRADIUM_TTS_VOICE_FR/EN). Those are read at process boot, not baked
# into the release, so rotating them means editing the plist directly
# (see PREPROD_CONFIGURATION.md) — this script only restarts the agent,
# which is enough to pick up an already-edited plist too.
#
# Usage: devops/scripts/deploy_preprod.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist"

if [[ ! -f "$ROOT_DIR/.env.local" || ! -f "$ROOT_DIR/.env.preprod" ]]; then
  echo "error: .env.local / .env.preprod not found in $ROOT_DIR" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$ROOT_DIR/.env.local"
# shellcheck source=/dev/null
source "$ROOT_DIR/.env.preprod"

cd "$ROOT_DIR/workout_backend"

echo "==> Building preprod assets..."
MIX_ENV=preprod mix assets.deploy

echo "==> Building preprod release..."
MIX_ENV=preprod mix release --overwrite

echo "==> Reloading launchd agent..."
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "==> Waiting for boot..."
sleep 3
echo "==> Last 20 log lines:"
tail -n 20 log/preprod.log log/preprod.err.log 2>/dev/null || true

echo "==> Done. Verify with: devops/docs/PREPROD_SMOKE_TESTS.md"
