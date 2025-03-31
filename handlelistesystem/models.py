from datetime import UTC, datetime
from typing import Annotated
from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine

from handlelistesystem.config import SQLITE_DB


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)


def setup_engine():
    sqlite_url = f'sqlite:///{SQLITE_DB}'

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
    updated_at: Annotated[
        datetime,
        Field(
            default_factory=lambda: datetime.now(UTC),
            sa_column_kwargs={'onupdate': lambda: datetime.now(UTC)},
        ),
    ]
