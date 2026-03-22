from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProcessingJobResponse(BaseModel):
    id: int
    document_id: int
    task_id: str | None
    status: str
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)