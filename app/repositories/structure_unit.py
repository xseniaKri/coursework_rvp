from sqlalchemy import select

from app.models.structure_unit import StructureUnit
from app.repositories.base import BaseRepository


class StructureUnitRepository(BaseRepository):
    async def get_all(self) -> list[StructureUnit]:
        result = await self.session.execute(select(StructureUnit).order_by(StructureUnit.name))
        return list(result.scalars().all())

    async def get_by_id(self, su_id: int) -> StructureUnit | None:
        result = await self.session.execute(
            select(StructureUnit).where(StructureUnit.id == su_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, name: str, address: str) -> StructureUnit:
        su = StructureUnit(name=name, address=address)
        self.session.add(su)
        await self.session.flush()
        await self.session.refresh(su)
        return su

    async def update(self, su: StructureUnit, **kwargs) -> StructureUnit:
        for key, value in kwargs.items():
            if value is not None:
                setattr(su, key, value)
        await self.session.flush()
        await self.session.refresh(su)
        return su

    async def delete(self, su: StructureUnit) -> None:
        await self.session.delete(su)
        await self.session.flush()
