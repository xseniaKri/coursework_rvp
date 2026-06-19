from app.models.enums import EventStatus
from app.models.event_history import EventHistory
from app.repositories.base import BaseRepository


class EventHistoryRepository(BaseRepository):
    async def create(
        self,
        *,
        event_id: int,
        user_id: int,
        old_status: EventStatus | None,
        new_status: EventStatus,
        comment: str | None = None,
    ) -> EventHistory:
        record = EventHistory(
            event_id=event_id,
            user_id=user_id,
            old_status=old_status,
            new_status=new_status,
            comment=comment,
        )
        self.session.add(record)
        await self.session.flush()
        return record
