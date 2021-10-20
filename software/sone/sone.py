from typing import Callable, List

from fastapi import HTTPException

from .models import Status, Schedule, Program
from .singletone import Singleton
from .utils import get_sauna_id, get_sauna_name, get_default_status


class SOne(Singleton):

    sauna_id: str = get_sauna_id()
    model_name: str = get_sauna_name()
    status: Status = get_default_status()
    schedules: List[Schedule] = []
    programs: List[Program] = []

    kfive_update: Callable = lambda x: x

    def set_state(self, state: str) -> Status:
        if state not in ['standby', 'playing', 'paused']:
            raise HTTPException(
                status_code=422,
                detail="Sauna state must be one of 'standby', 'playing', and 'paused'")
        self.status.state = state
        self.kfive_update(self.status)
        return self.status

    def set_target_timer(self) -> Status:
        pass

    def set_target_temperature(self) -> Status:
        pass

    def set_heaters(self) -> Status:
        pass
