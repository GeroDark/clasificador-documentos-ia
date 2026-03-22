from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_classification import DocumentClassification
from app.models.document_summary import DocumentSummary
from app.models.document_text import DocumentText
from app.models.extracted_field import ExtractedField
from app.services.classifier import classify_text
from app.services.field_extractor import extract_fields
from app.services.semantic_indexer import reindex_document_chunks
from app.services.summarizer import generate_summary
from app.services.text_extractor import extract_text_by_extension


def process_document_pipeline(db: Session, document: Document) -> None:
    if not document.file_path:
        raise ValueError("El documento no tiene file_path.")

    extension = ""
    if document.original_filename:
        extension = "." + document.original_filename.split(".")[-1].lower()

    extracted_text = extract_text_by_extension(document.file_path, extension)

    if not extracted_text:
        document.status = "uploaded"
        db.add(document)
        db.commit()
        return

    existing_text = db.scalar(
        select(DocumentText).where(DocumentText.document_id == document.id)
    )
    if existing_text is None:
        db.add(
            DocumentText(
                document_id=document.id,
                raw_text=extracted_text,
            )
        )
    else:
        existing_text.raw_text = extracted_text
        db.add(existing_text)

    classification_result = classify_text(extracted_text)
    existing_classification = db.scalar(
        select(DocumentClassification).where(DocumentClassification.document_id == document.id)
    )
    if existing_classification is None:
        db.add(
            DocumentClassification(
                document_id=document.id,
                category=str(classification_result["category"]),
                confidence=float(classification_result["confidence"]),
                method=str(classification_result["method"]),
                matched_keywords=classification_result["matched_keywords"],
            )
        )
    else:
        existing_classification.category = str(classification_result["category"])
        existing_classification.confidence = float(classification_result["confidence"])
        existing_classification.method = str(classification_result["method"])
        existing_classification.matched_keywords = classification_result["matched_keywords"]
        db.add(existing_classification)

    summary_result = generate_summary(extracted_text)
    existing_summary = db.scalar(
        select(DocumentSummary).where(DocumentSummary.document_id == document.id)
    )
    if existing_summary is None:
        db.add(
            DocumentSummary(
                document_id=document.id,
                short_summary=str(summary_result["short_summary"]),
                key_points=summary_result["key_points"],
                keywords=summary_result["keywords"],
                method=str(summary_result["method"]),
            )
        )
    else:
        existing_summary.short_summary = str(summary_result["short_summary"])
        existing_summary.key_points = summary_result["key_points"]
        existing_summary.keywords = summary_result["keywords"]
        existing_summary.method = str(summary_result["method"])
        db.add(existing_summary)

    existing_fields = list(
        db.scalars(
            select(ExtractedField).where(ExtractedField.document_id == document.id)
        ).all()
    )
    for item in existing_fields:
        db.delete(item)

    for field in extract_fields(extracted_text):
        db.add(
            ExtractedField(
                document_id=document.id,
                field_name=str(field["field_name"]),
                field_value=str(field["field_value"]),
                confidence=float(field["confidence"]),
                method=str(field["method"]),
            )
        )

    existing_chunks = list(
        db.scalars(
            select(DocumentChunk).where(DocumentChunk.document_id == document.id)
        ).all()
    )
    for item in existing_chunks:
        db.delete(item)

    reindex_document_chunks(db, document.id, extracted_text)

    document.status = "indexed"
    db.add(document)
    db.commit()