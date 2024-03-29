import typer
from rich import print
from sqlmodel import SQLModel, Session, select

from .core import engine, DB_URI, User


app = typer.Typer()
users = typer.Typer()
app.add_typer(users, name="user", help="Manage User records")


@app.command()
def create():
    "Creates database schema"
    SQLModel.metadata.create_all(engine)
    print(f"Creating database :right_arrow: {DB_URI}")


@app.command()
def drop():
    "Drops database schema"
    SQLModel.metadata.drop_all(engine)
    print(f":wastebasket: Deleting database :right_arrow: {DB_URI}")


@users.command()
def add(tg_id=None, tg_username=None, email=None, gsheet_id=None):
    "Adds a new User record into DB"
    user = User.add(
        tg_id=tg_id,
        tg_username=tg_username,
        email=email,
        gsheet_id=gsheet_id
    )
    print(user)


@users.command()
def get(id):
    "Get user with the given ID"
    user = User.get(id)
    print(user)


@users.command()
def get_all():
    "Get all users in DB"
    users = User.get_all()
    print(users)
    print(f"Total {len(users)} users")


@users.command()
def update(id, tg_id=None, tg_username=None, email=None, gsheet_id=None):
    "Updates user with the given ID"

    user = User.get(id)
    if user is None:
        print(":confused_face: User does not exists!")
        return 

    user.update(
        tg_id=tg_id,
        tg_username=tg_username,
        gsheet_id=gsheet_id,
        email=email,
    )

    print(user)


@users.command()
def delete(id):
    "Removes user with the given ID from DB"
    user = User.get(id)
    if user is None:
        print(":confused_face: User does not exists!")
        return 

    user.delete()

    print(f":wastebasket: Deleted user", user)