from fastapi import HTTPException
from pytest import raises

from sone.singletone import Singleton
from sone.models import Program
from sone.sone import SOne


def test_sone():
    so = SOne.instance()
    assert isinstance(so, Singleton)


def test_set_state(mocker):
    so = SOne.instance()
    assert so.status.state == 'standby'

    spy = mocker.spy(so, 'kfive_update')

    so.set_state('heating')
    assert so.status.state =='heating'
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


def test_set_program(mocker):
    so = SOne.instance()
    program = Program.deserialize(so.status.program.serialize())
    program.target_temperature = 52
    so.set_program(program)
    assert so.status.program.target_temperature == program.target_temperature
    assert so.status.target_temperature == program.target_temperature
    so.set_target_temperature(45)
    assert so.status.program.target_temperature != 45
