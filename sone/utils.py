import asyncio
import base64
from functools import wraps, partial
from io import BytesIO
import os
import uuid

import qrcode
from qrcode.image.pil import PilImage

from . import __name__, __version__
from .conf import DEFAULT_STATUS
from .models import Status
from .singletone import Singleton
import typer


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
    return str(uuid.getnode())


def get_sauna_name() -> str:
    return '%s %s' % (__name__, __version__)


def get_default_status() -> Status:
    return Status.deserialize(DEFAULT_STATUS)


def _img_to_base64(img: PilImage) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_byte = buffered.getvalue()
    img_str = "data:image/png;base64," + base64.b64encode(img_byte).decode()
    return img_str


def get_sauna_id_qr() -> str:
    code = '%s-%s-%s' % (__name__, __version__, get_sauna_id())
    img = qrcode.make(code)
    return _img_to_base64(img)


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


def restart_os():
    os.system("reboot")


def upgrade_firmware():
    os.system("pip3 install --upgrade git+https://github.com/hotteshen/eastec.s1@release/1.0")


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run 
