from datetime import date
import locale
from typing import Any
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from handlelistesystem.config import SECRET_KEY
from handlelistesystem.helpers.flash import get_flashed_messages
from handlelistesystem.models import setup_engine
from handlelistesystem.routers import history, index, login


def date_format(value: date | Any):
    if isinstance(value, date):
        weekday = value.strftime('%A')
        date_ = value.strftime('%d')
        month_abbreviated = value.strftime('%b').rstrip('.')
        year = value.strftime('%Y')
        return f'{weekday}, {date_}. {month_abbreviated}, {year}'
    return value


def float_format(value: float | Any):
    if isinstance(value, float):
        return f'{value:.2f}'.replace('.', ',')
    return value


def create_app():
    # Application uses Norwegian locale
    locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

    app.mount('/static', StaticFiles(directory='handlelistesystem/static'), name='static')

    engine = setup_engine()

    templates = Jinja2Templates(directory='handlelistesystem/templates')

    templates.env.filters['date_format'] = date_format  # type: ignore
    templates.env.filters['float_format'] = float_format  # type: ignore
    templates.env.globals['get_flashed_messages'] = get_flashed_messages  # type: ignore

    app.include_router(index.create_router(engine, templates))
    app.include_router(history.create_router(engine, templates))
    app.include_router(login.create_router(engine, templates))

    return app


main = create_app()
