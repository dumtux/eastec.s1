import asyncio
import json
import pathlib
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI, WebSocket, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.endpoints import WebSocketEndpoint

from . import __title__, __version__
from .models import Schedule, Status, SaunaID, HTTPError, StateUpdate, TemperatureUpdate, TimerUpdate, Program
from .auth import verify_token


STATIC_DIR = pathlib.Path(__file__).parent / "static"

connections: Dict[str, WebSocket] = dict()
responses: Dict[str, Any] = dict()

app = FastAPI(
    title=f"{__title__} Cloud",
    version=__version__,
    description="Cloud REST API for sauna status fetching and control")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(STATIC_DIR / "template"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index_cloud.html", {"request": request, "device_ids": list(connections.keys())})


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


async def tick_ws(sauna_id: str, request: Request) -> Any:
    if sauna_id not in connections:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    if request.method =='POST' or request.method == 'PUT':
        body = await request.json()
    else:
        body = None
    data = {
        "path": request.url.path,
        "method": request.method,
        "body": body,
    }
    await connections[sauna_id].send_json(data)
    while responses[sauna_id] is None:
        await asyncio.sleep(0.8)
    r = dict(responses[sauna_id])
    responses[sauna_id] = None

    if r['status_code'] not in [200, 201]:
        raise HTTPException(status_code = r['status_code'], detail=r['body']['detail'])
    return r['body']


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


@meta_router.get("/list_sauna", response_model=List[Any])
async def get_sauna_list_sauna():
    return [
        {
            "sauna_id": "35023221449471",
            "sauna_name": "Arnold's sauna",
            "is_online": True,
        },
        {
            "sauna_id": "12345678901234",
            "sauna_name": "Kemal's sauna",
            "is_online": False,
        },
        {
            "sauna_id": "12345678905678",
            "sauna_name": "Hotte's sauna",
            "is_online": False,
        },
    ]


@meta_router.get("/protected", dependencies=[Depends(verify_token)])
async def get_protected():
    return "You've got the protected data successfully!"


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_status(sauna_id: str, request: Request):
    return await tick_ws(sauna_id, request)

@control_router.put("/{sauna_id}/state", response_model=Status)
async def update_state(sauna_id: str, update: StateUpdate, request: Request):
    return await tick_ws(sauna_id, request)


@control_router.put("/{sauna_id}/temperature", response_model=Status)
async def update_target_temperature(sauna_id: str, update: TemperatureUpdate, request: Request):
    return await tick_ws(sauna_id, request)


@control_router.put("/{sauna_id}/timer", response_model=Status)
async def update_timer(sauna_id: str, update: TimerUpdate, request: Request):
    return await tick_ws(sauna_id, request)


@scheduling_router.get(
    "/{sauna_id}/schedules",
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID not found", "model": HTTPError},
    },
)
async def get_schedules(sauna_id: str, request: Request):
    return await tick_ws(sauna_id, request)


@control_router.post("/{sauna_id}/program", response_model=Status)
async def update_timer(sauna_id: str, program: Program, request: Request):
    return await tick_ws(sauna_id, request)


@scheduling_router.post(
    "/{sauna_id}/schedules",
    status_code=201,
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError},
        409: {"description": "Schedule ID conflicts", "model": HTTPError},
    },
)
async def add_schedule(sauna_id: str, schedule: Schedule, request: Request):
    return await tick_ws(sauna_id, request)


@scheduling_router.delete(
    "/{sauna_id}/schedules/{schedule_id}",
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError},
    },
)
async def delete_schedule(sauna_id: str, schedule_id: str, request: Request):
    return await tick_ws(sauna_id, request)


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
