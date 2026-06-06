from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.enums import EventStatus, Role
from app.models.event import Event
from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.event_history import EventHistoryRepository
from app.schemas.event import EventCreate, EventResponse, EventStatusUpdate, EventUpdate

router = APIRouter()


async def _get_event_or_404(event_id: int, session: AsyncSession) -> Event:
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("", response_model=list[EventResponse])
async def list_events(
    status: EventStatus | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Event]:
    return await EventRepository(session).get_all(status=status, search=search)


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
    event = await EventRepository(session).create(
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        author_id=current_user.id,
        planned_date=data.planned_date,
        responsible_id=data.responsible_id,
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
    updates = data.model_dump(exclude_none=True)
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
    old_status = event.status
    repo = EventRepository(session)
    event = await repo.update(event, status=data.status)
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
    event = await _get_event_or_404(event_id, session)
    if current_user.role not in (Role.ADMIN, Role.DEPARTMENT_HEAD) and event.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    await EventRepository(session).delete(event)
    await session.commit()
