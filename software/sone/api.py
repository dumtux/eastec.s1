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
    title=__title__,
    version=__version__,
    description="REST API for sauna status fetching and control")
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


root_router = APIRouter(prefix="/sauna")
meta_router = APIRouter(tags=["Sauna Meta"])
status_router = APIRouter(
    tags=["Sauna Status"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}})
control_router = APIRouter(
    tags=["Sauna Control"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}})
scheduling_router = APIRouter(tags=["Sauna Scheduling"])


@meta_router.get("/list", response_model=List[str])
async def get_sauna_list():
    return list(connections.keys())


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_status(sauna_id: str):
    if sauna_id not in connections:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    await connections[sauna_id].send_json({"message": "is this working?"})
    while responses[sauna_id] is None:
        await asyncio.sleep(0.8)
    r = dict(responses[sauna_id])
    responses[sauna_id] = None
    return r


@control_router.put("/{sauna_id}/state", response_model=Status)
async def update_state(sauna_id: str, update: StateUpdate):
    raise Exception("Not implemented yet")


@control_router.put("/{sauna_id}/temperature", response_model=Status)
async def update_target_temperature(sauna_id: str, update: TemperatureUpdate):
    raise Exception("Not implemented yet")


@control_router.put("/{sauna_id}/timer", response_model=Status)
async def update_timer(sauna_id: str, update: TimerUpdate):
    raise Exception("Not implemented yet")


@control_router.post("/{sauna_id}/program", response_model=Status)
async def update_timer(sauna_id: str, program: Program):
    raise Exception("Not implemented yet")


@scheduling_router.get(
    "/{sauna_id}/schedules",
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID not found", "model": HTTPError},
    },
)
async def get_schedules(sauna_id: str):
    raise Exception("Not implemented yet")


@scheduling_router.post(
    "/{sauna_id}/schedules",
    status_code=201,
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError},
        409: {"description": "Schedule ID conflicts", "model": HTTPError},
    },
)
async def add_schedule(sauna_id: str, schedule: Schedule):
    raise Exception("Not implemented yet")


@scheduling_router.delete(
    "/{sauna_id}/schedules/{schedule_id}",
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError},
    },
)
async def delete_schedule(sauna_id: str, schedule_id: str):
    raise Exception("Not implemented yet")


root_router.include_router(meta_router)
root_router.include_router(status_router)
root_router.include_router(control_router)
root_router.include_router(scheduling_router)
app.include_router(root_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
