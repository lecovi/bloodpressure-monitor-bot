#!/usr/bin/env python
import typer

from bloodpressure_monitor_bot.db.cli import app as db
from bloodpressure_monitor_bot.gapi.cli import app as gapi


app = typer.Typer()
app.add_typer(db, name="db")
app.add_typer(gapi, name="drive")


@app.command()
def main(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
