from typing import List, Optional
from pydantic import BaseModel, validator


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
    name: str
    state: bool
    color: Color = None
    brightness: int = None

    @validator('brightness', always=True)
    def check_rgb_or_mono(cls, v, values, **kwargs):
        ''' Validates that the model is passed either RGB values or a brightness '''
        if values.get('color') is None and v is None:
            raise ValueError('Either brightness or color is required')
        return v

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        data = dict(data)
        if data.get('color') is not None:
            data['color'] = Color(**data['color'])
        return Light(**data)


class Heater(BaseModel):
    name: str
    level: int

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        return Heater(**data)


class Program(BaseModel):
    name: str
    target_temperature: int
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
    first_fire_time: str
    frequency: str
    program: Program

    def serialize(self) -> dict:
        return self.dict()

    @staticmethod
    def deserialize(data: dict):
        data = dict(data)
        data['program'] = Program(**data['program'])
        return Schedule(**data)


class Sysinfo(BaseModel):
    model_name: str = 'unknown'
    firmware_version: str
    time_since_sys_boot: str
    time_since_app_start: str


class Status(BaseModel):
    state: str
    sauna_id: str
    sysinfo: Sysinfo
    target_temperature: int
    current_temperature: int
    timer: int
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
        data['sysinfo'] = Sysinfo(**data['sysinfo'])
        return Status(**data)


class StateUpdate(BaseModel):
    state: str


class TemperatureUpdate(BaseModel):
    target_temperature: int


class TimerUpdate(BaseModel):
    timer: int


class Sauna(BaseModel):
    sauna_id: str
    model_name: str
    status: Status
    schedules: List[Schedule]
    programs: List[Program]


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "description about the HTTPException"},
        }


class SaunaID(BaseModel):
    sauna_id: str
    model_name: str

    def serialize(self) -> dict:
        return self.dict()


class WiFiProfile(BaseModel):
    ssid: str
    key: str


class APNModel(BaseModel):
    apn: str
