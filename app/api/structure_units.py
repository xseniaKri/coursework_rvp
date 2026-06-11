from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_roles
from app.core.database import get_db
from app.models.enums import Role
from app.models.structure_unit import StructureUnit
from app.repositories.structure_unit import StructureUnitRepository
from app.schemas.structure_unit import StructureUnitCreate, StructureUnitResponse, StructureUnitUpdate

router = APIRouter(dependencies=[Depends(get_current_user)])


async def _get_su_or_404(su_id: int, session: AsyncSession) -> StructureUnit:
    su = await StructureUnitRepository(session).get_by_id(su_id)
    if su is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Structure unit not found")
    return su


@router.get("", response_model=list[StructureUnitResponse])
async def list_structure_units(
    session: AsyncSession = Depends(get_db),
) -> list[StructureUnit]:
    return await StructureUnitRepository(session).get_all()


@router.post("", response_model=StructureUnitResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles([Role.ADMIN]))])
async def create_structure_unit(
    data: StructureUnitCreate,
    session: AsyncSession = Depends(get_db),
) -> StructureUnit:
    su = await StructureUnitRepository(session).create(name=data.name, address=data.address)
    await session.commit()
    return su


@router.patch("/{su_id}", response_model=StructureUnitResponse,
              dependencies=[Depends(require_roles([Role.ADMIN]))])
async def update_structure_unit(
    su_id: int,
    data: StructureUnitUpdate,
    session: AsyncSession = Depends(get_db),
) -> StructureUnit:
    su = await _get_su_or_404(su_id, session)
    su = await StructureUnitRepository(session).update(su, **data.model_dump(exclude_none=True))
    await session.commit()
    return su


@router.delete("/{su_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_roles([Role.ADMIN]))])
async def delete_structure_unit(
    su_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    su = await _get_su_or_404(su_id, session)
    await StructureUnitRepository(session).delete(su)
    await session.commit()
