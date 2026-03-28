from adsb_tracker.decoder import parse_sbs_message


def test_parse_valid_msg3() -> None:
    """MSG type 3 contains airborne position."""
    line = "MSG,3,1,1,A1B2C3,1,2024/01/15,12:00:00.000,2024/01/15,12:00:00.000,,35000,,,47.6062,-122.3321,,,,,,0"
    update = parse_sbs_message(line)
    assert update is not None
    assert update.icao_hex == "A1B2C3"
    assert update.altitude_ft == 35000
    assert update.lat == 47.6062
    assert update.lon == -122.3321


def test_parse_valid_msg1() -> None:
    """MSG type 1 contains callsign."""
    line = "MSG,1,1,1,A1B2C3,1,2024/01/15,12:00:00.000,2024/01/15,12:00:00.000,UAL123,,,,,,,,,,0"
    update = parse_sbs_message(line)
    assert update is not None
    assert update.icao_hex == "A1B2C3"
    assert update.callsign == "UAL123"


def test_parse_invalid_short_line() -> None:
    result = parse_sbs_message("MSG,3,1,1,A1B2C3")
    assert result is None


def test_parse_non_msg_type() -> None:
    line = "STA,3,1,1,A1B2C3,1,2024/01/15,12:00:00.000,2024/01/15,12:00:00.000,,35000,,,47.6,-122.3,,,,,,0"
    result = parse_sbs_message(line)
    assert result is None


def test_parse_empty_icao() -> None:
    line = "MSG,3,1,1,,1,2024/01/15,12:00:00.000,2024/01/15,12:00:00.000,,35000,,,47.6,-122.3,,,,,,0"
    result = parse_sbs_message(line)
    assert result is None


def test_parse_ground_flag() -> None:
    line = "MSG,2,1,1,A1B2C3,1,2024/01/15,12:00:00.000,2024/01/15,12:00:00.000,,0,0,,47.6,-122.3,,,,,,-1"
    update = parse_sbs_message(line)
    assert update is not None
    assert update.is_on_ground is True
