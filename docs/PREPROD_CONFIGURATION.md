# Pre-production environment (MacBook)

Pre-production runs the `workout_backend` Phoenix release directly on this
MacBook, exposed over HTTPS via a reserved ngrok domain, for EAS internal
distribution beta testing (`workout_frontend` `beta` build profile / `beta`
update channel).

- Backend: `https://workoutcoach.ngrok.app` → `localhost:4001`
- Database: `workout_backend_preprod` (same local Postgres instance/port as dev, 5435)
- Both the backend release and the ngrok tunnel run as launchd agents
  (auto-start on login, auto-restart on crash).

---

## Components

### 1. Runtime config — `workout_backend/config/preprod.exs`

- Separate DB `workout_backend_preprod`
- `force_ssl: [rewrite_on: [:x_forwarded_proto]]` (ngrok terminates TLS, forwards plain HTTP)
- `SECRET_KEY_BASE`, `PHX_HOST`, `NGROK_URL` read from env vars at **compile time**
  (baked into the release when `mix release` is run — see below)
- AI/LLM provider config: defaults to Ollama unless `LLM_PROVIDER` env var is set

### 2. Secrets — `.env.local` + `.env.preprod` (repo root, gitignored)

`.env.local` holds shared secrets (API keys, `SECRET_KEY_BASE`).
`.env.preprod` holds preprod-specific overrides, sourced *after* `.env.local`:

```bash
export PORT="4001"
export PHX_HOST="workoutcoach.ngrok.app"
export NGROK_URL="https://workoutcoach.ngrok.app"
```

`PORT` is the only one read at **runtime** (via `config/runtime.exs`). Everything
else is baked into the release at build time.

### 3. Database

```bash
source .env.local && source .env.preprod
cd workout_backend
MIX_ENV=preprod mix ecto.create
MIX_ENV=preprod mix ecto.migrate
```

### 4. HTTPS ingress — reserved ngrok domain

Domain `workoutcoach.ngrok.app` reserved on the ngrok dashboard
(https://dashboard.ngrok.com/domains), free plan (account already authenticated
via `~/Library/Application Support/ngrok/ngrok.yml`).

#### Beta gate (HAP-170)

The tunnel is publicly reachable, so it's gated with an ngrok Traffic Policy
(`devops/ngrok-preprod-policy.yml`, gitignored — contains the shared secret).
Every request must include the header:

```
X-Beta-Key: <secret, see devops/ngrok-preprod-policy.yml>
```

Requests without it get a `401` at the ngrok edge. A separate header (not
`Authorization`) is used deliberately, since `Authorization: Bearer <token>`
is already used by the mobile app's own login.

The `workout_frontend` `beta` EAS profile selects the **preview** environment, which must define `EXPO_PUBLIC_BETA_GATE_KEY`,
which `apiClient.ts` and `hyperviewFetch.tsx` attach to every request
automatically. CLI smoke tests must pass `-H "X-Beta-Key: ..."` manually
(see `PREPROD_SMOKE_TESTS.md`).

**Source of truth & rotation:** the value lives in `BETA_GATE_KEY` in
`.env.preprod` (repo root, gitignored). To rotate:

1. Generate a new value and update `BETA_GATE_KEY` in `.env.preprod`.
2. From the workspace root, run `python3 devops/scripts/render_ngrok_policy.py --env-file .env.preprod`. This atomically generates the ignored policy with mode `0600`; missing or invalid keys leave the existing policy untouched.
3. Set `EXPO_PUBLIC_BETA_GATE_KEY` to the same value in the Expo project’s **preview** EAS environment (use sensitive visibility). The `beta` build profile selects this environment. For local Metro, set it in the ignored `workout_frontend/.env.local` and restart Metro. Never put the value in `eas.json`.
4. Reload the ngrok agent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.hapteo.ngrok.preprod.plist
   launchctl load   ~/Library/LaunchAgents/com.hapteo.ngrok.preprod.plist
   ```
5. Publish the new value to existing beta installs:
   ```bash
   cd workout_frontend && eas update --channel beta --message "Rotate beta gate key" --environment preview
   ```

#### MCP admin token (HAP-174)

`/mcp/admin` (data-access tools: `find_user`, `list_sessions`,
`get_session_details`, `get_feedback_summary`, etc.) requires
`Authorization: Bearer <MCP_ADMIN_TOKEN>`. If `MCP_ADMIN_TOKEN` is unset, the
endpoint is **open** (with a warning logged) — so it must always be set in
preprod.

`MCP_ADMIN_TOKEN` is read via `System.get_env` at **request time**, so it's
set directly in `~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist`
(`EnvironmentVariables`), not via `.env.preprod` (which only applies to
manually-sourced shell sessions, not the launchd-managed release).

To rotate: generate a new value (`openssl rand -hex 24`), update the token in
the plist's `EnvironmentVariables`, then:

```bash
launchctl unload ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
launchctl load   ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
```

#### Gradium TTS (HAP-270)

`GRADIUM_API_KEY`, `GRADIUM_TTS_VOICE_FR`, and `GRADIUM_TTS_VOICE_EN` (same
API key as `gradium_stt`/STT) are read via `System.get_env` in
`config/runtime.exs` at **boot time**, not baked into the release at build
time — so, like `MCP_ADMIN_TOKEN`, they must be set directly in the plist's
`EnvironmentVariables`, not via `.env.preprod`. If unset, cue/coach-chat TTS
silently fails per-request (logged as a warning; the client falls back to
device speech) rather than breaking the release.

To rotate or add a voice: update the plist's `EnvironmentVariables`, then
reload the agent as above (or run `devops/scripts/deploy_preprod.sh`, which
reloads it as its last step regardless of whether the release itself
changed).

### 5. Release + launchd agents

Build and restart (after any code change):

```bash
devops/scripts/deploy_preprod.sh
```

This automates: sourcing `.env.local`/`.env.preprod`, `mix assets.deploy`,
`mix release --overwrite`, and reloading the `workoutbackend.preprod`
launchd agent so it picks up the new release binary. It does not manage
plist-only secrets (see "MCP admin token" / "Gradium TTS" above) — edit
those in the plist directly, then the script's reload step (or a manual
`launchctl unload`/`load`) picks them up.

Equivalent manual steps, if you need to run a piece in isolation:

```bash
source .env.local && source .env.preprod
cd workout_backend
MIX_ENV=preprod mix assets.deploy
MIX_ENV=preprod mix release --overwrite
launchctl unload ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
launchctl load   ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
```

Two launchd agents (in `~/Library/LaunchAgents/`, not committed — created manually,
see plist contents below):

- **`com.hapteo.workoutbackend.preprod.plist`**
  Runs `workout_backend/_build/preprod/rel/workout_backend/bin/workout_backend start`,
  `RunAtLoad` + `KeepAlive`, only `PORT=4001` passed at runtime.
  Logs: `workout_backend/log/preprod.log`, `preprod.err.log`.

- **`com.hapteo.ngrok.preprod.plist`**
  Runs `ngrok http --url=https://workoutcoach.ngrok.app 4001`,
  `RunAtLoad` + `KeepAlive`.
  Logs: `workout_backend/log/ngrok.log`, `ngrok.err.log`.

### 6. EAS beta build profile — `workout_frontend/eas.json`

```json
"beta": {
  "distribution": "internal",
  "channel": "beta",
  "env": {
    "EXPO_PUBLIC_NGROK_URL": "https://workoutcoach.ngrok.app"
  }
}
```

```bash
eas build --platform android --profile beta
eas build --platform ios --profile beta
eas update --channel beta --message "..." --environment preview
```

### 7. Seed data

```bash
source .env.local && source .env.preprod
cd workout_backend
MIX_ENV=preprod mix run priv/repo/seeds.exs
# Admin login for /admin pages (not part of the base seeds):
MIX_ENV=preprod mix run -e "WorkoutBackend.Seeds.Prescribers.seed!()"
```

- Test users: `*@beta.test` (PIN login, see `priv/repo/seeds/02_users.exs`)
- Admin: `admin@example.com` / `Admin1234!`

Note: when running ad-hoc `mix` commands that boot the app (`mix run`,
`mix phx.server`), the launchd-managed release must be stopped first to free
port 4001:

```bash
launchctl unload ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
# ... do the work ...
launchctl load ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
```

---

## Operations

```bash
# Status
launchctl list | grep -E "workoutbackend|ngrok"

# Stop / start
launchctl unload ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
launchctl load   ~/Library/LaunchAgents/com.hapteo.workoutbackend.preprod.plist
launchctl unload ~/Library/LaunchAgents/com.hapteo.ngrok.preprod.plist
launchctl load   ~/Library/LaunchAgents/com.hapteo.ngrok.preprod.plist

# Logs
tail -f workout_backend/log/preprod.log
tail -f workout_backend/log/ngrok.log

# Health check
curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:4001/
curl -sS -o /dev/null -w "%{http_code}\n" https://workoutcoach.ngrok.app/
```

## Troubleshooting

- **`port 4001 already in use`**: another process (manual `mix phx.server`,
  leftover release, or the launchd agent itself) is bound to 4001. Find it
  with `lsof -nP -iTCP:4001 -sTCP:LISTEN` and stop it.
- **`ERR_NGROK_334` (endpoint already online)**: a duplicate ngrok process is
  running for `workoutcoach.ngrok.app`. Find it with
  `pgrep -fl "ngrok http --url"` and kill the stray one.
- **Tunnel up but 502/connection refused**: the backend release isn't running —
  check `launchctl list | grep workoutbackend` and `workout_backend/log/preprod.err.log`.

### Beta gate security limits

The beta key is distributed in client JavaScript and is only a coarse traffic gate.
Per-user authentication and the separate MCP admin token remain required. Sensitive
EAS visibility prevents accidental console display; it does not hide a public Expo
variable from app recipients. Never reuse this key for admin access.

The old policy and EAS value remain in Git history. Removing the current copies does
not revoke them. Coordinate rotation, the tunnel restart, and the beta app update:
old app builds lose access once the tunnel accepts only the new key. The generator
never reloads ngrok or modifies EAS variables. EAS updates must select the preview
environment explicitly (`--environment preview`) to use the matching key.

Generate a replacement with `openssl rand -hex 32`, save it only in the ignored env
file and EAS environment, then follow the rotation steps above. Do not paste it into
chat, commits, or command-line arguments. After restarting the tunnel, verify that
missing, incorrect, duplicate, and old keys are rejected and the new key succeeds.
