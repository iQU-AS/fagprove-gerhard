from datetime import UTC, datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, not_, select

from handlelistesystem.dependencies.auth import UserRedirectDependency
from handlelistesystem.models import Item, User, UserRole

RECENT_PURCHASES_DURATION = timedelta(hours=1)


class ItemId(BaseModel):
    id: int


def create_router(engine: Engine, templates: Jinja2Templates):  # noqa C901
    router = APIRouter(
        prefix='', dependencies=[Depends(UserRedirectDependency(engine, role=UserRole.VIEWER))]
    )

    @router.get('/')
    def get_grocery_list(request: Request):
        now = datetime.now(UTC)

        print(request.session.pop('flash_error', 'no'))

        with Session(engine) as session:
            query = (
                select(Item)
                .options(  # to allow use in template
                    selectinload(Item.created_by_user), selectinload(Item.purchased_by_user)  # type: ignore
                )
                .where(not_(Item.is_purchased))
                .order_by(col(Item.updated_at))
            )
            items = session.exec(query).all()

            query = (
                select(Item)
                .options(  # to allow use in template
                    selectinload(Item.created_by_user), selectinload(Item.purchased_by_user)  # type: ignore
                )
                .where(Item.is_purchased)
                .where(col(Item.purchased_at) > now - RECENT_PURCHASES_DURATION)
                .order_by(col(Item.updated_at))
            )
            recent_purchases = session.exec(query).all()

            # load user for items and recent_purchases

        return templates.TemplateResponse(
            'index.html.jinja',
            {
                'request': request,
                'items': items,
                'recent_purchases': recent_purchases,
            },
        )

    @router.post('/add')
    def add_item(
        user: Annotated[User, Depends(UserRedirectDependency(engine, role=UserRole.MEMBER))],
        name: Annotated[str, Form(...)],
    ):
        with Session(engine) as session:
            item = Item(name=name, created_by_user=user)
            session.add(item)
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    @router.post('/purchase')
    def purchase_item(
        user: Annotated[User, Depends(UserRedirectDependency(engine, role=UserRole.MEMBER))],
        item_id: Annotated[ItemId, Form()],
    ):
        with Session(engine) as session:
            item = session.get(Item, item_id.id)
            if item is None:
                return RedirectResponse(url='/', status_code=303)

            item.is_purchased = True
            item.purchased_by_user = user
            item.purchased_at = datetime.now(UTC)
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    @router.post(
        '/unpurchase', dependencies=[Depends(UserRedirectDependency(engine, role=UserRole.MEMBER))]
    )
    def unpurchase_item(item_id: Annotated[ItemId, Form()]):
        with Session(engine) as session:
            item = session.get(Item, item_id.id)
            if item is None:
                return RedirectResponse(url='/', status_code=303)

            item.is_purchased = False
            item.purchased_by_user_id = None
            item.purchased_at = None
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    @router.get(
        '/delete/{item_id}',
        dependencies=[Depends(UserRedirectDependency(engine, role=UserRole.MEMBER))],
    )
    def delete_item(item_id: int):
        with Session(engine) as session:
            item = session.get(Item, item_id)
            if item is None:
                return RedirectResponse(url='/', status_code=303)

            session.delete(item)
            session.commit()

        return RedirectResponse(url='/', status_code=303)

    return router
