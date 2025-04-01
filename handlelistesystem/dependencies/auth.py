from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy import Engine
from sqlmodel import Session, select

from handlelistesystem.config import SECRET_KEY
from handlelistesystem.helpers.flash import flash
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


class UserDependency:
    def __init__(self, engine: Engine, *, role: UserRole):
        self.engine = engine
        self.role = role

    def __call__(self, token: Annotated[str, Depends(get_access_token)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get('sub')
        except InvalidTokenError as e:
            raise credentials_exception from e

        with Session(self.engine) as session:
            user = session.get(User, user_id)
        if user is None:
            raise credentials_exception

        if user.role < self.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not enough permissions',
            )

        return user


class UserRedirectDependency:
    def __init__(self, engine: Engine, *, role: UserRole = UserRole.VIEWER):
        self.engine = engine
        self.role = role
        self.user_dependency = UserDependency(engine, role=role)

    def __call__(self, request: Request, token: Annotated[str, Depends(get_access_token)]):
        try:
            user = self.user_dependency(token)
        except HTTPException as e:
            if e.status_code == status.HTTP_403_FORBIDDEN:
                flash(request, 'Du har ikke tilgang')
                raise HTTPException(
                    status_code=status.HTTP_303_SEE_OTHER,
                    headers={'Location': request.headers.get('referer', '/')},
                ) from e
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={'Location': '/login'},
            ) from e
        return user
