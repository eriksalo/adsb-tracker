# ADS-B Tracker

## Project Overview
ADS-B aircraft tracking station using a Nooelec RTL-SDR dongle. Primary deployment is a Raspberry Pi 3B running 24/7 with Docker, feeding data to AirNav RadarBox and Flightradar24 for free premium accounts.

## Architecture

### Production (Raspberry Pi)
```
Nooelec SDR ──► Ultrafeeder container (readsb + tar1090)
                  ├── :8080 tar1090 web UI ──► Cloudflare Tunnel ──► airplane.esalo.com
                  └── :30005 Beast output
                        ├── AirNav RadarBox container (EXTRPI718471)
                        └── Flightradar24 container (KBDU59)
```

### Development (Windows)
```
Nooelec SDR ──► dump1090.exe (gvanem build, config-file based)
                  ├── :30003 SBS ──► Python/FastAPI ──► WebSocket ──► Leaflet map
                  └── :8081 dump1090 built-in web UI
```

## Pi Deployment
- Host: 10.0.0.77 (static IP, WiFi)
- Hostname: airplane
- SSH: key auth configured
- Docker Compose: `deploy/pi/docker-compose.yml`
- Containers: ultrafeeder, airnavradar, flightradar24
- Cloudflare Tunnel: airplane.esalo.com → localhost:8080
- All services auto-start on boot

## Code Style
- Python 3.11+, type hints on all functions
- f-strings, never .format()
- loguru for logging, never print()
- Small composable functions
- snake_case everywhere
- pydantic models for data, pydantic-settings for config

## Project Layout
- `src/adsb_tracker/` — Python application (FastAPI + WebSocket + Leaflet map)
- `src/adsb_tracker/static/` — Frontend HTML/JS/CSS (map, raw data table)
- `deploy/pi/` — Raspberry Pi Docker Compose deployment
- `scripts/` — Windows PowerShell setup and launch scripts
- `tests/` — pytest test suite
- `bin/` — gitignored, holds dump1090 Windows binary

## Running

### Pi (production)
```bash
cd deploy/pi && docker compose up -d
```

### Windows (development)
```bash
powershell scripts/start_all.ps1
# or separately:
powershell scripts/start_dump1090.ps1
python -m adsb_tracker
```

## Testing
```bash
pip install -e ".[dev]"
pytest
```
