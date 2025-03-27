from datetime import UTC, datetime
from typing import Annotated
from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)


def setup_engine():
    sqlite_file_name = 'database.db'
    sqlite_url = f'sqlite:///{sqlite_file_name}'

    connect_args = {'check_same_thread': False}
    engine = create_engine(sqlite_url, connect_args=connect_args)

    create_db_and_tables(engine)

    return engine


class Item(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    name: str
    is_purchased: Annotated[bool, Field(index=True)] = False
    purchased_at: Annotated[datetime | None, Field(index=True)] = None
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(UTC))]
