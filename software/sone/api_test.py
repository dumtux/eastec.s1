from fastapi.testclient import TestClient

from .api import app
from .sone import SOne


client = TestClient(app)


def test_ping():
    response = client.get("/sauna/ping")
    assert response.status_code == 200
    assert 'sauna_id' in response.json().keys()
    assert 'model_name' in response.json().keys()


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

    response = client.put("/sauna/%s/state" % sauna_id, data={"state": "playing"})
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()


def test_update_target_temperature():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.put("/sauna/%s/temperature" % sauna_id, data={"target_termperature": 50})
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()


def test_update_timer():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.put("/sauna/%s/timer" % sauna_id, data={"timer": 30})
    assert response.status_code == 200
    assert response.json() == SOne.instance().status.serialize()


def test_get_schedules():
    response = client.get("/sauna/ping")
    sauna_id = response.json().get("sauna_id")

    response = client.get("/sauna/%s/schedules" % sauna_id)
    assert response.status_code == 200
    assert response.json() == [s.serialize() for s in SOne.instance().schedules]
