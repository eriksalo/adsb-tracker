import pytest

from adsb_tracker.config import Settings
from adsb_tracker.store import AircraftStore


@pytest.fixture
def settings() -> Settings:
    return Settings(
        dump1090_host="127.0.0.1",
        dump1090_sbs_port=30003,
        station_lat=47.6062,
        station_lon=-122.3321,
    )


@pytest.fixture
def store(settings: Settings) -> AircraftStore:
    return AircraftStore(
        ttl_seconds=settings.aircraft_ttl_seconds,
        station_lat=settings.station_lat,
        station_lon=settings.station_lon,
    )
