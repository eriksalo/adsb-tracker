// WebSocket client with auto-reconnect
const AircraftWS = (() => {
    let ws = null;
    let reconnectDelay = 1000;
    let totalMessages = 0;

    function connect() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${location.host}/ws`;
        ws = new WebSocket(url);

        ws.onopen = () => {
            reconnectDelay = 1000;
            setStatus(true);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'snapshot') {
                const activeIcaos = [];
                for (const ac of data.data) {
                    AircraftMap.updateAircraft(ac);
                    AircraftFeed.updateAircraft(ac);
                    activeIcaos.push(ac.icao_hex);
                }
                AircraftMap.pruneStale(activeIcaos);
                AircraftFeed.renderTable();
            } else {
                AircraftMap.updateAircraft(data);
                AircraftFeed.updateAircraft(data);
                AircraftFeed.addRawLine(data);
                AircraftFeed.renderTable();
            }

            totalMessages++;
            updateStats();
        };

        ws.onclose = () => {
            setStatus(false);
            setTimeout(() => {
                reconnectDelay = Math.min(reconnectDelay * 1.5, 10000);
                connect();
            }, reconnectDelay);
        };

        ws.onerror = () => {
            ws.close();
        };
    }

    function setStatus(connected) {
        const el = document.getElementById('stats-status');
        el.textContent = connected ? 'Connected' : 'Disconnected';
        el.className = connected ? 'connected' : 'disconnected';
    }

    function updateStats() {
        document.getElementById('ac-count').textContent = AircraftMap.getTrackedCount();
        document.getElementById('msg-count').textContent = totalMessages.toLocaleString();
    }

    async function pollStats() {
        try {
            const resp = await fetch('/api/stats');
            const stats = await resp.json();
            document.getElementById('msg-count').textContent = stats.total_messages.toLocaleString();
            document.getElementById('ac-count').textContent = stats.aircraft_count;

            if (stats.station_lat && stats.station_lon && !AircraftWS._mapInitialized) {
                AircraftMap.init(stats.station_lat, stats.station_lon);
                AircraftWS._mapInitialized = true;
            }
        } catch (e) {
            // Server not ready yet
        }
    }

    function start() {
        AircraftMap.init();
        AircraftWS._mapInitialized = true;

        pollStats().then(() => {});

        connect();
        setInterval(pollStats, 5000);
    }

    document.addEventListener('DOMContentLoaded', start);

    return { connect, start, _mapInitialized: false };
})();
