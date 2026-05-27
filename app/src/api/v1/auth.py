from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.core.database import get_db
from src.models.user import User
from src.schemas.auth import LoginRequest, TokenResponse
from src.schemas.user import UserCreate, UserResponse
from src.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> User:
    return await AuthService(session).register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService(session).login(credentials)


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
