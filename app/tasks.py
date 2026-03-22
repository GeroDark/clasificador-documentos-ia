from datetime import datetime

from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.services.document_pipeline import process_document_pipeline


@celery_app.task(bind=True)
def process_document_task(self, document_id: int, job_id: int) -> dict[str, str | int]:
    db: Session = SessionLocal()
    try:
        job = db.get(ProcessingJob, job_id)
        document = db.get(Document, document_id)

        if job is None or document is None:
            raise ValueError("Job o documento no encontrado.")

        job.task_id = self.request.id
        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.add(job)

        document.status = "processing"
        db.add(document)
        db.commit()

        process_document_pipeline(db, document)

        job.status = "completed"
        job.finished_at = datetime.utcnow()
        db.add(job)
        db.commit()

        return {
            "job_id": job_id,
            "document_id": document_id,
            "status": "completed",
        }
    except Exception as exc:
        job = db.get(ProcessingJob, job_id)
        document = db.get(Document, document_id)

        if job is not None:
            job.status = "failed"
            job.error_message = str(exc)
            job.finished_at = datetime.utcnow()
            db.add(job)

        if document is not None:
            document.status = "failed"
            db.add(document)

        db.commit()
        raise
    finally:
        db.close()