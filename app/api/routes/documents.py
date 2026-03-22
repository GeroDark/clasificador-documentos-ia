from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.document_classification import DocumentClassification
from app.models.document_text import DocumentText
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.document_classification import DocumentClassificationResponse
from app.schemas.document_text import DocumentTextResponse
from app.services.classifier import classify_text
from app.services.storage import save_upload_file
from app.services.text_extractor import extract_text_by_extension

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


@router.post("/upload/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Document:
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
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    extracted_text = extract_text_by_extension(file_path, extension)

    if extracted_text:
        document_text = DocumentText(
            document_id=document.id,
            raw_text=extracted_text,
        )
        db.add(document_text)

        classification_result = classify_text(extracted_text)
        classification = DocumentClassification(
            document_id=document.id,
            category=str(classification_result["category"]),
            confidence=float(classification_result["confidence"]),
            method=str(classification_result["method"]),
            matched_keywords=classification_result["matched_keywords"],
        )
        db.add(classification)

        document.status = "classified"
        db.add(document)

        db.commit()
        db.refresh(document)

    return document


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

    document.status = "classified"
    db.add(document)

    db.commit()
    db.refresh(existing)

    return existing