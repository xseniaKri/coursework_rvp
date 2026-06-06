from pydantic import Field

from app.schemas.base import BaseSchema


class StructureUnitCreate(BaseSchema):
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)


class StructureUnitUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1)
    address: str | None = Field(None, min_length=1)


class StructureUnitResponse(BaseSchema):
    id: int
    name: str
    address: str
