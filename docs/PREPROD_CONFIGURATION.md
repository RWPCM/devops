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

The `workout_frontend` `beta` EAS profile sets `EXPO_PUBLIC_BETA_GATE_KEY`,
which `apiClient.ts` and `hyperviewFetch.tsx` attach to every request
automatically. CLI smoke tests must pass `-H "X-Beta-Key: ..."` manually
(see `PREPROD_SMOKE_TESTS.md`).

**Source of truth & rotation:** the value lives in `BETA_GATE_KEY` in
`.env.preprod` (repo root, gitignored). To rotate:

1. Generate a new value and update `BETA_GATE_KEY` in `.env.preprod`.
2. Copy it into `devops/ngrok-preprod-policy.yml` (the `X-Beta-Key` check).
3. Copy it into `workout_frontend/eas.json` (`beta.env.EXPO_PUBLIC_BETA_GATE_KEY`).
4. Reload the ngrok agent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.hapteo.ngrok.preprod.plist
   launchctl load   ~/Library/LaunchAgents/com.hapteo.ngrok.preprod.plist
   ```
5. Publish the new value to existing beta installs:
   ```bash
   cd workout_frontend && eas update --channel beta --message "Rotate beta gate key"
   ```

### 5. Release + launchd agents

Build (after any code change):

```bash
source .env.local && source .env.preprod
cd workout_backend
MIX_ENV=preprod mix assets.deploy
MIX_ENV=preprod mix release
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
eas update --channel beta --message "..."
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
