from datetime import datetime

from pydantic import EmailStr, Field

from src.models.enums import Role
from src.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)
    role: Role = Role.EMPLOYEE


class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    created_at: datetime
