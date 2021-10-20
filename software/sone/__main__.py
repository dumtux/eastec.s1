import typer
import uvicorn

from .api import app as api_app


typer_app = typer.Typer()


@typer_app.command()
def server():
    'run API server'
    uvicorn.run(api_app)


typer_app()
