from datetime import datetime

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2)
    document_id: int | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class AnswerSourceChunkResponse(BaseModel):
    chunk_id: int
    document_id: int
    document_filename: str
    chunk_index: int
    chunk_text: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    document_id: int | None
    sources: list[AnswerSourceChunkResponse]


class QueryLogResponse(BaseModel):
    id: int
    document_id: int | None
    question: str
    answer: str
    confidence: float
    top_k: int
    created_at: datetime