from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Role

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.event_history import EventHistory
    from app.models.structure_unit import StructureUnit


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="role"),
        nullable=False,
        default=Role.EMPLOYEE,
    )
    su_id: Mapped[int] = mapped_column(ForeignKey("structure_units.id"), nullable=False)

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
    structure_unit: Mapped["StructureUnit"] = relationship(
        back_populates="user",
    )
