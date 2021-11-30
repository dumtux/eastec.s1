try:
    from asyncio.exceptions import TimeoutError
except:
    # for Python 3.7 of Raspberry OS
    from concurrent.futures._base import TimeoutError
from typing import Callable, List

from async_timeout import timeout
from fastapi import HTTPException
from tinydb import TinyDB, Query

from .conf import DB_FILE_PATH
from .models import Status, Schedule, Program
from .singletone import Singleton
from .utils import Logger, get_sauna_id, get_sauna_id_qr, get_sauna_name, get_default_status


TEMPERATURE_DELTA = 2  # terperature delta between target and current

logger = Logger.instance()

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
        return self.status

    async def set_timer(self, timer: int) -> Status:
        if timer > 90 or timer < 0:
            raise HTTPException(
                status_code=422,
                detail="Sauna timer value should be between 0 and 90")
        self.status.timer = timer
        await self._kfive_update(self.status)
        return self.status

    async def set_target_temperature(self, temperature: int) -> Status:
        if temperature > 70 or temperature < 20:
            raise HTTPException(
                status_code=422,
                detail="Sauna temperature value should be between 20 and 70")
        self.status.target_temperature = temperature
        await self._kfive_update(self.status)
        return self.status

    async def set_heaters(self) -> Status:
        raise Exception("Not implemented yet")

    async def set_lights(self) -> Status:
        raise Exception("Not implemented yet")

    async def set_program(self, program: Program) -> Status:
        self.status.program = program
        await self.set_timer(program.timer_duration)
        await self.set_target_temperature(program.target_temperature)
        # self.set_lights(program.lights)
        # self.set_heaters(program.heaters)
        return self.status

    async def _kfive_update(self, status: Status):
        try:
            async with timeout(1):
                await self.kfive_update(status)
        except TimeoutError:
            logger.error("No response from KFive, check the UART connection.")
