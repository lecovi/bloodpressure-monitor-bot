import typer
from rich import print
from sqlmodel import SQLModel, Session, select

from .core import engine, DB_URI, User


app = typer.Typer()
users = typer.Typer()
app.add_typer(users, name="user")


@app.command()
def create():
    SQLModel.metadata.create_all(engine)
    print(f"Creating database :right_arrow: {DB_URI}")


@app.command()
def delete():
    SQLModel.metadata.drop_all(engine)
    print(f"Deleting database :right_arrow: {DB_URI}")


@users.command()
def add(name=None, telegram_handler=None, email=None, sheet_id=None):
    user = User(name=name, telegram_handler=telegram_handler, email=email, sheet_id=sheet_id)
    with Session(engine) as session:
        session.add(user)
        session.commit()
    print(user)


@users.command()
def get(id):
    with Session(engine) as session:
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
    print(user)


@users.command()
def get_all():
    with Session(engine) as session:
        statement = select(User)
        users = session.exec(statement)
        for user in users:
            print(user)


@users.command()
def update(id, name=None, telegram_handler=None, email=None, sheet_id=None):
    with Session(engine) as session:
        # Get the user
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
        if user is None:
            print(":confused_face: User does not exists!")
            return 

        # Update values
        if name is not None:
            user.name = name
        if telegram_handler is not None:
            user.telegram_handler = telegram_handler
        if email is not None:
            user.email = email
        if sheet_id is not None:
            user.sheet_id = sheet_id

        # Save to DB
        session.add(user)
        session.commit()

        print(user)


@users.command()
def delete(id):
    with Session(engine) as session:
        # Get the user
        statement = select(User).where(User.id == id)
        user = session.exec(statement).first()
        if user is None:
            print(":confused_face: User does not exists!")
            return 

        session.delete(user)
        session.commit()

    print(f":wastebasket: Deleted user", user)