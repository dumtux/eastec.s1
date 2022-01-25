import abc
import asyncio
import base64
from functools import wraps, partial
from io import BytesIO
import os
import time
import uuid
import psutil
import typer
import vedis

from . import __name__, __version__
from .conf import DEFAULT_STATUS, TOKEN_FILE_PATH
from .models import Status
from .singletone import Singleton


class KVStore():

    '''For Vedis embedded key-value store'''

    def __init__(self, fpath):
        self._engine = vedis.Vedis(fpath)

    def exists(self, key: str) -> bool:
        return self._engine.exists(key)

    def get(self, key: str) -> str:
        return self._engine.get(key).decode()

    def set(self, key: str, value: str) -> str:
        self._engine.set(key, value)
        return value

    def pop(self, key: str) -> str:
        value = self.get(key)
        self._engine.delete(key)
        return value

    def commit(self):
        self._engine.commit()


class Logger(Singleton):

    def log(self, text: any):
        tag = typer.style(" [SOne] ", bold=True, bg=typer.colors.GREEN, fg=typer.colors.WHITE)
        typer.secho(tag + " " + str(text))

    def error(self, text: any):
        tag = typer.style(" [SOne] ", bold=True, bg=typer.colors.RED, fg=typer.colors.WHITE)
        typer.secho(tag + " " + str(text))

    def warn(self, text: any):
        tag = typer.style(" [SOne] ", bold=True, bg=typer.colors.YELLOW, fg=typer.colors.WHITE)
        typer.secho(tag + " " + str(text))


def get_sauna_id() -> str:
    with open("/proc/cpuinfo") as f:
        cpuinfo = f.read()
    try:
        _id = cpuinfo.split("\nSerial")[1].split("\nModel")[0].split(": ")[1]
    except IndexError:
        _id = str(uuid.getnode())
    return _id


def get_sauna_name() -> str:
    return '%s %s' % (__name__, __version__)


def get_default_status() -> Status:
    status = Status.deserialize(DEFAULT_STATUS)
    status.sauna_id = get_sauna_id()
    return status


def is_raspberry() -> bool:
    uname_result = os.uname()
    if uname_result.sysname != 'Linux':
        return False
    if uname_result.machine != 'armv7l':
        return False
    try:
        import RPi.GPIO
        return True
    except ModuleNotFoundError:
        return False


def restart_app():
    os.system("systemctl restart sone")


def reboot_os():
    os.system("reboot")


def upgrade_firmware():
    os.system(f"pip3 install --upgrade git+https://gitlab.com/eastec/sone.git@release/1.0")


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


def time_since_last_boot() -> float:
    return time.time() - psutil.boot_time()


def sec_to_readable(sec: float) -> str:
    s = int(sec)
    return f"{s//86400}d {(s%86400)//3600}h {(s%3600)//60}m"
