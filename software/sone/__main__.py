import asyncio
import json
from multiprocessing import Process
import socket
try:
    from asyncio.exceptions import TimeoutError
except:
    # for Python 3.7 of Raspberry OS
    from concurrent.futures._base import TimeoutError

import httpx
import typer
import uvicorn
import websockets

from .logger import Logger
from .utils import get_sauna_id


LOCAL_HOST = '0.0.0.0'
LOCAL_PORT = 8002
CLOUD_HOST = '0.0.0.0'
CLOUD_PORT = 8001

typer_app = typer.Typer()
logger = Logger.instance()


async def loop_ws_client(cloud_url: str):
    sauna_id = get_sauna_id()
    if cloud_url is None:
        url = "ws://%s:%d/ws/%s" % (CLOUD_HOST, CLOUD_PORT, sauna_id)
    else:
        if cloud_url.endswith('/'):
            cloud_url = cloud_url[:-1]
        url = f"ws{cloud_url[4:]}/ws/{sauna_id}"
        logger.log(f"Connecting to {url}")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                async with websockets.connect(url) as ws:
                    logger.log("websocket connected")
                    while True:
                        req = await ws.recv()
                        req = json.loads(req)
                        logger.log(req)
                        req = client.build_request(
                            req['method'],
                            f"http://{LOCAL_HOST}:{LOCAL_PORT}{req['path']}",
                            json=req['body'])
                        res = await client.send(req)
                        await ws.send(json.dumps({"status_code": res.status_code, "body": res.json()}))
            except websockets.exceptions.InvalidStatusCode:
                logger.error("Invalid server response for websocket, check Cloud URL and networking. Retrying in 5 seconds.")
            except socket.gaierror:
                logger.warn("Name or service not known, check Cloud URL and networking. Retrying in 5 seconds.")
            except ConnectionRefusedError:
                logger.warn("Connect call failed, check Cloud URL and networking. Retrying in 5 seconds.")
            except TimeoutError:
                logger.error("Timeout error, check Cloud URL and networking. Retrying in 5 seconds.")
            except websockets.exceptions.ConnectionClosedError:
                logger.error("Connection closed, check Cloud URL and networking. Retrying in 5 seconds.")

            await asyncio.sleep(5)


@typer_app.command()
def device(cloud_url=None):
    'run local API server'
    from . import api_local

    def run_app():
        uvicorn.run(api_local.app, host=LOCAL_HOST, port=LOCAL_PORT)

    def run_ws():
        try:
            asyncio.run(loop_ws_client(cloud_url))
        except KeyboardInterrupt:
            logger.log("Stopping by the user.")

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
