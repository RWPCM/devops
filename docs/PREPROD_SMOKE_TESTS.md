# Pre-production smoke tests (backend)

Backend-side checks for the MacBook-hosted pre-production environment
(`https://workoutcoach.ngrok.app` → `localhost:4001`). See
`PREPROD_CONFIGURATION.md` for setup details.

These checks cover everything that doesn't require an EAS build on a physical
device. Device-level checks (install, login UI, workout session, audio, voice
commands, OTA update) are tracked separately and must be run manually.

---

## 1. TLS certificate validity

Confirms the tunnel presents a publicly-trusted cert (no manual trust step
needed on tester devices).

```bash
echo | openssl s_client -connect workoutcoach.ngrok.app:443 -servername workoutcoach.ngrok.app 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

Expected: `issuer=... O=Let's Encrypt ...`, `subject=CN=*.ngrok.app`, and
`notAfter` in the future.

---

## 2. PIN login (mobile API)

Uses a seeded `*@beta.test` account (see `priv/repo/seeds/02_users.exs`).

```bash
curl -sS -X POST https://workoutcoach.ngrok.app/api/mobile/auth/login \
  -H "Content-Type: application/json" \
  -d '{"pin":"1111"}'
```

Expected: `{"success":true,"token":"...","entry_url":"/index.xml",...}`.

---

## 3. Authenticated screen fetch

Use the `token` and `entry_url` from step 2.

```bash
TOKEN="<token from step 2>"
curl -sS -o /dev/null -w "GET /index.xml -> %{http_code}\n" \
  https://workoutcoach.ngrok.app/index.xml \
  -H "Authorization: Bearer $TOKEN"
```

Expected: `200`.

---

## 4. launchd crash recovery

Confirms the backend auto-restarts if it crashes during the testing window.

```bash
PID=$(launchctl list | grep com.hapteo.workoutbackend.preprod | awk '{print $1}')
echo "current PID: $PID"
kill -9 "$PID"
sleep 6
launchctl list | grep workoutbackend   # expect a new PID
curl -sS -o /dev/null -w "localhost after restart: %{http_code}\n" http://localhost:4001/
```

Expected: a different PID than before, and `200` from the health check.

---

## 5. Tunnel health after restart

```bash
curl -sS -o /dev/null -w "tunnel: %{http_code}\n" https://workoutcoach.ngrok.app/
```

Expected: `200`.

---

## All-in-one

```bash
#!/usr/bin/env bash
set -euo pipefail

DOMAIN="workoutcoach.ngrok.app"

echo "--- 1. TLS certificate ---"
echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

echo "--- 2. PIN login ---"
LOGIN_RESPONSE=$(curl -sS -X POST "https://$DOMAIN/api/mobile/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"pin":"1111"}')
echo "$LOGIN_RESPONSE"
TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

echo "--- 3. Authenticated screen fetch ---"
curl -sS -o /dev/null -w "GET /index.xml -> %{http_code}\n" \
  "https://$DOMAIN/index.xml" -H "Authorization: Bearer $TOKEN"

echo "--- 4. launchd crash recovery ---"
PID=$(launchctl list | grep com.hapteo.workoutbackend.preprod | awk '{print $1}')
echo "current PID: $PID"
kill -9 "$PID"
sleep 6
launchctl list | grep workoutbackend
curl -sS -o /dev/null -w "localhost after restart: %{http_code}\n" http://localhost:4001/

echo "--- 5. Tunnel health ---"
curl -sS -o /dev/null -w "tunnel: %{http_code}\n" "https://$DOMAIN/"
```

---

## Pending (device-level, manual)

- EAS internal-distribution build install (Android + iOS)
- Login + full workout session via the app UI
- Audio cues / voice commands
- OTA update via `eas update --channel beta` (no reinstall required)

These are tracked in HAP-167 (left open until run manually).
