# ADS-B Tracker

## Project Overview
Windows 11 ADS-B aircraft tracker using a Nooelec SDR dongle. Decodes 1090 MHz ADS-B signals via dump1090 and displays live aircraft on a web map.

## Architecture
```
Nooelec SDR → dump1090.exe (RF decode) → TCP ports
                                           ├─ :30003 SBS-1 → Python (FastAPI) → WebSocket → Leaflet map
                                           └─ :30005 Beast  → RadarBox feeder
```

## Code Style
- Python 3.11+, type hints on all functions
- f-strings, never .format()
- loguru for logging, never print()
- Small composable functions
- snake_case everywhere
- pydantic models for data, pydantic-settings for config

## Key Dependencies
- **dump1090**: External process, decodes RF from SDR. Must be running before the Python app.
- **FastAPI + uvicorn**: Web server with WebSocket support
- **pyModeS**: ADS-B message decoding utilities (used for supplemental decoding)
- **Leaflet.js**: Frontend map rendering via CDN

## Running
```bash
# Start dump1090 first
powershell scripts/start_dump1090.ps1

# Start the web app
python -m adsb_tracker
```
Web UI at http://localhost:8080

## Project Layout
- `src/adsb_tracker/` — Python application
- `src/adsb_tracker/static/` — Frontend HTML/JS/CSS
- `scripts/` — PowerShell setup and launch scripts
- `bin/` — gitignored, holds dump1090 binary (downloaded via setup script)

## Testing
```bash
pytest
```
