// Feed tab: decoded table + raw messages
const AircraftFeed = (() => {
    const aircraft = {};
    let sortKey = 'distance_nm';
    let sortDir = 'asc';
    let currentView = 'decoded';

    function updateAircraft(ac) {
        aircraft[ac.icao_hex] = ac;
    }

    function addRawLine(data) {
        const log = document.getElementById('feed-raw');
        const ts = new Date().toLocaleTimeString();
        const div = document.createElement('div');
        div.innerHTML = `<span class="ts">${ts}</span> <span class="msg">${JSON.stringify(data)}</span>`;
        log.appendChild(div);
        if (log.children.length > 500) log.removeChild(log.firstChild);
        if (currentView === 'raw') log.scrollTop = log.scrollHeight;
    }

    function altClass(alt) {
        if (alt == null) return 'no-data';
        if (alt < 10000) return 'alt-low';
        if (alt < 30000) return 'alt-mid';
        return 'alt-high';
    }

    function fmt(val, suffix) {
        if (val == null) return '<span class="no-data">---</span>';
        return typeof val === 'number' ? val.toLocaleString() + (suffix || '') : val;
    }

    function fmtTime(ts) {
        if (!ts) return '<span class="no-data">---</span>';
        return new Date(ts).toLocaleTimeString();
    }

    function renderTable() {
        const list = Object.values(aircraft);
        list.sort((a, b) => {
            let av = a[sortKey], bv = b[sortKey];
            if (av == null) av = sortDir === 'asc' ? Infinity : -Infinity;
            if (bv == null) bv = sortDir === 'asc' ? Infinity : -Infinity;
            if (typeof av === 'string') return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
            return sortDir === 'asc' ? av - bv : bv - av;
        });

        document.getElementById('feed-tbody').innerHTML = list.map(ac => {
            const sq = ac.squawk;
            const sqClass = (sq === '7500' || sq === '7600' || sq === '7700') ? 'squawk-emerg' : '';
            const grClass = ac.is_on_ground ? 'on-ground' : '';
            return `<tr class="${grClass}">
                <td>${ac.icao_hex}</td>
                <td class="callsign">${ac.callsign || '<span class="no-data">---</span>'}</td>
                <td class="${altClass(ac.altitude_ft)}">${fmt(ac.altitude_ft, ' ft')}</td>
                <td>${fmt(ac.ground_speed_kt != null ? Math.round(ac.ground_speed_kt) : null, ' kt')}</td>
                <td>${fmt(ac.track_deg != null ? Math.round(ac.track_deg) : null, '\u00B0')}</td>
                <td>${fmt(ac.vertical_rate, ' ft/m')}</td>
                <td>${ac.lat != null ? ac.lat.toFixed(4) : '<span class="no-data">---</span>'}</td>
                <td>${ac.lon != null ? ac.lon.toFixed(4) : '<span class="no-data">---</span>'}</td>
                <td class="${sqClass}">${ac.squawk || '<span class="no-data">---</span>'}</td>
                <td>${fmt(ac.distance_nm, '')}</td>
                <td>${ac.message_count}</td>
                <td>${fmtTime(ac.last_seen)}</td>
            </tr>`;
        }).join('');
    }

    function pruneStale() {
        const now = Date.now();
        for (const [icao, ac] of Object.entries(aircraft)) {
            if (now - new Date(ac.last_seen).getTime() > 60000) delete aircraft[icao];
        }
    }

    function init() {
        // Tab switching
        document.querySelectorAll('#tab-bar .tab').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('#tab-bar .tab').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
                // Leaflet needs a resize nudge when the map tab becomes visible
                if (btn.dataset.tab === 'map' && typeof AircraftMap !== 'undefined') {
                    setTimeout(() => AircraftMap.invalidateSize(), 50);
                }
            });
        });

        // Feed sub-view toggle (decoded / raw)
        document.querySelectorAll('.feed-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                currentView = btn.dataset.view;
                document.querySelectorAll('.feed-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.feed-view').forEach(v => v.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('feed-' + btn.dataset.view).classList.add('active');
            });
        });

        // Column sorting
        document.querySelectorAll('#feed-table th[data-key]').forEach(th => {
            th.addEventListener('click', () => {
                const key = th.dataset.key;
                if (sortKey === key) {
                    sortDir = sortDir === 'asc' ? 'desc' : 'asc';
                } else {
                    sortKey = key;
                    sortDir = 'asc';
                }
                document.querySelectorAll('#feed-table th').forEach(t => t.classList.remove('sorted-asc', 'sorted-desc'));
                th.classList.add(sortDir === 'asc' ? 'sorted-asc' : 'sorted-desc');
                renderTable();
            });
        });

        // Periodic prune + re-render
        setInterval(() => {
            pruneStale();
            renderTable();
        }, 1000);
    }

    document.addEventListener('DOMContentLoaded', init);

    return { updateAircraft, addRawLine, renderTable };
})();
