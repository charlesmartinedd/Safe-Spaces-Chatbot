from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    """Schema for chat messages"""
    message: str
    use_rag: bool = True


class ChatResponse(BaseModel):
    """Schema for chat responses"""
    response: str
    sources: Optional[List[dict]] = None


class DocumentUpload(BaseModel):
    """Schema for document upload response"""
    filename: str
    chunks_created: int
    status: str


class HealthResponse(BaseModel):
    """Schema for health check"""
    status: str
    rag_enabled: bool
    documents_count: int
