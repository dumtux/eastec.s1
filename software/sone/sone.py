from typing import List

from .models import Status, Schedule, Program
from .singletone import Singleton


class SOne(Singleton):
    sauna_id: str
    model_name: str
    status: Status
    schedules: List[Schedule]
    programs: List[Program]
