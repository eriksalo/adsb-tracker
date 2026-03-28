// Aircraft map rendering with Leaflet
const AircraftMap = (() => {
    let map;
    let markers = {};  // icao_hex -> { marker, label }
    let selectedIcao = null;

    // Color by altitude (feet)
    function altitudeColor(alt) {
        if (alt == null) return '#888';
        if (alt < 1000) return '#4caf50';
        if (alt < 5000) return '#8bc34a';
        if (alt < 10000) return '#cddc39';
        if (alt < 20000) return '#ffeb3b';
        if (alt < 30000) return '#ff9800';
        if (alt < 40000) return '#f44336';
        return '#e91e63';
    }

    // SVG airplane icon rotated by heading
    function createIcon(track, altitude) {
        const color = altitudeColor(altitude);
        const rotation = track != null ? track : 0;
        const svg = `
            <svg width="28" height="28" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg"
                 style="transform: rotate(${rotation}deg)">
                <path d="M14 2 L16 12 L24 16 L16 15 L16 24 L18 26 L14 25 L10 26 L12 24 L12 15 L4 16 L12 12 Z"
                      fill="${color}" stroke="#000" stroke-width="0.5"/>
            </svg>`;
        return L.divIcon({
            html: svg,
            iconSize: [28, 28],
            iconAnchor: [14, 14],
            className: ''
        });
    }

    function init(lat, lon) {
        const centerLat = lat || 39.8283;
        const centerLon = lon || -98.5795;
        map = L.map('map').setView([centerLat, centerLon], 7);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
    }

    function updateAircraft(ac) {
        const icao = ac.icao_hex;

        if (ac.lat == null || ac.lon == null) {
            // No position yet, skip map rendering but update info panel if selected
            if (icao === selectedIcao) showInfo(ac);
            return;
        }

        if (markers[icao]) {
            // Update existing marker
            markers[icao].marker.setLatLng([ac.lat, ac.lon]);
            markers[icao].marker.setIcon(createIcon(ac.track_deg, ac.altitude_ft));
            markers[icao].label.setLatLng([ac.lat, ac.lon]);
            markers[icao].label.setContent(ac.callsign || icao);
            markers[icao].data = ac;
        } else {
            // Create new marker
            const marker = L.marker([ac.lat, ac.lon], {
                icon: createIcon(ac.track_deg, ac.altitude_ft),
                zIndexOffset: ac.altitude_ft || 0
            }).addTo(map);

            const label = L.tooltip({
                permanent: true,
                direction: 'right',
                offset: [14, 0],
                className: 'aircraft-label'
            }).setContent(ac.callsign || icao);
            marker.bindTooltip(label);

            marker.on('click', () => {
                selectedIcao = icao;
                showInfo(markers[icao].data);
            });

            markers[icao] = { marker, label, data: ac };
        }

        if (icao === selectedIcao) showInfo(ac);
    }

    function removeAircraft(icao) {
        if (markers[icao]) {
            map.removeLayer(markers[icao].marker);
            delete markers[icao];
            if (icao === selectedIcao) hideInfo();
        }
    }

    function showInfo(ac) {
        const panel = document.getElementById('aircraft-info');
        panel.classList.remove('hidden');
        document.getElementById('info-callsign').textContent = ac.callsign || '---';
        document.getElementById('info-icao').textContent = ac.icao_hex;
        document.getElementById('info-alt').textContent = ac.altitude_ft != null ? `${ac.altitude_ft.toLocaleString()} ft` : '---';
        document.getElementById('info-speed').textContent = ac.ground_speed_kt != null ? `${Math.round(ac.ground_speed_kt)} kt` : '---';
        document.getElementById('info-heading').textContent = ac.track_deg != null ? `${Math.round(ac.track_deg)}°` : '---';
        document.getElementById('info-vrate').textContent = ac.vertical_rate != null ? `${ac.vertical_rate} ft/min` : '---';
        document.getElementById('info-squawk').textContent = ac.squawk || '---';
        document.getElementById('info-dist').textContent = ac.distance_nm != null ? `${ac.distance_nm} nm` : '---';
    }

    function hideInfo() {
        selectedIcao = null;
        document.getElementById('aircraft-info').classList.add('hidden');
    }

    function getTrackedCount() {
        return Object.keys(markers).length;
    }

    // Prune aircraft not updated recently (called periodically)
    function pruneStale(activeIcaos) {
        const activeSet = new Set(activeIcaos);
        for (const icao of Object.keys(markers)) {
            if (!activeSet.has(icao)) {
                removeAircraft(icao);
            }
        }
    }

    // Close info panel on button click
    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('info-close').addEventListener('click', hideInfo);
    });

    return { init, updateAircraft, removeAircraft, showInfo, hideInfo, getTrackedCount, pruneStale };
})();
