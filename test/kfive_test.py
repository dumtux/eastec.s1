import pytest
import serial

from sone.kfive import KFive
from sone.singletone import Singleton
from sone.utils import get_default_status, is_raspberry


def test_kfive():
    kf = KFive.instance()
    assert isinstance(kf, Singleton)


def test_to_bytes():
    kf = KFive.instance()

    # # the KFive's initial value
    # assert kf.to_bytes() == b'\xcc\x09\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x42\xe1'

    # after KFive is synced with SOne, the values are set as DEFAULT_STATUS
    assert kf.to_bytes() == b'\xcc\x01\x3c\x00\x00\x1e\x56\x00\x00\x00\x00\x00\x00\x00\x42\x69'

    assert kf.to_bytes(set_time=True) == b'\xcc\x01\x3c\x00\x00\x1e\x56\x02\x00\x01\x00\x00\x00\x00\x42\x6c'
    assert kf.to_bytes(set_temp=True) == b'\xcc\x01\x3c\x00\x00\x1e\x56\x01\x00\x00\x00\x00\x00\x00\x42\x6a'


@pytest.mark.asyncio
async def test_update():
    kf = KFive.instance()
    status = get_default_status()
    await kf.update(status)
    print(kf.to_bytes())
    assert kf.to_bytes() == b'\xcc\x01\x3c\x00\x00\x1e\x56\x00\x00\x00\x00\x00\x00\x00\x42\x69'


def test_init_uart():
    kf = KFive.instance()
    kf.init_uart()
    if is_raspberry():
        assert isinstance(kf.uart, serial.Serial)
    else:
        assert kf.uart is None
