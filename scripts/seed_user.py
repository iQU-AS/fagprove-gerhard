import bcrypt
from sqlmodel import Session
from handlelistesystem.models import User, setup_engine


def main():
    engine = setup_engine()

    with Session(engine) as session:
        password = b'gerhard'
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        user = User(username='gerhard', password=hashed.decode())
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f'User created with ID: {user.id}')


if __name__ == '__main__':
    main()
