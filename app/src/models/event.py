from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.enums import EventStatus

if TYPE_CHECKING:
    from src.models.event_history import EventHistory
    from src.models.user import User


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
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
