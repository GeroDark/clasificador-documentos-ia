from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentSummaryResponse(BaseModel):
    id: int
    document_id: int
    short_summary: str
    key_points: str | None
    keywords: str | None
    method: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)