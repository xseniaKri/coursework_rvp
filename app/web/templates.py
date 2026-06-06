from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

templates.env.globals["ROLE_NAMES"] = {
    "ADMIN": "ИТ-администратор",
    "DEPARTMENT_HEAD": "Руководитель СП",
    "ART_DIRECTOR": "Художественный руководитель",
    "EMPLOYEE": "Сотрудник",
}

templates.env.globals["STATUS_NAMES"] = {
    "CREATED": "Создано",
    "ON_APPROVAL": "На согласовании",
    "APPROVED": "Согласовано",
    "REJECTED": "Отклонено",
    "PLANNED": "Запланировано",
    "COMPLETED": "Проведено",
}
