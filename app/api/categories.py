from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.event import CategoryResponse
from app.schemas.base import BaseSchema

router = APIRouter(dependencies=[Depends(get_current_user)])


class CategoryCreate(BaseSchema):
    name: str


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    session: AsyncSession = Depends(get_db),
) -> list[Category]:
    return await CategoryRepository(session).get_all()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_db),
) -> Category:
    cat = await CategoryRepository(session).create(name=data.name)
    await session.commit()
    return cat
