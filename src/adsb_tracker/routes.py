from pathlib import Path

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from adsb_tracker.store import AircraftStore

router = APIRouter()
INDEX_HTML = Path(__file__).parent / "static" / "index.html"


@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@router.get("/api/aircraft")
async def get_aircraft(request: Request) -> list[dict]:
    store: AircraftStore = request.app.state.store
    aircraft = await store.get_all()
    return [ac.model_dump() for ac in aircraft]


@router.get("/api/stats")
async def get_stats(request: Request) -> dict:
    store: AircraftStore = request.app.state.store
    return await store.stats()


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
