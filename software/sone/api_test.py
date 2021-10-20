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
