from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models.schemas import ChatRequest, ChatResponse, DocumentUploadResponse
from app.services.rag_service import rag_service

router = APIRouter()

# --- CHAT ENDPOINTS ---
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    FR-CH-01 & FR-RAG-04: Endpoint utama untuk berinteraksi dengan chatbot eksternal.
    """
    try:
        # Simulasi pengambilan history percakapan berdasarkan session_id
        chat_history = [] 
        
        # Panggil RAG Service untuk generate jawaban
        response = await rag_service.generate_response(request, chat_history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- KNOWLEDGE BASE ENDPOINTS ---
@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document():
    """
    FR-KM-01: Endpoint untuk mengunggah dokumen baru ke Ingestion Pipeline.
    (Saat ini mock-up, akan diintegrasikan dengan modul file upload/S3).
    """
    # TODO: Panggil ingestion_service (memilah chunk, embedding, simpan ke VectorDB)
    return DocumentUploadResponse(
        document_id="doc-mock-123",
        status="queued",
        message="Dokumen berhasil masuk antrean pemrosesan."
    )

@router.get("/documents")
async def list_documents():
    """
    FR-KM-05: Mengambil daftar dokumen beserta status indexing untuk ditampilkan di tabel Admin.
    """
    # TODO: Panggil database service untuk query tabel DocumentRecord
    return [
        {"id": "doc-1", "title": "Kebijakan Pengembalian Dana.pdf", "status": "indexed", "date": "2026-08-23"},
        {"id": "doc-2", "title": "FAQ_Produk_v2.docx", "status": "processing", "date": "2026-08-23"},
        {"id": "doc-3", "title": "Syarat_Ketentuan.html", "status": "failed", "date": "2026-08-22"},
    ]