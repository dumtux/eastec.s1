from .singletone import Singleton


def test_singletone():
    a = Singleton.instance()
    b = Singleton.instance()
    assert a == b
