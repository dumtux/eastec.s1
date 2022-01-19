try:
    from asyncio.exceptions import TimeoutError
except:
    # for Python 3.7 of Raspberry OS
    from concurrent.futures._base import TimeoutError
import time
from typing import Callable, List

from async_timeout import timeout
from fastapi import HTTPException
from tinydb import TinyDB

from sone.kfive import KFive

from .conf import (
    DB_FILE_PATH,
    LED_R_1,
    LED_G_1,
    LED_B_1,
    LED_R_2,
    LED_G_2,
    LED_B_2,
    TEMP_DELTA,
)
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

    initial_timer: int = 0

    kfive_update: Callable = lambda x: x

    pwm_dict: dict = None

    async def get_status(self) -> Status:
        await self._kfive_update(self.status)
        self._update_sysinfo()
        await self._check_heating()
        if self.status.state == 'heating':
            await self._kfive_update(self.status, set_time=True)
        return self.status

    async def _check_heating(self) -> Status:
        if self.status.state == 'heating' and self.status.current_temperature >= self.status.target_temperature - TEMP_DELTA:
            await self.set_state('ready')

    async def set_state(self, state: str) -> Status:
        if state not in self.VALID_STATES:
            raise HTTPException(
                status_code=422,
                detail="Sauna state must be one of %s" % str(self.VALID_STATES))

        if state == 'standby':
            self.status.state = state
            await self.set_timer(self.initial_timer)
        elif state == 'heating':
            if self.status.state != 'standby':
                raise HTTPException(
                    status_code=422,
                    detail="'heating' state can be set only from 'standby' state.")
            if self.status.current_temperature >= self.status.target_temperature - TEMP_DELTA:
                self.status.state = 'heating'
            else:
                self.status.state = 'ready'
        elif state == 'ready':
            if self.status.current_temperature >= self.status.target_temperature - TEMP_DELTA:
                self.status.state = 'ready'
            else:
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
            self.status.state = 'paused'

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

        self.initial_timer = timer

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

    def set_lights(self, lights: List[Light]) -> Status:
        if len(lights) not in [1, 2]:
            raise HTTPException(
                status_code=422,
                detail="1 or 2 lights should be given")

        for light in lights:
            if light.name not in ['RGB_1', 'RGB_2'] or light.name  not in ['RGB_1', 'RGB_2']:
                raise HTTPException(
                    status_code=422,
                    detail="Light names should be 'RGB_1' and/or 'RGB_2'")
            if light.name == 'RGB_1':
                self.status.lights[0] = light
                if light.state:
                    self._light_rgb_1(light.color.r, light.color.g, light.color.b)
                else:
                    self._light_rgb_1(0, 0, 0)
            if light.name == 'RGB_2':
                self.status.lights[1] = light
                if light.state:
                    self._light_rgb_2(light.color.r, light.color.g, light.color.b)
                else:
                    self._light_rgb_2(0, 0, 0)

        return self.status

    async def set_program(self, program: Program) -> Status:
        self.status.program = program
        await self.set_timer(program.timer_duration)
        await self.set_target_temperature(program.target_temperature)
        self.set_lights(program.lights)
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

    def _light_rgb_1(self, r: int, g: int, b: int):
        if (r not in range(256)) or (g not in range(256)) or (b not in range(256)):
            raise Exception("RGB values should be 0-255")
        if self.pwm_dict is None:
            return
        self.pwm_dict[LED_R_1].ChangeDutyCycle(int(r / 255 * 100))
        self.pwm_dict[LED_G_1].ChangeDutyCycle(int(g / 255 * 100))
        self.pwm_dict[LED_B_1].ChangeDutyCycle(int(b / 255 * 100))

    def _light_rgb_2(self, r: int, g: int, b: int):
        if (r not in range(256)) or (g not in range(256)) or (b not in range(256)):
            raise Exception("RGB values should be 0-255")
        if self.pwm_dict is None:
            return
        self.pwm_dict[LED_R_2].ChangeDutyCycle(int(r / 255 * 100))
        self.pwm_dict[LED_G_2].ChangeDutyCycle(int(g / 255 * 100))
        self.pwm_dict[LED_B_2].ChangeDutyCycle(int(b / 255 * 100))
