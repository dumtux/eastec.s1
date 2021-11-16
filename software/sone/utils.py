import base64
from io import BytesIO
import os
import uuid

import qrcode
from qrcode.image.pil import PilImage

from . import __name__, __version__
from .defaults import DEFAULT_STATUS
from .models import Status


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
