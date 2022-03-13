import asyncio
import base64
from functools import wraps, partial
from io import BytesIO
import os
import time
import uuid

import psutil
import qrcode

try:
    from qrcode.image.pil import PilImage
except:
    PilImage = None

from . import __name__, __version__
from .conf import DEFAULT_STATUS, TOKEN_FILE_PATH, DEPLOY_TOKEN, SSH_CONFIG, SSH_KNOWN_HOSTS
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


def _img_to_base64(img) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_byte = buffered.getvalue()
    img_str = "data:image/png;base64," + base64.b64encode(img_byte).decode()
    return img_str


def get_sauna_id_qr() -> str:
    try:
        code = '%s-%s-%s' % (__name__, __version__, get_sauna_id())
        img = qrcode.make(code)
        return _img_to_base64(img)
    except:
        return ""


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


def configure_update_ssh():
    ssh_path = '/root/.ssh'
    os.system('mkdir /root/.ssh')  # Make sure directory exists before creating files.
    with open(f'{ssh_path}/id_eastec.s1', 'w') as token_file:
        token_file.write(DEPLOY_TOKEN)
    os.system(f'chmod 600 {ssh_path}/id_eastec.s1')  # Token requires limited permissions
    with open(f'{ssh_path}/config', 'w') as config_file:
        config_file.write(SSH_CONFIG)
    os.system('ssh-keyscan github.com >>/root/.ssh/known_hosts')  # Add github to known hosts


def upgrade_firmware():
    # with open(TOKEN_FILE_PATH) as f:
    #     token = f.read().strip()
    # os.system(f"pip3 install --upgrade git+https://{token}@github.com/hotteshen/eastec.s1.git@release/1.0")
    configure_update_ssh()
    os.system(f'pip3 install -U git+ssh://git@github-eastec.s1/ksuaning-au/eastec.s1@alt-update')
    # os.system(f"pip3 install --no-cache-dir --upgrade git+https://gitlab.com/eastec/sone.git@release/1.0")


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
    return f"{s // 86400}d {(s % 86400) // 3600}h {(s % 3600) // 60}m"
