from typing import List

from fastapi import FastAPI, APIRouter

from .models import Schedule, Status, StatusUpdates
from .bt_facade import HTTPError, BluetoothFacade


def create_app(client_mode: bool=False) -> FastAPI:
    bt_facade = BluetoothFacade(client_mode=client_mode)
    sauna_router = APIRouter(
        prefix="/sauna",
    )
    status_router = APIRouter(
        tags=["Status"],
        responses={404: {"description": "Sauna ID not found", "model": HTTPError}},
    )
    schedules_router = APIRouter(
        tags=["Schedules"],
        responses={404: {"description": "Sauna ID not found", "model": HTTPError}},
    )


    @status_router.get("/{sauna_id}/status", response_model=Status)
    async def get_sauna_status(sauna_id: str):
        return await bt_facade.get_status(sauna_id)


    @status_router.put("/{sauna_id}/status", response_model=Status)
    async def update_sauna_status(sauna_id: str, status: StatusUpdates):
        print(status.dict())
        return await bt_facade.get_status(sauna_id)


    @schedules_router.get("/{sauna_id}/schedules", response_model=List[Schedule])
    async def get_sauna_schedules(sauna_id: str):
        return await bt_facade.get_schedules(sauna_id)


    @schedules_router.post("/{sauna_id}/schedules", response_model=List[Schedule], responses={409: {"description": "Schedule ID already exists", "model": HTTPError}})
    async def add_sauna_schedules(sauna_id: str, schedules: List[Schedule]):
        for sch in schedules:
            await bt_facade.add_schedule(sauna_id, sch)
        return await bt_facade.get_schedules(sauna_id)


    @schedules_router.delete("/{sauna_id}/schedules/{schedule_id}", response_model=List[Schedule], responses={404: {"description": "Sauna ID or Schedule ID not found", "model": HTTPError}})
    async def delete_sauna_schedule(sauna_id: str, schedule_id: str):
        await bt_facade.delete_schedule(sauna_id, schedule_id)
        return await bt_facade.get_schedules(sauna_id)


    app = FastAPI(
        title="SOne Bluetooth API",
        version="0.0.1",
        description="Bluetooth API Test Facade, each REST API call is converted to Bluetooth RFCOMM data and sent to the SOne device.")
    sauna_router.include_router(status_router)
    sauna_router.include_router(schedules_router)
    app.include_router(sauna_router)

    return app
