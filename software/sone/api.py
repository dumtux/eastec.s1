import asyncio
import json
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.endpoints import WebSocketEndpoint

from . import __title__, __version__
from .models import Schedule, Status, SaunaID, HTTPError, StateUpdate, TemperatureUpdate, TimerUpdate, Program
from .singletone import Singleton


app = FastAPI(
    title=f"{__title__} Cloud",
    version=__version__,
    description="Cloud REST API for sauna status fetching and control")
connections: Dict[str, WebSocket] = dict()
responses: Dict[str, Any] = dict()


@app.websocket_route("/ws/{sauna_id}", name="ws")
class DeviceCoManager(WebSocketEndpoint):

    encoding: str = "text"

    async def on_connect(self, ws):
        await ws.accept()
        sauna_id = DeviceCoManager.get_id_from_ws(ws)
        connections[sauna_id] = ws
        responses[sauna_id] = None
        print(f"Sauna {sauna_id} connected.")

    async def on_disconnect(self, ws, close_code: int):
        sauna_id = DeviceCoManager.get_id_from_ws(ws)
        connections.pop(sauna_id)
        responses.pop(sauna_id)
        print(f"Sauna {sauna_id} disconnected.")

    async def on_receive(self, ws, msg: Any):
        sauna_id = DeviceCoManager.get_id_from_ws(ws)
        responses[sauna_id] = json.loads(msg)

    @classmethod
    def get_id_from_ws(cls, ws: WebSocket) -> str:
        p = str(ws.url.path)
        if not p.startswith("/ws/"):
            raise Exception("Invalid WebSocket URL")
        sauna_id = p[4:]
        return sauna_id


async def tick_ws(sauna_id: str, data: Any) -> Any:
    await connections[sauna_id].send_json(data)
    while responses[sauna_id] is None:
        await asyncio.sleep(0.8)
    r = dict(responses[sauna_id])
    responses[sauna_id] = None
    return r


root_router = APIRouter(prefix="/sauna")
meta_router = APIRouter(tags=["Sauna Meta"])
status_router = APIRouter(
    tags=["Sauna Status"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}})


@meta_router.get("/list", response_model=List[str])
async def get_sauna_list():
    return list(connections.keys())


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_status(sauna_id: str):
    if sauna_id not in connections:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await tick_ws(sauna_id, {"message": "Hey"})


root_router.include_router(meta_router)
root_router.include_router(status_router)
app.include_router(root_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
