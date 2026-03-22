from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.processing_job import ProcessingJob
from app.schemas.processing_job import ProcessingJobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/", response_model=list[ProcessingJobResponse])
def list_jobs(
    status: str | None = Query(default=None),
    document_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ProcessingJob]:
    stmt = select(ProcessingJob)

    if status is not None:
        stmt = stmt.where(ProcessingJob.status == status)

    if document_id is not None:
        stmt = stmt.where(ProcessingJob.document_id == document_id)

    stmt = stmt.order_by(ProcessingJob.created_at.desc()).limit(limit)

    return list(db.scalars(stmt).all())


@router.get("/{job_id}/status", response_model=ProcessingJobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)) -> ProcessingJob:
    job = db.get(ProcessingJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado.")
    return job