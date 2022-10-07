import typer
from rich import print
from sqlmodel import SQLModel

from .core import engine, DB_URI


app = typer.Typer()


@app.command()
def create():
    SQLModel.metadata.create_all(engine)
    print(f"Creating database :right_arrow: {DB_URI}")


@app.command()
def delete():
    SQLModel.metadata.drop_all(engine)
    print(f"Deleting database :right_arrow: {DB_URI}")
