from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import ChatMessage, ChatResponse, DocumentUpload, HealthResponse, UserProfile
from backend.services.rag_service import RAGService
from backend.services.chat_service import ChatService
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
rag_service = RAGService()
chat_service = ChatService()

# Session storage (in-memory for now)
user_sessions: Dict[str, Dict] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        rag_enabled=True,
        documents_count=rag_service.get_document_count(),
        default_provider=chat_service.default_provider,
        providers=chat_service.available_providers(),
    )


@router.post("/setup-profile")
async def setup_profile(profile: UserProfile):
    """Store user profile for personalized responses"""
    user_sessions[profile.session_id] = {
        "grade_levels": profile.grade_levels,
        "scenario": profile.scenario
    }
    logger.info("Profile set up for session %s", profile.session_id)
    return {"status": "success", "session_id": profile.session_id}


@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Chat endpoint with mandatory RAG and context awareness"""
    try:
        # Always retrieve RAG context (forced)
        sources = rag_service.query(message.message, n_results=5)
        logger.info("Retrieved %d sources for query", len(sources))

        # Get user profile from session
        user_profile = user_sessions.get(message.session_id, {})

        # Generate response (always using xai/Grok-4)
        response_text, provider_used = chat_service.generate_response(
            user_message=message.message,
            context=sources,
            provider="xai",  # Force Grok-4
            user_profile=user_profile,
        )

        return ChatResponse(
            response=response_text,
            provider=provider_used,
            sources=sources  # Always return sources
        )

    except Exception as e:  # noqa: BLE001
        logger.error("Error in chat endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/upload", response_model=DocumentUpload)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the RAG system"""
    try:
        # Read file content
        content = await file.read()

        # Handle different file types
        if file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        elif file.filename.endswith('.pdf'):
            from pypdf import PdfReader  # lazy import for PDFs
            from io import BytesIO
            pdf_file = BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload .txt or .pdf files.")

        # Add to RAG system
        chunks_created = rag_service.add_document(text, file.filename)

        return DocumentUpload(
            filename=file.filename,
            chunks_created=chunks_created,
            status="success"
        )

    except Exception as e:  # noqa: BLE001
        logger.error("Error uploading document: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/documents")
async def clear_documents():
    """Clear all documents from the RAG system"""
    try:
        rag_service.clear_collection()
        return {"status": "success", "message": "All documents cleared"}
    except Exception as e:  # noqa: BLE001
        logger.error("Error clearing documents: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/documents/count")
async def get_document_count():
    """Get the number of document chunks in the system"""
    return {"count": rag_service.get_document_count()}
