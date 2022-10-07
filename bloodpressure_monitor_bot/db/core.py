import os
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine


DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URI = f"postgresql://postgres:{DB_PASSWORD}@db:5432/postgres"


engine = create_engine(DB_URI)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    telegram_handler: str
    email: str = Field(nullable=False, index=True, unique=True)
    sheet_id: str
    last_conection: datetime = Field(default_factory=datetime.utcnow, nullable=False)