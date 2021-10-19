import typer
import uvicorn

from .app import create_app


typer_app = typer.Typer()


@typer_app.command()
def server():
    'run API server'
    api_app = create_app(client_mode=False)
    uvicorn.run(api_app)


typer_app()
