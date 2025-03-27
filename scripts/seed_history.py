from datetime import UTC, datetime, timedelta
from random import randint

from sqlmodel import Session
from handlelistesystem.models import Item, setup_engine


def main():
    engine = setup_engine()
    now = datetime.now(UTC)
    current = now - timedelta(days=90)

    with Session(engine) as session:
        while current < now:
            item = Item(name='Item', is_purchased=True, purchased_at=current, created_at=now)
            current += timedelta(minutes=randint(0, 60 * 24 * 2))
            session.add(item)
        session.commit()


if __name__ == '__main__':
    main()
