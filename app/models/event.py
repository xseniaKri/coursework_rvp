from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EventStatus

if TYPE_CHECKING:
    from app.models.event_history import EventHistory
    from app.models.file import File
    from app.models.user import User
    from app.models.category import Category


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name="event_status"),
        nullable=False,
        default=EventStatus.CREATED,
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    responsible_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    planned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        back_populates="event",
        foreign_keys=[category_id],
    )
    author: Mapped["User"] = relationship(
        back_populates="authored_events",
        foreign_keys=[author_id],
    )
    responsible: Mapped["User | None"] = relationship(
        back_populates="responsible_events",
        foreign_keys=[responsible_id],
    )
    history: Mapped[list["EventHistory"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="EventHistory.created_at",
    )
    files: Mapped[list["File"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="File.uploaded_at",
    )
