from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import Role
from app.models.user import User
from app.repositories.event import EventRepository
from app.web.dependencies import get_current_user_from_cookie
from app.web.templates import templates

router = APIRouter()


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role == Role.ADMIN:
        return RedirectResponse(url="/admin", status_code=302)
    completed_count = await EventRepository(session).count_completed()
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "current_user": current_user,
        "completed_count": completed_count,
    })
