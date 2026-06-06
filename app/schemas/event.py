from datetime import datetime

from pydantic import Field

from app.models.enums import EventStatus
from app.schemas.base import BaseSchema


class EventCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category_id: int
    planned_date: datetime
    responsible_id: int | None = None


class EventUpdate(BaseSchema):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category_id: int | None = None
    planned_date: datetime | None = None
    responsible_id: int | None = None
    status: EventStatus | None = None


class EventStatusUpdate(BaseSchema):
    status: EventStatus
    comment: str | None = None


class CategoryResponse(BaseSchema):
    id: int
    name: str


class EventResponse(BaseSchema):
    id: int
    title: str
    description: str | None
    category_id: int
    category: CategoryResponse
    status: EventStatus
    author_id: int
    responsible_id: int | None
    planned_date: datetime
    created_at: datetime
    updated_at: datetime
