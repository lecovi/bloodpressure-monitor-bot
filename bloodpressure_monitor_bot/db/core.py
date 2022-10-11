import os
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select


DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URI = f"postgresql://postgres:{DB_PASSWORD}@db:5432/postgres"


engine = create_engine(DB_URI)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tg_id: int = Field(index=True, unique=True)
    tg_username: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    gsheet_id: str
    last_conection: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    @classmethod
    def add(cls, **kwargs):
        user = cls(**kwargs)
        with Session(engine) as session:
            session.add(user)
            session.commit()
        return user

    @classmethod
    def get(cls, id):
        with Session(engine) as session:
            user = session.get(cls, id)
        return user

    @classmethod
    def get_by_tg_username(cls, tg_username):
        # FIXME: evolve this to use **kwargs
        with Session(engine) as session:
            statement = select(cls).where(cls.tg_username == tg_username)
            user = session.exec(statement).first()
        return user

    @classmethod
    def get_by_tg_id(cls, tg_id):
        # FIXME: evolve this to use **kwargs
        with Session(engine) as session:
            statement = select(cls).where(cls.tg_id == tg_id)
            user = session.exec(statement).first()
        return user

    @classmethod
    def get_all(cls):
        with Session(engine) as session:
            statement = select(cls)
            users = session.exec(statement).all()
        return users

    def update(self, **kwargs):
        if kwargs.get("tg_id") is not None:
            self.tg_id = kwargs.get("tg_id")
        if kwargs.get("tg_username") is not None:
            self.tg_username = kwargs.get("tg_username")
        if kwargs.get("email") is not None:
            self.email = kwargs.get("email")
        if kwargs.get("gsheet_id") is not None:
            self.gsheet_id = kwargs.get("gsheet_id")
        
        with Session(engine) as session:
            session.add(self)
            session.commit()

    def delete(self):
        with Session(engine) as session:
            session.delete(self)
            session.commit()
