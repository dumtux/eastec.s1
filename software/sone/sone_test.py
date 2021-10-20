from fastapi import HTTPException
from pytest import raises

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

def test_set_timer(mocker):
    so = SOne.instance()
    assert so.status.timer == 60

    spy = mocker.spy(so, 'kfive_update')
    so.set_timer(30)
    assert so.status.timer == 30
    spy.assert_called_once()

    with raises(HTTPException):
        so.set_timer(100)

def test_set_target_temperature(mocker):
    so = SOne.instance()
    assert so.status.target_temperature == 30

    spy = mocker.spy(so, 'kfive_update')
    so.set_target_temperature(60)
    assert so.status.target_temperature == 60
    spy.assert_called_once()

    with raises(HTTPException):
        so.set_target_temperature(100)
