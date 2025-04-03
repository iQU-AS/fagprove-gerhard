from datetime import UTC, datetime, timedelta
import random

from sqlmodel import Session
from handlelistesystem.models import Item, setup_engine

items = [
    'Melk',
    'Brød',
    'Egg',
    'Smør',
    'Ost',
    'Kylling',
    'Fisk',
    'Ris',
    'Pasta',
    'Kjøttdeig',
    'Poteter',
    'Gulrøtter',
    'Løk',
    'Paprika',
    'Agurk',
    'Tomater',
    'Epler',
    'Bananer',
    'Appelsiner',
    'Druer',
    'Jordbær',
    'Blåbær',
    'Bringebær',
    'Kirsebær',
    'Vann',
    'Brus',
    'Kaffe',
]


def main():
    engine = setup_engine()
    now = datetime.now(UTC)
    current = now - timedelta(days=90)

    with Session(engine) as session:
        while current < now:
            item = Item(
                name=random.choice(items),
                is_purchased=True,
                purchased_at=current,
                purchased_by_user_id=1,
                created_by_user_id=1,
            )
            current += timedelta(minutes=random.randint(0, 60 * 24 * 2))
            session.add(item)
        session.commit()


if __name__ == '__main__':
    main()
