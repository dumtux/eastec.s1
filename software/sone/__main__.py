import asyncio
from multiprocessing import Process
import typer
import uvicorn


typer_app = typer.Typer()


@typer_app.command()
def device():
    'run local API server'
    from . import api_local

    def run_app():
        uvicorn.run(api_local.app, host='0.0.0.0', port=8000)

    def run_ws():
        asyncio.run(api_local.loop_ws_client("ws://localhost:8001/ws/0000"))

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
