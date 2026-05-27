from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.enums import Role

if TYPE_CHECKING:
    from src.models.event import Event
    from src.models.event_history import EventHistory


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="role"),
        nullable=False,
        default=Role.EMPLOYEE,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    authored_events: Mapped[list["Event"]] = relationship(
        back_populates="author",
        foreign_keys="Event.author_id",
    )
    responsible_events: Mapped[list["Event"]] = relationship(
        back_populates="responsible",
        foreign_keys="Event.responsible_id",
    )
    event_history_records: Mapped[list["EventHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
