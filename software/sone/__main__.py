import typer
import uvicorn

from .bt_app import create_app


app = typer.Typer()


@app.command()
def server():
    'with BlueDot server running'
    bt_app = create_app(client_mode=False)
    uvicorn.run(bt_app)


@app.command()
def client():
    'with BlueDot client running, to be used by develoepr debugging'
    bt_app = create_app(client_mode=True)
    uvicorn.run(bt_app)


app()
