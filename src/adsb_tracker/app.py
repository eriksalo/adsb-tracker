import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from adsb_tracker.config import Settings
from adsb_tracker.decoder import run_decoder
from adsb_tracker.feeder import run_beast_relay
from adsb_tracker.models import Aircraft
from adsb_tracker.routes import router
from adsb_tracker.store import AircraftStore

STATIC_DIR = Path(__file__).parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    store = AircraftStore(
        ttl_seconds=settings.aircraft_ttl_seconds,
        station_lat=settings.station_lat,
        station_lon=settings.station_lon,
    )
    ws_clients: set = set()

    async def broadcast(aircraft: Aircraft) -> None:
        if not ws_clients:
            return
        data = aircraft.model_dump_json()
        dead: set = set()
        for ws in ws_clients:
            try:
                await ws.send_text(data)
            except Exception:
                dead.add(ws)
        ws_clients.difference_update(dead)

    async def prune_loop() -> None:
        while True:
            await asyncio.sleep(10)
            await store.prune()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        logger.info(f"Starting ADS-B Tracker on {settings.web_host}:{settings.web_port}")
        tasks: list[asyncio.Task] = []

        tasks.append(asyncio.create_task(
            run_decoder(settings.dump1090_host, settings.dump1090_sbs_port, store, broadcast)
        ))
        tasks.append(asyncio.create_task(prune_loop()))

        if settings.radarbox_enabled:
            tasks.append(asyncio.create_task(
                run_beast_relay(
                    settings.dump1090_host, settings.dump1090_beast_port,
                    settings.radarbox_host, settings.radarbox_port,
                )
            ))
            logger.info("RadarBox feeder enabled")

        yield

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("ADS-B Tracker stopped")

    app = FastAPI(title="ADS-B Tracker", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.store = store
    app.state.ws_clients = ws_clients
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(router)

    return app
