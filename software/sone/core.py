import json
import time
from typing import List, Dict

from bluedot.btcomm import BluetoothClient
from fastapi import HTTPException
from pydantic import BaseModel

from .defaults import DEFAULT_STATUS, DEFAULT_SCHEDULE
from .models import Sauna, Status, Schedule, StatusUpdates
from .utils import randomize


BT_DEVICE_NAME = "Eastec-SOne"


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "description about the HTTPException"},
        }


class STone:

    sauna: Sauna

    def __init__(self, client_mode=False) -> None:
        self.client_mode = client_mode
        self.sauna = Sauna(
                status=Status.deserialize(DEFAULT_STATUS),
                schedules=[Schedule.deserialize(DEFAULT_SCHEDULE)],
                programs=[])

    def callback(self, data: str):
        print(data)

    async def get_status(self, sauna_id: str) -> Status:
        pass

    async def update_status(self, sauna_id: str, status: StatusUpdates) -> Status:
        pass

    async def get_schedules(self, sauna_id: str) -> List[Schedule]:
        return self.sauna.schedules

    async def add_schedule(self, sauna_id, schedule: Schedule) -> None:
        pass

    async def delete_schedule(self, sauna_id: str, schedule_id: str) -> None:
        pass
