from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.auth import LoginRequest, TokenResponse
from src.schemas.user import UserCreate
from src.services.base import BaseService


class AuthService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.users = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> User:
        existing_user = await self.users.get_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user = await self.users.create(
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
        )
        await self.session.commit()
        return user

    async def authenticate_user(self, credentials: LoginRequest) -> User:
        user = await self.users.get_by_email(credentials.email)
        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        return user

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        user = await self.authenticate_user(credentials)
        access_token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=access_token)
