from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_roles_flexible
from app.core.database import get_db
from app.core.security import hash_password
from app.models.enums import Role
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()

_admin_only = [Depends(require_roles_flexible([Role.ADMIN]))]


@router.get("", response_model=list[UserResponse], dependencies=_admin_only)
async def list_users(session: AsyncSession = Depends(get_db)) -> list[User]:
    return await UserRepository(session).get_all()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=_admin_only)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_db)) -> User:
    existing = await UserRepository(session).get_by_email(str(data.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    user = await UserRepository(session).create(
        email=str(data.email),
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        su_id=data.su_id,
    )
    await session.commit()
    return user


@router.patch("/{user_id}", response_model=UserResponse, dependencies=_admin_only)
async def update_user(user_id: int, data: UserUpdate, session: AsyncSession = Depends(get_db)) -> User:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = await UserRepository(session).update(user, **data.model_dump(exclude_none=True))
    await session.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=_admin_only)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_db)) -> None:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await UserRepository(session).delete(user)
    await session.commit()
