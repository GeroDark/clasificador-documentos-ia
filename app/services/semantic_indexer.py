from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.chunker import split_into_chunks
from app.services.embeddings import embed_documents


def reindex_document_chunks(db: Session, document_id: int, text: str) -> list[DocumentChunk]:
    existing = list(
        db.scalars(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        ).all()
    )

    for item in existing:
        db.delete(item)

    chunks = split_into_chunks(text)
    if not chunks:
        return []

    embeddings = embed_documents(chunks)
    created: list[DocumentChunk] = []

    for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        item = DocumentChunk(
            document_id=document_id,
            chunk_index=idx,
            chunk_text=chunk_text,
            embedding=embedding,
        )
        db.add(item)
        created.append(item)

    return created