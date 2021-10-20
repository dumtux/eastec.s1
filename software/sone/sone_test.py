from .singletone import Singleton
from .sone import SOne


def test_sone():
    so = SOne.instance()
    assert isinstance(so, Singleton)
