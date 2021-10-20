from fastapi.testclient import TestClient

from .api import app


client = TestClient(app)


def test_ping():
    response = client.get("/sauna/ping")
    assert response.status_code == 200
    assert 'sauna_id' in response.json().keys()
    assert 'model_name' in response.json().keys()
