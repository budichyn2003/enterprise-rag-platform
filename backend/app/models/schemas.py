from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- INGESTION SCHEMAS ---
class DocumentMetadata(BaseModel):
    source_type: str = Field(..., description="Tipe sumber, misal: pdf, confluence, manual")
    category: Optional[str] = None
    language: str = "id"

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str # queued, processing, indexed, failed
    chunks_processed: int = 0
    message: str

# --- CHAT SCHEMAS ---
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: str = "id"

class Citation(BaseModel):
    document_id: str
    title: str
    url: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: List[Citation] = []
    confidence_score: float = Field(..., description="Skor metrik akurasi jawaban RAG")
    needs_escalation: bool = Field(default=False, description="Flag eskalasi ke human agent")