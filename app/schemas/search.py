from pydantic import BaseModel


class SemanticSearchResultResponse(BaseModel):
    document_id: int
    document_filename: str
    chunk_id: int
    chunk_index: int
    chunk_text: str
    score: float