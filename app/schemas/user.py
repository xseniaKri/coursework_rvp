from pydantic import EmailStr, Field

from app.models.enums import Role
from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)
    role: Role = Role.EMPLOYEE
    su_id: int


class UserUpdate(BaseSchema):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    role: Role | None = None
    su_id: int | None = None


class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    su_id: int
