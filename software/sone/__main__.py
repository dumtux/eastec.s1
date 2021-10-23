import typer
import uvicorn

from . import ksix


typer_app = typer.Typer()


@typer_app.command()
def server():
    'run API server'
    uvicorn.run(ksix.app, host='0.0.0.0', port=8000)


typer_app()
