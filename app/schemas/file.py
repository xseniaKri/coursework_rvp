from datetime import datetime

from app.schemas.base import BaseSchema


class FileResponse(BaseSchema):
    id: int
    file_name: str
    file_type: str
    uploaded_at: datetime
    event_id: int
