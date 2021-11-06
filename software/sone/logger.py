import typer

from .singletone import Singleton


class Logger(Singleton):

    def log(self, text: str):
        tag = typer.style(" [SOne] ", bold=True, bg=typer.colors.GREEN, fg=typer.colors.WHITE)
        typer.secho(tag + " " + text)

    def error(self, text: str):
        tag = typer.style(" [SOne] ", bold=True, bg=typer.colors.RED, fg=typer.colors.WHITE)
        typer.secho(tag + " " + text)

    def warn(self, text: str):
        tag = typer.style(" [SOne] ", bold=True, bg=typer.colors.YELLOW, fg=typer.colors.WHITE)
        typer.secho(tag + " " + text)
