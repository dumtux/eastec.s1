from random import random

from .models import Status


def randomize(status: Status) -> Status:
    status = status.copy()
    status.set_temperature = float(int(random() * 100))
    status.current_temperature = float(int(random() * 100))
    return status
