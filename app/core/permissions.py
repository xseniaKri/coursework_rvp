from app.models.enums import EventStatus, Role
from app.models.event import Event
from app.models.user import User

_RESTRICTED_STATUSES = {EventStatus.APPROVED, EventStatus.REJECTED}


def can_create_event(user: User) -> bool:
    return user.role in (Role.DEPARTMENT_HEAD, Role.ART_DIRECTOR)


def can_edit_event(user: User, event: Event) -> bool:
    if user.role == Role.ART_DIRECTOR:
        return True
    if user.role in (Role.EMPLOYEE, Role.DEPARTMENT_HEAD):
        return event.responsible_id == user.id
    return False


def can_assign_responsible(user: User) -> bool:
    return user.role in (Role.DEPARTMENT_HEAD, Role.ART_DIRECTOR)


def can_delete_event(user: User) -> bool:
    return user.role == Role.ART_DIRECTOR


def can_change_status(user: User, event: Event, new_status: EventStatus) -> bool:
    if user.role == Role.ART_DIRECTOR:
        return True
    if user.role in (Role.EMPLOYEE, Role.DEPARTMENT_HEAD):
        if event.responsible_id != user.id:
            return False
        return new_status not in _RESTRICTED_STATUSES
    return False


def allowed_statuses(user: User, event: Event) -> list[EventStatus]:
    """Возвращает список статусов, доступных пользователю для этого мероприятия."""
    all_statuses = list(EventStatus)
    if user.role == Role.ART_DIRECTOR:
        return all_statuses
    if user.role in (Role.EMPLOYEE, Role.DEPARTMENT_HEAD) and event.responsible_id == user.id:
        return [s for s in all_statuses if s not in _RESTRICTED_STATUSES]
    return []
