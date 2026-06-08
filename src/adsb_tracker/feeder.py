import asyncio

from loguru import logger


async def run_beast_relay(
    source_host: str,
    source_port: int,
    dest_host: str,
    dest_port: int,
) -> None:
    """Relay Beast binary data from dump1090 to a remote feeder service (e.g., RadarBox).

    Connects to dump1090's Beast output port and forwards raw bytes to the destination.
    Reconnects both ends independently on failure.
    """
    while True:
        source_writer = None
        dest_writer = None
        try:
            logger.info(f"Beast relay: connecting to source {source_host}:{source_port}")
            source_reader, source_writer = await asyncio.open_connection(source_host, source_port)

            logger.info(f"Beast relay: connecting to destination {dest_host}:{dest_port}")
            _, dest_writer = await asyncio.open_connection(dest_host, dest_port)

            logger.info(f"Beast relay: forwarding {source_host}:{source_port} -> {dest_host}:{dest_port}")
            while True:
                data = await source_reader.read(4096)
                if not data:
                    logger.warning("Beast relay: source connection closed")
                    break
                dest_writer.write(data)
                await dest_writer.drain()

        except (ConnectionRefusedError, OSError) as e:
            logger.warning(f"Beast relay connection error: {e}")
        except Exception as e:
            logger.error(f"Beast relay unexpected error: {e}")
        finally:
            for w in (dest_writer, source_writer):
                if w:
                    w.close()
                    try:
                        await w.wait_closed()
                    except Exception:
                        pass

        logger.info("Beast relay: reconnecting in 10 seconds...")
        await asyncio.sleep(10)
