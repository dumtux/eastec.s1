from fastapi import HTTPException
import pytest
from pytest import raises

from sone.singletone import Singleton
from sone.models import Heater, Program
from sone.sone import SOne


def test_sone():
    so = SOne.instance()
    assert isinstance(so, Singleton)


@pytest.mark.asyncio
async def test_set_state(mocker):
    so = SOne.instance()
    assert so.status.state == 'standby'

    spy = mocker.spy(so, 'kfive_update')

    await so.set_state('heating')
    assert so.status.state =='heating'
    spy.assert_called_once()

    await so.set_state('standby')
    assert so.status.state =='standby'

@pytest.mark.asyncio
async def test_set_timer(mocker):
    so = SOne.instance()
    assert so.status.timer == 60

    spy = mocker.spy(so, 'kfive_update')
    await so.set_timer(30)
    assert so.status.timer == 30
    spy.assert_called_once()

    with raises(HTTPException):
        await so.set_timer(100)

@pytest.mark.asyncio
async def test_set_target_temperature(mocker):
    so = SOne.instance()
    assert so.status.target_temperature == 30

    spy = mocker.spy(so, 'kfive_update')
    await so.set_target_temperature(60)
    assert so.status.target_temperature == 60
    spy.assert_called_once()

    with raises(HTTPException):
        await so.set_target_temperature(100)


@pytest.mark.asyncio
async def test_set_program(mocker):
    so = SOne.instance()
    program = Program.deserialize(so.status.program.serialize())
    program.target_temperature = 52
    await so.set_program(program)
    assert so.status.program.target_temperature == program.target_temperature
    assert so.status.target_temperature == program.target_temperature
    await so.set_target_temperature(45)
    assert so.status.program.target_temperature != 45


@pytest.mark.asyncio
async def test_set_heaters(mocker):
    so = SOne.instance()
    spy = mocker.spy(so, 'kfive_update')

    heaters = [
        Heater(name='A', level=0),
        Heater(name='B', level=0),
        Heater(name='C', level=0),
    ]
    status = await so.set_heaters(heaters)
    assert status == so.status
    assert so.status.heaters == heaters
    spy.assert_called_once()

    heaters_with_invalid_level = [
        Heater(name='A', level=0),
        Heater(name='B', level=8),
        Heater(name='C', level=0),
    ]
    with raises(HTTPException):
        await so.set_heaters(heaters_with_invalid_level)

    heaters_with_invalid_order = [
        Heater(name='B', level=0),
        Heater(name='A', level=0),
        Heater(name='C', level=0),
    ]
    with raises(HTTPException):
        await so.set_heaters(heaters_with_invalid_order)
