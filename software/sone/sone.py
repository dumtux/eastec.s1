from typing import List

from .models import Status, Schedule, Program
from .singletone import Singleton
from .utils import get_sauna_id, get_sauna_name, get_default_status


class SOne(Singleton):

    sauna_id: str = get_sauna_id()
    model_name: str = get_sauna_name()
    status: Status = get_default_status()
    schedules: List[Schedule] = []
    programs: List[Program] = []
