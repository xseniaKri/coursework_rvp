from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import Role
from app.models.user import User
from app.repositories.structure_unit import StructureUnitRepository
from app.repositories.user import UserRepository
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _require_admin(current_user: User) -> None:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    _require_admin(current_user)
    users = await UserRepository(session).get_all()
    structure_units = await StructureUnitRepository(session).get_all()
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "current_user": current_user,
        "users": users,
        "structure_units": structure_units,
        "roles": list(Role),
    })
