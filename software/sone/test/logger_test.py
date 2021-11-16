from ..logger import Logger
from ..singletone import Singleton


def test_logger():
    logger = Logger.instance()
    assert isinstance(logger, Singleton)
