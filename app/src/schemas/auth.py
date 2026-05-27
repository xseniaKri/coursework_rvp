from pydantic import EmailStr, Field

from src.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
