try:
    from asyncio.exceptions import TimeoutError
except:
    # for Python 3.7 of Raspberry OS
    from concurrent.futures._base import TimeoutError
import time
from typing import Callable, List

from async_timeout import timeout
from fastapi import HTTPException
from tinydb import TinyDB, Query

from sone.kfive import KFive

from .conf import DB_FILE_PATH
from .io import light_rgb_1, light_rgb_2
from .models import Heater, Light, Status, Schedule, Program
from .singletone import Singleton
from .utils import (
    Logger,
    get_sauna_id,
    get_sauna_id_qr,
    get_sauna_name,
    get_default_status,
    time_since_last_boot,
    sec_to_readable,
)


TEMPERATURE_DELTA = 2  # terperature delta between target and current

logger = Logger.instance()
uptime = time.time()

class SOne(Singleton):
    VALID_STATES = ['standby', 'heating', 'ready', 'insession', 'paused']

    sauna_id: str = get_sauna_id()
    sauna_id_qr: str = get_sauna_id_qr()
    model_name: str = get_sauna_name()
    status: Status = get_default_status()
    db: TinyDB = TinyDB(DB_FILE_PATH)
    schedules: List[Schedule] = []

    kfive_update: Callable = lambda x: x

    async def get_status(self) -> Status:
        await self._kfive_update(self.status)
        self._update_sysinfo()
        return self.status

    async def set_state(self, state: str) -> Status:
        if state not in self.VALID_STATES:
            raise HTTPException(
                status_code=422,
                detail="Sauna state must be one of %s" % str(self.VALID_STATES))

        if state == 'standby':
            self.status.state = state
        elif state == 'heating':
            if self.status.state != 'standby':
                raise HTTPException(
                    status_code=422,
                    detail="'heating' state can be set only from 'standby' state.")
            if abs(self.status.target_temperature - self.status.current_temperature) > TEMPERATURE_DELTA:
                self.status.state = 'heating'
            else:
                self.status.state = 'ready'
        elif state == 'ready':
            raise HTTPException(
                status_code=422,
                detail="'ready' state can not be set manually.")
        elif state == 'insession':
            if self.status.state != 'ready':
                raise HTTPException(
                    status_code=422,
                    detail="'insession' state can be set only from 'ready' state.")
            self.status.state = 'insession'
        elif state == 'paused':
            if self.status.state != 'insession':
                raise HTTPException(
                    status_code=422,
                    detail="'paused' state can be set only from 'insession' state.")
            self.status.state = 'insession'

        await self._kfive_update(self.status)
        self._update_sysinfo()
        return self.status

    async def set_timer(self, timer: int) -> Status:
        if timer > 90 or timer < 0:
            raise HTTPException(
                status_code=422,
                detail="Sauna timer value should be between 0 and 90")
        self.status.timer = timer
        await self._kfive_update(self.status, set_time=True)
        self._update_sysinfo()
        return self.status

    async def set_target_temperature(self, temperature: int) -> Status:
        if temperature > 70 or temperature < 20:
            raise HTTPException(
                status_code=422,
                detail="Sauna temperature value should be between 20 and 70")
        self.status.target_temperature = temperature
        await self._kfive_update(self.status, set_temp=True)
        self._update_sysinfo()
        return self.status

    async def set_heaters(self, heaters: List[Heater]) -> Status:
        if len(heaters) != 3:
            raise HTTPException(
                status_code=422,
                detail="All 3 heaters should be given")
        if (heaters[0].name != 'A' or heaters[1].name != 'B' or heaters[2].name != 'C'):
            raise HTTPException(
                status_code=422,
                detail="Heater names should be 'A', 'B', 'C'")
        for h in heaters:
            if h.level not in KFive.HEATER_VALS.keys():
                raise HTTPException(
                    status_code=422,
                    detail="Heater values should be 0, 1, 2, 3, 4")
        self.status.heaters = heaters
        await self._kfive_update(self.status)
        self._update_sysinfo()
        return self.status

    async def set_lights(self, lights: List[Light]) -> Status:
        if len(lights) != 2:
            raise HTTPException(
                status_code=422,
                detail="All 2 light should be given")
        if lights[0].name != 'RGB_1' or lights[1].name != 'RGB_2':
            raise HTTPException(
                status_code=422,
                detail="Light names should be 'RGB_1' and 'RGB_2'")

        self.status.lights = lights

        if lights[0].state:
            print(type(lights[0].color.r), type(lights[0].color.g), type(lights[0].color.b))
            print(lights[0].color.r, lights[0].color.g, lights[0].color.b)
            light_rgb_1(lights[0].color.r, lights[0].color.g, lights[0].color.b)
        else:
            light_rgb_1(0, 0, 0)

        if lights[1].state:
            light_rgb_2(lights[1].color.r, lights[1].color.g, lights[1].color.b)
        else:
            light_rgb_2(0, 0, 0)

        return self.status

    async def set_program(self, program: Program) -> Status:
        self.status.program = program
        await self.set_timer(program.timer_duration)
        await self.set_target_temperature(program.target_temperature)
        await self.set_lights(program.lights)
        await self.set_heaters(program.heaters)
        self._update_sysinfo()
        return self.status

    async def _kfive_update(self, status: Status, set_time=False, set_temp=False):
        try:
            async with timeout(1):
                await self.kfive_update(status, set_time=set_time, set_temp=set_temp)
        except TimeoutError:
            logger.error("No response from KFive, check the UART connection.")

    def _update_sysinfo(self):
        self.status.sysinfo.time_since_sys_boot = sec_to_readable(time_since_last_boot())
        self.status.sysinfo.time_since_app_start = sec_to_readable(time.time() - uptime)
