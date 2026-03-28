from adsb_tracker.models import Aircraft, AircraftUpdate


def test_aircraft_apply_update() -> None:
    ac = Aircraft(icao_hex="A1B2C3")
    update = AircraftUpdate(
        icao_hex="A1B2C3",
        callsign="UAL123",
        altitude_ft=35000,
        lat=47.6,
        lon=-122.3,
    )
    ac.apply_update(update)
    assert ac.callsign == "UAL123"
    assert ac.altitude_ft == 35000
    assert ac.lat == 47.6
    assert ac.message_count == 1


def test_aircraft_partial_update() -> None:
    ac = Aircraft(icao_hex="A1B2C3", callsign="UAL123", altitude_ft=35000)
    ac.message_count = 1
    update = AircraftUpdate(icao_hex="A1B2C3", altitude_ft=36000)
    ac.apply_update(update)
    assert ac.callsign == "UAL123"  # unchanged
    assert ac.altitude_ft == 36000  # updated
    assert ac.message_count == 2


def test_aircraft_update_strips_callsign() -> None:
    ac = Aircraft(icao_hex="A1B2C3")
    update = AircraftUpdate(icao_hex="A1B2C3", callsign="  UAL123  ")
    ac.apply_update(update)
    assert ac.callsign == "UAL123"
