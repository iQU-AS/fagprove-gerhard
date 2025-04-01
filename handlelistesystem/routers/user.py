from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session

from handlelistesystem.dependencies.auth import (
    UserRedirectDependency,
    authenticate_user,
    create_access_token,
)
from handlelistesystem.helpers.flash import flash
from handlelistesystem.models import User, UserRole

RECENT_PURCHASES_DURATION = timedelta(hours=1)


class LoginForm(BaseModel):
    username: str
    password: str


def create_router(engine: Engine, templates: Jinja2Templates):  # noqa C901
    router = APIRouter(
        prefix='/user',
        dependencies=[Depends(UserRedirectDependency(engine))],
    )

    @router.get('/')
    def get_user(
        request: Request,
        user: Annotated[User, Depends(UserRedirectDependency(engine))],
    ):
        return templates.TemplateResponse('user.html.jinja', {'request': request, 'user': user})

    @router.get('/logout')
    def logout(request: Request):
        flash(request, 'You have been logged out.', 'success')
        response = RedirectResponse('/login')
        response.delete_cookie('access_token')
        return response

    @router.get('/delete')
    def delete_user(
        request: Request,
        user: Annotated[User, Depends(UserRedirectDependency(engine))],
    ):
        with Session(engine) as session:
            session.delete(user)
            session.commit()
        flash(request, 'User deleted successfully.', 'success')
        response = RedirectResponse('/login')
        response.delete_cookie('access_token')
        return response

    return router
