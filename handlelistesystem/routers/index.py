from datetime import UTC, datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, col, not_, select

from handlelistesystem.models import Item

RECENT_PURCHASES_LENGHT = timedelta(hours=5)


class ItemId(BaseModel):
    id: int


def create_router(engine: Engine, templates: Jinja2Templates):  # noqa C901
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

    @router.post('/add')
    def add_item(name: str = Form(...)):
        with Session(engine) as session:
            item = Item.model_validate({'name': name})
            session.add(item)
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    @router.post('/purchase')
    def purchase_item(item_id: Annotated[ItemId, Form()]):
        with Session(engine) as session:
            item = session.get(Item, item_id.id)
            if item is None:
                return RedirectResponse(url='/', status_code=303)

            item.is_purchased = True
            item.purchased_at = datetime.now(UTC)
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    @router.post('/unpurchase')
    def unpurchase_item(item_id: Annotated[ItemId, Form()]):
        with Session(engine) as session:
            item = session.get(Item, item_id.id)
            if item is None:
                return RedirectResponse(url='/', status_code=303)

            item.is_purchased = False
            item.purchased_at = None
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    @router.get('/delete/{item_id}')
    def delete_item(item_id: int):
        with Session(engine) as session:
            item = session.get(Item, item_id)
            if item is None:
                return RedirectResponse(url='/', status_code=303)

            session.delete(item)
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    return router
