import asyncio
import math
from datetime import datetime, timedelta, timezone

from loguru import logger

from adsb_tracker.models import Aircraft, AircraftUpdate


class AircraftStore:
    """In-memory aircraft state store with TTL-based pruning."""

    def __init__(self, ttl_seconds: int = 60, station_lat: float | None = None,
                 station_lon: float | None = None) -> None:
        self._aircraft: dict[str, Aircraft] = {}
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds
        self._station_lat = station_lat
        self._station_lon = station_lon
        self._total_messages = 0

    async def update(self, msg: AircraftUpdate) -> Aircraft:
        """Merge an update into the store. Returns the full aircraft state."""
        async with self._lock:
            self._total_messages += 1
            if msg.icao_hex in self._aircraft:
                ac = self._aircraft[msg.icao_hex]
                ac.apply_update(msg)
            else:
                ac = Aircraft(icao_hex=msg.icao_hex)
                ac.apply_update(msg)
                self._aircraft[msg.icao_hex] = ac
                logger.info(f"New aircraft: {msg.icao_hex}")

            ac.distance_nm = self._calc_distance(ac.lat, ac.lon)
            return ac

    async def get_all(self) -> list[Aircraft]:
        """Return all aircraft within TTL."""
        cutoff = self._cutoff()
        async with self._lock:
            return [ac for ac in self._aircraft.values() if ac.last_seen >= cutoff]

    async def prune(self) -> int:
        """Remove stale aircraft. Returns count removed."""
        cutoff = self._cutoff()
        async with self._lock:
            stale = [k for k, ac in self._aircraft.items() if ac.last_seen < cutoff]
            for k in stale:
                del self._aircraft[k]
            if stale:
                logger.info(f"Pruned {len(stale)} stale aircraft")
            return len(stale)

    async def stats(self) -> dict:
        async with self._lock:
            return {
                "aircraft_count": sum(
                    1 for ac in self._aircraft.values() if ac.last_seen >= self._cutoff()
                ),
                "total_messages": self._total_messages,
                "station_lat": self._station_lat,
                "station_lon": self._station_lon,
            }

    def _cutoff(self) -> datetime:
        return datetime.now(timezone.utc) - timedelta(seconds=self._ttl_seconds)

    def _calc_distance(self, lat: float | None, lon: float | None) -> float | None:
        """Haversine distance from station to aircraft in nautical miles."""
        if lat is None or lon is None or self._station_lat is None or self._station_lon is None:
            return None
        r_nm = 3440.065  # earth radius in nautical miles
        lat1, lon1 = math.radians(self._station_lat), math.radians(self._station_lon)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return round(2 * r_nm * math.asin(math.sqrt(a)), 1)
