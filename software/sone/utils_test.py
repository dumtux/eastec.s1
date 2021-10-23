import time

from .models import Status
from .utils import get_sauna_id, get_sauna_name, get_default_status, get_sauna_id_qr


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
