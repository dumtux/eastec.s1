from typing import List
from pydantic import BaseModel


class Color(BaseModel):
    r: int
    g: int
    b: int

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        return Color(**data)


class Light(BaseModel):
    identifier: str
    state: str
    color: Color
    brightness: int

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        data = dict(data)
        data['color'] = Color(**data['color'])
        return Light(**data)


class Heater(BaseModel):
    identifier: str
    state: str
    mode: str

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        return Heater(**data)


class Program(BaseModel):
    name: str
    target_temperature: float
    timer_duration: int
    lights: List[Light]
    heaters: List[Heater]

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        data = dict(data)
        data['lights'] = [Light(**item) for item in data['lights']]
        data['heaters'] = [Heater(**item) for item in data['heaters']]
        return Program(**data)


class Schedule(BaseModel):
    id: str
    user: str
    sauna: str
    frequency: str
    program: Program

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        data = dict(data)
        data['program'] = Program(**data['program'])
        return Schedule(**data)


class Status(BaseModel):
    state: str
    sauna_id: str
    firmware_version: int
    set_temperature: float
    current_temperature: float
    set_timer: int
    remaining_timer: int
    lights: List[Light]
    heaters: List[Heater]
    program: Program

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        data = dict(data)
        data['lights'] = [Light(**item) for item in data['lights']]
        data['heaters'] = [Heater(**item) for item in data['heaters']]
        data['program'] = Program(**data['program'])
        return Status(**data)


class StatusUpdates(BaseModel):
    state: str


class Sauna(BaseModel):
    status: Status
    schedules: List[Schedule]
    programs: List[Program]
