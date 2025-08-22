from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class IngestResponse(BaseModel):
    document_id: str
    title: str
    num_chunks: int

class Citation(BaseModel):
    doc_id: str
    title: str
    snippet: str
    source_uri: str | None = None
    page: int | None = None

class AnswerResponse(BaseModel):
    answer: str
    citations: List[Citation]
    metrics: dict

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = 5
    mode: Literal["answer","form"] = "answer"
    user_context: Optional[dict] = None
