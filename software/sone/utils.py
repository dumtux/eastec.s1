from . import __name__, __version__
from .defaults import DEFAULT_STATUS
from .models import Status


def get_sauna_id() -> str:
    return 'some unique string per device'


def get_sauna_name() -> str:
    return '%s %s' % (__name__, __version__)


def get_default_status() -> Status:
    return Status.deserialize(DEFAULT_STATUS)
