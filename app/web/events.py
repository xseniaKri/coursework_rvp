from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import Role
from app.core.permissions import (
    allowed_statuses,
    can_assign_responsible,
    can_create_event,
    can_delete_event,
    can_edit_event,
)
from app.models.enums import EventStatus
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.web.dependencies import get_current_user_from_cookie
from app.web.templates import templates

router = APIRouter()


@router.get("/events", response_class=HTMLResponse)
async def events_list(
    request: Request,
    search: str = "",
    status: str = "",
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role == Role.ADMIN:
        return RedirectResponse(url="/admin", status_code=302)
    status_filter = EventStatus(status) if status else None
    events = await EventRepository(session).get_all(
        status=status_filter,
        search=search or None,
    )

    editable_ids = {e.id for e in events if can_edit_event(current_user, e)}
    can_delete = can_delete_event(current_user)

    return templates.TemplateResponse("events/list.html", {
        "request": request,
        "events": events,
        "current_user": current_user,
        "search": search,
        "status_filter": status,
        "statuses": list(EventStatus),
        "can_create": can_create_event(current_user),
        "editable_ids": editable_ids,
        "can_delete": can_delete,
    })


@router.get("/events/create", response_class=HTMLResponse)
async def event_create_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role == Role.ADMIN:
        return RedirectResponse(url="/admin", status_code=302)
    if not can_create_event(current_user):
        return HTMLResponse("Нет доступа", status_code=403)

    categories = await CategoryRepository(session).get_all()
    users = await UserRepository(session).get_all()
    return templates.TemplateResponse("events/card.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "users": users,
        "event": None,
        "can_assign_responsible": can_assign_responsible(current_user),
    })


@router.get("/events/{event_id}", response_class=HTMLResponse)
async def event_view(
    event_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role == Role.ADMIN:
        return RedirectResponse(url="/admin", status_code=302)
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        return HTMLResponse("Мероприятие не найдено", status_code=404)

    return templates.TemplateResponse("events/view.html", {
        "request": request,
        "event": event,
        "current_user": current_user,
        "can_edit": can_edit_event(current_user, event),
        "allowed_statuses": allowed_statuses(current_user, event),
    })


@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
async def event_edit_page(
    event_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role == Role.ADMIN:
        return RedirectResponse(url="/admin", status_code=302)
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        return HTMLResponse("Мероприятие не найдено", status_code=404)

    if not can_edit_event(current_user, event):
        return HTMLResponse("Нет доступа", status_code=403)

    categories = await CategoryRepository(session).get_all()
    users = await UserRepository(session).get_all()
    return templates.TemplateResponse("events/card.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "users": users,
        "event": event,
        "can_assign_responsible": can_assign_responsible(current_user),
    })
