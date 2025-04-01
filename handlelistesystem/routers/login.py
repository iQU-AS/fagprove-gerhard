from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Engine

from handlelistesystem.dependencies.auth import authenticate_user, create_access_token
from handlelistesystem.helpers.flash import flash

RECENT_PURCHASES_DURATION = timedelta(hours=1)


class LoginForm(BaseModel):
    username: str
    password: str


def create_router(engine: Engine, templates: Jinja2Templates):  # noqa C901
    router = APIRouter(prefix='/login')

    @router.get('/')
    def get_login(request: Request):
        return templates.TemplateResponse('login.html.jinja', {'request': request})

    @router.post('/')
    def post_login(request: Request, login_form: Annotated[LoginForm, Form(...)]):
        user = authenticate_user(
            engine,
            username=login_form.username,
            password=login_form.password,
        )

        if not user:
            flash(
                request,
                'Feil brukernavn eller passord',
            )
            return templates.TemplateResponse(
                'login.html.jinja',
                {
                    'request': request,
                },
            )
        assert user.id is not None

        response = RedirectResponse(url='/', status_code=303)

        access_token = create_access_token(
            user_id=user.id,
        )
        response.set_cookie(key='access_token', value=access_token, expires='Session')

        return response

    return router
