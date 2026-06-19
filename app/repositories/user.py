from sqlalchemy import select

from app.models.enums import Role
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.full_name))
        return list(result.scalars().all())

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str,
        role: Role,
        su_id: int,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            su_id=su_id,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()
