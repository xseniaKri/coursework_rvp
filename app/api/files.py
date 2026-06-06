import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import can_edit_event
from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.file import FileRepository
from app.schemas.file import FileResponse as FileResponseSchema

router = APIRouter()


async def _get_event_or_404(event_id: int, session: AsyncSession):
    event = await EventRepository(session).get_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мероприятие не найдено")
    return event


async def _get_file_or_404(file_id: int, session: AsyncSession):
    file = await FileRepository(session).get_by_id(file_id)
    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")
    return file


@router.post("/events/{event_id}/files", response_model=FileResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(
    event_id: int,
    file: UploadFile = FastAPIFile(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = await _get_event_or_404(event_id, session)

    if not can_edit_event(current_user, event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    upload_dir = Path(settings.upload_dir) / str(event_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = file.filename or "file"
    ext = Path(original_name).suffix
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / stored_name

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    db_file = await FileRepository(session).create(
        event_id=event_id,
        file_name=original_name,
        file_path=str(file_path),
        file_type=file.content_type or "application/octet-stream",
    )
    await session.commit()
    return db_file


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_file = await _get_file_or_404(file_id, session)

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден на диске")

    return FileResponse(
        path=db_file.file_path,
        filename=db_file.file_name,
        media_type=db_file.file_type,
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_file = await _get_file_or_404(file_id, session)
    event = await _get_event_or_404(db_file.event_id, session)

    if not can_edit_event(current_user, event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    await FileRepository(session).delete(db_file)
    await session.commit()
