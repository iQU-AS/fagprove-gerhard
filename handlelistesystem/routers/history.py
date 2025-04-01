from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from typing import cast
from fastapi import APIRouter, Depends, Request, Security
from fastapi.templating import Jinja2Templates
from sqlalchemy import Engine
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from handlelistesystem.dependencies.auth import get_user_redirect_dependency
from handlelistesystem.models import Item

RECENT_PURCHASES_LENGHT = timedelta(hours=5)


class Period(Enum):
    TODAY = 'today'
    THIS_WEEK = 'this-week'
    PREVIOUS_MONTH = 'previous-month'


def create_router(engine: Engine, templates: Jinja2Templates):  # noqa C901
    get_user_redirect = get_user_redirect_dependency(engine)

    router = APIRouter(prefix='/history', dependencies=[Security(get_user_redirect)])

    @router.get('/')
    def get_history_root(request: Request):
        return get_history(request, Period.TODAY)

    @router.get('/{period}')
    def get_history(request: Request, period: Period):
        now = datetime.now(UTC)

        if period == Period.TODAY:
            start = datetime(now.year, now.month, now.day, tzinfo=UTC)
            end = start + timedelta(days=1)
        elif period == Period.THIS_WEEK:
            start = now - timedelta(days=now.weekday())
            start = datetime(start.year, start.month, start.day, tzinfo=UTC)
            end = start + timedelta(weeks=1)
        elif period == Period.PREVIOUS_MONTH:
            start = datetime(now.year, now.month - 1, 1, tzinfo=UTC)
            end = start
            while end.month == start.month:
                end += timedelta(days=1)
            end = datetime(end.year, end.month, end.day, tzinfo=UTC)

        with Session(engine) as session:
            query = (
                select(Item)
                .options(  # to allow use in template
                    selectinload(Item.created_by_user), selectinload(Item.purchased_by_user)  # type: ignore
                )
                .where(Item.is_purchased)
                .where(col(Item.purchased_at) >= start)
                .where(col(Item.purchased_at) < end)
            )
            items = session.exec(query).all()

        # history contains dates mapped to items
        history = defaultdict[date, list[Item]](list)
        for item in items:
            date_ = cast(datetime, item.purchased_at).date()
            history[date_].append(item)

        # sort history
        for items in history.values():
            items.sort(key=lambda item: cast(datetime, item.purchased_at), reverse=True)
        history = dict(sorted(history.items(), key=lambda item: item[0], reverse=True))

        return templates.TemplateResponse(
            'history.html.jinja',
            {
                'request': request,
                'history': history,
                'period': period.value,
            },
        )

    return router
