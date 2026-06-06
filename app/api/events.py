from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.permissions import (
    can_change_status,
    can_create_event,
    can_delete_event,
    can_edit_event,
    can_assign_responsible,
)
from app.models.event import Event
from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.event_history import EventHistoryRepository
from app.schemas.event import EventCreate, EventResponse, EventStatusUpdate, EventUpdate

router = APIRouter()


def _403(detail: str = "Недостаточно прав"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def _get_event_or_404(event_id: int, session: AsyncSession) -> Event:
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("", response_model=list[EventResponse])
async def list_events(
    status: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Event]:
    from app.models.enums import EventStatus
    status_filter = EventStatus(status) if status else None
    return await EventRepository(session).get_all(status=status_filter, search=search)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Event:
    return await _get_event_or_404(event_id, session)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Event:
    if not can_create_event(current_user):
        _403()

    responsible_id = data.responsible_id
    if responsible_id is not None and not can_assign_responsible(current_user):
        responsible_id = None

    event = await EventRepository(session).create(
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        author_id=current_user.id,
        planned_date=data.planned_date,
        responsible_id=responsible_id,
    )
    await session.commit()
    return event


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    data: EventUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Event:
    event = await _get_event_or_404(event_id, session)

    if not can_edit_event(current_user, event):
        _403()

    updates = data.model_dump(exclude_none=True)

    if not can_assign_responsible(current_user):
        updates.pop("responsible_id", None)

    event = await EventRepository(session).update(event, **updates)
    await session.commit()
    return event


@router.post("/{event_id}/status", response_model=EventResponse)
async def change_status(
    event_id: int,
    data: EventStatusUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Event:
    event = await _get_event_or_404(event_id, session)

    if not can_change_status(current_user, event, data.status):
        _403()

    old_status = event.status
    event = await EventRepository(session).update(event, status=data.status)
    await EventHistoryRepository(session).create(
        event_id=event.id,
        user_id=current_user.id,
        old_status=old_status,
        new_status=data.status,
        comment=data.comment,
    )
    await session.commit()
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if not can_delete_event(current_user):
        _403()
    event = await _get_event_or_404(event_id, session)
    await EventRepository(session).delete(event)
    await session.commit()
