import time
from pathlib import Path

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from adsb_tracker.store import AircraftStore

router = APIRouter()
STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"
RAW_HTML = STATIC_DIR / "raw.html"


@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@router.get("/raw", response_class=HTMLResponse)
async def raw_data() -> HTMLResponse:
    return HTMLResponse(RAW_HTML.read_text(encoding="utf-8"))


@router.get("/api/aircraft")
async def get_aircraft(request: Request) -> list[dict]:
    store: AircraftStore = request.app.state.store
    aircraft = await store.get_all()
    return [ac.model_dump() for ac in aircraft]


@router.get("/api/stats")
async def get_stats(request: Request) -> dict:
    store: AircraftStore = request.app.state.store
    return await store.stats()


# --- tar1090-compatible data endpoints ---

@router.get("/tar1090/data/receiver.json")
async def tar1090_receiver(request: Request) -> JSONResponse:
    """Provide receiver metadata in dump1090 format for tar1090."""
    settings = request.app.state.settings
    return JSONResponse({
        "version": "adsb-tracker 0.1.0",
        "refresh": 1000,
        "history": 0,
        "lat": settings.station_lat,
        "lon": settings.station_lon,
    })


@router.get("/tar1090/data/aircraft.json")
async def tar1090_aircraft(request: Request) -> JSONResponse:
    """Provide aircraft data in dump1090 JSON format for tar1090."""
    store: AircraftStore = request.app.state.store
    aircraft = await store.get_all()
    now = time.time()
    ac_list = []
    for ac in aircraft:
        entry: dict = {"hex": ac.icao_hex.lower()}
        if ac.callsign:
            entry["flight"] = ac.callsign.ljust(8)
        if ac.altitude_ft is not None:
            entry["alt_baro"] = ac.altitude_ft
        if ac.ground_speed_kt is not None:
            entry["gs"] = ac.ground_speed_kt
        if ac.track_deg is not None:
            entry["track"] = ac.track_deg
        if ac.lat is not None and ac.lon is not None:
            entry["lat"] = ac.lat
            entry["lon"] = ac.lon
        if ac.vertical_rate is not None:
            entry["baro_rate"] = ac.vertical_rate
        if ac.squawk:
            entry["squawk"] = ac.squawk
        if ac.is_on_ground:
            entry["alt_baro"] = "ground"
        seen = (now - ac.last_seen.timestamp())
        entry["seen"] = round(max(0, seen), 1)
        entry["messages"] = ac.message_count
        entry["rssi"] = -10.0
        ac_list.append(entry)
    return JSONResponse({
        "now": now,
        "messages": sum(a.message_count for a in aircraft),
        "aircraft": ac_list,
    })


@router.get("/tar1090/data/history_{n}.json")
async def tar1090_history(n: int) -> JSONResponse:
    """Return empty history (we don't store historical snapshots yet)."""
    return JSONResponse({"now": time.time(), "messages": 0, "aircraft": []})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    ws_clients: set = websocket.app.state.ws_clients
    store: AircraftStore = websocket.app.state.store
    ws_clients.add(websocket)

    try:
        # Send initial snapshot
        aircraft = await store.get_all()
        snapshot = [ac.model_dump_json() for ac in aircraft]
        await websocket.send_text(f'{{"type":"snapshot","data":[{",".join(snapshot)}]}}')

        # Keep connection alive, handle client messages (ping/pong)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(websocket)
