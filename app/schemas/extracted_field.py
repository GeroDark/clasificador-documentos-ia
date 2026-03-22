from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExtractedFieldResponse(BaseModel):
    id: int
    document_id: int
    field_name: str
    field_value: str
    confidence: float
    method: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)