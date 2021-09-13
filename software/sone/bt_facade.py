import json
import time
from typing import List, Dict

from bluedot.btcomm import BluetoothClient
from fastapi import HTTPException
from pydantic import BaseModel

from .defaults import DEFAULT_STATUS, DEFAULT_SCHEDULE
from .models import Sauna, Status, Schedule


BT_DEVICE_NAME = "Eastec-SOne"


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "description about the HTTPException"},
        }


class BluetoothFacade:

    bt_client: BluetoothClient
    sauna_db: Dict[str, Sauna]

    def __init__(self) -> None:
        while True:
            try:
                self.bt_client = BluetoothClient(BT_DEVICE_NAME, self.callback)
                break
            except ConnectionRefusedError:
                print("Bluetooth connection refused, trying again in 3 seconds ...")
                time.sleep(3)
                pass
        self.sauna_db = {
            "foo_sauna": Sauna(status=Status.deserialize(DEFAULT_STATUS), schedules=[], programs=[]),
            "bar_sauna": Sauna(status=Status.deserialize(DEFAULT_STATUS), schedules=[], programs=[]),
        }

    def callback(self, data: str):
        print(data)

    async def get_status(self, sauna_id: str) -> Status:
        if sauna_id not in self.sauna_db:
            raise HTTPException(status_code=404, detail="Sauna ID not found")

        data = {"method": "GET", "parameters": {"sauna_id": sauna_id}, "description": "get status"}
        self.bt_client.send(json.dumps(data))

        return self.sauna_db[sauna_id].status

    async def get_schedules(self, sauna_id: str) -> List[Schedule]:
        if sauna_id not in self.sauna_db:
            raise HTTPException(status_code=404, detail="Sauna ID not found")

        data = {"method": "GET", "parameters": {"sauna_id": sauna_id}, "description": "get schedules"}
        self.bt_client.send(json.dumps(data))

        return self.sauna_db[sauna_id].schedules

    async def add_schedule(self, sauna_id, schedule: Schedule) -> None:
        if sauna_id not in self.sauna_db:
            raise HTTPException(status_code=404, detail="Sauna ID not found")
        schedule_ids = [sch.id for sch in self.sauna_db[sauna_id].schedules]
        if schedule.id in schedule_ids:
            raise HTTPException(status_code=409, detail="Schedule ID already exists")

        data = {"method": "POST", "parameters": {"sauna_id": sauna_id}, "description": "add schedules", "body": schedule.serialize()}
        self.bt_client.send(json.dumps(data))

        self.sauna_db[sauna_id].schedules.append(schedule)

    async def delete_schedule(self, sauna_id: str, schedule_id: str) -> None:
        if sauna_id not in self.sauna_db:
            raise HTTPException(status_code=404, detail="Sauna ID not found")
        schedule_ids = [sch.id for sch in self.sauna_db[sauna_id].schedules]
        if schedule_id not in schedule_ids:
            raise HTTPException(status_code=404, detail="Schedule ID not found")
        for i in range(len(self.sauna_db[sauna_id].schedules)):
            if schedule_id == self.sauna_db[sauna_id].schedules[i].id:
                self.sauna_db[sauna_id].schedules.pop(i)
                break

        data = {"method": "DELETE", "parameters": {"sauna_id": sauna_id, "schedule_id": schedule_id}, "description": "delete schedules"}
        self.bt_client.send(json.dumps(data))

        raise Exception("And internal error occured")
