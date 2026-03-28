# ADS-B Tracker

Real-time aircraft tracking station using a Nooelec RTL-SDR dongle. Decodes ADS-B (1090 MHz) signals, displays live aircraft on a map, and feeds data to commercial tracking services in exchange for free premium memberships.

**Live map:** [airplane.esalo.com](https://airplane.esalo.com)

## Architecture

```
Nooelec SDR ──► Ultrafeeder (readsb + tar1090)
                  ├── Web UI (:8080) ──► Cloudflare Tunnel ──► airplane.esalo.com
                  └── Beast output (:30005)
                        ├── AirNav RadarBox  → free Business account ($399/yr)
                        └── Flightradar24    → free Premium subscription
```

The production deployment runs on a **Raspberry Pi 3B** with Docker Compose. A Windows development setup using dump1090 + a custom Python/FastAPI app is also included.

## Raspberry Pi Setup

### Prerequisites

- Raspberry Pi 3B or newer
- Nooelec NESDR (or any RTL-SDR dongle)
- MicroSD card with Raspberry Pi OS Lite

### Quick Start

```bash
# Clone the repo
git clone https://github.com/eriksalo/adsb-tracker.git
cd adsb-tracker/deploy/pi

# Install Docker and blacklist DVB-T drivers
chmod +x setup-pi.sh
./setup-pi.sh

# Configure station location
cp .env.example .env
nano .env  # set FEEDER_LAT, FEEDER_LONG, FEEDER_ALT_M, FEEDER_TZ

# Start
docker compose up -d
```

Open **http://pi-ip:8080** for the tar1090 map.

### Docker Containers

| Container | Image | Purpose |
|-----------|-------|---------|
| ultrafeeder | sdr-enthusiasts/docker-adsb-ultrafeeder | ADS-B decoding (readsb) + tar1090 web map |
| airnavradar | sdr-enthusiasts/docker-airnavradar | Feed to AirNav RadarBox |
| flightradar24 | sdr-enthusiasts/docker-flightradar24 | Feed to Flightradar24 |

### Feeder Services

Share your ADS-B data to receive free premium memberships:

| Service | What You Get | How to Sign Up |
|---------|-------------|----------------|
| **AirNav RadarBox** | Business account ($399/yr) | [airnavradar.com](https://www.airnavradar.com/raspberry-pi) — run `docker run --rm -it ghcr.io/sdr-enthusiasts/docker-airnavradar rbfeeder --showkey --no-start` to get a sharing key |
| **Flightradar24** | Premium subscription | Run `docker run --rm -it --entrypoint fr24feed ghcr.io/sdr-enthusiasts/docker-flightradar24 --signup` and follow the prompts |
| **FlightAware** | Enterprise account | [flightaware.com/adsb/piaware/claim](https://www.flightaware.com/adsb/piaware/claim) |
| **PlaneFinder** | Premium access | [planefinder.net/coverage/client](https://planefinder.net/coverage/client) |

Add sharing keys to `deploy/pi/.env` and restart: `docker compose up -d`

### Cloudflare Tunnel (Optional)

Expose the map publicly:

```bash
# Install cloudflared
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb

# Authenticate and create tunnel
cloudflared tunnel login
cloudflared tunnel create airplane
cloudflared tunnel route dns airplane airplane.yourdomain.com

# Configure
sudo mkdir -p /etc/cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: <TUNNEL_ID>
credentials-file: /home/$USER/.cloudflared/<TUNNEL_ID>.json
ingress:
  - hostname: airplane.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
EOF
sudo cp ~/.cloudflared/config.yml /etc/cloudflared/
sudo cp ~/.cloudflared/<TUNNEL_ID>.json /etc/cloudflared/

# Install as service
sudo cloudflared service install
sudo systemctl start cloudflared
```

### Pi Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FEEDER_LAT` | | Station latitude |
| `FEEDER_LONG` | | Station longitude |
| `FEEDER_ALT_M` | | Station altitude in meters |
| `FEEDER_TZ` | | Timezone (e.g. `America/Denver`) |
| `RADARBOX_SHARING_KEY` | | AirNav RadarBox sharing key |
| `FR24_SHARING_KEY` | | Flightradar24 sharing key |

## Windows Development Setup

For development and testing on Windows with a local SDR.

### Prerequisites

- Windows 10/11
- Python 3.11+
- Nooelec NESDR
- [Zadig](https://zadig.akeo.ie/) (USB driver installer)

### Setup

1. **Install SDR driver** with Zadig: select `RTL2832U` device, install WinUSB driver
2. **Get dump1090**: run `powershell scripts/setup_sdr.ps1` for instructions
3. **Install Python deps**: `pip install -e ".[dev]"`
4. **Configure**: `cp .env.example .env` and set `STATION_LAT`/`STATION_LON`
5. **Run**: `powershell scripts/start_all.ps1`

### Web Interface

| URL | Description |
|-----|-------------|
| `http://localhost:8080` | Custom Leaflet map with WebSocket updates |
| `http://localhost:8080/raw` | Sortable aircraft table + raw message stream |
| `http://localhost:8080/tar1090/` | tar1090 visualization (bundled with dump1090) |
| `http://localhost:8080/api/aircraft` | JSON API |
| `http://localhost:8080/api/stats` | Tracking statistics |

## Project Structure

```
adsb-tracker/
├── deploy/pi/               # Raspberry Pi Docker deployment
│   ├── docker-compose.yml   # Ultrafeeder + feeder containers
│   ├── .env.example         # Configuration template
│   ├── Dockerfile           # Custom Python app (optional)
│   └── setup-pi.sh          # Pi setup script
├── src/adsb_tracker/        # Python application
│   ├── app.py               # FastAPI factory with lifespan tasks
│   ├── config.py            # Pydantic settings
│   ├── decoder.py           # SBS TCP client + parser
│   ├── models.py            # Aircraft pydantic models
│   ├── store.py             # In-memory state with TTL
│   ├── feeder.py            # Beast TCP relay
│   ├── routes.py            # REST + WebSocket + tar1090 endpoints
│   └── static/              # Frontend (HTML, JS, CSS)
├── scripts/                 # Windows PowerShell scripts
├── tests/                   # pytest suite
├── pyproject.toml
└── CLAUDE.md
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/
```

## License

MIT
