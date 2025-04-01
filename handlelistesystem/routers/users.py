from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, delete, select

from handlelistesystem.dependencies.auth import UserRedirectDependency
from handlelistesystem.helpers.flash import flash
from handlelistesystem.models import User, UserRole


def create_router(engine: Engine, templates: Jinja2Templates):  # noqa C901
    router = APIRouter(
        prefix='/users',
        dependencies=[Depends(UserRedirectDependency(engine))],
    )

    @router.get('/me')
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

    @router.get('/{user_id}/delete')
    def delete_user(
        request: Request,
        user_id: int,
        current_user: Annotated[
            User, Depends(UserRedirectDependency(engine, role=UserRole.VIEWER))
        ],
    ):

        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            flash(request, 'Du har ikke tilgang til å slette denne brukeren.', 'error')
            return RedirectResponse(request.headers.get('referer', '/'))

        with Session(engine) as session:
            user = session.get(User, user_id)
            session.delete(user)
            session.commit()

        flash(request, 'Bruker slettet.', 'success')

        if user_id == current_user.id:
            response = RedirectResponse('/login')
            response.delete_cookie('access_token')
            return response
        return RedirectResponse(request.headers.get('referer', '/'))

    @router.get('/manage-users')
    def manage_users(
        request: Request,
        user: Annotated[User, Depends(UserRedirectDependency(engine, role=UserRole.ADMIN))],
    ):
        with Session(engine) as session:
            users = session.exec(select(User)).all()

        return templates.TemplateResponse(
            'manage_users.html.jinja',
            {
                'request': request,
                'users': users,
            },
        )

    return router
