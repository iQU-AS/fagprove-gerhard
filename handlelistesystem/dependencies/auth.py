from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi.security import SecurityScopes
import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy import Engine
from sqlmodel import Session, select

from handlelistesystem.config import SECRET_KEY
from handlelistesystem.models import User, UserRole

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_DURATION = timedelta(minutes=30)


def authenticate_user(engine: Engine, username: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return False
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return False
    return user


def create_access_token(user_id: int, expire_duration: timedelta = ACCESS_TOKEN_EXPIRE_DURATION):
    exp = datetime.now(UTC) + expire_duration
    return jwt.encode({'sub': str(user_id), 'exp': exp}, SECRET_KEY, algorithm=ALGORITHM)


def get_access_token(request: Request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(' ')[1]

    return request.cookies.get('access_token')


def get_user_dependency(engine: Engine):
    def get_user(role: UserRole, token: Annotated[str, Depends(get_access_token)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get('sub')
        except InvalidTokenError as e:
            print('mhmm')
            raise credentials_exception from e

        print(user_id)

        with Session(engine) as session:
            user = session.get(User, user_id)
        if user is None:
            raise credentials_exception

        if user.role < role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not enough permissions',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return user

    return get_user


def get_user_redirect_dependency(engine: Engine):
    get_current_user = get_user_dependency(engine)

    def get_user_redirect(role: UserRole, token: Annotated[str, Depends(get_access_token)]):
        print(token)
        try:
            user = get_current_user(role, token)
        except HTTPException as e:
            raise HTTPException(
                status_code=303,
                headers={'Location': '/login'},
                detail=e.detail,
            ) from e
        return user

    return get_user_redirect
