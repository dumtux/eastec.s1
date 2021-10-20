from .singletone import Singleton
from .sone import SOne


def test_sone():
    so = SOne.instance()
    assert isinstance(so, Singleton)


def test_set_state(mocker):
    so = SOne.instance()
    assert so.status.state == 'standby'

    spy = mocker.spy(so, 'kfive_update')

    so.set_state('playing')
    assert so.status.state =='playing'
    spy.assert_called_once()

    so.set_state('standby')
    assert so.status.state =='standby'
