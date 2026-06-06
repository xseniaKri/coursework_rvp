from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.enums import EventStatus
from app.models.event import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def _base_query(self):
        from app.models.event_history import EventHistory
        return select(Event).options(
            selectinload(Event.category),
            selectinload(Event.author),
            selectinload(Event.responsible),
            selectinload(Event.history).selectinload(EventHistory.user),
            selectinload(Event.files),
        )

    async def get_all(
        self,
        status: EventStatus | None = None,
        search: str | None = None,
    ) -> list[Event]:
        q = self._base_query().order_by(Event.planned_date.desc())
        if status:
            q = q.where(Event.status == status)
        if search:
            q = q.where(Event.title.ilike(f"%{search}%"))
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_by_id(self, event_id: int) -> Event | None:
        result = await self.session.execute(
            self._base_query().where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        title: str,
        description: str | None,
        category_id: int,
        author_id: int,
        planned_date: datetime,
        responsible_id: int | None = None,
    ) -> Event:
        event = Event(
            title=title,
            description=description,
            category_id=category_id,
            author_id=author_id,
            planned_date=planned_date,
            responsible_id=responsible_id,
            status=EventStatus.CREATED,
        )
        self.session.add(event)
        await self.session.flush()
        return await self.get_by_id(event.id)

    async def update(self, event: Event, **kwargs) -> Event:
        for key, value in kwargs.items():
            setattr(event, key, value)
        await self.session.flush()
        return await self.get_by_id(event.id)

    async def delete(self, event: Event) -> None:
        await self.session.delete(event)
        await self.session.flush()

    async def count_this_month(self) -> int:
        from datetime import date
        from sqlalchemy import func, extract
        today = date.today()
        result = await self.session.execute(
            select(func.count(Event.id)).where(
                extract("year", Event.planned_date) == today.year,
                extract("month", Event.planned_date) == today.month,
            )
        )
        return result.scalar_one()
