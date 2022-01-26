from fastapi.testclient import TestClient

from sone.api_local import app
from sone.conf import DEFAULT_SCHEDULE, DEFAULT_STATUS
from sone.models import Schedule
from sone.sone import SOne
from sone.utils import is_raspberry, get_sauna_id_qr
from sone.wifi import list_networks


client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_ping():
    response = client.get("/sauna/ping")
    assert response.status_code == 200
    assert 'sauna_id' in response.json().keys()
    assert 'model_name' in response.json().keys()


def test_get_qrcode():
    response = client.get("/sauna/qrcode")
    assert response.status_code == 200
    assert response.json() == get_sauna_id_qr()


def test_get_wifi_list():
    response = client.get("/sauna/wifi/networks")
    if is_raspberry():
        assert response.status_code == 200
        assert list_networks() == response.json()
    else:
        assert response.status_code == 422


def test_get_apn():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.get("/sauna/%s/apn" % sauna_id)
    if SOne.instance().db.exists("apn"):
        assert response.status_code == 200
    else:
        assert response.status_code == 404

    response = client.post("/sauna/%s/apn" % sauna_id, json={"apn": "APNSTRING"})
    assert response.status_code == 200
    assert response.json() == {"apn": "APNSTRING"}

    response = client.get("/sauna/%s/apn" % sauna_id)
    assert response.status_code == 200
    assert response.json() == {"apn": "APNSTRING"}


def test_get_status():
    response = client.get("/sauna/fake_sauna_id/status")
    assert response.status_code == 404

    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.get("/sauna/%s/status" % sauna_id)
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()


def test_update_state():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.put("/sauna/%s/state" % sauna_id, json={"state": "heating"})
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()

    # recover to the default value
    response = client.put("/sauna/%s/state" % sauna_id, json={"state": DEFAULT_STATUS["state"]})


def test_update_target_temperature():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.put("/sauna/%s/temperature" % sauna_id, json={"target_temperature": 50})
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()

    # recover to the default value
    response = client.put("/sauna/%s/temperature" % sauna_id, json={"target_temperature": DEFAULT_STATUS["target_temperature"]})


def test_update_timer():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.put("/sauna/%s/timer" % sauna_id, json={"timer": 30})
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()

    # recover to the default value
    response = client.put("/sauna/%s/timer" % sauna_id, json={"timer": DEFAULT_STATUS["timer"]})
    assert SOne.instance().status.timer == DEFAULT_STATUS["timer"]


def test_set_program():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.post("/sauna/%s/program" % sauna_id, json=DEFAULT_SCHEDULE["program"])
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()

    # recover to the default value
    response = client.put("/sauna/%s/temperature" % sauna_id, json={"target_temperature": DEFAULT_STATUS["target_temperature"]})
    response = client.put("/sauna/%s/timer" % sauna_id, json={"timer": DEFAULT_STATUS["timer"]})


def test_get_schedules():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.get("/sauna/%s/schedules" % sauna_id)
    assert response.status_code == 200
    assert response.json() == [s.serialize() for s in SOne.instance().schedules]


def test_add_schedules():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.get("/sauna/%s/schedules" % sauna_id)
    assert response.status_code == 200
    assert len(response.json()) == 0

    schedule = Schedule.deserialize(DEFAULT_SCHEDULE)
    response = client.post("/sauna/%s/schedules" % sauna_id, json=schedule.serialize())
    assert response.status_code == 201
    assert len(response.json()) == 1
