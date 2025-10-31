from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for chat messages"""
    message: str
    use_rag: bool = True
    provider: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat responses"""
    response: str
    provider: str
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
    default_provider: Optional[str] = None
    providers: List[str] = Field(default_factory=list)
