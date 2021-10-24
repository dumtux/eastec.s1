from fastapi.testclient import TestClient

from .api import app


client = TestClient(app)


def test_websocket():
    # with client.websocket_connect("/ws/10101") as websocket:
    #     data = websocket.receive_json()
    #     assert data == {"msg": "Hello WebSocket"}
    pass


def test_get_sauna_list():
    response = client.get("/sauna/list")
    assert response.status_code == 200
    assert response.json() == []
