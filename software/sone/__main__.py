import asyncio
import json
from multiprocessing import Process

import httpx
import typer
import uvicorn
import websockets

from .utils import get_sauna_id


LOCAL_HOST = '0.0.0.0'
LOCAL_PORT = 8000
CLOUD_HOST = '0.0.0.0'
CLOUD_PORT = 8001

typer_app = typer.Typer()


async def loop_ws_client(host: str, port: int):
    sauna_id = get_sauna_id()
    url = "ws://%s:%d/ws/%s" % (host, port, sauna_id)
    async with httpx.AsyncClient() as client:
        async with websockets.connect(url) as ws:
            while True:
                req = await ws.recv()
                req = json.loads(req)
                print(req)
                req = client.build_request(
                    req['method'],
                    f"http://{LOCAL_HOST}:{LOCAL_PORT}{req['path']}",
                    json=req['body'])
                res = await client.send(req)
                await ws.send(json.dumps(res.json()))


@typer_app.command()
def device():
    'run local API server'
    from . import api_local

    def run_app():
        uvicorn.run(api_local.app, host=LOCAL_HOST, port=LOCAL_PORT)

    def run_ws():
        asyncio.run(loop_ws_client(CLOUD_HOST, CLOUD_PORT))

    ws_app = Process(target = run_app)
    ws_proc = Process(target = run_ws)
    ws_app.start()
    ws_proc.start()
    ws_app.join()
    ws_proc.join()


@typer_app.command()
def cloud():
    'run cloud API server'
    from . import api
    uvicorn.run(api.app, host='0.0.0.0', port=8001)


typer_app()
