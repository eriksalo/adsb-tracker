#!/usr/bin/env bash
# ADS-B Tracker - Raspberry Pi 3B Setup
# Run this on a fresh Raspberry Pi OS Lite or DietPi install
set -euo pipefail

echo "=== ADS-B Tracker - Pi Setup ==="
echo ""

# Check if running on Pi
if ! grep -q "Raspberry Pi\|BCM" /proc/cpuinfo 2>/dev/null; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi. Continuing anyway..."
fi

# Install Docker if not present
if ! command -v docker &>/dev/null; then
    echo "[1/4] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    echo "  Docker installed. You may need to log out and back in for group changes."
else
    echo "[1/4] Docker already installed."
fi

# Install Docker Compose plugin if not present
if ! docker compose version &>/dev/null; then
    echo "[2/4] Installing Docker Compose plugin..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-compose-plugin
else
    echo "[2/4] Docker Compose already installed."
fi

# Blacklist DVB-T drivers so they don't grab the SDR
echo "[3/4] Blacklisting DVB-T kernel drivers for RTL-SDR..."
sudo tee /etc/modprobe.d/blacklist-rtlsdr.conf > /dev/null << 'BLACKLIST'
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
blacklist dvb_usb_v2
blacklist dvb_core
BLACKLIST

# Unload if currently loaded
sudo rmmod dvb_usb_rtl28xxu 2>/dev/null || true
sudo rmmod rtl2832 2>/dev/null || true

# Clone repo if not already cloned
echo "[4/4] Setting up project..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f .env ]; then
    echo ""
    echo "ERROR: .env file not found in $SCRIPT_DIR"
    echo "Copy .env.example to .env and edit with your station coordinates."
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your station location (if not already done)"
echo "  2. Start the tracker:"
echo "       cd $SCRIPT_DIR"
echo "       docker compose up -d"
echo "  3. View the web interface at http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "  To sign up for feeder services (free premium accounts):"
echo "    RadarBox:      https://www.radarbox.com/sharing-data"
echo "    Flightradar24: docker exec -it ultrafeeder fr24feed --signup"
echo "    FlightAware:   https://www.flightaware.com/adsb/piaware"
echo ""
echo "  Add your keys to .env and restart: docker compose up -d"
