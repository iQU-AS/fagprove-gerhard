from datetime import UTC, datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import Engine
from sqlmodel import Session, col, not_, select

from handlelistesystem.models import Item

RECENT_PURCHASES_LENGHT = timedelta(hours=1)


def create_router(engine: Engine, templates: Jinja2Templates):
    router = APIRouter(prefix='')

    @router.get('/')
    def get_grocery_list(request: Request):
        now = datetime.now(UTC)
        print(now + timedelta(hours=1))

        with Session(engine) as session:
            query = select(Item).where(not_(Item.is_purchased))
            items = session.exec(query).all()

            query = (
                select(Item)
                .where(Item.is_purchased)
                .where(col(Item.purchased_at) > now - RECENT_PURCHASES_LENGHT)
            )
            recent_purchases = session.exec(query).all()

        return templates.TemplateResponse(
            'index.html.jinja',
            {
                'request': request,
                'items': items,
                'recent_purchases': recent_purchases,
            },
        )

    return router
