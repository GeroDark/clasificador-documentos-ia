from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentTextResponse(BaseModel):
    id: int
    document_id: int
    raw_text: str
    extracted_at: datetime

    model_config = ConfigDict(from_attributes=True)