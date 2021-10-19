from typing import List

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .models import Schedule, Status, StatusUpdates, HTTPError, Sauna, SaunaID
from .defaults import DEFAULT_SCHEDULE, DEFAULT_STATUS


sauna = Sauna(
        status=Status.deserialize(DEFAULT_STATUS),
        schedules=[Schedule.deserialize(DEFAULT_SCHEDULE)],
        programs=[])


sauna_router = APIRouter(
    prefix="/sauna",
)
ping_router = APIRouter(tags=["Sauna Discovery"])
status_router = APIRouter(
    tags=["Status"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}},
)
schedules_router = APIRouter(
    tags=["Schedules"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}},
)


@ping_router.get("/ping", response_model=SaunaID)
async def get_sauna_id():
    return SaunaID(sauna_identifier="sauna_identifier", model="model")


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_sauna_status(sauna_id: str):
    return sauna.status


@status_router.put("/{sauna_id}/status", response_model=Status)
async def update_sauna_status(sauna_id: str, status: StatusUpdates):
    raise Exception("Not implemented yet")


@schedules_router.get("/{sauna_id}/schedules", response_model=List[Schedule])
async def get_sauna_schedules(sauna_id: str):
    return sauna.schedules


@schedules_router.post("/{sauna_id}/schedules", response_model=List[Schedule], responses={409: {"description": "Schedule ID already exists", "model": HTTPError}})
async def add_sauna_schedules(sauna_id: str, schedules: List[Schedule]):
    raise Exception("Not implemented yet")


@schedules_router.delete("/{sauna_id}/schedules/{schedule_id}", response_model=List[Schedule], responses={404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError}})
async def delete_sauna_schedule(sauna_id: str, schedule_id: str):
    raise Exception("Not implemented yet")


app = FastAPI(
    title="SOne API",
    version="0.1.0",
    description="REST API for sauna status fetching and control")
sauna_router.include_router(ping_router)
sauna_router.include_router(status_router)
sauna_router.include_router(schedules_router)
app.include_router(sauna_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
