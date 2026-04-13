from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_classification import DocumentClassification
from app.models.document_summary import DocumentSummary
from app.models.document_text import DocumentText
from app.models.extracted_field import ExtractedField
from app.models.processing_job import ProcessingJob
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.document_chunk import DocumentChunkResponse
from app.schemas.document_classification import DocumentClassificationResponse
from app.schemas.document_summary import DocumentSummaryResponse
from app.schemas.document_text import DocumentTextResponse
from app.schemas.extracted_field import ExtractedFieldResponse
from app.schemas.processing_job import ProcessingJobResponse
from app.services.classifier import classify_text
from app.services.storage import save_upload_file
from app.services.summarizer import generate_summary
from app.tasks import process_document_task

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)) -> Document:
    document = Document(
        original_filename=payload.original_filename,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
        status="metadata_only",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post("/upload/", response_model=ProcessingJobResponse, status_code=status.HTTP_202_ACCEPTED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProcessingJob:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Solo se aceptan PDF, DOCX y TXT.",
        )

    stored_filename, file_path = save_upload_file(file)

    document = Document(
        original_filename=filename,
        stored_filename=stored_filename,
        file_path=file_path,
        content_type=file.content_type,
        size_bytes=file.size,
        status="queued",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    job = ProcessingJob(
        document_id=document.id,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    async_result = process_document_task.delay(document.id, job.id)

    job.task_id = async_result.id
    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    stmt = select(Document).order_by(Document.created_at.desc())
    return list(db.scalars(stmt).all())


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado.",
        )
    return document


@router.get("/{document_id}/text", response_model=DocumentTextResponse)
def get_document_text(document_id: int, db: Session = Depends(get_db)) -> DocumentText:
    stmt = select(DocumentText).where(DocumentText.document_id == document_id)
    document_text = db.scalar(stmt)

    if document_text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Texto del documento no encontrado.",
        )

    return document_text


@router.get("/{document_id}/classification", response_model=DocumentClassificationResponse)
def get_document_classification(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentClassification:
    stmt = select(DocumentClassification).where(DocumentClassification.document_id == document_id)
    classification = db.scalar(stmt)

    if classification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clasificación no encontrada.",
        )

    return classification


@router.post("/{document_id}/classify", response_model=DocumentClassificationResponse)
def classify_document_again(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentClassification:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado.",
        )

    stmt = select(DocumentText).where(DocumentText.document_id == document_id)
    document_text = db.scalar(stmt)

    if document_text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Texto del documento no encontrado.",
        )

    result = classify_text(document_text.raw_text)

    stmt_existing = select(DocumentClassification).where(
        DocumentClassification.document_id == document_id
    )
    existing = db.scalar(stmt_existing)

    if existing is None:
        existing = DocumentClassification(
            document_id=document_id,
            category=str(result["category"]),
            confidence=float(result["confidence"]),
            method=str(result["method"]),
            matched_keywords=result["matched_keywords"],
        )
        db.add(existing)
    else:
        existing.category = str(result["category"])
        existing.confidence = float(result["confidence"])
        existing.method = str(result["method"])
        existing.matched_keywords = result["matched_keywords"]
        db.add(existing)

    db.commit()
    db.refresh(existing)

    return existing


@router.get("/{document_id}/summary", response_model=DocumentSummaryResponse)
def get_document_summary(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentSummary:
    stmt = select(DocumentSummary).where(DocumentSummary.document_id == document_id)
    summary = db.scalar(stmt)

    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resumen no encontrado.",
        )

    return summary


@router.post("/{document_id}/summarize", response_model=DocumentSummaryResponse)
def summarize_document_again(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentSummary:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado.",
        )

    stmt = select(DocumentText).where(DocumentText.document_id == document_id)
    document_text = db.scalar(stmt)

    if document_text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Texto del documento no encontrado.",
        )

    result = generate_summary(document_text.raw_text)

    stmt_existing = select(DocumentSummary).where(DocumentSummary.document_id == document_id)
    existing = db.scalar(stmt_existing)

    if existing is None:
        existing = DocumentSummary(
            document_id=document_id,
            short_summary=str(result["short_summary"]),
            key_points=result["key_points"],
            keywords=result["keywords"],
            method=str(result["method"]),
        )
        db.add(existing)
    else:
        existing.short_summary = str(result["short_summary"])
        existing.key_points = result["key_points"]
        existing.keywords = result["keywords"]
        existing.method = str(result["method"])
        db.add(existing)

    document.status = "summarized"
    db.add(document)

    db.commit()
    db.refresh(existing)

    return existing


@router.get("/{document_id}/fields", response_model=list[ExtractedFieldResponse])
def get_document_fields(
    document_id: int,
    db: Session = Depends(get_db),
) -> list[ExtractedField]:
    stmt = (
        select(ExtractedField)
        .where(ExtractedField.document_id == document_id)
        .order_by(ExtractedField.field_name.asc())
    )
    fields = list(db.scalars(stmt).all())

    if not fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campos extraídos no encontrados.",
        )

    return fields


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
) -> list[DocumentChunk]:
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    )
    chunks = list(db.scalars(stmt).all())

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunks no encontrados para este documento.",
        )

    return chunks