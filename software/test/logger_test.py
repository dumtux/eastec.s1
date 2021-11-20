from sone.logger import Logger
from sone.singletone import Singleton


def test_logger():
    logger = Logger.instance()
    assert isinstance(logger, Singleton)
