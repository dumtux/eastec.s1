import time

import psutil

from sone.models import Status
from sone.singletone import Singleton
from sone.utils import Logger, get_sauna_id, get_sauna_name, get_default_status, get_sauna_id_qr, is_raspberry, seconds_elapsed


def test_logger():
    logger = Logger.instance()
    assert isinstance(logger, Singleton)


def test_get_sauna_id():
    id_a = get_sauna_id()
    time.sleep(0.2)
    id_b = get_sauna_id()
    assert type(id_a) == str
    assert id_a == id_b


def test_get_sauna_name():
    name_a = get_sauna_name()
    name_b = get_sauna_name()
    assert type(name_a) == str
    assert name_a == name_b


def test_get_default_status():
    status = get_default_status()
    assert isinstance(status, Status)


def test_get_sauna_id_qr():
    qr = get_sauna_id_qr()
    assert type(qr) == str
    assert 'base64' in qr


def test_is_raspberry():
    try:
        import RPi.GPIO
        raspberry = True
    except ModuleNotFoundError:
        raspberry = False

    assert is_raspberry() == raspberry


def test_seconds_elapsed():
    assert int(seconds_elapsed()) == int(time.time() - psutil.boot_time())