from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.repositories.event import EventRepository
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    events_this_month = await EventRepository(session).count_this_month()
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "current_user": current_user,
        "events_this_month": events_this_month,
    })
