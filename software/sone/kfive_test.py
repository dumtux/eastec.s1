from .kfive import KFive
from .singletone import Singleton


def test_kfive():
    kf = KFive.instance()
    assert isinstance(kf, Singleton)
