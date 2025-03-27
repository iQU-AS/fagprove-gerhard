from datetime import date
from typing import Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from handlelistesystem.models import setup_engine
from handlelistesystem.routers import history, index


def date_format(value: date | Any):
    if isinstance(value, date):
        return value.strftime('%d/%m-%Y')
    return value


def float_format(value: float | Any):
    if isinstance(value, float):
        return f'{value:.2f}'.replace('.', ',')
    return value


def create_app():
    app = FastAPI()

    app.mount('/static', StaticFiles(directory='handlelistesystem/static'), name='static')

    engine = setup_engine()

    templates = Jinja2Templates(directory='handlelistesystem/templates')

    templates.env.filters['date_format'] = date_format  # type: ignore
    templates.env.filters['float_format'] = float_format  # type: ignore

    app.include_router(index.create_router(engine, templates))
    app.include_router(history.create_router(engine, templates))

    return app


main = create_app()
