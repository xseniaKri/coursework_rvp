from sqlalchemy import select

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    async def get_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, name: str) -> Category:
        cat = Category(name=name)
        self.session.add(cat)
        await self.session.flush()
        await self.session.refresh(cat)
        return cat
