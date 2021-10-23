from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from . import __title__, __version__
from .singletone import Singleton


class ConnectionStore(Singleton):

    connections: Dict[str, WebSocket] = dict()

    async def connect(self, device_id: str, ws: WebSocket) -> None:
        await ws.accept()
        if device_id in self.connections:
            raise Exception("Device ID already exists")
        self.connections[device_id] = ws

    def disconnect(self, device_id: str) -> None:
        self.connections.pop(device_id)

    async def send_to(self, message: str, device_id: str) -> None:
        await self.connections[device_id].send_text(message)

    async def send_to_all(self, message: str) -> None:
        for device_id, ws in self.connections:
            await connection.send_text(message)

    def get_device_ids(self) -> List[str]:
        return list(self.connections.keys())


store = ConnectionStore.instance()
app = FastAPI(
    title=__title__,
    version=__version__,
    description="REST API for sauna status fetching and control")


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(ws: WebSocket, device_id: int):
    await store.connect(device_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            await store.send_to(f"Got this from SOne: {data}", device_id)
    except WebSocketDisconnect:
        store.disconnect(device_id)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
