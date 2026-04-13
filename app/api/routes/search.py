from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import ERROR_RESPONSES
from app.core.config import get_settings
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.search import SemanticSearchResultResponse
from app.services.embeddings import embed_query

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get(
    "/semantic/",
    response_model=list[SemanticSearchResultResponse],
    summary="Ejecutar búsqueda semántica",
    description="Busca los chunks más cercanos a la consulta y devuelve contexto documental relevante.",
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: ERROR_RESPONSES[status.HTTP_422_UNPROCESSABLE_CONTENT],
    },
)
def semantic_search(
    q: str = Query(..., min_length=2, description="Consulta semántica"),
    limit: int | None = Query(None, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[SemanticSearchResultResponse]:
    settings = get_settings()
    final_limit = limit or settings.semantic_search_top_k

    query_embedding = embed_query(q)
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(DocumentChunk, Document, distance.label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(distance.asc())
        .limit(final_limit)
    )

    rows = db.execute(stmt).all()

    results: list[SemanticSearchResultResponse] = []
    for chunk, document, distance_value in rows:
        score = round(max(0.0, 1.0 - float(distance_value)), 4)
        results.append(
            SemanticSearchResultResponse(
                document_id=document.id,
                document_filename=document.original_filename,
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                score=score,
            )
        )

    return results
