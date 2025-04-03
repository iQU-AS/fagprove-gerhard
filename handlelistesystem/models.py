from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Optional
import logging
import bcrypt
from sqlalchemy import Engine
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine, select, text

from handlelistesystem.config import SQLITE_DB

logger = logging.getLogger(__name__)


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        # Enable foreign key constraints
        connection.execute(text('PRAGMA foreign_keys=ON'))

    # Create the initial user if no user exists
    with Session(engine) as session:
        initial_user = session.exec(select(User)).first()
        if not initial_user:
            password = b'admin'
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode()

            initial_user = User(
                username='admin',
                password=hashed_password,
                role=UserRole.ADMIN,
            )
            session.add(initial_user)
            session.commit()
            logger.info('Created inital admin user...')


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

    created_by_user_id: Annotated[
        int | None,
        Field(foreign_key='user.id', ondelete='SET NULL'),
    ] = None
    created_by_user: Optional['User'] = Relationship(
        back_populates='created_items',
        sa_relationship_kwargs={'foreign_keys': '[Item.created_by_user_id]'},
    )

    purchased_by_user_id: Annotated[
        int | None,
        Field(foreign_key='user.id', ondelete='SET NULL'),
    ] = None
    purchased_by_user: Optional['User'] = Relationship(
        back_populates='purchased_items',
        sa_relationship_kwargs={'foreign_keys': '[Item.purchased_by_user_id]'},
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={'onupdate': lambda: datetime.now(UTC)},
    )


class UserRole(Enum):
    # least privileged to most privileged
    VIEWER = 'viewer'
    MEMBER = 'member'
    ADMIN = 'admin'

    def __lt__(self, other: 'UserRole') -> bool:
        """Allows comparison of UserRole instances."""
        if not isinstance(other, UserRole):  # type: ignore # failsafe
            return NotImplemented
        if self == other:
            return False
        self_index = list(UserRole).index(self)
        other_index = list(UserRole).index(other)
        return self_index < other_index


class User(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    username: Annotated[str, Field(index=True, unique=True)]
    password: str

    role: UserRole

    created_items: list[Item] = Relationship(
        back_populates='created_by_user',
        passive_deletes='all',
        sa_relationship_kwargs={'foreign_keys': '[Item.created_by_user_id]'},
    )

    purchased_items: list[Item] = Relationship(
        back_populates='purchased_by_user',
        passive_deletes='all',
        sa_relationship_kwargs={'foreign_keys': '[Item.purchased_by_user_id]'},
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={'onupdate': lambda: datetime.now(UTC)},
    )
