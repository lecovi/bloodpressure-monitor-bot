import os
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select


DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URI = f"postgresql://postgres:{DB_PASSWORD}@db:5432/postgres"


engine = create_engine(DB_URI)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    telegram_handler: str
    email: str = Field(index=True, unique=True)
    sheet_id: str
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
            statement = select(cls).where(cls.id == id)
            user = session.exec(statement).first()
        return user

    @classmethod
    def get_all(cls):
        with Session(engine) as session:
            statement = select(cls)
            users = session.exec(statement).all()
        return users

    def update(self, **kwargs):
        if kwargs.get("name") is not None:
            self.name = kwargs.get("name")
        if kwargs.get("telegram_handler") is not None:
            self.telegram_handler = kwargs.get("telegram_handler")
        if kwargs.get("email") is not None:
            self.email = kwargs.get("email")
        if kwargs.get("sheet_id") is not None:
            self.sheet_id = kwargs.get("sheet_id")
        
        with Session(engine) as session:
            session.add(self)
            session.commit()

    def delete(self):
        with Session(engine) as session:
            session.delete(self)
            session.commit()
