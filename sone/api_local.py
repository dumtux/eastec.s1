import pathlib
from typing import List

from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import __title__, __version__
from .kfive import KFive
from .sone import SOne
from .models import (
    Heater,
    Light,
    Schedule,
    Status,
    SaunaID,
    HTTPError,
    StateUpdate,
    TemperatureUpdate,
    TimerUpdate,
    Program,
    WiFiProfile,
    APNModel
)
from .wifi import list_networks, connect_wifi, wifi_ip_addr
from .utils import Logger, restart_app, reboot_os, upgrade_firmware, get_sauna_id_qr


STATIC_DIR = pathlib.Path(__file__).parent / "static"

sone = SOne.instance()
from . import io as _io  # for GPIO initializing
kfive = KFive.instance()
# kfive.update(sone.status)         # update KFive with the default Status of SOne
sone.kfive_update = kfive.update  # sync SOne with KFive

logger = Logger.instance()

app = FastAPI(
    title=f"{__title__} Device",
    version=__version__,
    description="Device REST API for sauna status fetching and control")

static_dir = pathlib.Path(__file__).parent / 'static'
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=str(STATIC_DIR / "template"))


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index_device.html",
        {"request": request, "device_id": sone.sauna_id, "device_id_qr": get_sauna_id_qr()})


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


@meta_router.get("/ping", response_model=SaunaID)
async def get_id():
    return SaunaID(sauna_id=sone.sauna_id, model_name=sone.model_name)


@meta_router.get("/qrcode")
async def get_id_qrcode():
    return get_sauna_id_qr()


@meta_router.get("/wifi/networks")
def get_wifi_networks():
    return list_networks()


@meta_router.post("/wifi/connect")
async def setup_wifi(wifi_profile: WiFiProfile):
    sone.db.set("wifi-ssid", wifi_profile.ssid)
    sone.db.set("wifi-key", wifi_profile.key)
    sone.db.commit()
    return await connect_wifi(wifi_profile.ssid, wifi_profile.key)


@meta_router.get("/wifi/ip")
async def get_wifi_ip():
    return wifi_ip_addr()


@meta_router.get("/{sauna_id}/restart")
async def restart(sauna_id: str):
    '''Restart the SOne systemd service'''
    return restart_app()


@meta_router.get("/{sauna_id}/reboot")
async def reboot(sauna_id: str):
    '''Reboot the SOne device'''
    return reboot_os()


@meta_router.get("/{sauna_id}/upgrade")
async def upgrade(sauna_id: str):
    logger.log("Upgrading SOne PIP package...")
    upgrade_firmware()
    logger.log("Upgrading SOne finished.")
    return {
        "detail": f"Firmware of {sauna_id} upgraded, reboot the device to run the upgraded firmware."
    }


@meta_router.get("/{sauna_id}/apn", response_model=APNModel)
async def get(sauna_id: str):
    if sone.db.exists("apn"):
        return APNModel(apn=sone.db.get("apn"))
    else:
        raise HTTPException(status_code=404, detail="APN not resistered")


@meta_router.post("/{sauna_id}/apn", response_model=APNModel)
async def post_apn(sauna_id: str, apn: APNModel):
    sone.db.set("apn", apn.apn)
    sone.db.commit()
    return apn


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_status(sauna_id: str):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await sone.get_status()


@control_router.put("/{sauna_id}/state", response_model=Status)
async def update_state(sauna_id: str, update: StateUpdate):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await sone.set_state(update.state)


@control_router.put("/{sauna_id}/temperature", response_model=Status)
async def update_target_temperature(sauna_id: str, update: TemperatureUpdate):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await sone.set_target_temperature(update.target_temperature)


@control_router.put("/{sauna_id}/timer", response_model=Status)
async def update_timer(sauna_id: str, update: TimerUpdate):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await sone.set_timer(update.timer)


@control_router.put("/{sauna_id}/heaters", response_model=Status)
async def update_heaters(sauna_id: str, update: List[Heater]):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await sone.set_heaters(update)


@control_router.put("/{sauna_id}/lights", response_model=Status)
async def update_lights(sauna_id: str, update: List[Light]):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return sone.set_lights(update)


@control_router.post("/{sauna_id}/program", response_model=Status)
async def update_timer(sauna_id: str, program: Program):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID not found")
    return await sone.set_program(program)


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
