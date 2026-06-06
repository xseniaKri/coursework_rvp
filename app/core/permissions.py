from app.models.enums import EventStatus, Role
from app.models.event import Event
from app.models.user import User

# Разрешённые переходы между статусами
_TRANSITIONS: dict[EventStatus, set[EventStatus]] = {
    EventStatus.CREATED:     {EventStatus.ON_APPROVAL},
    EventStatus.ON_APPROVAL: {EventStatus.APPROVED, EventStatus.REJECTED},
    EventStatus.APPROVED:    {EventStatus.PLANNED},
    EventStatus.PLANNED:     {EventStatus.COMPLETED},
    EventStatus.COMPLETED:   set(),
    EventStatus.REJECTED:    set(),
}

# Статусы, которые может выставлять только ART_DIRECTOR
_ART_DIRECTOR_ONLY = {EventStatus.APPROVED, EventStatus.REJECTED}


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
    # Проверяем допустимость перехода
    if new_status not in _TRANSITIONS.get(event.status, set()):
        return False

    # APPROVED / REJECTED — только ART_DIRECTOR
    if new_status in _ART_DIRECTOR_ONLY:
        return user.role == Role.ART_DIRECTOR

    # Остальные переходы
    if user.role == Role.ART_DIRECTOR:
        return True
    if user.role in (Role.EMPLOYEE, Role.DEPARTMENT_HEAD):
        return event.responsible_id == user.id
    return False


def allowed_statuses(user: User, event: Event) -> list[EventStatus]:
    """Статусы, доступные пользователю для данного мероприятия с учётом текущего статуса."""
    return [s for s in EventStatus if can_change_status(user, event, s)]
