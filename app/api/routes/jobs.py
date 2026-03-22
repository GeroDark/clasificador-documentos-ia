from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.processing_job import ProcessingJob
from app.schemas.processing_job import ProcessingJobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}/status", response_model=ProcessingJobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)) -> ProcessingJob:
    job = db.get(ProcessingJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado.")
    return job