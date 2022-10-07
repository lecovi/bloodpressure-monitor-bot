#!/usr/bin/env python
import typer

from bloodpressure_monitor_bot.db.cli import app as db_cli


app = typer.Typer()
app.add_typer(db_cli, name="db")


@app.command()
def main(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
