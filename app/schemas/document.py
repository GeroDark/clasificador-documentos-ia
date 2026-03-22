from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    original_filename: str
    content_type: str | None = None
    size_bytes: int | None = None


class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str | None
    file_path: str | None
    content_type: str | None
    size_bytes: int | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)