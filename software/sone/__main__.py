import typer
import uvicorn


typer_app = typer.Typer()


@typer_app.command()
def device():
    'run local API server'
    from . import api_local
    uvicorn.run(api_local.app, host='0.0.0.0', port=8000)


@typer_app.command()
def cloud():
    'run cloud API server'
    from . import api
    uvicorn.run(api.app, host='0.0.0.0', port=8001)


typer_app()
