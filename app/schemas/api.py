from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class IngestResponse(BaseModel):
    """Response for single file ingestion"""
    document_id: str
    title: str
    num_chunks: int

class MultiIngestResponse(BaseModel):
    """Enhanced response for multiple file ingestion (React frontend)"""
    documents: List[IngestResponse]
    total_files: int
    total_chunks: int
    message: str

class Citation(BaseModel):
    """Citation with source information"""
    document_id: str
    chunk_id: str
    text: str
    score: Optional[float] = None
    page_number: Optional[int] = None
    source_uri: Optional[str] = None

class QueryRequest(BaseModel):
    """Query request with enhanced options"""
    question: str
    mode: Optional[str] = "chat"  # "chat" or "form"
    top_k: Optional[int] = 5
    user_context: Optional[Dict[str, Any]] = None
    include_metadata: Optional[bool] = True

class AnswerResponse(BaseModel):
    """Enhanced answer response with detailed metrics"""
    answer: str
    citations: List[Citation] = []
    metrics: Optional[Dict[str, Any]] = None

class DocumentInfo(BaseModel):
    """Document metadata"""
    id: str
    title: str
    source_uri: str
    created_at: str
    tags: str
    num_chunks: Optional[int] = None

class DocumentResponse(BaseModel):
    """Document retrieval response"""
    document: DocumentInfo
    chunks_preview: List[Dict[str, Any]] = []

class DocumentListResponse(BaseModel):
    """List of all documents"""
    documents: List[DocumentInfo]
    total_count: int

class EvaluationResponse(BaseModel):
    """Evaluation results"""
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str