from typing import Dict, List

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import __title__, __version__
from .models import Schedule, Status, SaunaID, HTTPError, StateUpdate, TemperatureUpdate, TimerUpdate, Program
from .singletone import Singleton


class ConnectionStore(Singleton):

    connections: Dict[str, WebSocket] = dict()

    async def connect(self, sauna_id: str, ws: WebSocket) -> None:
        await ws.accept()
        if sauna_id in self.connections:
            raise Exception("Device ID already exists")
        self.connections[sauna_id] = ws

    def disconnect(self, sauna_id: str) -> None:
        self.connections.pop(sauna_id)

    async def send_to(self, message: str, sauna_id: str) -> None:
        await self.connections[sauna_id].send_text(message)

    async def send_to_all(self, message: str) -> None:
        for sauna_id, ws in self.connections:
            await connection.send_text(message)

    def get_sauna_list(self) -> List[str]:
        return list(self.connections.keys())

    def exists(self, sauna_id: str) -> bool:
        return sauna_id in self.connections


store = ConnectionStore.instance()
app = FastAPI(
    title=__title__,
    version=__version__,
    description="REST API for sauna status fetching and control")


@app.websocket("/ws/{sauna_id}")
async def websocket_endpoint(ws: WebSocket, sauna_id: int):
    await store.connect(sauna_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            await store.send_to(f"Got this from SOne: {data}", sauna_id)
    except WebSocketDisconnect:
        store.disconnect(sauna_id)


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
    return store.get_sauna_list()


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_status(sauna_id: str):
    if not store.exists(sauna_id):
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    raise Exception("Not implemented yet")


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
