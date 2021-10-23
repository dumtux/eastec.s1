from typing import List

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import websockets

from . import __title__, __version__
from .kfive import KFive
from .sone import SOne
from .models import Schedule, Status, SaunaID, HTTPError, StateUpdate, TemperatureUpdate, TimerUpdate, Program


sone = SOne.instance()
kfive = KFive.instance()
kfive.update(sone.status)         # update KFive with the default Status of SOne
sone.kfive_update = kfive.update  # sync SOne with KFive


async def loop_ws_client(url):
    async with websockets.connect(url) as ws:
        await ws.send('hello sone server')
        while True:
            resp = await ws.recv()
            print(resp)


app = FastAPI(
    title=__title__,
    version=__version__,
    description="REST API for sauna status fetching and control")

root_router = APIRouter(prefix="/sauna")
meta_router = APIRouter(
    tags=["Sauna Meta"])
status_router = APIRouter(
    tags=["Sauna Status"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}})
control_router = APIRouter(
    tags=["Sauna Control"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}})
scheduling_router = APIRouter(tags=["Sauna Scheduling"])

@app.get("/")
async def home():
    return HTMLResponse('<img src="%s">' % sone.sauna_id_qr)


@meta_router.get("/ping", response_model=SaunaID)
async def get_id():
    return SaunaID(sauna_id=sone.sauna_id, model_name=sone.model_name)


@meta_router.get("/qrcode")
async def get_id_qrcode():
    return sone.sauna_id_qr


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_status(sauna_id: str):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.status


@control_router.put("/{sauna_id}/state", response_model=Status)
async def update_state(sauna_id: str, update: StateUpdate):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.set_state(update.state)


@control_router.put("/{sauna_id}/temperature", response_model=Status)
async def update_target_temperature(sauna_id: str, update: TemperatureUpdate):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.set_target_temperature(update.target_temperature)


@control_router.put("/{sauna_id}/timer", response_model=Status)
async def update_timer(sauna_id: str, update: TimerUpdate):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.set_timer(update.timer)


@control_router.post("/{sauna_id}/program", response_model=Status)
async def update_timer(sauna_id: str, program: Program):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.set_program(program)


@scheduling_router.get(
    "/{sauna_id}/schedules",
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID not found", "model": HTTPError},
    },
)
async def get_schedules(sauna_id: str):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.schedules


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
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    for s in sone.schedules:
        if schedule.id == s.id:
            raise HTTPException(status_code=409, detail="Schedule ID conflicts")
    sone.schedules.append(schedule)
    return sone.schedules


@scheduling_router.delete(
    "/{sauna_id}/schedules/{schedule_id}",
    response_model=List[Schedule],
    responses={
        404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError},
    },
)
async def delete_schedule(sauna_id: str, schedule_id: str):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    for i in range(len(sone.schedules)):
        if sone.schedules[i].id == schedule_id:
            sone.schedules.pop(i)
            return sone.schedules
    raise HTTPException(status_code=404, detail="Schedule ID not found")


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
