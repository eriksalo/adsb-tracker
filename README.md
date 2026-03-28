# ADS-B Tracker

Real-time aircraft tracker using a Nooelec RTL-SDR dongle. Decodes ADS-B (1090 MHz) signals, displays live aircraft on a web map, and feeds data to commercial tracking services for free premium memberships. Runs on **Windows** (dump1090 + Python) or **Raspberry Pi** (Docker + Ultrafeeder).

## Architecture

```
Nooelec SDR ──► dump1090.exe ──► TCP :30003 (SBS) ──► Python/FastAPI ──► WebSocket ──► Leaflet Map
                                 TCP :30005 (Beast) ──► RadarBox / Flightradar24 / PlaneFinder
```

## Prerequisites

- **Windows 10/11**
- **Python 3.11+**
- **Nooelec NESDR** (or any RTL-SDR compatible dongle)
- **Zadig** — USB driver installer ([download](https://zadig.akeo.ie/))
- **dump1090** — ADS-B decoder ([Windows builds](https://github.com/MalcolmRobb/dump1090))

## Quick Start

### 1. Install SDR Driver

Run Zadig as administrator to replace the default DVB-T driver with WinUSB:

1. Options → List All Devices
2. Select **Bulk-In, Interface (Interface 0)** — verify USB ID is `0BDA:2838`
3. Select **WinUSB** as target driver
4. Click **Install Driver**

> **Warning:** Do NOT install the driver to Interface 1 (IR receiver).

### 2. Get dump1090

Download a Windows build of dump1090 and place `dump1090.exe` in `bin/dump1090/`. Or run the setup script for guidance:

```powershell
powershell scripts/setup_sdr.ps1
```

### 3. Install Python Dependencies

```bash
pip install -e .
```

Or install directly:

```bash
pip install -e ".[dev]"
```

### 4. Configure

Copy `.env.example` to `.env` and set your station location:

```bash
cp .env.example .env
```

Edit `.env`:

```
STATION_LAT=47.6062
STATION_LON=-122.3321
```

### 5. Run

**Option A** — Start everything together:

```powershell
powershell scripts/start_all.ps1
```

**Option B** — Start separately:

```powershell
# Terminal 1: dump1090
powershell scripts/start_dump1090.ps1

# Terminal 2: Web app
python -m adsb_tracker
```

Open **http://localhost:8080** in your browser.

## Web Interface

- Real-time aircraft positions on an OpenStreetMap base layer
- Aircraft icons colored by altitude and rotated by heading
- Click any aircraft for detailed info (callsign, altitude, speed, squawk, distance)
- Stats overlay showing tracked aircraft count and message rate
- WebSocket-based updates — no polling needed

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Web map interface |
| `GET /api/aircraft` | JSON array of all tracked aircraft |
| `GET /api/stats` | Tracking statistics |
| `WebSocket /ws` | Real-time aircraft updates |

## Feeding Data to Commercial Services

Share your ADS-B data to receive **free premium memberships**:

### RadarBox (Recommended)

**Free Business account** ($399/year value) for data feeders. Full Windows support.

1. Sign up at [radarbox.com/sharing-data](https://www.radarbox.com/sharing-data)
2. Download and install the RadarBox Windows feeder client
3. Point it at dump1090's Beast output: `127.0.0.1:30005`

Or use the built-in Python feeder — set in `.env`:

```
RADARBOX_ENABLED=true
```

### Flightradar24

**Free Premium subscription** for data feeders. Official Windows feeder software.

1. Download from [flightradar24.com/share-your-data](https://www.flightradar24.com/share-your-data)
2. Install and configure — it connects to dump1090 automatically

### PlaneFinder

**Free Premium access** for data feeders. Windows 8+ client available.

1. Download client from [planefinder.net/coverage/client](https://planefinder.net/coverage/client)
2. Contact PlaneFinder support for feed credentials
3. Configure to connect to dump1090's Beast output

### Other Services

- **FlightAware** — Enterprise membership for feeders, but requires Linux/Raspberry Pi (no Windows support)
- **ADS-B Exchange** — Non-profit, primarily Docker/Linux feeders
- **OpenSky Network** — Research-focused, Linux-only feeder software

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DUMP1090_HOST` | `127.0.0.1` | dump1090 hostname |
| `DUMP1090_SBS_PORT` | `30003` | SBS-1 output port |
| `DUMP1090_BEAST_PORT` | `30005` | Beast binary output port |
| `WEB_HOST` | `0.0.0.0` | Web server bind address |
| `WEB_PORT` | `8080` | Web server port |
| `STATION_LAT` | *(none)* | Station latitude (for distance calc) |
| `STATION_LON` | *(none)* | Station longitude (for distance calc) |
| `AIRCRAFT_TTL_SECONDS` | `60` | Remove aircraft after N seconds without updates |
| `RADARBOX_ENABLED` | `false` | Enable built-in RadarBox Beast relay |
| `RADARBOX_HOST` | `feed.radarbox.com` | RadarBox ingestion server |
| `RADARBOX_PORT` | `30005` | RadarBox ingestion port |

## Raspberry Pi Deployment

Run the tracker 24/7 on a Raspberry Pi 3B (or newer) using Docker. Uses the [sdr-enthusiasts Ultrafeeder](https://github.com/sdr-enthusiasts/docker-adsb-ultrafeeder) image — an all-in-one container with readsb, tar1090, and multi-feeder support.

### Quick Start (Pi)

1. Flash **Raspberry Pi OS Lite** (or DietPi) to an SD card
2. SSH in and clone this repo:
   ```bash
   git clone https://github.com/eriksalo/adsb-tracker.git
   cd adsb-tracker/deploy/pi
   ```
3. Run the setup script:
   ```bash
   chmod +x setup-pi.sh
   ./setup-pi.sh
   ```
4. Edit `.env` with your station coordinates (pre-filled for Niwot, CO)
5. Plug in your Nooelec SDR and start:
   ```bash
   docker compose up -d
   ```
6. Open **http://pi-ip-address:8080** for tar1090 map

### Pi Architecture

```
Nooelec SDR ──► Ultrafeeder container (readsb + tar1090 + feeders)
                  ├── :8080  tar1090 web UI
                  ├── :30003 SBS output
                  └── :30005 Beast output ──► RadarBox / FR24 / FlightAware
                          │
                Custom app container (optional, :8081)
                  └── Our Python/FastAPI tracker with raw data view
```

### Feeder Signups

After the Pi is running, sign up for free premium accounts:

| Service | Value | Signup |
|---------|-------|--------|
| RadarBox | $399/yr Business | [radarbox.com/sharing-data](https://www.radarbox.com/sharing-data) |
| FlightAware | Enterprise | [flightaware.com/adsb/piaware](https://www.flightaware.com/adsb/piaware) |
| Flightradar24 | Premium | `docker exec -it ultrafeeder fr24feed --signup` |
| ADSB.fi | Community | Uncomment in docker-compose.yml |

Add your keys to `deploy/pi/.env` and restart: `docker compose up -d`

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/
```

## License

MIT
