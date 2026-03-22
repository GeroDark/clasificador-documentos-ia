from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentClassificationResponse(BaseModel):
    id: int
    document_id: int
    category: str
    confidence: float
    method: str
    matched_keywords: str | None
    classified_at: datetime

    model_config = ConfigDict(from_attributes=True)