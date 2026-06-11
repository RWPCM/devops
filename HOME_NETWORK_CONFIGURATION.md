# Bougival — Home LAN Documentation

> Living document for the home network at Bougival. Update it whenever hardware or services change.

---

## Table of Contents

- [1. Network Overview](#1-network-overview)

- [2. IP Address Plan](#2-ip-address-plan)

- [3. Hardware Inventory](#3-hardware-inventory)

- [4. Machines & Hosts](#4-machines--hosts)

- [5. DNS & Hostnames](#5-dns--hostnames)

- [6. Services](#6-services)

- [7. VLANs & Network Segmentation](#7-vlans--network-segmentation)

- [8. Firewall & Port Forwarding](#8-firewall--port-forwarding)

- [9. Wi-Fi](#9-wi-fi)

- [10. Remote Access](#10-remote-access)

- [11. Backups](#11-backups)

- [12. Credentials & Secrets](#12-credentials--secrets)

- [13. Maintenance Runbooks](#13-maintenance-runbooks)

- [14. Topology Diagram](#14-topology-diagram)

---

## 1. Network Overview

| Field | Value |

|---|---|

| Site name | Bougival / Louveciennes |

| ISP | Free |

| WAN type | FTTH |

| Public IP | IPv4: 82.64.5.160 — IPv6: 2a01:e0a:8d0:4780:8b7d:848f:62fe:40a1 |

| LAN subnet | `192.168.1.0/24` |

| Default gateway | `192.168.1.254` |

| Local domain | `bougival.lan` |

| External domain | `bougival.savary.space` (TLS Let's Encrypt via Gandi) |

| Primary DNS | `192.168.1.11` (AdGuard Home sur maximus) |

| Secondary DNS | `1.1.1.1` (Freebox DHCP fallback) |

| NTP server | `192.168.1.254` |

---

## 2. IP Address Plan

### Reserved ranges

| Range | Purpose |

|---|---|

| `192.168.1.1 – .9` | Network infrastructure (gateway, switches, APs, LoRaWAN GW) |

| `192.168.1.10 – .29` | Servers & always-on hosts (static) |

| `192.168.1.30 – .59` | IoT piscine & domotique (Shelly) |

| `192.168.1.60 – .99` | VMs, containers & services |

| `192.168.1.100 – .149` | Workstations, NAS & laptops |

| `192.168.1.150 – .199` | IoT & smart-home (Apple, divers) |

| `192.168.1.200 – .253` | DHCP pool (phones, guests, unknowns) |

| `192.168.1.254` | Gateway (Freebox Revolution) |

### Fixed IP assignments

| IP | Hostname | MAC | Type | Notes |

|---|---|---|---|---|

| `192.168.1.2` | `ap-etage` | `F0:A7:31:49:3C:BC` | TP-Link AP | Wi-Fi 1st floor — SSID `WIFI_1012` |

| `192.168.1.3` | `lorawan-gateway` | `A8:40:41:26:60:7A` | Dragino LPS8-N | Passerelle LoRaWAN |

| `192.168.1.11` | `maximus` | `18:31:BF:6C:CD:ED` | Server | Serveur principal Ubuntu 24.04 |

| `192.168.1.12` | `watchdog` | `2C:CF:67:64:41:D2` | Server | Raspberry Pi 4 — surveillance réseau |

| `192.168.1.30` | `shelly-eclairage-petit-bassin` | `E4:B3:23:27:EE:30` | Shelly IoT | Éclairage petit bassin |

| `192.168.1.31` | `shelly-eclairage-grand-bassin` | `30:C9:22:4B:8A:88` | Shelly IoT | Éclairage grand bassin |

| `192.168.1.32` | `shelly-vanne-remplissage` | `30:C9:22:4C:A8:08` | Shelly IoT | Vanne remplissage piscine |

| `192.168.1.33` | `shellyplus1pm-345f45206b28` | `34:5F:45:20:6B:28` | Shelly Plus 1PM | Filtration petit bassin |

| `192.168.1.34` | `shellyplus1pm-b0a7324b49bc` | `B0:A7:32:4B:49:BC` | Shelly Plus 1PM | Filtration grand bassin |

| `192.168.1.35` | `shelly1minig3-e4b3231ded1c` | `E4:B3:23:1D:ED:1C` | Shelly 1 Mini G3 | Electrolyseur |

| `192.168.1.36` | `shellyplus1pm-78ee4cc68660` | `78:EE:4C:C6:86:60` | Shelly Plus 1PM | Radiateur SDB parents |

| `192.168.1.37` | `shellyplus1pm-30c922501c90` | `30:C9:22:50:1C:90` | Shelly Plus 1PM | Radiateur SDB filles |

| `192.168.1.117` | `nas-bougival` | `00:08:9B:BF:0A:70` | QNAP NAS | NAS principal |

| `192.168.1.124` | _fill in_ | _fill in_ | Apple Mac | |

| `192.168.1.157` | `apple-watch-philippe` | `10:BD:3A:91:F0:A3` | Apple Watch | Wi-Fi WIFI_1012 |

| `192.168.1.188` | _fill in_ | _fill in_ | Ricoh printer | |

| `192.168.1.254` | `_gateway` | — | Router | Freebox Revolution — Wi-Fi SSID `WIFI_1013` |

### Discovered hosts (2026-04-28 nmap scan)

| IP | Hostname | Type | Open ports / Service | Notes |

|---|---|---|---|---|

| `192.168.1.3` | `lorawan-gateway` | Dragino LPS8-N | 8000 HTTP | Passerelle LoRaWAN — admin `http://192.168.1.3:8000` |

| `192.168.1.30` | `shelly-eclairage-petit-bassin` | Shelly IoT | 80 ShellyHTTP | Éclairage petit bassin |

| `192.168.1.31` | `shelly-eclairage-grand-bassin` | Shelly IoT | 80 ShellyHTTP | Éclairage grand bassin |

| `192.168.1.32` | `shelly-vanne-remplissage` | Shelly IoT | 80 ShellyHTTP | Vanne remplissage piscine |

| `192.168.1.33` | `shellyplus1pm-345f45206b28` | Shelly Plus 1PM | 80 ShellyHTTP | Filtration petit bassin |

| `192.168.1.34` | `shellyplus1pm-b0a7324b49bc` | Shelly Plus 1PM | 80 ShellyHTTP | Filtration grand bassin |

| `192.168.1.35` | `shelly1minig3-e4b3231ded1c` | Shelly 1 Mini G3 | 80 ShellyHTTP | Electrolyseur |

| `192.168.1.36` | `shellyplus1pm-78ee4cc68660` | Shelly Plus 1PM | 80 ShellyHTTP | Radiateur SDB parents |

| `192.168.1.37` | `shellyplus1pm-30c922501c90` | Shelly Plus 1PM | 80 ShellyHTTP | Radiateur SDB filles |

| `192.168.1.82` | — | Apple AirPlay | 5000/7000 RTSP | HomePod / Apple TV — _identify_ |

| `192.168.1.12` | `watchdog` | Server | 3001 Uptime Kuma | **Raspberry Pi 4** — surveillance réseau |

| `192.168.1.117` | `nas-bougival` | QNAP NAS | _fill in_ | NAS principal |

| `192.168.1.2` | `ap-etage` | TP-Link AP | 80/443 BusyBox HTTP | Wi-Fi 1st floor — SSID `WIFI_1012` (ex `.103`, maintenant IP fixe) |

| `192.168.1.124` | — | Apple Mac | 548 AFP, 631 CUPS | Mac with file sharing + printer sharing |

| `192.168.1.136` | — | Unknown | _(no TCP ports)_ | Mobile device / sleeping host |

| `192.168.1.140` | — | Apple AirPlay | 5000/7000 RTSP | HomePod / Apple TV — _identify_ |

| `192.168.1.11` | `maximus` | Server | 22 SSH, 53 DNS, 80/443 Traefik, 1883 MQTT, 3002 Uptime Kuma, 5000 AirTunes, 8081 AdGuard, 8082 ChirpStack, 8085 Traefik dashboard, 8090 ChirpStack REST, 8123 HA | This machine (Ubuntu 24.04) |

| `192.168.1.157` | `apple-watch-philippe` | Apple Watch | — | Wi-Fi WIFI_1012 |

| `192.168.1.174` | — | Apple + DNS | 53 dnsmasq, 5000/7000 RTSP | HomePod / Apple TV with Bonjour DNS |

| `192.168.1.188` | — | Printer | 21 FTP, 23 Telnet, 80/443, 515 LPD, 631 IPP, 2049 NFS, 9100 JetDirect | **Ricoh printer** ⚠️ exposes FTP/Telnet/NFS |

| `192.168.1.189` | — | Apple AirPlay | 5000/7000 RTSP | HomePod / Apple TV — _identify_ |

| `192.168.1.231` | — | Apple + DNS | 53 dnsmasq, 5000/7000 RTSP | HomePod / Apple TV with Bonjour DNS |

| `192.168.1.254` | `_gateway` | Router | 53 DNS, 80/443 nginx, 445 SMB, 5000 RTSP | **Freebox Revolution** |

---

## 3. Hardware Inventory

### Router / Gateway

| Field | Value |

|---|---|

| Model | Freebox Revolution |

| Firmware | _version_ |

| Admin UI | `http://192.168.1.254` |

| DHCP server | Enabled |

| DNS | dnsmasq 2.91 |

| Notes | Also serves SMB (445), AirPlay (5000) |

### Switches

| Name | Model | Location | Ports | Managed? |

|---|---|---|---|---|

| `sw-salon` | _model_ | Living room | _?_ | No |

| `sw-bureau` | _model_ | Office | _?_ | _?_ |

### Access Points

| Name | Model | Location | IP | SSID |

|---|---|---|---|---|

| `ap-rdc` | Freebox Revolution (built-in) | Ground floor | `192.168.1.254` | `WIFI_1013` |

| `ap-etage` | TP-Link | First floor | `192.168.1.2` | `WIFI_1012` |

### NAS

| Name | Model | IP | MAC | Admin UI |

|---|---|---|---|---|

| `nas-bougival` | QNAP | `192.168.1.117` | `00:08:9B:BF:0A:70` | `http://192.168.1.117` |

### LoRaWAN Gateway

| Name | Model | IP | Admin UI | Notes |

|---|---|---|---|---|

| `dragino` | Dragino LPS8-N | `192.168.1.3` | `http://192.168.1.3:8000` | Passerelle LoRaWAN — MAC `A8:40:41:26:60:7A` |

### LoRa Sensors

| Name | Model | devEUI | Application | Mesures |

|---|---|---|---|---|

| `lsn50v2` | Dragino LSN50v2 | `a84041d6635ae072` | Bougival-piscine | Température, niveau, batterie |

### Printers

| Name | Model | IP | Admin UI | Notes |

|---|---|---|---|---|

| _ricoh_ | Ricoh Aficio (NRG) | `192.168.1.188` | `http://192.168.1.188` | ⚠️ FTP(21), Telnet(23), NFS(2049) exposed — disable if unused |

### IoT Devices — Shelly (piscine & domotique)

| IP | Hostname | Modèle | Circuit | Admin UI |

|---|---|---|---|---|

| `192.168.1.30` | `shelly-eclairage-petit-bassin` | Shelly | Éclairage petit bassin | `http://192.168.1.30` |

| `192.168.1.31` | `shelly-eclairage-grand-bassin` | Shelly | Éclairage grand bassin | `http://192.168.1.31` |

| `192.168.1.32` | `shelly-vanne-remplissage` | Shelly | Vanne remplissage piscine | `http://192.168.1.32` |

| `192.168.1.33` | `shellyplus1pm-345f45206b28` | Shelly Plus 1PM | Filtration petit bassin | `http://192.168.1.33` |

| `192.168.1.34` | `shellyplus1pm-b0a7324b49bc` | Shelly Plus 1PM | Filtration grand bassin | `http://192.168.1.34` |

| `192.168.1.35` | `shelly1minig3-e4b3231ded1c` | Shelly 1 Mini G3 | Electrolyseur | `http://192.168.1.35` |

| `192.168.1.36` | `shellyplus1pm-78ee4cc68660` | Shelly Plus 1PM | Radiateur SDB parents | `http://192.168.1.36` |

| `192.168.1.37` | `shellyplus1pm-30c922501c90` | Shelly Plus 1PM | Radiateur SDB filles | `http://192.168.1.37` |

### Apple Devices (AirPlay)

| IP | Type | Name | Notes |

|---|---|---|---|

| `192.168.1.82` | HomePod / Apple TV | _identify_ | AirPlay (5000/7000) |

| `192.168.1.140` | HomePod / Apple TV | _identify_ | AirPlay (5000/7000) |

| `192.168.1.174` | HomePod / Apple TV | _identify_ | AirPlay + dnsmasq DNS |

| `192.168.1.189` | HomePod / Apple TV | _identify_ | AirPlay (5000/7000) |

| `192.168.1.231` | HomePod / Apple TV | _identify_ | AirPlay + dnsmasq DNS |

| `192.168.1.124` | Mac | _identify_ | AFP file sharing + CUPS printer |

---

## 4. Machines & Hosts

### `maximus` — Server / Main machine

| Field | Value |

|---|---|

| IP | `192.168.1.11` |

| OS | Ubuntu 24.04 LTS |

| MAC | `18:31:BF:6C:CD:ED` |

| CPU / RAM | _fill in_ |

| Admin | SSH `maximus` / `ssh maximus.bougival.lan` |

| Docker data-root | `/mnt/HD-R1/docker/` → `volumes/` (volumes nommés), `traefik/letsencrypt/`, `supervision/data/` |

| Docker réseau | `bougival.services` |

| Services | AdGuard (8081), Traefik v3 (80/443/8085), HA (8123), ChirpStack (8082/8090), MQTT (1883), Uptime Kuma B (3002), n8n (5678), AirTunes (5000) |

| Notes | systemd-resolved reconfiguré : `DNSStubListener=no` — FallbackDNS: `1.1.1.1 8.8.8.8` |

### `watchdog` — Network Monitoring (RPi4)

| Field | Value |

|---|---|

| IP | `192.168.1.12` |

| Hardware | Raspberry Pi 4 |

| MAC | `2C:CF:67:64:41:D2` |

| OS | Raspbian (Debian) |

| Admin | SSH `watchdog` |

| Services | Uptime Kuma instance A — `http://192.168.1.12:3001` — surveille maximus et ses services |

| Alerting | Telegram (token dans Vaultwarden → `Telegram-Alerting`) |

| Notes | Monitoring croisé avec Uptime Kuma instance B sur maximus (port 3002) |

### Apple Mac

| Field | Value |

|---|---|

| IP | `192.168.1.124` |

| OS | macOS _version_ |

| Hostname | _fill in_ |

| Services | AFP file sharing (548), CUPS printer sharing (631) |

| Notes | |

### Ricoh Printer

| Field | Value |

|---|---|

| IP | `192.168.1.188` |

| Model | Ricoh Aficio / NRG |

| Admin UI | `http://192.168.1.188` |

| Print ports | 515 LPD, 631 IPP, 9100 JetDirect |

| ⚠️ Risk | FTP (21), Telnet (23), NFS (2049) open — disable in printer admin |

### `homeassistant` — Home Automation (Docker sur maximus)

| Field | Value |

|---|---|

| Host | `maximus` (`192.168.1.11`) |

| Image | `ghcr.io/home-assistant/home-assistant:stable` |

| Runtime | Docker — réseau host |

| Compose | `~/docker/homeassistant/docker-compose.yml` |

| Config | `/mnt/HD-R1/docker/volumes/homeassistant_homeassistant_config/_data/` |

| Fichiers config | `configuration.yaml`, `sensors.yaml`, `automations.yaml` |

| Admin UI | `http://192.168.1.11:8123` — `https://ha.bougival.savary.space` |

| MQTT | broker `192.168.1.11:1883` — auth anonyme |

| Telegram Bot | intégration via UI (credentials dans n8n) |

| Ressources | memory 1G (reservation 512M), cpus 2.0 (reservation 0.5) |

| Trusted proxies | `http.use_x_forwarded_for: true` — `trusted_proxies: [192.168.1.11, 172.0.0.0/8]` |

**Sensors MQTT piscine** (`sensors.yaml`) — topic `application/ab5c11a8-4748-402e-b68f-f7d9ba99c357/device/a84041d6635ae072/event/up` :

| Entité | Champ MQTT | Unité |

|---|---|---|

| `sensor.piscine_temperature` | `object.water_temperature` | °C |

| `sensor.piscine_niveau` | `object.water_level` | 0/1 |

| `sensor.piscine_niveau_status` | `object.water_level_status` | HIGH/LOW |

| `sensor.piscine_batterie` | `object.BatV` | V |

**REST sensors Uptime Kuma** (`configuration.yaml`) — resource `http://192.168.1.12:3001/api/status-page/heartbeat/piscine` (interval 60s) :

| Entité | Monitor ID |

|---|---|

| `sensor.uptime_eclairage_grand_bassin` | 19 |

| `sensor.uptime_electrolyseur` | 25 |

| `sensor.uptime_filtration_petit_bassin` | 21 |

| `sensor.uptime_vanne_remplissage` | 20 |

| `sensor.uptime_filtration_grand_bassin` | 22 |

**Automation** : `alerte_piscine_niveau_bas` — déclenche si `sensor.piscine_niveau = 0` pendant 5 min → notification Telegram|

### `n8n` — Supervision & Automation (Docker sur maximus)

| Field | Value |

|---|---|

| Host | `maximus` (`192.168.1.11`) |

| Image | `n8nio/n8n` |

| Port | 5678 |

| URL | `https://n8n.bougival.savary.space` |

| Compose | `~/code/bougival-services/supervision/docker-compose.yml` |

| Data | `/mnt/HD-R1/docker/supervision/data/incidents.json` (20 derniers incidents) |

| Timezone | `Europe/Paris` |

**Workflows** :

| Workflow | Déclencheur | Description |

|---|---|---|

| Supervision Bougival | Webhook Uptime Kuma | Webhook → ReadIncidents → AI Agent Claude → WriteIncidents → Telegram |

| Bougival Daily Report | Schedule 08h00 | ReadIncidents → AI Agent Claude → Telegram |

Credentials stockées dans n8n (chiffrées) : Anthropic API, Telegram Bot

### `chirpstack` — LoRaWAN Network Server (Docker sur maximus)

| Field | Value |

|---|---|

| Host | `maximus` (`192.168.1.11`) |

| Compose | `~/code/bougival-services/chirpstack/` |

| Admin UI | `http://192.168.1.11:8082` — `https://chirpstack.bougival.savary.space` |

| REST API | `http://192.168.1.11:8090` |

| Gateway Bridge | BasicStation `:3001` — UDP `:1700` |

| Device LoRa | Dragino LSN50v2 — devEUI `a84041d6635ae072` — Application `Bougival-piscine` |

### `nas-bougival` — NAS QNAP

| Field | Value |

|---|---|

| IP | `192.168.1.117` |

| MAC | `00:08:9B:BF:0A:70` |

| Model | QNAP |

| Admin UI | `http://192.168.1.117` |

| Notes | Volume Docker : `/mnt/HD-R1/docker` |

### Unknown host

| IP | Notes |

|---|---|

| `192.168.1.136` | Responds to ping only — likely a mobile device |

---

## 5. DNS & Hostnames

DNS server: `192.168.1.11` — AdGuard Home installé en natif (systemd) dans `/opt/AdGuardHome/`

- Port DNS : **53** — Port UI : **8081**

- Upstream DoH : `https://1.1.1.1/dns-query`, `https://8.8.8.8/dns-query`

- Prérequis Ubuntu 24.04 : `DNSStubListener=no` dans `/etc/systemd/resolved.conf` — `FallbackDNS=1.1.1.1 8.8.8.8`

### DNS Rewrites (AdGuard Home — configurés)

| Hostname FQDN | IP | Notes |

|---|---|---|

| `*.bougival.lan` | `192.168.1.11` | Wildcard → maximus |

| `maximus.bougival.lan` | `192.168.1.11` | Serveur principal |

| `adguard.bougival.lan` | `192.168.1.11` | AdGuard Home UI |

| `dragino.bougival.lan` | `192.168.1.3` | Passerelle LoRaWAN LPS8-N |

| `*.bougival.savary.space` | `192.168.1.11` | Wildcard externe → Traefik sur maximus |

### Domaine externe — `bougival.savary.space`

TLS : DNS challenge Gandi (provider `gandiv5`) — `GANDIV5_PERSONAL_ACCESS_TOKEN` dans `~/code/bougival-services/proxy/.env`

Certificats stockés dans `/mnt/HD-R1/docker/traefik/letsencrypt/acme.json`

### Zone DNS Gandi — `savary.space`

| Enregistrement | Type | Valeur | TTL |

|---|---|---|---|

| `*.bougival` | A | `82.64.5.160` | 300 |

| `bougival` | A | `82.64.5.160` | 300 |

| URL | Config Traefik | Backend | Cert |

|---|---|---|---|

| `https://adguard.bougival.savary.space` | `config/adguard.yml` | `192.168.1.11:8081` | Let's Encrypt — expire 2026-07-28 |

| `https://ha.bougival.savary.space` | `config/homeassistant.yml` | `192.168.1.11:8123` | Let's Encrypt |

| `https://chirpstack.bougival.savary.space` | `config/chirpstack.yml` | `192.168.1.11:8082` | Let's Encrypt |

| `https://uptime.bougival.savary.space` | `config/uptime.yml` | `192.168.1.11:3002` | Let's Encrypt |

| `https://uptime-watchdog.bougival.savary.space` | `config/uptime-watchdog.yml` | `192.168.1.12:3001` | Let's Encrypt |

| `https://dragino.bougival.savary.space` | `config/dragino.yml` | `192.168.1.3:8000` | Let's Encrypt |

| `https://traefik.bougival.savary.space/dashboard/` | `config/traefik-dashboard.yml` | `api@internal` | Let's Encrypt |

| `https://n8n.bougival.savary.space` | `config/n8n.yml` | `192.168.1.11:5678` | Let's Encrypt |

| `https://cloud.savary.space` | existant | Nextcloud | Let's Encrypt — expire 2026-07-28 |

---

## 6. Services

### Infrastructure

| Service | Host | Port | Notes |

|---|---|---|---|

| DHCP | `192.168.1.254` | — | Freebox built-in — DNS primaire configuré sur `192.168.1.11` |

| DNS / AdGuard Home | `maximus` | 53 / 8081 | Natif systemd — admin `http://adguard.bougival.lan` / `https://adguard.bougival.savary.space` |

| Reverse proxy | `maximus` | 80 / 443 / 8085 | Traefik **v3** Docker `bougival.services` — compose `~/code/bougival-services/proxy/traefik-compose.yml` — DNS challenge `gandiv5` — provider file `./config/` (watch=true) — ressources: 256M / 0.5 cpu |

| MQTT broker | `maximus` | 1883 | Mosquitto — auth anonyme — utilisé par HA + Shelly + ChirpStack |

### Applications sur `maximus`

| Service | Port | Runtime | URL externe | Notes |

|---|---|---|---|---|

| Home Assistant | 8123 | Docker (réseau host) | `https://ha.bougival.savary.space` | Compose `~/docker/homeassistant/docker-compose.yml` |

| ChirpStack UI | 8082 | Docker | `https://chirpstack.bougival.savary.space` | Compose `~/code/bougival-services/chirpstack/` |

| ChirpStack REST API | 8090 | Docker | — | |

| ChirpStack Gateway Bridge | 3001 (BasicStation) / 1700 UDP | Docker | — | |

| Uptime Kuma B | 3002 | Docker `louislam/uptime-kuma:1` | `https://uptime.bougival.savary.space` | Compose `~/docker/uptime-kuma/docker-compose.yml` |

| n8n | 5678 | Docker `n8nio/n8n` | `https://n8n.bougival.savary.space` | Compose `~/code/bougival-services/supervision/docker-compose.yml` — data `/mnt/HD-R1/docker/supervision/data/` |

| AirTunes | 5000 | Apple AirTunes rtspd 105.1 | — | AirPlay audio receiver |

### Monitoring — Uptime Kuma (monitoring croisé)

**Instance A — watchdog** (`https://uptime-watchdog.bougival.savary.space`) :

| Monitor | Type | Cible |

|---|---|---|

| AdGuard Home | HTTPS | `https://adguard.bougival.savary.space` |

| Home Assistant | HTTPS | `https://ha.bougival.savary.space` |

| ChirpStack | HTTPS | `https://chirpstack.bougival.savary.space` |

| Uptime Kuma maximus | HTTPS | `https://uptime.bougival.savary.space` |

| Traefik Dashboard | HTTPS | `https://traefik.bougival.savary.space/dashboard/` |

| Dragino | Ping | `192.168.1.3` |

| Mosquitto MQTT | TCP | `192.168.1.11:1883` |

| ChirpStack REST API | HTTP | `http://192.168.1.11:8090` |

| n8n | HTTPS | `https://n8n.bougival.savary.space` |

**Instance B — maximus** (`https://uptime.bougival.savary.space`) :

| Monitor | Type | Cible |

|---|---|---|

| RPi4 watchdog | Ping | `192.168.1.12` |

| Uptime Kuma watchdog | HTTPS | `https://uptime-watchdog.bougival.savary.space` |

| Home Assistant | HTTPS | `https://ha.bougival.savary.space` |

| n8n | HTTPS | `https://n8n.bougival.savary.space` |

Status page piscine : `https://uptime-watchdog.bougival.savary.space/status/piscine`

Alerting sur les deux instances — 2 canaux par monitor :

1. Telegram direct — credentials Vaultwarden → `Telegram-Alerting`

2. n8n webhook `http://192.168.1.11:5678/webhook/5d26730c-a282-49b0-af94-d700d50f5202` → analyse Claude → Telegram

### Domotique

| Service | Host | Port / URL | Notes |

|---|---|---|---|

| Shelly piscine | `.30/.31/.32/.33/.34/.35` | `:80` | Éclairages, vanne, filtration, électrolyseur |

| Shelly chauffage | `.36/.37` | `:80` | Radiateurs SDB parents / filles |

### Printing

| Service | Host | Port | Notes |

|---|---|---|---|

| IPP (AirPrint) | `192.168.1.188` | 631 | Ricoh printer |

| CUPS (Mac sharing) | `192.168.1.124` | 631 | Mac printer sharing |

---

## 7. VLANs & Network Segmentation

| VLAN ID | Name | Subnet | Purpose |

|---|---|---|---|

| 1 | `default` | `192.168.1.0/24` | Main LAN (current — all devices on flat network) |

| 10 | `iot` | `192.168.10.0/24` | _Planned — Shelly devices + Apple IoT_ |

| 20 | `guest` | `192.168.20.0/24` | _Planned — Guest Wi-Fi_ |

> **Note:** all 19 discovered hosts are currently on the flat `192.168.1.0/24` network. Shelly IoT devices and the Ricoh printer are candidates for isolation in a dedicated IoT VLAN.

---

## 8. Firewall & Port Forwarding

### Inbound (WAN → LAN)

| External port | Protocol | Internal host | Internal port | Service |

|---|---|---|---|---|

| 80 | TCP | `192.168.1.11` | 80 | Traefik — redirect HTTPS |

| 443 | TCP | `192.168.1.11` | 443 | Traefik — HTTPS (Nextcloud, HA, ChirpStack, etc.) |

### Security notes

| Host | Risk | Recommendation |

|---|---|---|

| `192.168.1.188` (Ricoh) | FTP (21), Telnet (23), NFS (2049) open | Disable in printer admin panel |

| `192.168.1.11` (maximus) | MQTT (1883) auth anonyme | Acceptable si MQTT non exposé sur WAN — surveiller |

---

## 9. Wi-Fi

| SSID | AP | Location | Band | Security | IP AP |

|---|---|---|---|---|---|

| `WIFI_1013` | Freebox Revolution (built-in) | Ground floor | _fill in_ | _fill in_ | `192.168.1.254` |

| `WIFI_1012` | TP-Link | First floor | _fill in_ | _fill in_ | `192.168.1.2` |

---

## 10. Remote Access

| Method | Tool | Entry point | Notes |

|---|---|---|---|

| HTTPS — AdGuard | Traefik | `https://adguard.bougival.savary.space` | |

| HTTPS — Home Assistant | Traefik | `https://ha.bougival.savary.space` | |

| HTTPS — ChirpStack | Traefik | `https://chirpstack.bougival.savary.space` | |

| HTTPS — Uptime maximus | Traefik | `https://uptime.bougival.savary.space` | |

| HTTPS — Uptime watchdog | Traefik | `https://uptime-watchdog.bougival.savary.space` | |

| HTTPS — Dragino | Traefik | `https://dragino.bougival.savary.space` | |

| HTTPS — Traefik dashboard | Traefik | `https://traefik.bougival.savary.space/dashboard/` | |

| HTTPS — Nextcloud | Traefik | `https://cloud.savary.space` | |

| SSH | OpenSSH | `ssh maximus` / `ssh watchdog` | Ubuntu 24.04 / Raspbian |

---

## 11. Backups

| What | Method | Destination | Frequency | Retention |

|---|---|---|---|---|

| Home Assistant config | HA built-in backup | _fill in_ | Daily | _?_ |

| maximus Docker volumes | _fill in_ | _fill in_ | Daily | 7 days |

| Router config | Manual export | _fill in_ | On change | All versions |

Offsite / cloud backup: _fill in_

Restore test schedule: _quarterly_

---

## 12. Credentials & Secrets

> **Never store passwords here.** Use a password manager.

| System | Where credentials are stored |

|---|---|

| Freebox admin | Vaultwarden → `Freebox` |

| AdGuard Home | Vaultwarden → `AdGuard` |

| Home Assistant | Vaultwarden → `HomeAssistant` |

| ChirpStack | Vaultwarden → `ChirpStack` |

| Traefik / Gandi token | `.env` sur maximus — `~/code/bougival-services/proxy/.env` (`GANDI_TOKEN`) |

| Telegram alerting | Vaultwarden → `Telegram-Alerting` (bot token + chat ID) — aussi stocké dans n8n credentials |

| Anthropic API (n8n) | n8n credentials (chiffrées) |

| Ricoh printer admin | Vaultwarden → `Printer` |

| SSH keys | `~/.ssh/` sur maximus |

| Wi-Fi passphrases | Vaultwarden → `Wi-Fi` |

Password manager URL: _fill in_

---

## 13. Maintenance Runbooks

### Access a Shelly device

```bash

# Open admin UI

xdg-open http://192.168.1.6   # replace IP with target Shelly

```

### SSH into watchdog (RPi4)

```bash

ssh watchdog   # or ssh 192.168.1.12

```

### Disable dangerous services on Ricoh printer

1. Browse to `http://192.168.1.188`

2. Login as admin

3. Network Settings → disable FTP server, Telnet, NFS

4. Save and reboot printer

### Add a new static DHCP lease

1. Log into Freebox at `http://192.168.1.254`

2. Paramètres Freebox → DHCP → Baux statiques → Ajouter

3. Update §2 IP Address Plan table in this document

4. Commit this file

### SSH into maximus

```bash

ssh maximus   # or ssh 192.168.1.11

```

---

## 14. Topology Diagram

```

Internet (Free FTTH)

    │  IPv4: 82.64.5.160

    │  bougival.savary.space → TLS Let's Encrypt (Gandi)

    │

    ▼

┌──────────────────────┐

│  Freebox Revolution  │  192.168.1.254  DHCP → DNS primaire: 192.168.1.11

└──────────┬───────────┘

           │ 192.168.1.0/24 (flat LAN)

           │

    ┌──────┴────────────────────────────────────────────────────────┐

    │  Servers                              │  Infrastructure       │  IoT / Media

    │                                       │                       │

    ├── maximus       .11  Ubuntu 24.04     ├── lorawan-gw   .3     ├── Shelly piscine  .30-.35

    │   ├─ AdGuard    :8081 (DNS :53)       │   Dragino LPS8-N      ├── Shelly chauff.  .36-.37

    │   ├─ Traefik    :80/:443/:8085        ├── ap-etage     .2     ├── LSN50v2    (LoRa radio)

    │   ├─ HA         :8123                 │   TP-Link Wi-Fi       ├── HomePod/TV .82 .140 .174 .189 .231

    │   ├─ ChirpStack :8082/:8090           │                       ├── Ricoh      .188  ⚠️

    │   ├─ MQTT       :1883                 │  Workstations / NAS   │

    │   ├─ n8n        :5678 (Claude+TG)     ├── Mac         .124    │

    │   └─ Uptime B   :3002                 ├── NAS QNAP    .117    │

    └── watchdog      .12  RPi4             │                       │

        └─ Uptime A   :3001 → Telegram + n8n webhook                │

```

_Replace with a draw.io or Mermaid diagram once VLANs and topology are confirmed._

---

_Last updated: 2026-05-04 — n8n supervision (workflows Claude+Telegram), HA REST sensors Uptime Kuma + automation piscine + sensors détaillés, Traefik v3, upstream DoH AdGuard, zone Gandi, middleware allow-iframe_
