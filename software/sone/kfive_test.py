from .kfive import KFive
from .singletone import Singleton
from .utils import get_default_status


def test_kfive():
    kf = KFive.instance()
    assert isinstance(kf, Singleton)


def test_to_bytes():
    kf = KFive.instance()
    assert kf.to_bytes() == b'\xcc\x09\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x42\xe1'


def test_update():
    kf = KFive.instance()
    status = get_default_status()
    kf.update(status)
    print(kf.to_bytes())
    assert kf.to_bytes() == b'\xcc\x09\x3c\x00\x00\x1e\x56\x00\x00\x00\x00\x00\x00\x00\x42\x71'
