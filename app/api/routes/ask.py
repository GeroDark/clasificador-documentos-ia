from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import ERROR_RESPONSES, not_found
from app.core.config import get_settings
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.query_log import QueryLog
from app.schemas.ask import (
    AnswerSourceChunkResponse,
    AskRequest,
    AskResponse,
    QueryLogResponse,
)
from app.services.embeddings import embed_query
from app.services.question_answering import answer_question

router = APIRouter(prefix="/api/ask", tags=["ask"])


def fetch_ask_rows(
    db: Session,
    query_embedding: list[float],
    limit: int,
    document_id: int | None = None,
) -> list[tuple[DocumentChunk, Document, float]]:
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(DocumentChunk, Document, distance.label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
    )

    if document_id is not None:
        stmt = stmt.where(DocumentChunk.document_id == document_id)

    stmt = stmt.order_by(distance.asc()).limit(limit)
    return list(db.execute(stmt).all())


@router.post(
    "/",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Responder una pregunta sobre documentos",
    description="Recupera chunks relevantes, genera una respuesta y registra la consulta realizada.",
    responses={
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
        status.HTTP_422_UNPROCESSABLE_CONTENT: ERROR_RESPONSES[status.HTTP_422_UNPROCESSABLE_CONTENT],
    },
)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    settings = get_settings()
    final_top_k = payload.top_k or settings.semantic_search_top_k

    query_embedding = embed_query(payload.question)
    rows = fetch_ask_rows(db, query_embedding, final_top_k, payload.document_id)

    if not rows:
        raise not_found("No se encontraron fragmentos relevantes para responder.")

    sources: list[AnswerSourceChunkResponse] = []
    raw_sources: list[dict[str, str | int | float]] = []

    for chunk, document, distance_value in rows:
        score = round(max(0.0, 1.0 - float(distance_value)), 4)

        source = AnswerSourceChunkResponse(
            chunk_id=chunk.id,
            document_id=document.id,
            document_filename=document.original_filename,
            chunk_index=chunk.chunk_index,
            chunk_text=chunk.chunk_text,
            score=score,
        )
        sources.append(source)
        raw_sources.append(source.model_dump())

    result = answer_question(payload.question, raw_sources)

    log = QueryLog(
        document_id=payload.document_id,
        question=payload.question,
        answer=str(result["answer"]),
        confidence=float(result["confidence"]),
        top_k=final_top_k,
    )
    db.add(log)
    db.commit()

    return AskResponse(
        question=payload.question,
        answer=str(result["answer"]),
        confidence=float(result["confidence"]),
        document_id=payload.document_id,
        sources=sources,
    )


@router.get(
    "/logs/",
    response_model=list[QueryLogResponse],
    summary="Listar consultas realizadas",
    description="Retorna el historial de preguntas respondidas por la API.",
)
def list_query_logs(
    document_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[QueryLog]:
    stmt = select(QueryLog)

    if document_id is not None:
        stmt = stmt.where(QueryLog.document_id == document_id)

    stmt = stmt.order_by(QueryLog.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())
