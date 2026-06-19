from sqlalchemy import select

from app.models.file import File
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository):
    async def get_by_id(self, file_id: int) -> File | None:
        result = await self.session.execute(select(File).where(File.id == file_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        event_id: int,
        file_name: str,
        file_path: str,
        file_type: str,
    ) -> File:
        file = File(
            event_id=event_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
        )
        self.session.add(file)
        await self.session.flush()
        return file

    async def delete(self, file: File) -> None:
        await self.session.delete(file)
        await self.session.flush()
