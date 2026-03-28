import asyncio
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

from loguru import logger

from adsb_tracker.models import AircraftUpdate
from adsb_tracker.store import AircraftStore


async def connect_sbs(host: str, port: int) -> AsyncIterator[str]:
    """Connect to dump1090 SBS port, yield one line at a time. Reconnects on failure."""
    while True:
        try:
            logger.info(f"Connecting to dump1090 SBS at {host}:{port}")
            reader, writer = await asyncio.open_connection(host, port)
            logger.info("Connected to dump1090 SBS output")
            buffer = ""
            while True:
                data = await reader.read(4096)
                if not data:
                    logger.warning("dump1090 SBS connection closed")
                    break
                buffer += data.decode("ascii", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        yield line
            writer.close()
        except (ConnectionRefusedError, OSError) as e:
            logger.warning(f"Cannot connect to dump1090 SBS: {e}")
        logger.info("Reconnecting to dump1090 in 5 seconds...")
        await asyncio.sleep(5)


def parse_sbs_message(line: str) -> AircraftUpdate | None:
    """Parse an SBS-1 BaseStation format line into an AircraftUpdate.

    SBS-1 format has 22 comma-separated fields:
    0: message_type, 1: transmission_type, 2: session_id, 3: aircraft_id,
    4: icao_hex, 5: flight_id, 6: date_generated, 7: time_generated,
    8: date_logged, 9: time_logged, 10: callsign, 11: altitude,
    12: ground_speed, 13: track, 14: lat, 15: lon, 16: vertical_rate,
    17: squawk, 18: alert, 19: emergency, 20: spi, 21: is_on_ground
    """
    fields = line.split(",")
    if len(fields) < 22:
        return None

    msg_type = fields[0].strip()
    if msg_type != "MSG":
        return None

    icao_hex = fields[4].strip().upper()
    if not icao_hex:
        return None

    update = AircraftUpdate(icao_hex=icao_hex)

    callsign = fields[10].strip()
    if callsign:
        update.callsign = callsign

    if fields[11].strip():
        try:
            update.altitude_ft = int(fields[11].strip())
        except ValueError:
            pass

    if fields[12].strip():
        try:
            update.ground_speed_kt = float(fields[12].strip())
        except ValueError:
            pass

    if fields[13].strip():
        try:
            update.track_deg = float(fields[13].strip())
        except ValueError:
            pass

    if fields[14].strip() and fields[15].strip():
        try:
            update.lat = float(fields[14].strip())
            update.lon = float(fields[15].strip())
        except ValueError:
            pass

    if fields[16].strip():
        try:
            update.vertical_rate = int(fields[16].strip())
        except ValueError:
            pass

    if fields[17].strip():
        update.squawk = fields[17].strip()

    if fields[21].strip():
        update.is_on_ground = fields[21].strip() == "-1"

    return update


BroadcastFn = Callable[["Aircraft"], Coroutine[Any, Any, None]]


async def run_decoder(
    host: str,
    port: int,
    store: AircraftStore,
    broadcast: BroadcastFn,
) -> None:
    """Main decoder loop: read SBS, parse, update store, broadcast."""
    async for line in connect_sbs(host, port):
        update = parse_sbs_message(line)
        if update is None:
            continue
        aircraft = await store.update(update)
        try:
            await broadcast(aircraft)
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
