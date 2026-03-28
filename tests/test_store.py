import pytest

from adsb_tracker.models import AircraftUpdate
from adsb_tracker.store import AircraftStore


@pytest.mark.asyncio
async def test_update_creates_aircraft(store: AircraftStore) -> None:
    update = AircraftUpdate(icao_hex="A1B2C3", callsign="UAL123", altitude_ft=35000)
    ac = await store.update(update)
    assert ac.icao_hex == "A1B2C3"
    assert ac.callsign == "UAL123"
    assert ac.altitude_ft == 35000
    assert ac.message_count == 1


@pytest.mark.asyncio
async def test_update_merges_fields(store: AircraftStore) -> None:
    await store.update(AircraftUpdate(icao_hex="A1B2C3", callsign="UAL123"))
    await store.update(AircraftUpdate(icao_hex="A1B2C3", altitude_ft=35000))
    aircraft = await store.get_all()
    assert len(aircraft) == 1
    assert aircraft[0].callsign == "UAL123"
    assert aircraft[0].altitude_ft == 35000
    assert aircraft[0].message_count == 2


@pytest.mark.asyncio
async def test_get_all_returns_active(store: AircraftStore) -> None:
    await store.update(AircraftUpdate(icao_hex="A1B2C3"))
    await store.update(AircraftUpdate(icao_hex="D4E5F6"))
    aircraft = await store.get_all()
    assert len(aircraft) == 2


@pytest.mark.asyncio
async def test_distance_calculated(store: AircraftStore) -> None:
    update = AircraftUpdate(icao_hex="A1B2C3", lat=48.0, lon=-122.0)
    ac = await store.update(update)
    assert ac.distance_nm is not None
    assert ac.distance_nm > 0


@pytest.mark.asyncio
async def test_stats(store: AircraftStore) -> None:
    await store.update(AircraftUpdate(icao_hex="A1B2C3"))
    await store.update(AircraftUpdate(icao_hex="A1B2C3"))
    stats = await store.stats()
    assert stats["aircraft_count"] == 1
    assert stats["total_messages"] == 2
