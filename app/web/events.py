from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import EventStatus
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/events", response_class=HTMLResponse)
async def events_list(
    request: Request,
    search: str = "",
    status: str = "",
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    status_filter = EventStatus(status) if status else None
    events = await EventRepository(session).get_all(
        status=status_filter,
        search=search or None,
    )
    return templates.TemplateResponse("events/list.html", {
        "request": request,
        "events": events,
        "current_user": current_user,
        "search": search,
        "status_filter": status,
        "statuses": list(EventStatus),
    })


@router.get("/events/create", response_class=HTMLResponse)
async def event_create_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    categories = await CategoryRepository(session).get_all()
    users = await UserRepository(session).get_all()
    return templates.TemplateResponse("events/card.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "users": users,
        "event": None,
    })


@router.get("/events/{event_id}", response_class=HTMLResponse)
async def event_view(
    event_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        return HTMLResponse("Мероприятие не найдено", status_code=404)
    return templates.TemplateResponse("events/view.html", {
        "request": request,
        "event": event,
        "current_user": current_user,
        "statuses": list(EventStatus),
    })


@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
async def event_edit_page(
    event_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        return HTMLResponse("Мероприятие не найдено", status_code=404)
    categories = await CategoryRepository(session).get_all()
    users = await UserRepository(session).get_all()
    return templates.TemplateResponse("events/card.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "users": users,
        "event": event,
    })
