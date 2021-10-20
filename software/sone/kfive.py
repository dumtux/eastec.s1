from typing import Callable

from .singletone import Singleton


class KFive(Singleton):

    def write(data: bytes):
        raise Exception("Not implemented yet")

    def read(callback: Callable):
        raise Exception("Not implemented yet")
